from agents import Agent, Runner, function_tool
from app.hevy.client import HevyClient, HevyClientError
from app.config import config
import logging
from typing import List, Dict, Any
from app.models import *
from app.services.exercise_cache import exercise_cache

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


OPENAI_MODEL = config.OPENAI_MODEL
OPENAI_API_KEY = config.OPENAI_API_KEY

logger = logging.getLogger(__name__)

hevy_client = HevyClient()


# Configuration constants
DEFAULT_REST_SECONDS = 90
DEFAULT_REPS = 10
DEFAULT_REP_RANGE = (8, 12)
DEFAULT_EXERCISE_NOTES = "Focus on good form."


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
def get_workout_by_id(workout_id: str):
    """Get a specific workout by its ID."""
    logger.info(f"🔧 Tool called: get_workout_by_id with workout_id={workout_id}")
    workout = hevy_client.get_workout_by_id(workout_id)
    logger.info(f"✅ get_workout_by_id completed successfully")
    return workout

@function_tool
def get_workouts():
    """Get a list of recent workouts."""
    logger.info(f"🔧 Tool called: get_workouts")
    workouts = hevy_client.get_workouts()
    logger.info(f"✅ get_workouts completed successfully, returned {len(workouts.workouts)} workouts")
    return workouts

@function_tool
def get_routine_by_id(routine_id: str):
    """Get a specific routine by its ID."""
    logger.info(f"🔧 Tool called: get_routine_by_id with routine_id={routine_id}")
    routine = hevy_client.get_routine_by_id(routine_id)
    logger.info(f"✅ get_routine_by_id completed successfully")
    return routine

@function_tool
def get_routines():
    """Get a list of saved routines."""
    logger.info(f"🔧 Tool called: get_routines")
    routines = hevy_client.get_routines()
    logger.info(f"✅ get_routines completed successfully, returned {len(routines.routines)} routines")
    return routines

@function_tool
def get_exercise_templates():
    """Get all available exercise templates from the static file (instant access)."""
    logger.info(f"🔧 Tool called: get_exercise_templates")
    exercise_templates = exercise_cache.get_exercise_templates()
    logger.info(f"✅ get_exercise_templates completed successfully, returned {len(exercise_templates)} exercise templates")
    return exercise_templates

@function_tool
def refresh_exercise_cache():
    """Reload exercise templates from the static file."""
    logger.info(f"🔧 Tool called: refresh_exercise_cache")
    exercise_templates = exercise_cache.refresh_cache()
    logger.info(f"✅ refresh_exercise_cache completed successfully, reloaded {len(exercise_templates)} exercise templates")
    return {"status": "success", "exercise_count": len(exercise_templates)}

@function_tool
def get_cache_info():
    """Get information about the exercise templates static file."""
    logger.info(f"🔧 Tool called: get_cache_info")
    cache_info = exercise_cache.get_cache_info()
    logger.info(f"✅ get_cache_info completed successfully")
    return cache_info

@function_tool
def create_routine(routine_title: str, notes: str, exercise_template_ids: List[str]) -> Dict[str, Any]:
    """Create a new workout routine with the specified exercises."""
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


agent = Agent(
    name="Fitness Assistant",
    instructions="""
    You are a helpful and knowledgeable workout and fitness assistant. 
    Your role is to help the user manage their workouts, routines, and exercises through the Hevy platform.

    ### You can do the following:
    - Retrieve detailed information about the user's past workouts, including dates, exercises performed, sets, reps, and more.
    - Retrieve the user's saved routines, including specific exercises included in each routine.
    - Retrieve the list of available exercise templates that can be used to build new routines (now cached for faster access).
    - Provide clear and concise answers about the user's workout history and fitness tracking.

    ### You can also:
    - Create new workout routines when requested. 
    - When creating a new routine, you should:
        1. Retrieve the list of available exercises using the `get_exercise_templates` tool (instant access from static file).
        2. Select exercises based on user instructions (e.g., "choose 5 at random", "focus on chest").
        2a. After retrieving the list of available exercises, ensure you use the `exercise_template_id` values from the API, **not the exercise names**. Do not guess or substitute names as IDs.
        3. Ensure the selected exercises are formatted correctly for the `create_routine` tool.
        4. Provide a sensible name and description for the routine based on the user's goal or the theme of the exercises.
        5. Call the `create_routine` tool to create the routine.
        6. Confirm success back to the user, mentioning the routine name and how many exercises were included.

    ### Exercise Templates:
    - Exercise templates are loaded from a static JSON file for instant access.
    - You can use `refresh_exercise_cache` to reload the file if it's been updated.
    - You can use `get_cache_info` to check information about the exercise file.

    ### General Guidelines:
    - Be proactive in using available tools to retrieve the necessary information before answering or creating something.
    - Always ensure the data you provide the user is accurate and sourced from the latest API results.
    - For creating routines, only use exercises from the available exercise templates.
    - For any multi-step reasoning, break down the problem and think step-by-step.

    ### Examples of what you can do:
    - "What was my workout yesterday?" → Retrieve workouts and provide details.
    - "How many sets did I do on Monday?" → Retrieve and summarize.
    - "Create a random routine for me with 5 exercises." → Retrieve exercises, choose 5, format, create routine, confirm.
    - "Create a chest-focused routine." → Retrieve exercises, pick relevant ones, format, create routine, confirm.
    - "Check exercise file info" → Get information about the static exercise templates file.
    """,
    model=OPENAI_MODEL,
    tools=[get_workout_by_id, get_workouts, get_routine_by_id, get_routines, get_exercise_templates, refresh_exercise_cache, get_cache_info, create_routine],
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    result = Runner.run_sync(agent, "Create a routine for me with 5 exercises")

    print(result.final_output)