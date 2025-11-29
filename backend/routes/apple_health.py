from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from backend.config import config
from backend.parsers.apple_health import AppleHealthParser
from backend.services.apple_health_service import save_apple_health_data
from backend.db.database import get_db
import tempfile
import os


router = APIRouter(prefix="/apple-health", tags=["apple_health"])

TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"  # Use a fixed test user ID for uploads


@router.post("/upload")  # Full path: /apple-health/upload
async def upload_apple_health_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Upload and parse an Apple Health JSON export file.

    Extracts:
    - Daily health metrics (steps, weight, heart rate, etc.)
    - Raw time-series data (workout HR samples, step counts, energy)
    - Workout summaries (outdoor walks, bike rides, strength training, etc.)

    Args:
        file: JSON file (.json) exported from Apple Health (via HealthAutoExport app)

    Returns:
        Summary of parsed and saved data
    """

    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .json file.")

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")

    try:
        # Parse the Apple Health JSON
        parser = AppleHealthParser(tmp_file_path)
        parsed_data = parser.parse()

        # Save to database (3 tables: daily metrics, raw metrics, workouts)
        result = await save_apple_health_data(
            db=db,
            user_id=TEST_USER_ID,
            parsed_data=parsed_data,
        )

    except Exception as e:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Error parsing Apple Health file: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    return {
        "message": "Apple Health data parsed and saved successfully.",
        "summary": result.get('summary', {}),
        "details": {
            "daily_metrics": {
                "count": len(parsed_data.get('daily_metrics', [])),
                "date_range": {
                    "first": str(parsed_data['daily_metrics'][0]['metric_date']) if parsed_data.get('daily_metrics') else None,
                    "last": str(parsed_data['daily_metrics'][-1]['metric_date']) if parsed_data.get('daily_metrics') else None,
                }
            },
            "raw_metrics": {
                "count": len(parsed_data.get('raw_metrics', [])),
            },
            "workouts": {
                "count": len(parsed_data.get('workouts', [])),
                "date_range": {
                    "first": str(parsed_data['workouts'][0]['workout_date']) if parsed_data.get('workouts') else None,
                    "last": str(parsed_data['workouts'][-1]['workout_date']) if parsed_data.get('workouts') else None,
                }
            }
        },
        "database_result": result,
    }
