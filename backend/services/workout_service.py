"""
Workout caching service layer.
Handles syncing workouts from Hevy API to local database with duplicate detection.
Uses Model Context Protocol (MCP) for standardized Hevy integration.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, List, Set
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import json
from backend.db.models import WorkoutCache
from backend.mcp_client import call_hevy_tool

# Load exercise templates for fast lookup
try:
    # backend/services/workout_service.py -> backend/services -> backend -> root
    root_dir = Path(__file__).parent.parent.parent
    cache_path = root_dir / "cache" / "exercise_templates_cache.json"
    data_path = root_dir / "backend" / "data" / "exercise_templates.json"
    
    templates_path = cache_path
    if not templates_path.exists():
        templates_path = data_path
    
    if templates_path.exists():
        with open(templates_path, "r") as f:
            data = json.load(f)
            # Handle both list (legacy) and dict wrapper (current) formats
            if isinstance(data, dict) and "exercises" in data:
                templates_list = data["exercises"]
            elif isinstance(data, list):
                templates_list = data
            else:
                templates_list = []

            # Create mappings
            TEMPLATE_MAP = {t["id"]: t.get("primary_muscle_group", "other") for t in templates_list}
            TEMPLATE_NAME_MAP = {t["title"].lower(): t.get("primary_muscle_group", "other") for t in templates_list}
            print(f"DEBUG: WorkoutService loaded {len(TEMPLATE_MAP)} templates.", flush=True)
    else:
        print(f"WARNING: Template file not found at {templates_path}", flush=True)
        TEMPLATE_MAP = {}
        TEMPLATE_NAME_MAP = {}
except Exception as e:
    print(f"Warning: WorkoutService could not load exercise templates: {e}", flush=True)
    TEMPLATE_MAP = {}
    TEMPLATE_NAME_MAP = {}


def deduplicate_workouts(workouts: List[WorkoutCache]) -> List[WorkoutCache]:
    """
    Filter out Apple Health workouts that overlap with Hevy workouts.
    
    Strategy:
    1. Keep all Hevy workouts (Source of Truth).
    2. For each Apple Health workout, check if it starts within 30 minutes 
       of any Hevy workout (direct overlap).
    3. Also check for Timezone-shifted duplicates (e.g. Hevy in UTC, Apple in EST):
       - If duration matches (within 2 mins)
       - AND start time matches modulo 1 hour (within 5 mins)
       - AND start time within 24 hours.
    4. If it overlaps/matches, assume it's a duplicate entry and discard it.
    5. If it doesn't overlap (e.g. a separate morning walk), keep it.
    """
    if not workouts:
        return []

    # Separate by source
    hevy_workouts = [w for w in workouts if w.source == 'hevy']
    other_workouts = [w for w in workouts if w.source != 'hevy']
    
    # If no Hevy workouts, return everything (nothing to duplicate against)
    if not hevy_workouts:
        return workouts

    # Create a list of Hevy start times for quick lookup
    hevy_data = [(w.workout_date, w.duration_minutes or 0) for w in hevy_workouts]
    
    filtered_others = []
    for other in other_workouts:
        is_duplicate = False
        other_dur = other.duration_minutes or 0
        
        for h_time, h_dur in hevy_data:
            # Time difference in seconds
            delta = abs((other.workout_date - h_time).total_seconds())
            
            # 1. Direct Overlap Check (< 30 minutes)
            if delta < 1800:
                is_duplicate = True
                break
                
            # 2. Timezone Shift Check
            # Check if duration matches closely (within 2 mins)
            if abs(other_dur - h_dur) <= 2:
                # Check if start time is roughly same time of day (modulo hour)
                # allowing for 5 min drift
                # We also assume duplicate must be within 24 hours (usually same day)
                if delta < 86400: 
                    remainder = delta % 3600
                    # Check if remainder is close to 0 (0-5 mins) or close to 3600 (55-60 mins)
                    if remainder < 300 or remainder > 3300:
                        is_duplicate = True
                        break
        
        if not is_duplicate:
            filtered_others.append(other)
            
    # Combine and sort by date descending
    combined = hevy_workouts + filtered_others
    combined.sort(key=lambda x: x.workout_date, reverse=True)
    
    return combined


def _calculate_workout_metrics(workout: dict) -> dict:
    """
    Calculate summary metrics from raw Hevy workout data.

    Args:
        workout: Raw workout dict from Hevy API (supports both camelCase and snake_case)

    Returns:
        Dict with calculated metrics (duration, volume, sets, etc.)
    """
    # Calculate duration in minutes
    # MCP returns camelCase (startTime), REST API returns snake_case (start_time)
    start_time = workout.get('startTime') or workout.get('start_time')
    end_time = workout.get('endTime') or workout.get('end_time')
    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    duration_minutes = int((end - start).total_seconds() / 60)

    # Initialize counters
    total_sets = 0
    total_volume_kg = 0.0
    bodyweight_reps = 0
    exercise_count = len(workout.get('exercises', []))

    # Process each exercise and set
    for exercise in workout.get('exercises', []):
        sets = exercise.get('sets', [])
        total_sets += len(sets)

        for set_data in sets:
            weight = set_data.get('weight_kg')
            reps = set_data.get('reps', 0)

            if weight is not None:
                # Weighted exercise - add to volume
                total_volume_kg += weight * reps
            elif reps:
                # Bodyweight exercise (weight is None) - count reps
                bodyweight_reps += reps

    return {
        'duration_minutes': duration_minutes,
        'total_sets': total_sets,
        'total_volume_kg': round(total_volume_kg, 2),
        'bodyweight_reps': bodyweight_reps,
        'exercise_count': exercise_count,
    }

def _extract_muscle_groups(workout: dict) -> List[str]:
    """Extract distinct muscle groups from workout exercises using ID or Name lookup."""
    muscle_groups = set()
    for ex in workout.get('exercises', []):
        # 1. ID Lookup
        tid = ex.get('exercise_template_id') or ex.get('exerciseTemplateId')
        if tid and tid in TEMPLATE_MAP:
            muscle_groups.add(TEMPLATE_MAP[tid])
            continue
            
        # 2. Name Lookup
        name = ex.get('name', '').lower()
        if name in TEMPLATE_NAME_MAP:
            muscle_groups.add(TEMPLATE_NAME_MAP[name])
        elif "(" in name:
            # Try stripping suffix like "Bench Press (Barbell)" -> "Bench Press"
            base = name.split("(")[0].strip()
            if base in TEMPLATE_NAME_MAP:
                 muscle_groups.add(TEMPLATE_NAME_MAP[base])
                 
        # 3. Direct field (rare but possible in some exports)
        if 'muscle_group' in ex:
             muscle_groups.add(ex['muscle_group'])
             
    return list(muscle_groups)

async def sync_hevy_workouts(
    db: AsyncSession,
    user_id: str,
    page_size: int = 10,  # MCP server maximum is 10
    sync_all: bool = False,
) -> Dict:
    """
    Sync workouts from Hevy API to local database cache via MCP.

    Uses PostgreSQL's ON CONFLICT to handle duplicates:
    - If (user_id, source, source_workout_id) already exists: UPDATE the row
    - If new: INSERT the row

    Args:
        db: Database session
        user_id: UUID string of the user
        page_size: Number of workouts to fetch per page (default 10)
        sync_all: Whether to fetch all history (paginated) or just the most recent page

    Returns:
        Dict with summary (total_processed, message)
    """
    user_uuid = uuid.UUID(user_id)

    total_processed = 0
    page = 1

    while True:
        # Fetch workouts from Hevy via MCP using the reusable utility
        workouts_json = await call_hevy_tool(
            "get-workouts",
            arguments={"pageSize": page_size, "page": page}
        )

        # MCP returns a list directly, or it might be wrapped depending on version
        workouts = workouts_json if isinstance(workouts_json, list) else workouts_json.get('workouts', [])

        if not workouts:
            break

        # Process each workout
        records_to_insert = []
        for workout in workouts:
            # Calculate metrics
            metrics = _calculate_workout_metrics(workout)
            
            # Extract muscle groups
            muscle_groups = _extract_muscle_groups(workout)

            # Parse workout date - handle both camelCase (MCP) and snake_case (REST)
            start_time = workout.get('startTime') or workout.get('start_time')
            workout_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            workout_date = workout_date.replace(tzinfo=None)  # Remove timezone for PostgreSQL

            # Build record for database
            record = {
                'user_id': user_uuid,
                'source': 'hevy',
                'source_workout_id': workout['id'],
                'workout_date': workout_date,
                'title': workout.get('title', 'Untitled Workout'),
                'duration_minutes': metrics['duration_minutes'],
                'total_sets': metrics['total_sets'],
                'total_volume_kg': metrics['total_volume_kg'],
                'bodyweight_reps': metrics['bodyweight_reps'],
                'exercise_count': metrics['exercise_count'],
                'calories_burned': None,  # Hevy doesn't provide this
                'muscle_groups': muscle_groups,  # Now populated!
                'workout_data': workout,  # Store complete raw data
            }
            records_to_insert.append(record)

        # Bulk insert with UPSERT logic
        stmt = insert(WorkoutCache).values(records_to_insert)

        # On conflict (duplicate workout), update all fields
        stmt = stmt.on_conflict_do_update(
            index_elements=['user_id', 'source', 'source_workout_id'],
            set_={
                'workout_date': stmt.excluded.workout_date,
                'title': stmt.excluded.title,
                'duration_minutes': stmt.excluded.duration_minutes,
                'total_sets': stmt.excluded.total_sets,
                'total_volume_kg': stmt.excluded.total_volume_kg,
                'bodyweight_reps': stmt.excluded.bodyweight_reps,
                'exercise_count': stmt.excluded.exercise_count,
                'calories_burned': stmt.excluded.calories_burned,
                'muscle_groups': stmt.excluded.muscle_groups,
                'workout_data': stmt.excluded.workout_data,
                # updated_at will be automatically set by PostgreSQL's onupdate trigger
            }
        )

        await db.execute(stmt)
        await db.commit()

        total_processed += len(workouts)

        # If not syncing all, or if we got fewer workouts than requested (end of list), break
        if not sync_all or len(workouts) < page_size:
            break
        
        page += 1

    return {
        'total_processed': total_processed,
        'message': f'Successfully synced {total_processed} workouts from Hevy via MCP.'
    }
