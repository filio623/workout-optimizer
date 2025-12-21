"""
Cross-domain analysis tools for the Pydantic AI agent.

These tools combine data from multiple sources (Workout, Nutrition, Health)
to provide deeper insights and correlations.
"""

from pydantic_ai import RunContext
from backend.agents.dependencies import AgentDependencies
from backend.agents.agent import agent
from sqlalchemy import select, func
from backend.db.models import WorkoutCache, NutritionDaily, HealthMetricsDaily
from typing import Dict, Any, List
from datetime import datetime, timedelta, UTC

# Conversion constant
KG_TO_LBS = 2.20462

@agent.tool
async def analyze_nutrition_vs_training(
    ctx: RunContext[AgentDependencies],
    days: int = 30,
) -> Dict:
    """
    Analyze the relationship between nutrition and training performance.

    This tool correlates caloric/protein intake with workout volume and frequency.
    Use it when users ask:
    - "Why am I not building muscle?"
    - "Is my diet affecting my workouts?"
    - "Am I eating enough for how much I train?"

    Args:
        ctx: Run context
        days: Number of days to analyze (default: 30)

    Returns:
        Analysis dictionary with averages, ratios, and insights.
    """
    cutoff_date = datetime.now(UTC).date() - timedelta(days=days)

    async with ctx.deps.session_factory() as db:
        # 1. Get Nutrition Averages
        nut_stmt = select(
            func.avg(NutritionDaily.calories).label("avg_calories"),
            func.avg(NutritionDaily.protein_g).label("avg_protein_g"),
        ).where(
            NutritionDaily.user_id == ctx.deps.user_id,
            NutritionDaily.log_date >= cutoff_date,
        )
        nut_result = await db.execute(nut_stmt)
        nut_row = nut_result.one()
        
        avg_calories = float(nut_row.avg_calories or 0)
        avg_protein = float(nut_row.avg_protein_g or 0)

        # 2. Get Workout Totals
        workout_stmt = select(
            func.count(WorkoutCache.id).label("total_workouts"),
            func.sum(WorkoutCache.total_volume_kg).label("total_volume_kg")
        ).where(
            WorkoutCache.user_id == ctx.deps.user_id,
            WorkoutCache.workout_date >= cutoff_date,
        )
        work_result = await db.execute(workout_stmt)
        work_row = work_result.one()
        
        total_workouts = int(work_row.total_workouts or 0)
        total_volume_kg = float(work_row.total_volume_kg or 0)
        total_volume_lbs = total_volume_kg * KG_TO_LBS

        # 3. Get Average Bodyweight (for relative protein calc)
        weight_stmt = select(func.avg(HealthMetricsDaily.weight_kg)).where(
            HealthMetricsDaily.user_id == ctx.deps.user_id,
            HealthMetricsDaily.metric_date >= cutoff_date
        )
        weight_result = await db.execute(weight_stmt)
        avg_weight_kg = weight_result.scalar() or 75.0 # Default fallback if no weight data
        avg_weight_lbs = avg_weight_kg * KG_TO_LBS

    # 4. Perform Analysis
    weeks = max(days / 7, 1)
    workouts_per_week = total_workouts / weeks
    
    # Protein ratio (g per lb of bodyweight)
    protein_per_lb = avg_protein / avg_weight_lbs if avg_weight_lbs > 0 else 0
    
    # Calorie balance estimation (Very rough: TDEE ~ bodyweight_lbs * 15)
    est_maintenance = avg_weight_lbs * 15
    calorie_diff = avg_calories - est_maintenance
    
    insights = []
    
    # Protein Insight
    if protein_per_lb < 0.7:
        insights.append(f"Protein intake ({avg_protein:.0f}g) is low ({protein_per_lb:.2f}g/lb). Aim for 0.8-1.0g/lb to support muscle growth.")
    elif protein_per_lb > 1.2:
        insights.append(f"Protein intake is very high ({protein_per_lb:.2f}g/lb). You could trade some protein for carbs to fuel workouts.")
    else:
        insights.append("Protein intake is optimal for muscle building.")

    # Workout/Calorie Insight
    if workouts_per_week > 4 and calorie_diff < -300:
        insights.append("High training volume with significant calorie deficit. Watch out for burnout/recovery issues.")
    elif workouts_per_week < 2 and calorie_diff > 300:
        insights.append("Calorie surplus with low training volume. High risk of gaining fat rather than muscle.")

    return {
        "period_analyzed": f"{days} days",
        "averages": {
            "daily_calories": round(avg_calories),
            "daily_protein_g": round(avg_protein),
            "bodyweight_lbs": round(avg_weight_lbs, 1),
            "workouts_per_week": round(workouts_per_week, 1)
        },
        "ratios": {
            "protein_g_per_lb_bodyweight": round(protein_per_lb, 2),
            "est_calorie_balance": round(calorie_diff)
        },
        "insights": insights,
        "recommendation": insights[0] if insights else "Keep up the balanced routine!"
    }
