from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from backend.db.database import get_db
from backend.db.models import WorkoutCache, NutritionDaily
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
from backend.services.workout_service import deduplicate_workouts
import math
import json
from pathlib import Path

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Hardcoded user ID for MVP
TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

# Load exercise templates for fast lookup
try:
    # Try root cache directory first (most likely to be fresh)
    # backend/routes/dashboard.py -> backend/routes -> backend -> root
    root_dir = Path(__file__).parent.parent.parent
    cache_path = root_dir / "cache" / "exercise_templates_cache.json"
    data_path = root_dir / "backend" / "data" / "exercise_templates.json"
    
    templates_path = cache_path
    if not templates_path.exists():
        templates_path = data_path
        print(f"DEBUG: Cache not found, falling back to: {templates_path.resolve()}", flush=True)
    else:
        print(f"DEBUG: Loading templates from: {templates_path.resolve()}", flush=True)
    
    if not templates_path.exists():
        print(f"ERROR: Template file not found at {templates_path.resolve()}", flush=True)
        TEMPLATE_MAP = {}
    else:
        with open(templates_path, "r") as f:
            data = json.load(f)
            
            # Handle both list (legacy) and dict wrapper (current) formats
            if isinstance(data, dict) and "exercises" in data:
                templates_list = data["exercises"]
            elif isinstance(data, list):
                templates_list = data
            else:
                templates_list = []
                print("ERROR: Unexpected JSON format in exercise templates", flush=True)

            # Create a mapping: template_id -> primary_muscle_group
            TEMPLATE_MAP = {t["id"]: t.get("primary_muscle_group", "other") for t in templates_list}
            print(f"DEBUG: Successfully loaded {len(TEMPLATE_MAP)} templates.", flush=True)
except Exception as e:
    print(f"Warning: Could not load exercise templates: {e}", flush=True)
    TEMPLATE_MAP = {}

def map_workout_to_category(title: str) -> str:
    """Fall back categorization for workouts without muscle group data."""
    title = title.lower()
    if "strength" in title: return "Strength"
    if "walk" in title or "run" in title or "cycle" in title or "bike" in title: return "Cardio"
    if "yoga" in title: return "Flexibility"
    if "hiit" in title: return "HIIT"
    return "Other"

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
    
    weekly_data = {}
    for i in range(7):
        date_key = (seven_days_ago + timedelta(days=i)).isoformat()
        day_name = (seven_days_ago + timedelta(days=i)).strftime("%a")
        weekly_data[date_key] = {"day": day_name, "value": 0, "raw_date": date_key}

    query = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date >= seven_days_ago
    )
    result = await db.execute(query)
    raw_workouts = result.scalars().all()
    workouts = deduplicate_workouts(raw_workouts) # Deduplicate!

    for w in workouts:
        date_key = w.workout_date.date().isoformat()
        if date_key in weekly_data:
            duration = w.duration_minutes or 0
            # Score is normalized intensity (minutes vs 60m goal)
            score = min(100, (duration / 60) * 100) 
            weekly_data[date_key]["value"] = max(weekly_data[date_key]["value"], score)

    weekly_progress = list(weekly_data.values())

    # 2. Muscle Group Distribution (Last 90 Days)
    # -------------------------------------------
    # Expanded window to 90 days to capture workout preferences even with gaps
    ninety_days_ago = today - timedelta(days=90)
    query_month = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date >= ninety_days_ago
    )
    result_month = await db.execute(query_month)
    raw_month_workouts = result_month.scalars().all()
    month_workouts = deduplicate_workouts(raw_month_workouts) # Deduplicate!

    category_counts = {}
    total_points = 0

    for w in month_workouts:
        # Strategy: Only use Hevy data for muscle groups to ensure specific anatomy (e.g. "Chest") 
        # rather than generic categories (e.g. "Strength").
        if w.source != 'hevy':
            continue

        m_groups = []
        
        if w.workout_data and 'exercises' in w.workout_data:
            for ex in w.workout_data['exercises']:
                # Look up template ID in our loaded map
                template_id = ex.get('exercise_template_id')
                if template_id and template_id in TEMPLATE_MAP:
                    m_groups.append(TEMPLATE_MAP[template_id].capitalize())
                
                # Fallback to embedded data if map lookup fails
                elif 'muscle_group' in ex:
                    m_groups.append(ex['muscle_group'].capitalize())
        
        for g in m_groups:
            category_counts[g] = category_counts.get(g, 0) + 1
            total_points += 1

    muscle_groups = []
    colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-red-500', 'bg-yellow-500']
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    
    for i, (name, count) in enumerate(sorted_cats):
        percentage = round((count / total_points) * 100) if total_points > 0 else 0
        muscle_groups.append({
            "name": name,
            "percentage": percentage,
            "color": colors[i % len(colors)]
        })

    # 3. Performance & Summary Stats
    # ------------------------------
    
    # Workouts this week
    workouts_this_week = len(workouts)
    
    # Calculate Streak (Active weeks in last month)
    active_days = len(set(w.workout_date.date() for w in month_workouts))
    
    # Avg duration
    avg_dur = 0
    if month_workouts:
        avg_dur = sum(w.duration_minutes or 0 for w in month_workouts) / len(month_workouts)

    # Volume trend (Minutes trend if no volume)
    last_14_days = [w for w in month_workouts if w.workout_date.date() >= (today - timedelta(days=14))]
    prev_14_days_query = select(WorkoutCache).where(
        WorkoutCache.user_id == TEST_USER_ID,
        WorkoutCache.workout_date < (today - timedelta(days=14)),
        WorkoutCache.workout_date >= (today - timedelta(days=28))
    )
    prev_result = await db.execute(prev_14_days_query)
    raw_prev_14_days = prev_result.scalars().all()
    prev_14_days = deduplicate_workouts(raw_prev_14_days) # Deduplicate!

    # Use duration as fallback metric for trend
    curr_metric = sum(w.duration_minutes or 0 for w in last_14_days)
    prev_metric = sum(w.duration_minutes or 0 for w in prev_14_days)
    
    perf_trend = 0
    if prev_metric > 0:
        perf_trend = round(((curr_metric - prev_metric) / prev_metric) * 100)
    elif curr_metric > 0:
        perf_trend = 100

    # 4. Heatmap Data (Last 28 Days)
    # ------------------------------
    heatmap_map = {}
    start_date = today - timedelta(days=27)
    for i in range(28):
        heatmap_map[(start_date + timedelta(days=i)).isoformat()] = 0

    for w in month_workouts:
        d_key = w.workout_date.date().isoformat()
        if d_key in heatmap_map:
            intensity = min(1.0, (w.duration_minutes or 0) / 90.0)
            heatmap_map[d_key] = max(heatmap_map[d_key], intensity)

    return {
        "weeklyProgress": weekly_progress,
        "muscleGroups": muscle_groups,
        "performance": {
            "volumeTrend": perf_trend,
            "consistency": "+12%" # Mock logic for now
        },
        "heatmap": list(heatmap_map.values()),
        "quickStats": {
            "weeklyGoals": f"{workouts_this_week}/5",
            "streak": f"{active_days} active days",
            "avgDuration": f"{round(avg_dur)} min",
            "progress": f"{'+' if perf_trend >= 0 else ''}{perf_trend}%"
        }
    }
