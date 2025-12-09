from pydantic_ai import RunContext
from backend.agents.agent import agent
from backend.agents.dependencies import AgentDependencies
from sqlalchemy import func, select
from backend.db.models import HealthMetricsDaily
from typing import Dict, List, Optional
from datetime import datetime, timedelta, UTC

@agent.tool
async def get_health_metrics(
    ctx: RunContext[AgentDependencies],
    days: int = 30,
    metrics: Optional[List[str]] = None,
) -> Dict:
    """
    Get daily health metrics (weight, body fat percentage) over the past specified number of days.

    This tool queries the health_metrics_daily table and retrieves daily records for the user.

    Args:
        ctx: The run context containing db session and user_id
        days: Number of days to analyze (default is 30)
        metrics: List of metric types to retrieve (e.g., ['steps', 'weight_lbs', 'active_calories', 'exercise_minutes']).
                 If None, retrieves all available metrics.
    Returns:
        A Dictionary with:
        - days_analyzed: Number of days with data
        - days_requested: Number of days requested
        - data_coverage: Percentage of days with data
        - averages: Average values for each requested metric
        - recent_trend: List of daily records for the most recent 7 days
    """
    cutoff_date = datetime.now(UTC).date() - timedelta(days=days)

    if metrics is None:
        metric_fields = ["steps", "weight_lbs", "active_calories", "exercise_minutes"]
    else:
        metric_fields = metrics

    stmt = (
        select(HealthMetricsDaily)
        .where(
            HealthMetricsDaily.user_id == ctx.deps.user_id,
            HealthMetricsDaily.metric_date >= cutoff_date,
        )
        .order_by(HealthMetricsDaily.metric_date.desc())
    )

    result = await ctx.deps.db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        return {
            "days_analyzed": 0,
            "days_requested": days,
            "data_coverage": "0%",
            "message": f"No health metrics data found for specified period."
        }
    averages = {}
    for metric in metric_fields:
        values = []
        for row in rows:
            value = getattr(row, metric, None)
            if value is not None:
                values.append(value)
        if values:
            averages[metric] = round(sum(values) / len(values), 1)

    recent_trend = []
    for row in rows[:7]:
        record = {"date": row.metric_date.isoformat()}
        for metric in metric_fields:
            value = getattr(row, metric, None)
            if value is not None:
                record[metric] = value
        recent_trend.append(record)
    recent_trend = recent_trend[::-1]  # Reverse to chronological order

    return {
        "days_analyzed": len(rows),
        "days_requested": days,
        "data_coverage": f"{(len(rows)/days)*100:.1f}%",
        "averages": averages,
        "recent_trend": recent_trend
    }


        