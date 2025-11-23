"""
Nutrition data service layer.
Handles saving nutrition data to the database with duplicate detection.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from typing import Dict, List
from datetime import date
import uuid
from backend.db.models import NutritionDaily


async def save_nutrition_data(
        db: AsyncSession,
        user_id: str,
        nutrition_data: List[Dict],
) -> Dict:
    """
    Save nutrition data to database with duplicate detection.
    
    Uses PostgreSQL's ON CONFLICT to handle duplicates:
    - If (user_id, log_date) already exists: UPDATE the row
    - If (user_id, log_date) is new: INSERT the row
    
    Args:
        db: Database session
        user_id: UUID string of the user
        nutrition_data: List of dicts from MyNetDiary parser
        
    Returns:
        Dict with summary (inserted_count, updated_count, total_count)
    """
    user_uuid = uuid.UUID(user_id)

    records_to_insert = []
    for entry in nutrition_data:
        record = {
            'user_id': user_uuid,
            'log_date': entry['log_date'],
            'calories': entry.get('calories'),
            'protein_g': entry.get('protein_g'),
            'carbs_g': entry.get('carbs_g'),
            'fats_g': entry.get('fats_g'),
            'fiber_g': entry.get('fiber_g'),
            'source': entry.get('source', 'mynetdiary'),
            'raw_data': entry.get('raw_data'),
        }
        records_to_insert.append(record)

    stmt = insert(NutritionDaily).values(records_to_insert)

    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'log_date'],
        set_ = {
            'calories': stmt.excluded.calories,
            'protein_g': stmt.excluded.protein_g,
            'carbs_g': stmt.excluded.carbs_g,
            'fats_g': stmt.excluded.fats_g,
            'fiber_g': stmt.excluded.fiber_g,
            'source': stmt.excluded.source,
            'raw_data': stmt.excluded.raw_data,
        }
    )

    await db.execute(stmt)
    await db.commit()

    return {
        'total_processed': len(nutrition_data),
        'message': 'Nutrition data saved with UPSERT logic.'
    }