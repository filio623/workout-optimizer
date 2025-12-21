from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from backend.db.database import get_db
from backend.db.models import WorkoutCache
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
import math

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Hardcoded user ID for MVP
TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Get aggregated statistics for the frontend dashboard.
    """
    now = datetime.now(UTC)
    today = now.date()
    
    # 1. Weekly Progress (Last 7 Days)
    # --------------------------------
    seven_days_ago = today - timedelta(days=6)
    
    # Initialize dictionary for last 7 days
    weekly_data = {}
    for i in range(7):
        date_key = (seven_days_ago + timedelta(days=i)).isoformat()
        day_name = (seven_days_ago + timedelta(days=i)).strftime("%a")
        weekly_data[date_key] = {"day": day_name, "value": 0, "raw_date": date_key}

    # Query workouts
    query = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date >= seven_days_ago
    )
    result = await db.execute(query)
    workouts = result.scalars().all()

    # Fill data
    for w in workouts:
        date_key = w.workout_date.date().isoformat()
        if date_key in weekly_data:
            # Value is percentage of "good workout" (arbitrary 60 mins = 100%)
            duration = w.duration_minutes or 0
            score = min(100, (duration / 60) * 100) 
            # If multiple workouts, take max or sum? Let's take max for "intensity"
            weekly_data[date_key]["value"] = max(weekly_data[date_key]["value"], score)

    weekly_progress = list(weekly_data.values())

    # 2. Muscle Group Distribution (Last 30 Days)
    # -------------------------------------------
    thirty_days_ago = today - timedelta(days=30)
    query_month = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date >= thirty_days_ago
    )
    result_month = await db.execute(query_month)
    month_workouts = result_month.scalars().all()

    muscle_counts = {}
    total_exercises = 0

    for w in month_workouts:
        # Check if muscle_groups column is populated (it's JSONB)
        # Note: In previous sessions we noticed muscle_groups might be empty,
        # so we fallback to workout_data parsing if needed.
        # But for MVP speed, let's try to extract from workout_data exercises
        
        if w.workout_data and 'exercises' in w.workout_data:
            for ex in w.workout_data['exercises']:
                # Hevy data usually has 'muscle_group' or we infer from template
                # This is a simplification. Real Hevy API returns "muscle_group" in template.
                # We'll try to find it.
                
                # Try to find muscle group string
                m_group = "Other"
                if 'muscle_group' in ex:
                    m_group = ex['muscle_group']
                elif 'exercise_template' in ex and 'muscle_group' in ex['exercise_template']:
                    m_group = ex['exercise_template']['muscle_group']
                
                # Normalize
                m_group = m_group.capitalize()
                muscle_counts[m_group] = muscle_counts.get(m_group, 0) + 1
                total_exercises += 1

    # Convert to percentage format
    muscle_groups = []
    colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-red-500', 'bg-yellow-500']
    
    sorted_muscles = sorted(muscle_counts.items(), key=lambda x: x[1], reverse=True)[:4] # Top 4
    
    for i, (name, count) in enumerate(sorted_muscles):
        percentage = round((count / total_exercises) * 100) if total_exercises > 0 else 0
        muscle_groups.append({
            "name": name,
            "percentage": percentage,
            "color": colors[i % len(colors)]
        })

    # 3. Performance Metrics (Trend)
    # ------------------------------
    # Compare volume of last 14 days vs previous 14 days
    last_14 = sum(float(w.total_volume_kg or 0) for w in month_workouts if w.workout_date.date() >= (today - timedelta(days=14)))
    
    prev_14_query = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date < (today - timedelta(days=14)),
        WorkoutCache.workout_date >= (today - timedelta(days=28))
    )
    result_prev = await db.execute(prev_14_query)
    prev_workouts = result_prev.scalars().all()
    prev_14 = sum(float(w.total_volume_kg or 0) for w in prev_workouts)

    vol_diff = 0
    if prev_14 > 0:
        vol_diff = round(((last_14 - prev_14) / prev_14) * 100)
    elif last_14 > 0:
        vol_diff = 100 # Infinite growth from 0

    # 4. Heatmap Data (Last 28 Days)
    # ------------------------------
    heatmap_data = []
    # Initialize map
    heatmap_map = {}
    start_date = today - timedelta(days=27) # 28 days inclusive
    
    for i in range(28):
        d = start_date + timedelta(days=i)
        heatmap_map[d.isoformat()] = 0

    # Populate with workout counts/intensity
    for w in month_workouts: # Reusing month query (covers 30 days, enough for 28)
        d_key = w.workout_date.date().isoformat()
        if d_key in heatmap_map:
            # Intensity score based on duration (simple)
            # 0.2 = light, 0.5 = medium, 0.8+ = hard
            duration = w.duration_minutes or 0
            intensity = min(1.0, duration / 90.0) # 90 mins is max intensity
            heatmap_map[d_key] = max(heatmap_map[d_key], intensity)

    heatmap_data = list(heatmap_map.values())

    return {
        "weeklyProgress": weekly_progress,
        "muscleGroups": muscle_groups,
        "performance": {
            "volumeTrend": vol_diff,
            "consistency": "+5%" # Placeholder/Mock for now
        },
        "heatmap": heatmap_data
    }
