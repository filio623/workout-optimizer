"""
Apple Health data service layer.
Handles saving Apple Health data to the database with duplicate detection.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from typing import Dict, List
from datetime import date, datetime
import uuid
from backend.db.models import HealthMetricsDaily, HealthMetricsRaw, WorkoutCache


async def save_daily_metrics(
    db: AsyncSession,
    user_id: str,
    daily_metrics: List[Dict],
) -> Dict:
    """
    Save daily health metrics to database with UPSERT logic.

    Uses PostgreSQL's ON CONFLICT to handle duplicates:
    - If (user_id, metric_date) already exists: UPDATE the row
    - If (user_id, metric_date) is new: INSERT the row

    Args:
        db: Database session
        user_id: UUID string of the user
        daily_metrics: List of dicts from AppleHealthParser._parse_daily_metrics()

    Returns:
        Dict with summary
    """
    user_uuid = uuid.UUID(user_id)

    records_to_insert = []
    for entry in daily_metrics:
        record = {
            'user_id': user_uuid,
            'metric_date': entry['metric_date'],
            'steps': entry.get('steps'),
            'weight_lbs': entry.get('weight_lbs'),
            'active_calories': entry.get('active_calories'),
            'resting_heart_rate': entry.get('resting_heart_rate'),
            'distance_miles': entry.get('distance_miles'),
            'workout_minutes': entry.get('workout_minutes'),
            'exercise_minutes': entry.get('exercise_minutes'),
            'stand_minutes': entry.get('stand_minutes'),
            'additional_metrics': entry.get('additional_metrics', {}),
        }
        records_to_insert.append(record)

    stmt = insert(HealthMetricsDaily).values(records_to_insert)

    # UPSERT: Update all columns on conflict
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'metric_date'],
        set_={
            'steps': stmt.excluded.steps,
            'weight_lbs': stmt.excluded.weight_lbs,
            'active_calories': stmt.excluded.active_calories,
            'resting_heart_rate': stmt.excluded.resting_heart_rate,
            'distance_miles': stmt.excluded.distance_miles,
            'workout_minutes': stmt.excluded.workout_minutes,
            'exercise_minutes': stmt.excluded.exercise_minutes,
            'stand_minutes': stmt.excluded.stand_minutes,
            'additional_metrics': stmt.excluded.additional_metrics,
            'updated_at': func.now(),
        }
    )

    await db.execute(stmt)
    await db.commit()

    return {
        'total_processed': len(daily_metrics),
        'message': 'Daily metrics saved with UPSERT logic.'
    }


async def save_raw_metrics(
    db: AsyncSession,
    user_id: str,
    raw_metrics: List[Dict],
) -> Dict:
    """
    Save raw health metrics (time-series data) to database with UPSERT.

    These are individual data points from workouts (HR samples, step counts, etc.).
    Uses UPSERT to prevent duplicates when re-uploading same Apple Health export.

    Args:
        db: Database session
        user_id: UUID string of the user
        raw_metrics: List of dicts from AppleHealthParser._parse_raw_metrics()

    Returns:
        Dict with summary
    """
    if not raw_metrics:
        return {
            'total_processed': 0,
            'message': 'No raw metrics to save.'
        }

    user_uuid = uuid.UUID(user_id)

    # Deduplicate raw metrics by (metric_type, metric_date)
    # If multiple values exist for same timestamp, keep the last one
    unique_metrics = {}
    for entry in raw_metrics:
        key = (entry['metric_type'], entry['metric_date'])
        unique_metrics[key] = entry

    print(f"[DEBUG] Deduplicated {len(raw_metrics)} raw metrics to {len(unique_metrics)} unique entries")

    records_to_insert = []
    for entry in unique_metrics.values():
        record = {
            'user_id': user_uuid,
            'metric_date': entry['metric_date'],
            'metric_type': entry['metric_type'],
            'value': entry['value'],
            'unit': entry['unit'],
            'source': entry.get('source'),
            'source_metadata': entry.get('source_metadata', {}),
        }
        records_to_insert.append(record)

    # Batch insert to avoid PostgreSQL parameter limit (32767)
    # With 8 columns per row, we can safely do ~4000 rows per batch
    batch_size = 4000
    total_inserted = 0
    total_batches = (len(records_to_insert) + batch_size - 1) // batch_size

    print(f"[DEBUG] Processing {len(records_to_insert)} raw metrics in {total_batches} batches")

    for i in range(0, len(records_to_insert), batch_size):
        batch = records_to_insert[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        print(f"[DEBUG] Batch {batch_num}/{total_batches}: Inserting {len(batch)} records...")

        stmt = insert(HealthMetricsRaw).values(batch)

        # UPSERT: Update on conflict with unique constraint (user_id, metric_type, metric_date)
        stmt = stmt.on_conflict_do_update(
            index_elements=['user_id', 'metric_type', 'metric_date'],
            set_={
                'value': stmt.excluded.value,
                'unit': stmt.excluded.unit,
                'source': stmt.excluded.source,
                'source_metadata': stmt.excluded.source_metadata,
            }
        )

        await db.execute(stmt)
        total_inserted += len(batch)
        print(f"[DEBUG] Batch {batch_num}/{total_batches} complete. Total so far: {total_inserted}")

    await db.commit()
    print(f"[DEBUG] All raw metrics committed successfully")

    return {
        'total_processed': total_inserted,
        'message': f'Raw metrics saved with UPSERT logic ({len(range(0, len(records_to_insert), batch_size))} batches).'
    }


async def save_workouts(
    db: AsyncSession,
    user_id: str,
    workouts: List[Dict],
) -> Dict:
    """
    Save Apple Health workouts to workout_cache table with UPSERT logic.

    Uses source_workout_id to detect duplicates when re-uploading same export.

    Args:
        db: Database session
        user_id: UUID string of the user
        workouts: List of dicts from AppleHealthParser._parse_workouts()

    Returns:
        Dict with summary
    """
    if not workouts:
        return {
            'total_processed': 0,
            'message': 'No workouts to save.'
        }

    user_uuid = uuid.UUID(user_id)

    records_to_insert = []
    for entry in workouts:
        record = {
            'user_id': user_uuid,
            'source': entry['source'],
            'source_workout_id': entry['source_workout_id'],
            'workout_date': entry['workout_date'],
            'title': entry['title'],
            'duration_minutes': entry.get('duration_minutes'),
            'total_sets': entry.get('total_sets'),
            'total_volume_kg': entry.get('total_volume_kg'),
            'exercise_count': entry.get('exercise_count'),
            'calories_burned': entry.get('calories_burned'),
            'muscle_groups': entry.get('muscle_groups'),
            'workout_data': entry['workout_data'],
        }
        records_to_insert.append(record)

    stmt = insert(WorkoutCache).values(records_to_insert)

    # UPSERT: Update on conflict with unique constraint (user_id, source, source_workout_id)
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'source', 'source_workout_id'],
        set_={
            'workout_date': stmt.excluded.workout_date,
            'title': stmt.excluded.title,
            'duration_minutes': stmt.excluded.duration_minutes,
            'total_sets': stmt.excluded.total_sets,
            'total_volume_kg': stmt.excluded.total_volume_kg,
            'exercise_count': stmt.excluded.exercise_count,
            'calories_burned': stmt.excluded.calories_burned,
            'muscle_groups': stmt.excluded.muscle_groups,
            'workout_data': stmt.excluded.workout_data,
            'last_synced': func.now(),
            'updated_at': func.now(),
        }
    )

    await db.execute(stmt)
    await db.commit()

    return {
        'total_processed': len(workouts),
        'message': 'Workouts saved with UPSERT logic.'
    }


async def save_apple_health_data(
    db: AsyncSession,
    user_id: str,
    parsed_data: Dict,
) -> Dict:
    """
    Main entry point to save all Apple Health data.

    Saves to three tables:
    - health_metrics_daily (daily aggregates)
    - health_metrics_raw (time-series data)
    - workout_cache (workout summaries)

    Args:
        db: Database session
        user_id: UUID string of the user
        parsed_data: Dict with 'daily_metrics', 'raw_metrics', 'workouts' keys

    Returns:
        Dict with summary of all operations
    """
    results = {}

    # Save daily metrics
    print(f"[DEBUG] Starting daily metrics save: {len(parsed_data.get('daily_metrics', []))} records")
    daily_result = await save_daily_metrics(
        db, user_id, parsed_data.get('daily_metrics', [])
    )
    results['daily_metrics'] = daily_result
    print(f"[DEBUG] Daily metrics complete: {daily_result}")

    # Save raw metrics (time-series)
    print(f"[DEBUG] Starting raw metrics save: {len(parsed_data.get('raw_metrics', []))} records")
    raw_result = await save_raw_metrics(
        db, user_id, parsed_data.get('raw_metrics', [])
    )
    results['raw_metrics'] = raw_result
    print(f"[DEBUG] Raw metrics complete: {raw_result}")

    # Save workouts
    print(f"[DEBUG] Starting workouts save: {len(parsed_data.get('workouts', []))} records")
    workout_result = await save_workouts(
        db, user_id, parsed_data.get('workouts', [])
    )
    results['workouts'] = workout_result
    print(f"[DEBUG] Workouts complete: {workout_result}")

    return {
        'success': True,
        'results': results,
        'summary': {
            'daily_metrics': daily_result['total_processed'],
            'raw_metrics': raw_result['total_processed'],
            'workouts': workout_result['total_processed'],
        }
    }
