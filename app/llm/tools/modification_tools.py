"""
Routine modification tools for exercise swapping and workout optimization.
Enables intelligent exercise substitution and real-time routine updates.
"""

import logging
from typing import List, Dict, Any, Optional
from agents import function_tool
from app.hevy.client import HevyClient
from app.models import *
from app.services.exercise_analyzer import exercise_analyzer
from app.llm.config import DEFAULT_REST_SECONDS, DEFAULT_REPS, DEFAULT_REP_RANGE, DEFAULT_EXERCISE_NOTES

logger = logging.getLogger(__name__)

# Initialize client
hevy_client = HevyClient()

@function_tool
def find_exercise_alternatives(
    exercise_name: str,
    muscle_group: str = None,
    equipment: str = "gym",
    limit: int = 5
) -> Dict[str, Any]:
    """Find alternative exercises for substitution based on muscle group and equipment.
    
    Searches for exercises that target the same primary muscle group and can be
    performed with available equipment. Useful for creating exercise variations
    or replacing exercises the user dislikes.
    
    Args:
        exercise_name: Name of the exercise to find alternatives for
        muscle_group: Target muscle group (optional, will be inferred if not provided)
        equipment: Available equipment types (comma-separated: "gym,home,minimal")
        limit: Maximum number of alternatives to return
    
    Returns:
        dict: List of alternative exercises with details and similarity scoring
    
    Example:
        >>> find_exercise_alternatives("Bench Press", equipment="gym")
        >>> find_exercise_alternatives("Push-ups", "chest", "home")
    """
    logger.info(f"🔧 Tool called: find_exercise_alternatives for {exercise_name}")
    
    # Parse equipment list
    equipment_list = [eq.strip() for eq in equipment.split(",") if eq.strip()] if equipment else ["gym"]
    
    # Find the original exercise to understand its characteristics
    original_exercise = None
    for exercise in exercise_analyzer.exercises:
        if exercise_name.lower() in exercise.title.lower():
            original_exercise = exercise
            break
    
    if not original_exercise:
        return {
            "success": False,
            "error": f"Could not find exercise '{exercise_name}' in database",
            "suggestion": "Try a more specific or different exercise name"
        }
    
    # Use provided muscle group or infer from original exercise
    target_muscle_group = muscle_group or original_exercise.primary_muscle_group
    
    # Get exercises for the same muscle group
    similar_exercises = exercise_analyzer.get_exercises_by_muscle_group(target_muscle_group)
    
    # Filter by equipment availability
    available_alternatives = []
    for exercise in similar_exercises:
        # Skip the original exercise
        if exercise.id == original_exercise.id:
            continue
            
        # Check equipment compatibility
        if "gym" in equipment_list or exercise.equipment in equipment_list:
            # Calculate similarity score based on multiple factors
            similarity_score = _calculate_exercise_similarity(original_exercise, exercise)
            
            available_alternatives.append({
                "id": exercise.id,
                "title": exercise.title,
                "equipment": exercise.equipment,
                "type": exercise.type,
                "primary_muscle_group": exercise.primary_muscle_group,
                "secondary_muscle_groups": exercise.secondary_muscle_groups,
                "similarity_score": similarity_score,
                "reason": _get_substitution_reason(original_exercise, exercise)
            })
    
    # Sort by similarity score and limit results
    available_alternatives.sort(key=lambda x: x["similarity_score"], reverse=True)
    top_alternatives = available_alternatives[:limit]
    
    return {
        "success": True,
        "original_exercise": {
            "title": original_exercise.title,
            "muscle_group": original_exercise.primary_muscle_group,
            "equipment": original_exercise.equipment
        },
        "alternatives_found": len(top_alternatives),
        "alternatives": top_alternatives,
        "summary": f"Found {len(top_alternatives)} alternatives for {exercise_name} targeting {target_muscle_group}"
    }

@function_tool
def swap_exercise_in_routine(
    routine_id: str,
    old_exercise_name: str,
    new_exercise_id: str,
    reason: str = "User requested substitution"
) -> Dict[str, Any]:
    """Replace an exercise in an existing routine with a new exercise.
    
    Updates a routine by replacing one exercise with another, maintaining
    the same set structure and position in the routine.
    
    Args:
        routine_id: ID of the routine to modify
        old_exercise_name: Name of the exercise to replace
        new_exercise_id: ID of the new exercise template to use
        reason: Reason for the substitution (for notes)
    
    Returns:
        dict: Success status and details of the modification
    
    Example:
        >>> swap_exercise_in_routine("routine_123", "Bench Press", "68CE0B9B", "Better for home gym")
    """
    logger.info(f"🔧 Tool called: swap_exercise_in_routine for routine {routine_id}")
    
    try:
        # Get the current routine
        current_routine = hevy_client.get_routine_by_id(routine_id)
        
        # Find the exercise to replace
        exercise_to_replace = None
        exercise_index = None
        
        for i, exercise in enumerate(current_routine.exercises):
            if old_exercise_name.lower() in exercise.title.lower():
                exercise_to_replace = exercise
                exercise_index = i
                break
        
        if exercise_to_replace is None:
            return {
                "success": False,
                "error": f"Could not find exercise '{old_exercise_name}' in routine '{current_routine.title}'",
                "available_exercises": [ex.title for ex in current_routine.exercises]
            }
        
        # Get new exercise details
        new_exercise_template = None
        for template in exercise_analyzer.exercises:
            if template.id == new_exercise_id:
                new_exercise_template = template
                break
        
        if not new_exercise_template:
            return {
                "success": False,
                "error": f"Could not find exercise template with ID '{new_exercise_id}'"
            }
        
        # Create updated routine with swapped exercise
        updated_exercises = []
        for i, exercise in enumerate(current_routine.exercises):
            if i == exercise_index:
                # Replace with new exercise, keeping similar set structure
                new_exercise = ExerciseCreate(
                    exercise_template_id=new_exercise_id,
                    superset_id=exercise.superset_id,
                    rest_seconds=exercise.rest_seconds or DEFAULT_REST_SECONDS,
                    notes=f"Substituted for {old_exercise_name}. {reason}",
                    sets=[
                        SetCreate(
                            type=set_item.type,
                            weight_kg=set_item.weight_kg,
                            reps=set_item.reps,
                            distance_meters=set_item.distance_meters,
                            duration_seconds=set_item.duration_seconds,
                            custom_metric=set_item.custom_metric,
                            rep_range=set_item.rep_range or RepRange(start=DEFAULT_REP_RANGE[0], end=DEFAULT_REP_RANGE[1])
                        )
                        for set_item in exercise.sets
                    ]
                )
                updated_exercises.append(new_exercise)
            else:
                # Keep existing exercise as-is
                updated_exercises.append(ExerciseCreate(
                    exercise_template_id=exercise.exercise_template_id,
                    superset_id=exercise.superset_id,
                    rest_seconds=exercise.rest_seconds,
                    notes=exercise.notes,
                    sets=[
                        SetCreate(
                            type=set_item.type,
                            weight_kg=set_item.weight_kg,
                            reps=set_item.reps,
                            distance_meters=set_item.distance_meters,
                            duration_seconds=set_item.duration_seconds,
                            custom_metric=set_item.custom_metric,
                            rep_range=set_item.rep_range
                        )
                        for set_item in exercise.sets
                    ]
                ))
        
        # Update the routine
        updated_routine = RoutineCreate(
            title=current_routine.title,
            folder_id=current_routine.folder_id,
            notes=f"{current_routine.notes or ''}\n\nModified: Replaced {old_exercise_name} with {new_exercise_template.title}",
            exercises=updated_exercises
        )
        
        # Update in Hevy (this requires updating the existing routine)
        payload = RoutineCreatePayload(routine=updated_routine)
        result = hevy_client.update_routine(routine_id, payload)
        
        return {
            "success": True,
            "routine_id": routine_id,
            "routine_title": current_routine.title,
            "old_exercise": old_exercise_name,
            "new_exercise": new_exercise_template.title,
            "reason": reason,
            "message": f"Successfully replaced '{old_exercise_name}' with '{new_exercise_template.title}' in routine '{current_routine.title}'"
        }
        
    except Exception as e:
        logger.error(f"❌ swap_exercise_in_routine failed: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to swap exercise: {str(e)}"
        }

@function_tool
def optimize_routine_for_goal(
    routine_id: str,
    optimization_goal: str,
    max_time_minutes: int = None,
    available_equipment: str = "gym"
) -> Dict[str, Any]:
    """Optimize an existing routine for a specific goal or constraint.
    
    Analyzes a routine and suggests modifications to better align with
    training goals, time constraints, or equipment limitations.
    
    Args:
        routine_id: ID of the routine to optimize
        optimization_goal: Goal to optimize for ("time_efficient", "hypertrophy", "strength", "home_gym")
        max_time_minutes: Maximum time constraint in minutes (optional)
        available_equipment: Available equipment (comma-separated: "gym,home,dumbbells")
    
    Returns:
        dict: Optimization suggestions and optional automatic implementation
    
    Example:
        >>> optimize_routine_for_goal("routine_123", "time_efficient", 45)
        >>> optimize_routine_for_goal("routine_456", "home_gym", available_equipment="dumbbells")
    """
    logger.info(f"🔧 Tool called: optimize_routine_for_goal for {optimization_goal}")
    
    # Parse equipment list and create constraints
    equipment_list = [eq.strip() for eq in available_equipment.split(",") if eq.strip()] if available_equipment else ["gym"]
    user_constraints = {
        "max_time": max_time_minutes,
        "equipment": equipment_list
    }
    
    try:
        # Get the current routine
        current_routine = hevy_client.get_routine_by_id(routine_id)
        
        # Analyze current routine
        analysis = _analyze_routine_for_optimization(current_routine, optimization_goal, user_constraints)
        
        # Generate optimization suggestions
        suggestions = _generate_optimization_suggestions(current_routine, optimization_goal, analysis, user_constraints)
        
        return {
            "success": True,
            "routine_title": current_routine.title,
            "optimization_goal": optimization_goal,
            "current_analysis": analysis,
            "optimization_suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "summary": f"Found {len(suggestions)} optimization opportunities for {optimization_goal} goal"
        }
        
    except Exception as e:
        logger.error(f"❌ optimize_routine_for_goal failed: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to optimize routine: {str(e)}"
        }

def _calculate_exercise_similarity(exercise1, exercise2) -> float:
    """Calculate similarity score between two exercises (0-100)."""
    score = 0
    
    # Primary muscle group match (40 points)
    if exercise1.primary_muscle_group == exercise2.primary_muscle_group:
        score += 40
    
    # Exercise type match (20 points)
    if exercise1.type == exercise2.type:
        score += 20
    
    # Equipment similarity (20 points)
    if exercise1.equipment == exercise2.equipment:
        score += 20
    elif (exercise1.equipment in ["barbell", "dumbbell"] and exercise2.equipment in ["barbell", "dumbbell"]):
        score += 15  # Free weights are similar
    elif (exercise1.equipment in ["machine", "cable"] and exercise2.equipment in ["machine", "cable"]):
        score += 15  # Machine-based exercises are similar
    
    # Secondary muscle group overlap (10 points)
    if exercise1.secondary_muscle_groups and exercise2.secondary_muscle_groups:
        overlap = set(exercise1.secondary_muscle_groups) & set(exercise2.secondary_muscle_groups)
        if overlap:
            score += 10
    
    # Movement pattern bonus (10 points for common patterns)
    movement_patterns = {
        "press": ["press", "push"],
        "pull": ["pull", "row", "chin", "pullup"],
        "squat": ["squat", "lunge"],
        "hinge": ["deadlift", "rdl", "goodmorning"]
    }
    
    for pattern, keywords in movement_patterns.items():
        ex1_has_pattern = any(keyword in exercise1.title.lower() for keyword in keywords)
        ex2_has_pattern = any(keyword in exercise2.title.lower() for keyword in keywords)
        if ex1_has_pattern and ex2_has_pattern:
            score += 10
            break
    
    return min(100, score)

def _get_substitution_reason(original, substitute) -> str:
    """Generate a reason for the exercise substitution."""
    reasons = []
    
    if original.equipment != substitute.equipment:
        reasons.append(f"Uses {substitute.equipment} instead of {original.equipment}")
    
    if original.type != substitute.type:
        reasons.append(f"Different exercise type ({substitute.type})")
    
    if substitute.equipment == "bodyweight":
        reasons.append("No equipment required")
    elif substitute.equipment == "dumbbell" and original.equipment == "barbell":
        reasons.append("More unilateral and stabilization challenge")
    elif substitute.equipment == "machine" and original.equipment in ["barbell", "dumbbell"]:
        reasons.append("More controlled movement pattern")
    
    if not reasons:
        reasons.append("Similar movement pattern and muscle activation")
    
    return "; ".join(reasons)

def _analyze_routine_for_optimization(routine, goal: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze routine for optimization opportunities."""
    
    analysis = {
        "total_exercises": len(routine.exercises),
        "estimated_duration": len(routine.exercises) * 8 + 10,  # Rough estimate
        "muscle_groups": [],
        "equipment_types": [],
        "exercise_types": [],
        "potential_issues": []
    }
    
    # Analyze exercises
    for exercise in routine.exercises:
        # Find exercise template
        template = None
        for t in exercise_analyzer.exercises:
            if t.id == exercise.exercise_template_id:
                template = t
                break
        
        if template:
            analysis["muscle_groups"].append(template.primary_muscle_group)
            analysis["equipment_types"].append(template.equipment)
            analysis["exercise_types"].append(template.type)
    
    # Count unique values
    analysis["unique_muscle_groups"] = len(set(analysis["muscle_groups"]))
    analysis["unique_equipment_types"] = len(set(analysis["equipment_types"]))
    
    # Identify potential issues based on goal
    if goal == "time_efficient":
        max_time = constraints.get("max_time", 45)
        if analysis["estimated_duration"] > max_time:
            analysis["potential_issues"].append(f"Routine too long ({analysis['estimated_duration']} min > {max_time} min target)")
        
        if analysis["total_exercises"] > 6:
            analysis["potential_issues"].append("Too many exercises for time efficiency")
    
    elif goal == "hypertrophy":
        if analysis["total_exercises"] < 4:
            analysis["potential_issues"].append("May need more exercises for adequate volume")
    
    elif goal == "home_gym":
        available_equipment = constraints.get("equipment", ["dumbbells"])
        problematic_equipment = [eq for eq in analysis["equipment_types"] if eq not in available_equipment and eq != "bodyweight"]
        if problematic_equipment:
            analysis["potential_issues"].append(f"Uses unavailable equipment: {set(problematic_equipment)}")
    
    return analysis

def _generate_optimization_suggestions(routine, goal: str, analysis: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate specific optimization suggestions."""
    
    suggestions = []
    
    if goal == "time_efficient":
        if analysis["total_exercises"] > 6:
            suggestions.append({
                "type": "remove_exercises",
                "priority": "high",
                "description": "Remove 1-2 isolation exercises to reduce workout time",
                "rationale": "Focus on compound movements for time efficiency"
            })
        
        # Suggest supersets
        if len(routine.exercises) >= 4:
            suggestions.append({
                "type": "create_supersets",
                "priority": "medium",
                "description": "Combine opposing muscle group exercises into supersets",
                "rationale": "Reduce rest time while maintaining training quality"
            })
    
    elif goal == "hypertrophy":
        if analysis["total_exercises"] < 6:
            suggestions.append({
                "type": "add_exercises",
                "priority": "high",
                "description": "Add 1-2 isolation exercises for target muscle groups",
                "rationale": "Increase training volume for muscle growth"
            })
    
    elif goal == "home_gym":
        available_equipment = constraints.get("equipment", ["dumbbells"])
        
        # Find exercises that need equipment substitution
        for i, exercise in enumerate(routine.exercises):
            template = None
            for t in exercise_analyzer.exercises:
                if t.id == exercise.exercise_template_id:
                    template = t
                    break
            
            if template and template.equipment not in available_equipment and template.equipment != "bodyweight":
                suggestions.append({
                    "type": "exercise_substitution",
                    "priority": "high",
                    "description": f"Replace {template.title} with home-friendly alternative",
                    "rationale": f"Current exercise requires {template.equipment}, not available in home setup",
                    "exercise_to_replace": template.title,
                    "target_muscle_group": template.primary_muscle_group
                })
    
    return suggestions

# Export all tools for easy importing
__all__ = [
    'find_exercise_alternatives',
    'swap_exercise_in_routine',
    'optimize_routine_for_goal'
]