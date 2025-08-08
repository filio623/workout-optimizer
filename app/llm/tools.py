"""
Function tools for the LLM agent.
"""

import logging
from typing import List, Dict, Any
from agents import function_tool
from app.hevy.client import HevyClient
from app.models import *
from app.services.workout_analyzer import WorkoutAnalyzer
from app.services.exercise_analyzer import exercise_analyzer
from app.llm.config import DEFAULT_REST_SECONDS, DEFAULT_REPS, DEFAULT_REP_RANGE, DEFAULT_EXERCISE_NOTES
import dateparser

logger = logging.getLogger(__name__)

# Initialize Hevy client
hevy_client = HevyClient()

def _create_default_exercise(exercise_template_id: str) -> ExerciseCreate:
    """Create a default exercise configuration."""
    return ExerciseCreate(
        exercise_template_id=exercise_template_id,
        superset_id=None,
        rest_seconds=DEFAULT_REST_SECONDS,
        notes=DEFAULT_EXERCISE_NOTES,
        sets=[
            SetCreate(
                type="normal",
                weight_kg=None,
                reps=DEFAULT_REPS,
                distance_meters=None,
                duration_seconds=None,
                custom_metric=None,
                rep_range=RepRange(start=DEFAULT_REP_RANGE[0], end=DEFAULT_REP_RANGE[1])
            )
        ]
    )

@function_tool
def get_workout_data(time_period: str = "6 months", limit: int = 10) -> Dict[str, Any]:
    """Retrieve workout data for analysis over a specified time period.
    
    This tool fetches workout data from the Hevy API and returns it in a format suitable
    for analysis. The data includes workouts, exercises, and sets performed during the
    specified time period. Data is limited to prevent context length issues.
    
    Args:
        time_period: Natural language time period to analyze. Examples: "past year", 
            "last month", "3 weeks ago", "6 months", "all time". Defaults to "6 months".
        limit: Maximum number of workouts to return. Defaults to 50 to avoid context 
            length issues.
    
    Returns:
        dict: A dictionary containing:
            - workouts: List of workout data (limited to specified count)
            - exercises: List of exercise data (limited to 100)
            - sets: List of set data (limited to 200)
            - time_period: The time period that was analyzed
            - summary: Summary statistics and metadata
    
    Example:
        >>> get_workout_data("past year", 25)
        >>> get_workout_data("last month")
        >>> get_workout_data("all time", 100)
    """
    logger.info(f"🔧 Tool called: get_workout_data with time_period={time_period}")
    
    # Create analyzer and load data
    analyzer = WorkoutAnalyzer()
    
    # Parse the time period to get cutoff date
    if time_period.lower() != "all time":
        cutoff_date = dateparser.parse(time_period)
        if cutoff_date:
            # Filter workouts from cutoff date to now
            analyzer.workouts_df = analyzer.workouts_df[
                analyzer.workouts_df['start_time'] >= cutoff_date
            ]
            logger.info(f"Filtered workouts from {cutoff_date} to now")
    
    # Convert DataFrames to dictionaries (agent-friendly format) with limits
    workouts_data = analyzer.workouts_df.head(limit).to_dict('records')
    
    # Limit exercises and sets to avoid context length issues
    exercises_data = analyzer.exercises_df.head(20).to_dict('records')  # Limit to 20 exercises
    sets_data = analyzer.sets_df.head(50).to_dict('records')  # Limit to 50 sets
    
    return {
        "workouts": workouts_data,
        "exercises": exercises_data,
        "sets": sets_data,
        "time_period": time_period,
        "summary": {
            "total_workouts": len(workouts_data),
            "total_exercises": len(exercises_data),
            "total_sets": len(sets_data),
            "date_range": f"From {time_period} ago to now",
            "note": f"Showing limited data (max {limit} workouts, 20 exercises, 50 sets) to avoid context length issues"
        }
    }

@function_tool
def get_exercise_data(muscle_group: str = None, equipment: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve exercise templates filtered by muscle group and equipment.
    
    This tool provides access to the exercise database, allowing filtering by muscle
    groups and equipment types. Useful for creating targeted workout routines and
    providing exercise recommendations.
    
    Args:
        muscle_group: Primary muscle group to filter by. Examples: "chest", "back", 
            "legs", "shoulders", "arms", "core", "full body". If None, returns all exercises.
        equipment: Equipment type to filter by. Examples: "barbell", "dumbbell", 
            "machine", "bodyweight", "cable", "kettlebell". If None, returns all equipment types.
        limit: Maximum number of exercises to return. Defaults to 50.
    
    Returns:
        list: List of exercise dictionaries containing exercise template data including
            id, title, muscle groups, equipment, and exercise type.
    
    Example:
        >>> get_exercise_data("chest", "barbell", 10)
        >>> get_exercise_data("legs", limit=20)
        >>> get_exercise_data(equipment="bodyweight")
    """
    logger.info(f"🔧 Tool called: get_exercise_data with muscle_group={muscle_group}, equipment={equipment}")
    
    # Get exercises based on filters
    if muscle_group:
        exercises = exercise_analyzer.get_exercises_by_muscle_group(muscle_group)
    else:
        exercises = exercise_analyzer.exercises
    
    # Filter by equipment if specified
    if equipment:
        exercises = [ex for ex in exercises if ex.equipment == equipment]
    
    # Convert to dictionaries and limit results
    exercise_data = [exercise.model_dump() for exercise in exercises[:limit]]
    
    return exercise_data

@function_tool
def get_workout_by_id(workout_id: str) -> Dict[str, Any]:
    """Retrieve a specific workout by its unique identifier.
    
    Fetches detailed information about a single workout including all exercises,
    sets, weights, reps, and metadata.
    
    Args:
        workout_id: The unique identifier of the workout to retrieve.
    
    Returns:
        dict: Complete workout data including exercises, sets, and metadata.
    
    Example:
        >>> get_workout_by_id("workout_12345")
    """
    logger.info(f"🔧 Tool called: get_workout_by_id with workout_id={workout_id}")
    workout = hevy_client.get_workout_by_id(workout_id)
    logger.info(f"✅ get_workout_by_id completed successfully")
    return workout

@function_tool
def get_workouts() -> Dict[str, Any]:
    """Retrieve a list of recent workouts from the Hevy API.
    
    Fetches the user's workout history, typically the most recent workouts.
    Useful for getting an overview of recent training activity.
    
    Returns:
        dict: Paginated list of workouts with metadata including workout count
            and pagination information.
    
    Example:
        >>> get_workouts()
    """
    logger.info(f"🔧 Tool called: get_workouts")
    workouts = hevy_client.get_workouts()
    logger.info(f"✅ get_workouts completed successfully, returned {len(workouts.workouts)} workouts")
    return workouts

@function_tool
def get_routine_by_id(routine_id: str) -> Dict[str, Any]:
    """Retrieve a specific workout routine by its unique identifier.
    
    Fetches detailed information about a saved routine including all exercises,
    sets, and routine metadata.
    
    Args:
        routine_id: The unique identifier of the routine to retrieve.
    
    Returns:
        dict: Complete routine data including exercises, sets, and metadata.
    
    Example:
        >>> get_routine_by_id("routine_67890")
    """
    logger.info(f"🔧 Tool called: get_routine_by_id with routine_id={routine_id}")
    routine = hevy_client.get_routine_by_id(routine_id)
    logger.info(f"✅ get_routine_by_id completed successfully")
    return routine

@function_tool
def get_routines() -> Dict[str, Any]:
    """Retrieve a list of saved workout routines from the Hevy API.
    
    Fetches all user-created routines that can be used for workouts.
    Useful for reviewing existing routines and selecting one to use.
    
    Returns:
        dict: Paginated list of routines with metadata including routine count
            and pagination information.
    
    Example:
        >>> get_routines()
    """
    logger.info(f"🔧 Tool called: get_routines")
    routines = hevy_client.get_routines()
    logger.info(f"✅ get_routines completed successfully, returned {len(routines.routines)} routines")
    return routines

@function_tool
def create_routine(routine_title: str, notes: str, exercise_template_ids: List[str]) -> Dict[str, Any]:
    """Create a new workout routine with specified exercises.
    
    Creates and saves a new workout routine to the Hevy API with the specified
    exercises. Each exercise is configured with default settings (3 sets, 8-12 reps,
    90 seconds rest) that can be adjusted later.
    
    Args:
        routine_title: The name/title for the new routine.
        notes: Optional notes or description for the routine.
        exercise_template_ids: List of exercise template IDs to include in the routine.
            Each ID corresponds to a specific exercise from the exercise database.
    
    Returns:
        dict: Creation status including success status, routine title, and routine ID.
    
    Example:
        >>> create_routine("Push Day", "Focus on chest, shoulders, triceps", ["ex_1", "ex_2", "ex_3"])
        >>> create_routine("Full Body", "Complete workout", ["squat", "bench", "deadlift"])
    """
    logger.info(f"🔧 Tool called: create_routine with {len(exercise_template_ids)} exercises")
    
    exercises = [_create_default_exercise(exercise_id) for exercise_id in exercise_template_ids]
    
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
def update_routine(routine_title: str, notes: str, exercise_template_ids: List[str]) -> Dict[str, Any]:
    """Updates a workout routine.
    
    Creates and saves a new workout routine to the Hevy API with the specified
    exercises. Each exercise is configured with default settings (3 sets, 8-12 reps,
    90 seconds rest) that can be adjusted later.
    
    Args:
        routine_title: The name/title for the new routine.
        notes: Optional notes or description for the routine.
        exercise_template_ids: List of exercise template IDs to include in the routine.
            Each ID corresponds to a specific exercise from the exercise database.
    
    Returns:
        dict: Creation status including success status, routine title, and routine ID.
    
    Example:
        >>> create_routine("Push Day", "Focus on chest, shoulders, triceps", ["ex_1", "ex_2", "ex_3"])
        >>> create_routine("Full Body", "Complete workout", ["squat", "bench", "deadlift"])
    """
    logger.info(f"🔧 Tool called: update_routine with {len(exercise_template_ids)} exercises")
    
    exercises = [_create_default_exercise(exercise_id) for exercise_id in exercise_template_ids]
    
    routine_payload = RoutineCreate(
        title=routine_title,
        folder_id=None,
        notes=notes,
        exercises=exercises
    )
    
    payload = RoutineCreatePayload(routine=routine_payload)
    
    try:
        routine = hevy_client.update_routine(payload)
        logger.info(f"✅ create_routine completed successfully, created routine: {routine.title}")
        return {
            "status": "success", 
            "routine_title": routine_title, 
            "routine_id": routine.id
        }
    except Exception as e:
        logger.error(f"❌ create_routine failed: {str(e)}")
        raise

# Export all tools for easy importing
__all__ = [
    'get_workout_data',
    'get_exercise_data', 
    'get_workout_by_id',
    'get_workouts',
    'get_routine_by_id',
    'get_routines',
    'create_routine'
] 