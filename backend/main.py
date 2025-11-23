from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from backend.config import config
from backend.hevy.client import HevyClient
#from backend.llm.interface import run_agent_with_session
from backend.services.workout_analyzer import WorkoutAnalyzer
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import User
from uuid import UUID
import logfire
from backend.routes import nutrition

# Configure Logfire
if config.LOGFIRE_TOKEN:
    logfire.configure(
        token=config.LOGFIRE_TOKEN,
        service_name="workout-optimizer"
    )
else:
    # Configure without token for local development
    logfire.configure(
        send_to_logfire=False,
        service_name="workout-optimizer"
    )

# Instrument OpenAI for automatic agent tracing (must be after configure)
logfire.instrument_openai()

# Initialize clients
hevy_client = HevyClient()
workout_analyzer = WorkoutAnalyzer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up...")
    yield
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

# Instrument FastAPI with Logfire
logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:8000", "http://127.0.0.1:8000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nutrition.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user"  # Default session if none provided

class ChatResponse(BaseModel):
    response: str
    session_id: str

class UserProfileCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: str

class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True # Allows SQLAlchemy model to Pydantic model conversion

# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     """Chat endpoint with session management for conversation history."""
#     try:
#         response = await run_agent_with_session(request.message, request.session_id)
#         return ChatResponse(response=response, session_id=request.session_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/api/workout-frequency")
def workout_frequency():
    try:
        data = workout_analyzer.get_weekly_workout_counts()
        return {'data': data}
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/top-exercises")
def top_exercises():
    try:
        data = workout_analyzer.get_top_exercises()
        return {'data': data}
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/top-muscle-groups")
def top_muscle_groups():
    try:
        data = workout_analyzer.get_top_muscle_groups()
        return {'data': data}
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/workout-history")
async def workout_history():
    try:
        data = hevy_client.get_workouts(page_size=7).model_dump(mode="json")
        workouts = data['workouts'][:7]

        formatted_workouts = []
        for workout in workouts:
            start_time = datetime.fromisoformat(workout['start_time'])
            end_time = datetime.fromisoformat(workout['end_time'])
            duration_seconds = (end_time - start_time).total_seconds()
            duration_minutes = int(duration_seconds / 60)
            duration_hours = int(duration_minutes / 60)

            # Format duration to show only relevant units
            if duration_hours > 0:
                duration_str = f"{duration_hours} hours, {duration_minutes % 60} minutes"
            else:
                duration_str = f"{duration_minutes} minutes"

            total_sets = sum(len(exercise['sets']) for exercise in workout['exercises'])

            formatted_workouts.append({
                'id': workout['id'],
                'title': workout['title'],
                'date': start_time.isoformat(),
                'duration': duration_str,
                'sets': total_sets,
            })
        return formatted_workouts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.post("/user/profile", response_model=UserProfileResponse)
async def create_user_profile(user_data: UserProfileCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user profile."""
    try:
        new_user = User(
            name=user_data.name,
            email=user_data.email
        )
        #add and commit new user
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user) #refresh to get new ID

        #convert to response model
        return UserProfileResponse(
            id=str(new_user.id),
            name=new_user.name,
            email=new_user.email,
            created_at=new_user.created_at.isoformat(),
            updated_at=new_user.updated_at.isoformat()
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user profile: {str(e)}")
    
@app.get("/user/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a user profile by ID."""
    try:
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        #convert to response model
        return UserProfileResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user profile: {str(e)}")

# Note: /analyze endpoint removed - analysis is now handled through AI chat interface


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)