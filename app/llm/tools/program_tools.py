"""
Enhanced program generation tools for intelligent workout program creation.
Creates research-backed, goal-oriented workout programs with smart exercise selection.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from agents import function_tool
from pydantic import BaseModel
from app.hevy.client import HevyClient
from app.models import *
from app.llm.config import DEFAULT_REST_SECONDS, DEFAULT_REPS, DEFAULT_REP_RANGE, DEFAULT_EXERCISE_NOTES, DEFAULT_NUM_OF_SETS
from app.services.exercise_analyzer import exercise_analyzer

logger = logging.getLogger(__name__)

# Enhanced program models
class ProgramRoutineTemplate(BaseModel):
    name: str
    notes: Optional[str] = None
    exercise_template_ids: List[str]
    target_muscle_groups: List[str] = []
    estimated_duration_minutes: Optional[int] = None

class WorkoutProgramTemplate(BaseModel):
    program_name: str
    program_notes: Optional[str] = None
    routines: List[ProgramRoutineTemplate]
    target_goals: List[str] = []
    experience_level: str = "intermediate"
    estimated_weeks: Optional[int] = None

# Initialize client
hevy_client = HevyClient()

def _create_default_exercise(exercise_template_id: str, rep_range: List[int] = None, rest_seconds: int = None) -> ExerciseCreate:
    """Create a default exercise configuration with optional customization."""
    rep_range = rep_range or DEFAULT_REP_RANGE
    rest_seconds = rest_seconds or DEFAULT_REST_SECONDS
    
    return ExerciseCreate(
        exercise_template_id=exercise_template_id,
        superset_id=None,
        rest_seconds=rest_seconds,
        notes=DEFAULT_EXERCISE_NOTES,
        sets=[
            SetCreate(
                type="normal",
                weight_kg=None,
                reps=DEFAULT_REPS,
                distance_meters=None,
                duration_seconds=None,
                custom_metric=None,
                rep_range=RepRange(start=rep_range[0], end=rep_range[1])
            )
        ]
    )

@function_tool
def generate_workout_program(
    program_name: str,
    primary_goal: str,
    target_physique: str = None,
    focus_areas: str = "",
    days_per_week: int = 4,
    session_duration: int = 60,
    experience_level: str = "intermediate",
    equipment: str = "gym"
) -> Dict[str, Any]:
    """Generate a complete workout program based on user goals and constraints.
    
    Creates an intelligent, research-backed workout program tailored to the user's
    specific goals, experience level, and available time. The program includes
    multiple routines designed to work together for optimal results.
    
    Args:
        program_name: Name for the workout program
        primary_goal: Main objective ("strength", "hypertrophy", "aesthetic", "endurance")
        target_physique: Desired body type ("surfer", "model", "powerlifter", etc.)
        focus_areas: Specific areas to emphasize (comma-separated: "upper_body,chest,arms")
        days_per_week: Number of training days per week (3-6)
        session_duration: Available time per session in minutes (30-120)
        experience_level: Training experience ("beginner", "intermediate", "advanced")
        equipment: Available equipment (comma-separated: "gym,home,minimal")
    
    Returns:
        dict: Complete program structure ready for creation with routine details
    
    Example:
        >>> generate_workout_program("Surfer Physique", "aesthetic", "surfer", "upper_body", 4, 60)
    """
    logger.info(f"🔧 Tool called: generate_workout_program for {primary_goal} goal")
    
    # Parse comma-separated strings to lists
    equipment_list = [eq.strip() for eq in equipment.split(",") if eq.strip()] if equipment else ["gym"]
    focus_areas_list = [fa.strip() for fa in focus_areas.split(",") if fa.strip()] if focus_areas else []
    
    # Determine program template based on goals and constraints
    program_template = _select_program_template(
        primary_goal, target_physique, days_per_week, experience_level, focus_areas_list
    )
    
    # Generate routines for the program
    routines = []
    for routine_template in program_template["routines"]:
        exercise_template_ids = _select_exercises_for_routine(
            routine_template["target_muscle_groups"],
            routine_template["exercise_count"],
            primary_goal,
            experience_level,
            equipment_list,
            focus_areas_list
        )
        
        # Estimate duration
        estimated_duration = len(exercise_template_ids) * 8 + 10  # ~8 min per exercise + warmup
        
        routine = ProgramRoutineTemplate(
            name=routine_template["name"],
            notes=routine_template["notes"],
            exercise_template_ids=exercise_template_ids,
            target_muscle_groups=routine_template["target_muscle_groups"],
            estimated_duration_minutes=min(estimated_duration, session_duration)
        )
        routines.append(routine)
    
    # Create program structure
    program = WorkoutProgramTemplate(
        program_name=program_name,
        program_notes=f"Generated for {primary_goal} goal targeting {target_physique or 'general fitness'}. {days_per_week} days/week program.",
        routines=routines,
        target_goals=[primary_goal] + focus_areas_list,
        experience_level=experience_level,
        estimated_weeks=program_template.get("duration_weeks", 8)
    )
    
    return {
        "program_generated": True,
        "program_template": program.model_dump(),
        "routines_count": len(routines),
        "total_exercises": sum(len(r.exercise_template_ids) for r in routines),
        "program_summary": f"{program_name}: {len(routines)} routines, {primary_goal} focus, {days_per_week}x/week",
        "next_step": "Use create_workout_program() to save this program to Hevy",
        "preview": {
            "routine_names": [r.name for r in routines],
            "target_muscle_groups": list(set(mg for r in routines for mg in r.target_muscle_groups))
        }
    }

@function_tool
def create_routine(routine_title: str, notes: str, exercise_template_ids: str) -> Dict[str, Any]:
    """Create a new workout routine with specified exercises.
    
    Creates and saves a new workout routine to the Hevy API with the specified
    exercises. Each exercise is configured with default settings (3 sets, 8-12 reps,
    90 seconds rest) that can be adjusted later.
    
    Args:
        routine_title: The name/title for the new routine.
        notes: Optional notes or description for the routine.
        exercise_template_ids: Comma-separated list of exercise template IDs to include in the routine.
            Each ID corresponds to a specific exercise from the exercise database.
    
    Returns:
        dict: Creation status including success status, routine title, and routine ID.
    
    Example:
        >>> create_routine("Push Day", "Focus on chest, shoulders, triceps", "ex_1,ex_2,ex_3")
        >>> create_routine("Full Body", "Complete workout", "squat,bench,deadlift")
    """
    # Parse comma-separated exercise IDs
    exercise_ids_list = [ex_id.strip() for ex_id in exercise_template_ids.split(",") if ex_id.strip()]
    logger.info(f"🔧 Tool called: create_routine with {len(exercise_ids_list)} exercises")
    
    exercises = [_create_default_exercise(exercise_id) for exercise_id in exercise_ids_list]
    
    routine_payload = RoutineCreate(
        title=routine_title,
        folder_id=None,
        notes=notes,
        exercises=exercises
    )
    
    payload = RoutineCreatePayload(routine=routine_payload)
    
    try:
        routine = hevy_client.create_routine(payload)
        logger.info(f"✅ create_routine completed successfully, created routine: {routine.title}")
        return {
            "status": "success", 
            "routine_title": routine_title, 
            "routine_id": routine.id
        }
    except Exception as e:
        logger.error(f"❌ create_routine failed: {str(e)}")
        raise

@function_tool
def create_workout_program(program_data: str) -> str:
    """Create a complete workout program from generated program structure.
    
    Takes a program template (from generate_workout_program) and creates all
    routines in Hevy, organized in a program folder for easy access.
    
    Args:
        program_data: JSON string containing program structure with:
            - program_name: Name of the program  
            - program_notes: Optional description
            - routines: List of routines, each with:
                - name: Routine name
                - notes: Optional routine notes
                - exercise_template_ids: List of exercise template IDs
    
    Returns:
        str: Success message with program creation details
    
    Example JSON structure:
    {
        "program_name": "PPL Hypertrophy",
        "program_notes": "Push/Pull/Legs split for muscle growth",
        "routines": [
            {
                "name": "Push Day",
                "notes": "Chest, shoulders, triceps",
                "exercise_template_ids": ["68CE0B9B", "99C1F2AD", "37FCC2BB"]
            }
        ]
    }
    """
    logger.info(f"🔧 Tool called: create_workout_program")
    
    try:
        program_dict = json.loads(program_data)
        
        # Fix exercise_template_ids if they come as strings instead of lists
        if "routines" in program_dict:
            for routine in program_dict["routines"]:
                if "exercise_template_ids" in routine:
                    template_ids = routine["exercise_template_ids"]
                    # If it's a string, convert to list
                    if isinstance(template_ids, str):
                        routine["exercise_template_ids"] = [id.strip() for id in template_ids.split(",") if id.strip()]
        
        program_template = WorkoutProgramTemplate(**program_dict)
        
        # Validate exercise template IDs before creating
        all_exercise_ids = []
        for routine in program_template.routines:
            all_exercise_ids.extend(routine.exercise_template_ids)
        
        logger.info(f"Program: {program_template.program_name} with {len(program_template.routines)} routines")
        logger.info(f"Exercise IDs to validate: {all_exercise_ids}")
        
        # Validate that all exercise IDs exist in our database
        from app.services.exercise_analyzer import exercise_analyzer
        valid_ids = set(ex.id for ex in exercise_analyzer.exercises)
        invalid_ids = [ex_id for ex_id in all_exercise_ids if ex_id not in valid_ids]
        
        if invalid_ids:
            logger.error(f"Invalid exercise template IDs: {invalid_ids}")
            # Try to find similar exercises as suggestions
            suggestions = []
            for invalid_id in invalid_ids[:3]:  # Limit suggestions
                # Find exercises with similar IDs or names
                similar = [ex for ex in exercise_analyzer.exercises if invalid_id.lower() in ex.title.lower() or ex.id.startswith(invalid_id[:4])]
                if similar:
                    suggestions.append(f"{invalid_id} -> try {similar[0].id} ({similar[0].title})")
            
            suggestion_text = " Suggestions: " + "; ".join(suggestions) if suggestions else ""
            return f"❌ Error: Invalid exercise template IDs found: {invalid_ids}.{suggestion_text} Please use valid IDs from the exercise database."
        
        result = _create_program_in_hevy(program_template)
        return f"✅ Created '{program_template.program_name}' with {len(result['routines'])} routines! Program folder ID: {result['folder'].id}"
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return f"❌ Error: Invalid JSON format - {str(e)}"
    except Exception as e:
        logger.error(f"Program creation error: {str(e)}")
        return f"❌ Error creating program: {str(e)}"

def _select_program_template(goal: str, physique: str, days_per_week: int, experience: str, focus_areas: List[str]) -> Dict[str, Any]:
    """Select appropriate program template based on user parameters."""
    
    # Upper body focused programs for aesthetic goals
    if "upper_body" in focus_areas or physique in ["surfer", "model"]:
        if days_per_week >= 4:
            return {
                "type": "upper_lower_focused",
                "duration_weeks": 8,
                "routines": [
                    {
                        "name": "Upper Body Power",
                        "notes": "Heavy compound movements for upper body strength",
                        "target_muscle_groups": ["chest", "back", "shoulders", "arms"],
                        "exercise_count": 6
                    },
                    {
                        "name": "Lower Body",
                        "notes": "Complete lower body development",
                        "target_muscle_groups": ["legs", "glutes"],
                        "exercise_count": 5
                    },
                    {
                        "name": "Upper Body Hypertrophy",
                        "notes": "Volume-focused upper body for muscle growth",
                        "target_muscle_groups": ["chest", "back", "shoulders", "arms"],
                        "exercise_count": 7
                    },
                    {
                        "name": "Athletic/Core",
                        "notes": "Functional movement and core strength",
                        "target_muscle_groups": ["core", "shoulders", "back"],
                        "exercise_count": 5
                    }
                ]
            }
    
    # Classic Push/Pull/Legs for hypertrophy
    if goal == "hypertrophy" and days_per_week >= 3:
        routines_base = [
            {
                "name": "Push Day",
                "notes": "Chest, shoulders, and triceps",
                "target_muscle_groups": ["chest", "shoulders", "arms"],
                "exercise_count": 6
            },
            {
                "name": "Pull Day", 
                "notes": "Back and biceps",
                "target_muscle_groups": ["back", "arms"],
                "exercise_count": 6
            },
            {
                "name": "Leg Day",
                "notes": "Legs and glutes",
                "target_muscle_groups": ["legs", "glutes"],
                "exercise_count": 6
            }
        ]
        
        # Add extra days if available
        if days_per_week >= 6:
            routines_base.extend([
                {
                    "name": "Push Day 2",
                    "notes": "Chest, shoulders, and triceps - variation",
                    "target_muscle_groups": ["chest", "shoulders", "arms"],
                    "exercise_count": 6
                },
                {
                    "name": "Pull Day 2",
                    "notes": "Back and biceps - variation", 
                    "target_muscle_groups": ["back", "arms"],
                    "exercise_count": 6
                },
                {
                    "name": "Leg Day 2",
                    "notes": "Legs and glutes - variation",
                    "target_muscle_groups": ["legs", "glutes"],
                    "exercise_count": 6
                }
            ])
        elif days_per_week >= 4:
            routines_base.append({
                "name": "Upper Body Focus",
                "notes": "Additional upper body volume",
                "target_muscle_groups": ["chest", "back", "shoulders", "arms"],
                "exercise_count": 5
            })
            
        return {
            "type": "push_pull_legs",
            "duration_weeks": 8,
            "routines": routines_base
        }
    
    # Upper/Lower split for strength or 4-day programs
    if goal == "strength" or days_per_week == 4:
        return {
            "type": "upper_lower",
            "duration_weeks": 8,
            "routines": [
                {
                    "name": "Upper Body Strength",
                    "notes": "Heavy compound upper body movements",
                    "target_muscle_groups": ["chest", "back", "shoulders", "arms"],
                    "exercise_count": 6
                },
                {
                    "name": "Lower Body Strength",
                    "notes": "Heavy compound lower body movements",
                    "target_muscle_groups": ["legs", "glutes"],
                    "exercise_count": 5
                },
                {
                    "name": "Upper Body Volume",
                    "notes": "Higher volume upper body training",
                    "target_muscle_groups": ["chest", "back", "shoulders", "arms"],
                    "exercise_count": 7
                },
                {
                    "name": "Lower Body Volume",
                    "notes": "Higher volume lower body training",
                    "target_muscle_groups": ["legs", "glutes"],
                    "exercise_count": 6
                }
            ]
        }
    
    # Full body for beginners or 3-day programs
    return {
        "type": "full_body",
        "duration_weeks": 6,
        "routines": [
            {
                "name": "Full Body A",
                "notes": "Complete body workout with compound movements",
                "target_muscle_groups": ["chest", "back", "legs", "shoulders"],
                "exercise_count": 6
            },
            {
                "name": "Full Body B",
                "notes": "Complete body workout with exercise variations",
                "target_muscle_groups": ["chest", "back", "legs", "shoulders"],
                "exercise_count": 6
            },
            {
                "name": "Full Body C",
                "notes": "Complete body workout with accessory focus",
                "target_muscle_groups": ["chest", "back", "legs", "shoulders", "arms"],
                "exercise_count": 7
            }
        ]
    }

def _select_exercises_for_routine(target_muscle_groups: List[str], exercise_count: int, goal: str, experience: str, equipment: List[str], focus_areas: List[str]) -> List[str]:
    """Select appropriate exercises for a routine based on parameters and return template IDs."""
    
    selected_exercises = []
    exercises_per_group = max(1, exercise_count // len(target_muscle_groups))
    
    # Priority order based on goal
    if goal == "strength":
        movement_priority = ["compound", "isolation"]
        equipment_priority = ["barbell", "dumbbell", "machine"]
    else:  # hypertrophy/aesthetic
        movement_priority = ["compound", "isolation"] 
        equipment_priority = ["dumbbell", "barbell", "machine", "cable"]
    
    for muscle_group in target_muscle_groups:
        group_exercises = exercise_analyzer.get_exercises_by_muscle_group(muscle_group)
        
        # Filter by available equipment
        available_exercises = [
            ex for ex in group_exercises 
            if any(eq in equipment for eq in ["gym"]) or ex.equipment in equipment
        ]
        
        if not available_exercises:
            continue
            
        # Prioritize compound movements for main muscle groups
        if muscle_group in ["chest", "back", "legs"]:
            compound_exercises = [ex for ex in available_exercises if ex.type == "weight_reps"]
            if compound_exercises:
                selected_exercises.extend(compound_exercises[:exercises_per_group])
            else:
                selected_exercises.extend(available_exercises[:exercises_per_group])
        else:
            # Mix of compound and isolation for smaller muscle groups
            selected_exercises.extend(available_exercises[:exercises_per_group])
    
    # Ensure we don't exceed the target count
    selected_exercises = selected_exercises[:exercise_count]
    
    # Fill remaining slots if needed
    while len(selected_exercises) < exercise_count:
        # Add more exercises from focus areas or popular choices
        all_available = exercise_analyzer.exercises
        remaining_exercises = [ex for ex in all_available if ex not in selected_exercises]
        if remaining_exercises:
            selected_exercises.append(remaining_exercises[0])
        else:
            break
    
    # Return just the template IDs (strings)
    return [ex.id for ex in selected_exercises]

def _create_program_in_hevy(program: WorkoutProgramTemplate) -> dict:
    """Create the program in Hevy with folder organization."""
    
    # Create program folder
    folder = hevy_client.create_routine_folder(program.program_name)
    folder_id = folder.id
    
    created_routines = []
    
    # Create each routine in the program folder
    for routine_template in program.routines:
        exercises = []
        for exercise_id in routine_template.exercise_template_ids:
            # Create exercise with proper set structure (matching working version exactly)
            exercise = ExerciseCreate(
                exercise_template_id=exercise_id,
                rest_seconds=DEFAULT_REST_SECONDS,
                notes="",
                sets=[SetCreate(
                    type="normal",
                    reps=DEFAULT_REPS,
                    rep_range=RepRange(
                        start=DEFAULT_REP_RANGE[0],
                        end=DEFAULT_REP_RANGE[1]
                    )
                ) for _ in range(DEFAULT_NUM_OF_SETS)]
            )
            exercises.append(exercise)
        
        routine = RoutineCreate(
            title=routine_template.name,
            folder_id=folder_id,
            notes=routine_template.notes,
            exercises=exercises
        )
        
        routine_payload = RoutineCreatePayload(routine=routine)
        created_routine = hevy_client.create_routine(routine_payload)
        created_routines.append(created_routine)
    
    return {
        "folder": folder,
        "routines": created_routines,
        "success": True,
    }

# Export all tools for easy importing
__all__ = [
    'generate_workout_program',
    'create_routine',
    'create_workout_program'
]