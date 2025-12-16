"""
Test script to create sample data for the new models.
This verifies that our nutrition, health metrics, and workout cache tables work correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.append(str(Path(__file__).parent.parent))

from datetime import date, datetime, timedelta
from sqlalchemy import select
from backend.db.database import AsyncSessionLocal
from backend.db.models import (
    User,
    NutritionDaily,
    HealthMetricsRaw,
    HealthMetricsDaily,
    WorkoutCache
)


async def create_sample_data():
    """Create sample data for all new tables"""

    async with AsyncSessionLocal() as session:
        # Get an existing user (or create one)
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No users found! Create a user first.")
            return

        print(f"✅ Using user: {user.name} ({user.id})")

        # 1. Create sample nutrition data
        print("\n📊 Creating sample nutrition data...")
        nutrition = NutritionDaily(
            user_id=user.id,
            log_date=date.today() - timedelta(days=1),  # Yesterday
            calories=2500,
            protein_g=180.5,
            carbs_g=250.0,
            fats_g=80.0,
            fiber_g=30.0,
            meal_count=4,
            protein_per_kg_bodyweight=2.2,
            calorie_surplus_deficit=200,
            meals={
                "breakfast": {"calories": 600, "protein": 40},
                "lunch": {"calories": 800, "protein": 50},
                "dinner": {"calories": 900, "protein": 70},
                "snack": {"calories": 200, "protein": 20}
            },
            source="mynetdiary"
        )
        session.add(nutrition)
        print(f"  ✅ Added nutrition entry for {nutrition.log_date}")

        # 2. Create sample raw health metrics
        print("\n📊 Creating sample raw health metrics...")
        today = datetime.now()

        # Steps metric
        steps_metric = HealthMetricsRaw(
            user_id=user.id,
            metric_date=today,
            metric_type="steps",
            value=12543,
            unit="count",
            source="apple_health",
            source_metadata={"device": "iPhone 15", "ios_version": "17.2"}
        )
        session.add(steps_metric)

        # Weight metric
        weight_metric = HealthMetricsRaw(
            user_id=user.id,
            metric_date=today,
            metric_type="weight",
            value=82.5,
            unit="kg",
            source="apple_health",
            source_metadata={"device": "Apple Watch"}
        )
        session.add(weight_metric)

        # Heart rate metric
        hr_metric = HealthMetricsRaw(
            user_id=user.id,
            metric_date=today - timedelta(hours=2),
            metric_type="heart_rate",
            value=72,
            unit="bpm",
            source="apple_health",
            source_metadata={"context": "resting"}
        )
        session.add(hr_metric)

        print(f"  ✅ Added 3 raw health metrics (steps, weight, heart_rate)")

        # 3. Create sample daily health metrics (aggregated)
        print("\n📊 Creating sample daily health metrics...")
        daily_health = HealthMetricsDaily(
            user_id=user.id,
            metric_date=date.today() - timedelta(days=1),
            steps=12543,
            weight_kg=82.5,
            active_calories=650,
            resting_heart_rate=68,
            sleep_hours=7.5,
            distance_meters=8500,
            additional_metrics={
                "vo2_max": 45.2,
                "hrv": 62,
                "body_fat_percentage": 15.3
            }
        )
        session.add(daily_health)
        print(f"  ✅ Added daily health metrics for {daily_health.metric_date}")

        # 4. Create sample workout cache
        print("\n📊 Creating sample workout cache...")
        workout = WorkoutCache(
            user_id=user.id,
            source="hevy",
            source_workout_id="hevy_123456",
            workout_date=datetime.now() - timedelta(days=2),
            title="Push Day - Chest & Triceps",
            duration_minutes=75,
            total_sets=24,
            total_volume_kg=5400.0,
            exercise_count=6,
            calories_burned=320,
            muscle_groups=["chest", "triceps", "shoulders"],
            workout_data={
                "exercises": [
                    {
                        "name": "Bench Press",
                        "sets": [
                            {"reps": 8, "weight_kg": 100},
                            {"reps": 8, "weight_kg": 100},
                            {"reps": 6, "weight_kg": 105},
                            {"reps": 5, "weight_kg": 105}
                        ]
                    },
                    {
                        "name": "Incline Dumbbell Press",
                        "sets": [
                            {"reps": 10, "weight_kg": 35},
                            {"reps": 10, "weight_kg": 35},
                            {"reps": 8, "weight_kg": 37.5}
                        ]
                    },
                    {
                        "name": "Tricep Dips",
                        "sets": [
                            {"reps": 12, "weight_kg": 0},
                            {"reps": 10, "weight_kg": 0},
                            {"reps": 8, "weight_kg": 10}
                        ]
                    }
                ],
                "notes": "Great session, felt strong on bench!"
            }
        )
        session.add(workout)
        print(f"  ✅ Added workout cache for '{workout.title}'")

        # Commit all changes
        await session.commit()
        print("\n✅ All sample data committed to database!")

        # Query back to verify
        print("\n🔍 Verifying data was saved...")

        # Check nutrition
        result = await session.execute(
            select(NutritionDaily).where(NutritionDaily.user_id == user.id)
        )
        nutrition_count = len(result.scalars().all())
        print(f"  📊 Nutrition entries: {nutrition_count}")

        # Check raw health metrics
        result = await session.execute(
            select(HealthMetricsRaw).where(HealthMetricsRaw.user_id == user.id)
        )
        raw_metrics_count = len(result.scalars().all())
        print(f"  📊 Raw health metrics: {raw_metrics_count}")

        # Check daily health metrics
        result = await session.execute(
            select(HealthMetricsDaily).where(HealthMetricsDaily.user_id == user.id)
        )
        daily_metrics_count = len(result.scalars().all())
        print(f"  📊 Daily health metrics: {daily_metrics_count}")

        # Check workouts
        result = await session.execute(
            select(WorkoutCache).where(WorkoutCache.user_id == user.id)
        )
        workout_count = len(result.scalars().all())
        print(f"  📊 Workout cache entries: {workout_count}")

        print("\n🎉 Success! All models are working correctly!")


if __name__ == "__main__":
    asyncio.run(create_sample_data())
