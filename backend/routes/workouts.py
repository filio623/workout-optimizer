"""
Workout routes for syncing and querying cached workout data.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.db.database import get_db
from backend.db.models import WorkoutCache
from backend.services.workout_service import sync_hevy_workouts
from typing import Optional

router = APIRouter(prefix="/workouts", tags=["workouts"])

TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"  # Use a fixed test user ID


@router.post("/sync")
async def sync_workouts(
    page_size: int = Query(default=10, description="Number of workouts to fetch from Hevy (max 10)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync workouts from Hevy API to local database cache.

    Uses UPSERT logic to handle duplicates gracefully:
    - New workouts are inserted
    - Existing workouts are updated with latest data

    Args:
        page_size: Number of workouts to fetch (default 100)

    Returns:
        Summary of sync operation with count of workouts processed
    """
    try:
        result = await sync_hevy_workouts(
            db=db,
            user_id=TEST_USER_ID,
            page_size=page_size,
        )
        return {
            "success": True,
            "message": result['message'],
            "workouts_synced": result['total_processed'],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing workouts: {str(e)}"
        )


@router.get("/cached")
async def get_cached_workouts(
    limit: int = Query(default=10, description="Number of workouts to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve cached workouts from the database.

    Returns workouts ordered by date (most recent first).

    Args:
        limit: Number of workouts to return (default 10)

    Returns:
        List of cached workout summaries
    """
    try:
        # Query cached workouts
        stmt = (
            select(WorkoutCache)
            .where(WorkoutCache.user_id == TEST_USER_ID)
            .order_by(WorkoutCache.workout_date.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        workouts = result.scalars().all()

        # Format response
        formatted_workouts = []
        for workout in workouts:
            formatted_workouts.append({
                'id': str(workout.id),
                'source': workout.source,
                'source_workout_id': workout.source_workout_id,
                'title': workout.title,
                'date': workout.workout_date.isoformat(),
                'duration_minutes': workout.duration_minutes,
                'exercise_count': workout.exercise_count,
                'total_sets': workout.total_sets,
                'total_volume_kg': float(workout.total_volume_kg) if workout.total_volume_kg else 0,
                'bodyweight_reps': workout.bodyweight_reps,
                'last_synced': workout.last_synced.isoformat() if workout.last_synced else None,
            })

        return {
            "count": len(formatted_workouts),
            "workouts": formatted_workouts,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cached workouts: {str(e)}"
        )


@router.get("/stats")
async def get_workout_stats(db: AsyncSession = Depends(get_db)):
    """
    Get summary statistics for cached workouts.

    Returns aggregate metrics across all cached workouts.
    """
    try:
        stmt = select(
            func.count(WorkoutCache.id).label('total_workouts'),
            func.sum(WorkoutCache.total_volume_kg).label('total_volume'),
            func.sum(WorkoutCache.total_sets).label('total_sets'),
            func.sum(WorkoutCache.bodyweight_reps).label('total_bodyweight_reps'),
            func.avg(WorkoutCache.duration_minutes).label('avg_duration'),
        ).where(WorkoutCache.user_id == TEST_USER_ID)

        result = await db.execute(stmt)
        stats = result.first()

        return {
            'total_workouts': stats.total_workouts or 0,
            'total_volume_kg': float(stats.total_volume or 0),
            'total_sets': stats.total_sets or 0,
            'total_bodyweight_reps': stats.total_bodyweight_reps or 0,
            'avg_duration_minutes': float(stats.avg_duration or 0),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating workout stats: {str(e)}"
        )
