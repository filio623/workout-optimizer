"""
Workout tools for the Pydantic AI agent.

These tools allow the agent to query and analyze workout data from the cache.
"""

from pydantic_ai import RunContext
from backend.agents.dependencies import AgentDependencies
from backend.agents.agent import agent
from sqlalchemy import select
from backend.db.models import WorkoutCache
from typing import Dict, Any, List

@agent.tool
async def get_recent_workouts(
    ctx: RunContext[AgentDependencies],
    limit: int = 10,
) -> List[Dict]:
    """
    Get the user's most recent workouts from the cache.
    
    This tool queries the workout_cache table which contains workouts from
    both Hevy (via MCP) and Apple Health. Returns workout summaries with
    date, duration, volume, and exercise count.
    
    Args:
        ctx: The run context containing db session and user_id
        limit: Maximum number of workouts to return (default: 10)
    
    Returns:
        List of workout dictionaries, ordered by date (newest first)
        Example: [{
            "title": "Upper Body Day",
            "date": "2025-12-07",
            "duration_minutes": 65,
            "total_volume_kg": 4250.5,
            "exercise_count": 6,
            "total_sets": 24
        }, ...]
    """

    # Query the database
    stmt = (
        select(WorkoutCache)
        .where(WorkoutCache.user_id == ctx.deps.user_id)
        .order_by(WorkoutCache.workout_date.desc())
        .limit(limit)
    )

    result = await ctx.deps.db.execute(stmt)
    workouts = result.scalars().all()

    #Format the results
    formatted_workouts = []
    for workout in workouts:
        formatted_workouts.append({
            "title": workout.title,
            "date": workout.workout_date.isoformat(),
            "duration_minutes": workout.duration_minutes,
            "total_volume_kg": float(workout.total_volume_kg) if workout.total_volume_kg else 0,
            "exercise_count": workout.exercise_count,
            "total_sets": workout.total_sets,
            "source": workout.source,
        })
    return formatted_workouts
