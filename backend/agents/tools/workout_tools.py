"""
Workout tools for the Pydantic AI agent.

These tools allow the agent to query and analyze workout data from the cache
as well as live data directly from Hevy via MCP.
"""

from pydantic_ai import RunContext
from backend.agents.dependencies import AgentDependencies
from backend.agents.agent import agent
from sqlalchemy import select, func
from backend.db.models import WorkoutCache
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, UTC
from backend.mcp_client import call_hevy_tool

# Conversion constant
KG_TO_LBS = 2.20462

def _convert_workout_to_lbs(workout: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert a detailed Hevy workout/routine from kg to lbs."""
    if not workout or 'exercises' not in workout:
        return workout
        
    for exercise in workout.get('exercises', []):
        for set_data in exercise.get('sets', []):
            if set_data.get('weight_kg') is not None:
                set_data['weight_lbs'] = round(set_data['weight_kg'] * KG_TO_LBS, 1)
    return workout

@agent.tool
async def get_recent_workouts(
    ctx: RunContext[AgentDependencies],
    limit: int = 10,
) -> List[Dict]:
    """
    Get the user's recent workouts from the local cache.

    This tool queries the database which contains synced workouts from
    both Hevy and Apple Health. Returns workout summaries.
    For the absolute latest workout (just finished), use get_live_workouts instead.

    Args:
        ctx: The run context containing session_factory and user_id
        limit: Maximum number of workouts to return (default: 10)

    Returns:
        List of workout dictionaries, ordered by date (newest first)
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
                "workout_id": workout.source_workout_id
            })
        return formatted_workouts


@agent.tool
async def get_live_workouts(
    ctx: RunContext[AgentDependencies],
    limit: int = 5,
) -> List[Dict]:
    """
    Get the absolute latest workouts directly from Hevy (real-time).

    Use this tool when the user asks about a workout they just finished,
    or when you need the most up-to-date data that might not be in the cache yet.
    Returns full workout details including exercises and sets.

    Args:
        ctx: The run context (contains user_id)
        limit: Number of recent workouts to fetch (default: 5, max: 10)

    Returns:
        List of detailed workout dictionaries from Hevy.
    """
    # Hevy MCP max pageSize is 10
    safe_limit = min(limit, 10)
    
    workouts = await call_hevy_tool("get-workouts", {"pageSize": safe_limit})
    
    # Hevy MCP returns a list directly or wrapped
    workout_list = workouts if isinstance(workouts, list) else workouts.get('workouts', [])
    
    # Convert units and return
    return [_convert_workout_to_lbs(w) for w in workout_list]


@agent.tool
async def get_live_routines(
    ctx: RunContext[AgentDependencies],
) -> List[Dict]:
    """
    Get the user's saved workout routines directly from Hevy.

    Use this to see what routines the user already has saved in Hevy.
    Useful for understanding their current program or before creating a new routine.

    Args:
        ctx: The run context

    Returns:
        List of routine dictionaries.
    """
    routines = await call_hevy_tool("get-routines")
    
    routine_list = routines if isinstance(routines, list) else routines.get('routines', [])
    
    return [_convert_workout_to_lbs(r) for r in routine_list]


@agent.tool
async def search_exercises(
    ctx: RunContext[AgentDependencies],
    query: str,
) -> List[Dict]:
    """
    Search for exercise templates in Hevy.

    Use this tool when you need to find the correct exercise ID or name
    before recommending an exercise or creating a routine.

    Args:
        ctx: The run context
        query: Search term (e.g., "bench press", "squat")

    Returns:
        List of matching exercise templates.
    """
    query_lower = query.lower()
    matches = []
    page = 1
    max_pages = 5  # Limit to 5 pages (500 exercises) to keep it fast
    
    while page <= max_pages:
        exercises = await call_hevy_tool("get-exercise-templates", {"page": page, "pageSize": 100})
        exercise_list = exercises if isinstance(exercises, list) else exercises.get('exercise_templates', [])
        
        if not exercise_list:
            break
            
        # Filter by query
        page_matches = [
            e for e in exercise_list 
            if query_lower in e.get('title', '').lower()
        ]
        matches.extend(page_matches)
        
        # If we have enough matches or reached end of list
        if len(matches) >= 10 or len(exercise_list) < 100:
            break
            
        page += 1
    
    return matches[:10]

@agent.tool
async def create_routine(
    ctx: RunContext[AgentDependencies],
    title: str,
    exercises: List[Dict[str, Any]],
) -> Dict:
    """
    Create a new workout routine in the user's Hevy account.

    Use this tool when the user asks you to create a workout plan, program, or specific routine.
    The routine will be saved to their Hevy app so they can use it during their next workout.

    IMPORTANT: Hevy API requires weight in KILOGRAMS (kg). 
    If you have weight in lbs, divide by 2.20462 before calling this tool.

    Args:
        ctx: The run context
        title: Title of the routine (e.g., "Push Day A", "Upper Body Hypertrophy")
        exercises: List of exercise objects. Each object MUST have:
            - exerciseTemplateId: UUID of the exercise template (use search_exercises to find these)
            - sets: List of set objects, each with:
                - type: "normal", "warmup", "failure", or "dropset"
                - weight_kg: Weight in kilograms (MANDATORY for weighted exercises)
                - reps: Number of reps (MANDATORY)

    Returns:
        The created routine object from Hevy.
    """
    # Clean up the exercise objects to ensure they use the correct camelCase names for MCP
    cleaned_exercises = []
    for ex in exercises:
        cleaned_ex = {
            "exerciseTemplateId": ex.get("exerciseTemplateId") or ex.get("exercise_template_id"),
            "sets": ex.get("sets", []),
            "notes": ex.get("notes", "")
        }
        cleaned_exercises.append(cleaned_ex)

    return await call_hevy_tool("create-routine", {
        "title": title,
        "exercises": cleaned_exercises
    })


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


@agent.tool
async def detect_plateaus(
    ctx: RunContext[AgentDependencies],
    exercise_name: str,
) -> Dict:
    """
    Analyze an exercise for performance plateaus.

    A plateau is defined as 4 or more consecutive sessions without a significant
    increase (> 2.5%) in Max Weight.

    Use this when a user complains about being stuck, stalled, or not progressing
    on a specific lift.

    Args:
        ctx: Run context
        exercise_name: The exercise to analyze (e.g. "Bench Press")

    Returns:
        Analysis of recent performance including plateau status and recommendations.
    """
    # Reuse get_exercise_history logic to get data
    # We look back 90 days to establish a baseline
    history = await get_exercise_history(ctx, exercise_name, days=90)

    if "message" in history and history.get("sessions_found", 0) == 0:
        return {
            "exercise_name": exercise_name,
            "status": "INSUFFICIENT_DATA",
            "message": history.get("message", "No data found")
        }

    sessions = history.get("session_history", [])
    
    # Need at least 4 sessions to detect a meaningful plateau
    if len(sessions) < 4:
        return {
            "exercise_name": history.get("exercise_name", exercise_name),
            "status": "INSUFFICIENT_DATA",
            "message": f"Only found {len(sessions)} sessions. Need at least 4 to detect a plateau."
        }

    # Sort by date ascending (just to be safe, though get_exercise_history should sort them)
    sessions.sort(key=lambda x: x["date"])

    # Analyze the last 5 sessions (or fewer if we don't have 5)
    recent_sessions = sessions[-5:]
    
    # Extract max weights
    weights = [s["max_weight_lbs"] for s in recent_sessions]
    dates = [s["date"] for s in recent_sessions]

    # Calculate trend
    first_weight = weights[0]
    last_weight = weights[-1]
    max_in_recent = max(weights)
    
    # Check for stagnation
    # 1. No improvement from start to end of window
    is_flat = last_weight <= first_weight * 1.025 # Less than 2.5% gain
    
    # 2. Fluctuating but stuck (max hasn't moved up)
    is_stuck = last_weight < max_in_recent

    # 3. Time duration
    from datetime import datetime
    days_stuck = (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days

    is_plateau = (is_flat or is_stuck) and days_stuck > 14  # At least 2 weeks of stagnation

    recommendations = []
    if is_plateau:
        recommendations = [
            "Implement a deload week (reduce volume by 40-50%).",
            "Switch to a variation of this exercise (e.g., Incline instead of Flat).",
            "Check your protein intake (aim for 1g per lb of bodyweight).",
            "Ensure you are sleeping 7-9 hours per night.",
            "Try changing your rep range (e.g., if doing 5x5, try 3x10)."
        ]

    return {
        "exercise_name": history.get("exercise_name", exercise_name),
        "status": "PLATEAU_DETECTED" if is_plateau else "PROGRESSING",
        "analysis": {
            "recent_sessions_analyzed": len(recent_sessions),
            "period_days": days_stuck,
            "starting_weight_lbs": first_weight,
            "current_weight_lbs": last_weight,
            "max_weight_in_period_lbs": max_in_recent,
            "growth_percentage": round(((last_weight - first_weight) / first_weight) * 100, 2)
        },
        "recent_weights": weights,
        "recommendations": recommendations if is_plateau else ["Keep pushing! You are making progress."]
    }
