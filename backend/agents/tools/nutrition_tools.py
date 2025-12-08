from pydantic_ai import RunContext
from backend.agents.agent import agent
from backend.agents.dependencies import AgentDependencies
from sqlalchemy import func, select
from backend.db.models import NutritionDaily
from typing import Dict
from datetime import datetime, timedelta, UTC


@agent.tool
async def get_nutrition_stats(
    ctx: RunContext[AgentDependencies],
    days: int = 7,
) -> Dict:
    """
    Get average nutrition data over the past specified number of days.

    This tool queris the nutrition_daily table and calculates averages for calories,
    protein, carbs, and fats over the specified time period.

    Args:
        ctx: The run context containing db session and user_id
        days: Number of days to analyze (default is 7)

    Returns:
        A dictionary with average nutrition data and day count
        Example: {
            "days_analyzed": 7,
            "avg_calories": 2200,
            "avg_protein_g": 150,
            "avg_carbs_g": 250,
            "avg_fats_g": 70
            }    
    """
    cutoff_date = datetime.now(UTC).date() - timedelta(days=days)

    stmt = select(
        func.count(NutritionDaily.id).label("day_count"),
        func.avg(NutritionDaily.calories).label("avg_calories"),
        func.avg(NutritionDaily.protein_g).label("avg_protein_g"),
        func.avg(NutritionDaily.carbs_g).label("avg_carbs_g"),
        func.avg(NutritionDaily.fats_g).label("avg_fats_g"),
    ).where(
        NutritionDaily.user_id == ctx.deps.user_id,
        NutritionDaily.log_date >= cutoff_date,
    )

    result = await ctx.deps.db.execute(stmt)
    row = result.one()
    return {
        "days_analyzed": row.day_count,
        "avg_calories": round(row.avg_calories, 1) if row.avg_calories else 0,
        "avg_protein_g": round(row.avg_protein_g, 1) if row.avg_protein_g else 0,
        "avg_carbs_g": round(row.avg_carbs_g, 1) if row.avg_carbs_g else 0,
        "avg_fats_g": round(row.avg_fats_g, 1) if row.avg_fats_g else 0,
    }