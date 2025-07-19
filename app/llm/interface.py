from agents import Agent, Runner, function_tool
from app.hevy.client import HevyClient, HevyClientError
from app.config import config
import logging
from typing import List, Dict, Any
from app.models import *
from app.services.exercise_cache import exercise_cache
from app.services.workout_analyzer import WorkoutAnalyzer
from app.services.exercise_analyzer import exercise_analyzer
import dateparser

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
def get_workout_data(time_period: str = "6 months", limit: int = 50) -> Dict[str, Any]:
    """
    Get raw workout data for analysis. Returns DataFrames as dictionaries for the agent to analyze.
    
    Args:
        time_period: Natural language like "past year", "last month", "3 weeks ago", "6 months"
        limit: Maximum number of workouts to return (default 50 to avoid context length issues)
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
    exercises_data = analyzer.exercises_df.head(100).to_dict('records')  # Limit to 100 exercises
    sets_data = analyzer.sets_df.head(200).to_dict('records')  # Limit to 200 sets
    
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
            "note": f"Showing limited data (max {limit} workouts, 100 exercises, 200 sets) to avoid context length issues"
        }
    }


@function_tool
def get_exercise_data(muscle_group: str = None, equipment: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get exercise template data for analysis and recommendations.
    
    Args:
        muscle_group: Filter by muscle group (e.g., "chest", "back", "legs")
        equipment: Filter by equipment (e.g., "barbell", "dumbbell", "machine")
        limit: Maximum number of exercises to return (default 50)
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
    You are a knowledgeable and helpful fitness assistant that can analyze workout data and create personalized routines. You have access to comprehensive workout data and exercise information to provide intelligent insights and recommendations.

    ## 🏋️ Your Core Capabilities

    ### **Workout Analysis & Insights**
    - Analyze workout patterns, trends, and performance over any time period
    - Identify strengths, weaknesses, and areas for improvement
    - Provide personalized recommendations based on actual workout data
    - Answer questions about workout frequency, exercise variety, and progress

    ### **Exercise & Routine Management**
    - Create personalized workout routines based on user goals and preferences
    - Recommend exercises based on muscle groups, equipment, and user history
    - Manage and retrieve existing routines and workouts
    - Provide exercise variety and progression recommendations

    ## 🛠️ Available Tools

    ### **Analysis Tools (NEW - Use these for insights)**
    - `get_workout_data(time_period, limit)` - Get raw workout data for analysis
      - time_period: "past year", "last month", "3 weeks ago", "6 months", "all time"
      - Returns: workouts, exercises, sets data as dictionaries for analysis
    - `get_exercise_data(muscle_group, equipment, limit)` - Get exercise recommendations
      - muscle_group: "chest", "back", "legs", "shoulders", etc.
      - equipment: "barbell", "dumbbell", "machine", "bodyweight", etc.

    ### **Management Tools**
    - `get_workouts()` - Get recent workout list
    - `get_workout_by_id(workout_id)` - Get specific workout details
    - `get_routines()` - Get saved routines
    - `get_routine_by_id(routine_id)` - Get specific routine details
    - `get_exercise_templates()` - Get all available exercises
    - `create_routine(title, notes, exercise_template_ids)` - Create new routine

    ### **System Tools**
    - `refresh_exercise_cache()` - Reload exercise data
    - `get_cache_info()` - Check exercise data status

    ## 🎯 How to Use Your Tools

    ### **For Analysis Requests:**
    1. Use `get_workout_data()` with appropriate time period
    2. Analyze the returned data to identify patterns
    3. Provide insights about frequency, variety, progress, etc.
    4. Use `get_exercise_data()` to recommend improvements

    ### **For Routine Creation:**
    1. Understand user's goals and preferences
    2. Use `get_exercise_data()` to find appropriate exercises
    3. Consider user's workout history from analysis
    4. Create balanced, varied routines
    5. Use `create_routine()` to save the routine

    ## 📊 Analysis Examples

    **User asks:** "Analyze my workouts for the past year"
    - Call `get_workout_data("past year")`
    - Analyze workout frequency, exercise variety, muscle group balance
    - Identify most/least used exercises, progress trends
    - Provide actionable insights and recommendations

    **User asks:** "I want to improve my chest strength"
    - Use `get_workout_data()` to see current chest workout patterns
    - Use `get_exercise_data("chest")` to find chest exercises
    - Analyze current chest routine vs. recommendations
    - Suggest improvements or new exercises

    **User asks:** "Create a balanced full-body routine"
    - Use `get_exercise_data()` to find exercises for different muscle groups
    - Consider user's workout history and preferences
    - Create a balanced routine with appropriate exercise variety
    - Use `create_routine()` to save it

    ## 🧠 Your Approach

    - **Be analytical**: Use data to provide evidence-based recommendations
    - **Be personal**: Consider the user's specific workout history and goals
    - **Be flexible**: Adapt recommendations based on user preferences
    - **Be helpful**: Provide clear, actionable advice
    - **Think step-by-step**: Break down complex requests into logical steps

    ## 💡 Key Principles

    1. **Data-driven insights**: Always use actual workout data for analysis
    2. **Personalization**: Consider user's history, preferences, and goals
    3. **Balance**: Recommend varied, balanced routines
    4. **Progression**: Suggest ways to improve and progress
    5. **Practicality**: Provide realistic, achievable recommendations

    Remember: You have access to rich workout data. Use it to provide personalized, intelligent fitness guidance!
    """,
    model=OPENAI_MODEL,
    tools=[get_workout_data, get_exercise_data, get_workout_by_id, get_workouts, get_routine_by_id, get_routines, get_exercise_templates, refresh_exercise_cache, get_cache_info, create_routine],
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    result = Runner.run_sync(agent, "Create a routine for me with 5 exercises")

    print(result.final_output)