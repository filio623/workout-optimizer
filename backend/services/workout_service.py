"""
Workout caching service layer.
Handles syncing workouts from Hevy API to local database with duplicate detection.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, List
from datetime import datetime
import uuid
from backend.db.models import WorkoutCache
from backend.hevy.client import HevyClient


def _calculate_workout_metrics(workout: dict) -> dict:
    """
    Calculate summary metrics from raw Hevy workout data.

    Args:
        workout: Raw workout dict from Hevy API

    Returns:
        Dict with calculated metrics (duration, volume, sets, etc.)
    """
    # Calculate duration in minutes
    start = datetime.fromisoformat(workout['start_time'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(workout['end_time'].replace('Z', '+00:00'))
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


async def sync_hevy_workouts(
    db: AsyncSession,
    user_id: str,
    page_size: int = 100,
) -> Dict:
    """
    Sync workouts from Hevy API to local database cache.

    Uses PostgreSQL's ON CONFLICT to handle duplicates:
    - If (user_id, source, source_workout_id) already exists: UPDATE the row
    - If new: INSERT the row

    Args:
        db: Database session
        user_id: UUID string of the user
        page_size: Number of workouts to fetch per page (default 100)

    Returns:
        Dict with summary (total_processed, message)
    """
    user_uuid = uuid.UUID(user_id)

    # Fetch workouts from Hevy API
    hevy_client = HevyClient()
    response = hevy_client.get_workouts(page_size=page_size)
    workouts_data = response.model_dump(mode="json")
    workouts = workouts_data.get('workouts', [])

    if not workouts:
        return {
            'total_processed': 0,
            'message': 'No workouts found from Hevy API.'
        }

    # Process each workout
    records_to_insert = []
    for workout in workouts:
        # Calculate metrics
        metrics = _calculate_workout_metrics(workout)

        # Parse workout date (use start_time) and convert to naive UTC
        workout_date = datetime.fromisoformat(workout['start_time'].replace('Z', '+00:00'))
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
            'muscle_groups': None,  # Could extract from exercise templates later
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

    return {
        'total_processed': len(workouts),
        'message': f'Successfully synced {len(workouts)} workouts from Hevy.'
    }
