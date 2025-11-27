"""add unique constraints for apple health data deduplication

Revision ID: 4238bb629b95
Revises: 3b86f5223fdc
Create Date: 2025-11-24 23:49:45.870386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4238bb629b95'
down_revision: Union[str, Sequence[str], None] = '3b86f5223fdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraints to prevent duplicate Apple Health data."""
    # Add unique constraint to health_metrics_raw
    # Prevents duplicate time-series data points (same user, metric, timestamp)
    op.create_unique_constraint(
        'uix_user_metric_type_date',
        'health_metrics_raw',
        ['user_id', 'metric_type', 'metric_date']
    )

    # Add unique constraint to workout_cache
    # Prevents duplicate workouts from same source (same user, source, workout ID)
    op.create_unique_constraint(
        'uix_user_source_workout_id',
        'workout_cache',
        ['user_id', 'source', 'source_workout_id']
    )


def downgrade() -> None:
    """Remove unique constraints."""
    op.drop_constraint('uix_user_metric_type_date', 'health_metrics_raw', type_='unique')
    op.drop_constraint('uix_user_source_workout_id', 'workout_cache', type_='unique')
