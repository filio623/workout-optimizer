from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from backend.config import config
from backend.parsers.mynetdiary import MyNetDiaryParser
from backend.services.nutrition_service import save_nutrition_data
from backend.db.database import get_db
import tempfile
import os



router = APIRouter(prefix="/nutrition", tags=["nutrition"])

TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5" # Use a fixed test user ID for uploads

@router.post("/upload") # Full path: /nutrition/upload
async def upload_nutrition_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Upload and parse a MyNetDiary Excel file to extract daily nutrition summaries.
    Args:
        file: Excel file (.xls) exported from MyNetDiary
    Returns:
        A list of daily nutrition summaries parsed from the file.
    """

    if not file.filename.endswith('.xls'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an .xls file.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xls') as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")
    
    try:
        parser = MyNetDiaryParser(tmp_file_path)
        daily_data = parser.parse()

        result = await save_nutrition_data(
            db=db,
            user_id=TEST_USER_ID,
            nutrition_data=daily_data,
        )
    except Exception as e:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Error parsing MyNetDiary file: {str(e)}")
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


    return {
        "message": "File parsed successfully and saved to database.",
        "days_parsed": len(daily_data),
        "date_range": {
            "first_date": str(daily_data[0]['log_date']) if daily_data else None,
            "last_date": str(daily_data[-1]['log_date']) if daily_data else None,
        },
        "database_result": result,
        "sample_day": daily_data[0] if daily_data else None,
    }

