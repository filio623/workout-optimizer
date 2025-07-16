from agents import Agent, Runner, function_tool
from app.hevy.client import HevyClient, HevyClientError
from app.config import config
import logging
from typing import List
from app.models import Routine, ExerciseTemplate, ExerciseTemplateResponse, Exercise, Set

OPENAI_MODEL = config.OPENAI_MODEL
OPENAI_API_KEY = config.OPENAI_API_KEY

logger = logging.getLogger(__name__)

hevy_client = HevyClient()


@function_tool
def get_workout_by_id(workout_id: str):
    logger.info(f"🔧 Tool called: get_workout_by_id with workout_id={workout_id}")
    workout = hevy_client.get_workout_by_id(workout_id)
    logger.info(f"✅ get_workout_by_id completed successfully")
    return workout

@function_tool
def get_workouts():
    logger.info(f"🔧 Tool called: get_workouts")
    workouts = hevy_client.get_workouts()
    logger.info(f"✅ get_workouts completed successfully, returned {len(workouts.workouts)} workouts")
    return workouts

@function_tool
def get_routine_by_id(routine_id: str):
    logger.info(f"Tool called: get_routine_by_id with routine_id={routine_id}")
    routine = hevy_client.get_routine_by_id(routine_id)
    logger.info(f"✅ get_routine_by_id completed successfully")
    return routine

@function_tool
def get_routines():
    logger.info(f"Tool called: get_routines")
    routines = hevy_client.get_routines()
    logger.info(f"✅ get_routines completed successfully, returned {len(routines.routines)} routines")
    return routines


@function_tool
def get_available_exercises() -> ExerciseTemplateResponse:
    logger.info("Tool called: get_available_exercises")
    exercise_templates = hevy_client.get_exercise_templates()
    exercises = [Exercise(**exercise_data) for exercise_data in exercise_templates.exercise_templates]
    logger.info(f"✅ get_available_exercises completed successfully, returned {len(exercise_templates.exercise_templates)} exercises")
    return exercise_templates

@function_tool
def create_routine():
    exercises_templates = get_available_exercises()

    routine = Runner.run_sync(agent, f"Create a routine of 5 exercises that are in {exercies_templates}")

    new_routine = hevy_client.create_routine(routine)
    return new_routine



agent = Agent(
    name="Fitness Assistant",
    instructions="You are a helpful workout and fitness assistant that provides advice on workout routines, nutrition, and fitness tracking.",
    model=OPENAI_MODEL,
    tools=[get_workout_by_id, get_workouts, get_routine_by_id, get_routines, get_available_exercises, create_routine],
)






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    result = Runner.run_sync(agent, "create a new routine for me")

    print(result.final_output)

