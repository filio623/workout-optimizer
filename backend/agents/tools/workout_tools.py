"""
Workout tools for the Pydantic AI agent.

These tools allow the agent to query and analyze workout data from the cache.
"""

from pydantic_ai import RunContext
from backend.agents.dependencies import AgentDependencies
from backend.agents.agent import agent
from sqlalchemy import select, func
from backend.db.models import WorkoutCache
from typing import Dict, Any, List
from datetime import datetime, timedelta, UTC

# Conversion constant
KG_TO_LBS = 2.20462

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
        ctx: The run context containing session_factory and user_id
        limit: Maximum number of workouts to return (default: 10)

    Returns:
        List of workout dictionaries, ordered by date (newest first)
        Example: [{
            "title": "Upper Body Day",
            "date": "2025-12-07",
            "duration_minutes": 65,
            "total_volume_lbs": 4250.5,
            "exercise_count": 6,
            "total_sets": 24
        }, ...]
    """

    # Create own database session for parallel execution
    async with ctx.deps.session_factory() as db:
        # Query the database
        stmt = (
            select(WorkoutCache)
            .where(WorkoutCache.user_id == ctx.deps.user_id)
            .order_by(WorkoutCache.workout_date.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        workouts = result.scalars().all()

        #Format the results
        formatted_workouts = []
        for workout in workouts:
            # Convert volume from kg to lbs for consistency with health metrics
            volume_kg = float(workout.total_volume_kg) if workout.total_volume_kg else 0
            volume_lbs = volume_kg * KG_TO_LBS

            formatted_workouts.append({
                "title": workout.title,
                "date": workout.workout_date.isoformat(),
                "duration_minutes": workout.duration_minutes,
                "total_volume_lbs": round(volume_lbs, 1),
                "exercise_count": workout.exercise_count,
                "total_sets": workout.total_sets,
                "source": workout.source,
            })
        return formatted_workouts


@agent.tool
async def get_workout_analysis(
    ctx: RunContext[AgentDependencies],
    days: int = 30,
) -> Dict:
    """
    Analyze workout patterns, frequency, and volume trends over time.

    This tool provides comprehensive analysis of workout data including:
    - Training frequency (workouts per week)
    - Volume trends (total volume, average per workout)
    - Consistency metrics (gaps between workouts)
    - Workout type distribution

    Use this for questions like:
    - "How's my training frequency?"
    - "Is my workout volume increasing?"
    - "Am I training consistently?"

    Args:
        ctx: The run context containing db session and user_id
        days: Number of days to analyze (default: 30)

    Returns:
        Dictionary with frequency, volume, and consistency analysis
        Example: {
            "period_analyzed": "30 days",
            "total_workouts": 12,
            "frequency": {
                "workouts_per_week": 2.8,
                "avg_days_between_workouts": 2.5
            },
            "volume": {
                "total_volume_lbs": 119754,
                "avg_volume_per_workout_lbs": 9979,
                "volume_trend": "increasing"
            },
            "consistency": {
                "longest_gap_days": 7,
                "consistency_score": 75
            }
        }
    """
    cutoff_date = datetime.now(UTC).date() - timedelta(days=days)

    # Create own database session for parallel execution
    async with ctx.deps.session_factory() as db:
        # Query workouts in the time period
        stmt = (
            select(WorkoutCache)
            .where(
                WorkoutCache.user_id == ctx.deps.user_id,
                WorkoutCache.workout_date >= cutoff_date,
            )
            .order_by(WorkoutCache.workout_date.asc())
        )

        result = await db.execute(stmt)
        workouts = result.scalars().all()

    # Handle no data case
    if not workouts:
        return {
            "period_analyzed": f"{days} days",
            "total_workouts": 0,
            "message": f"No workouts found in the last {days} days"
        }

    # Calculate frequency metrics
    total_workouts = len(workouts)
    weeks_analyzed = days / 7
    workouts_per_week = total_workouts / weeks_analyzed

    # Calculate gaps between workouts
    gaps = []
    if len(workouts) > 1:
        for i in range(1, len(workouts)):
            gap = (workouts[i].workout_date.date() - workouts[i-1].workout_date.date()).days
            gaps.append(gap)

    avg_days_between = sum(gaps) / len(gaps) if gaps else 0
    longest_gap = max(gaps) if gaps else 0

    # Calculate volume metrics (convert kg to lbs)
    volumes_kg = [float(w.total_volume_kg) if w.total_volume_kg else 0 for w in workouts]
    volumes_lbs = [v * KG_TO_LBS for v in volumes_kg]
    total_volume_lbs = sum(volumes_lbs)
    avg_volume_per_workout_lbs = total_volume_lbs / total_workouts if total_workouts > 0 else 0

    # Analyze volume trend (comparing first half vs second half)
    volume_trend = "stable"
    if len(volumes_lbs) >= 4:
        mid_point = len(volumes_lbs) // 2
        first_half_avg = sum(volumes_lbs[:mid_point]) / mid_point
        second_half_avg = sum(volumes_lbs[mid_point:]) / (len(volumes_lbs) - mid_point)

        if second_half_avg > first_half_avg * 1.1:
            volume_trend = "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            volume_trend = "decreasing"

    # Calculate consistency score (0-100)
    # Perfect score = 3-4 workouts/week with no gaps > 3 days
    frequency_score = min(100, (workouts_per_week / 3.5) * 70)  # 70% weight
    gap_penalty = (longest_gap - 3) * 5 if longest_gap > 3 else 0  # Penalty for long gaps
    consistency_score = max(0, frequency_score - gap_penalty)

    # Workout type distribution
    workout_types = {}
    for workout in workouts:
        title = workout.title or "Untitled"
        workout_types[title] = workout_types.get(title, 0) + 1

    return {
        "period_analyzed": f"{days} days",
        "total_workouts": total_workouts,
        "frequency": {
            "workouts_per_week": round(workouts_per_week, 1),
            "avg_days_between_workouts": round(avg_days_between, 1)
        },
        "volume": {
            "total_volume_lbs": round(total_volume_lbs, 1),
            "avg_volume_per_workout_lbs": round(avg_volume_per_workout_lbs, 1),
            "volume_trend": volume_trend
        },
        "consistency": {
            "longest_gap_days": longest_gap,
            "consistency_score": round(consistency_score, 1)
        },
        "workout_distribution": workout_types,
        "date_range": {
            "start": workouts[0].workout_date.isoformat(),
            "end": workouts[-1].workout_date.isoformat()
        }
    }


@agent.tool
async def get_exercise_history(
    ctx: RunContext[AgentDependencies],
    exercise_name: str,
    days: int = 90,
) -> Dict:
    """
    Get progression history for a specific exercise.

    This tool tracks personal records (PRs), volume trends, and progression
    for any exercise. Useful for answering questions like:
    - "How's my bench press progress?"
    - "What's my PR on squats?"
    - "Am I getting stronger on deadlifts?"

    The tool searches for the exercise name in workout data (case-insensitive,
    partial matches work - e.g., "bench" will match "Bench Press (Barbell)").

    Args:
        ctx: The run context containing db session and user_id
        exercise_name: Name of the exercise (e.g., "Bench Press", "Squat")
        days: Number of days to look back (default: 90)

    Returns:
        Dictionary with exercise history, PRs, and progression analysis
        Example: {
            "exercise_name": "Bench Press (Barbell)",
            "sessions_found": 12,
            "date_range": {"start": "2025-09-08", "end": "2025-12-08"},
            "personal_records": {
                "max_weight_lbs": 225.0,
                "max_weight_date": "2025-12-01",
                "max_volume_lbs": 12500,
                "max_reps_at_weight": 8
            },
            "progression": {
                "trend": "increasing",
                "first_session_max_lbs": 205,
                "latest_session_max_lbs": 225,
                "total_improvement_lbs": 20
            },
            "session_history": [
                {
                    "date": "2025-11-15",
                    "max_weight_lbs": 215,
                    "total_sets": 4,
                    "total_volume_lbs": 6880
                },
                ...
            ]
        }
    """
    cutoff_date = datetime.now(UTC).date() - timedelta(days=days)

    # Create own database session for parallel execution
    async with ctx.deps.session_factory() as db:
        # Query workouts that might contain this exercise
        stmt = (
            select(WorkoutCache)
            .where(
                WorkoutCache.user_id == ctx.deps.user_id,
                WorkoutCache.workout_date >= cutoff_date,
            )
            .order_by(WorkoutCache.workout_date.asc())
        )

        result = await db.execute(stmt)
        workouts = result.scalars().all()

    if not workouts:
        return {
            "exercise_name": exercise_name,
            "sessions_found": 0,
            "message": f"No workouts found in the last {days} days"
        }

    # Search through workout_data JSONB for this exercise
    exercise_sessions = []
    exercise_name_lower = exercise_name.lower()

    for workout in workouts:
        workout_data = workout.workout_data
        if not workout_data or 'exercises' not in workout_data:
            continue

        for exercise in workout_data.get('exercises', []):
            # Get exercise title (handle both camelCase and snake_case)
            ex_title = exercise.get('title') or exercise.get('exercise_template', {}).get('title', '')

            # Check if this is the exercise we're looking for (case-insensitive partial match)
            if exercise_name_lower not in ex_title.lower():
                continue

            # Found the exercise! Extract set data
            sets = exercise.get('sets', [])
            if not sets:
                continue

            # Calculate session metrics
            weights_kg = []
            reps = []
            session_volume_kg = 0

            for set_data in sets:
                weight_kg = set_data.get('weight_kg')
                set_reps = set_data.get('reps', 0)

                if weight_kg is not None:
                    weights_kg.append(weight_kg)
                    reps.append(set_reps)
                    session_volume_kg += weight_kg * set_reps

            if not weights_kg:  # Bodyweight exercise, skip for now
                continue

            # Convert to lbs
            max_weight_kg = max(weights_kg)
            max_weight_lbs = max_weight_kg * KG_TO_LBS
            session_volume_lbs = session_volume_kg * KG_TO_LBS

            exercise_sessions.append({
                "date": workout.workout_date.isoformat(),
                "max_weight_lbs": round(max_weight_lbs, 1),
                "total_sets": len(sets),
                "total_volume_lbs": round(session_volume_lbs, 1),
                "exact_exercise_name": ex_title
            })

    # Handle no sessions found
    if not exercise_sessions:
        return {
            "exercise_name": exercise_name,
            "sessions_found": 0,
            "message": f"No sessions found for '{exercise_name}' in the last {days} days. Try a different name or check spelling."
        }

    # Calculate personal records
    all_max_weights = [s['max_weight_lbs'] for s in exercise_sessions]
    all_volumes = [s['total_volume_lbs'] for s in exercise_sessions]

    max_weight_lbs = max(all_max_weights)
    max_weight_session = next(s for s in exercise_sessions if s['max_weight_lbs'] == max_weight_lbs)

    max_volume_lbs = max(all_volumes)

    # Analyze progression (first session vs last session)
    first_session_max = exercise_sessions[0]['max_weight_lbs']
    latest_session_max = exercise_sessions[-1]['max_weight_lbs']
    improvement = latest_session_max - first_session_max

    if improvement > 5:
        trend = "increasing"
    elif improvement < -5:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "exercise_name": exercise_sessions[0]['exact_exercise_name'],  # Use exact name from data
        "sessions_found": len(exercise_sessions),
        "date_range": {
            "start": exercise_sessions[0]['date'],
            "end": exercise_sessions[-1]['date']
        },
        "personal_records": {
            "max_weight_lbs": max_weight_lbs,
            "max_weight_date": max_weight_session['date'],
            "max_volume_lbs": max_volume_lbs,
        },
        "progression": {
            "trend": trend,
            "first_session_max_lbs": first_session_max,
            "latest_session_max_lbs": latest_session_max,
            "total_improvement_lbs": round(improvement, 1)
        },
        "session_history": exercise_sessions
    }
