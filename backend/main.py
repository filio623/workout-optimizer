from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from backend.config import config
#from backend.llm.interface import run_agent_with_session
#from backend.services.workout_analyzer import WorkoutAnalyzer
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import User
from uuid import UUID
from backend.routes import nutrition, apple_health, workouts

# Initialize analyzers
#workout_analyzer = WorkoutAnalyzer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up...")
    yield
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:8000", "http://127.0.0.1:8000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nutrition.router)
app.include_router(apple_health.router)
app.include_router(workouts.router)

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

# @app.get("/api/workout-frequency")
# def workout_frequency():
#     try:
#         data = workout_analyzer.get_weekly_workout_counts()
#         return {'data': data}
#     except ConnectionError:
#         raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# @app.get("/api/top-exercises")
# def top_exercises():
#     try:
#         data = workout_analyzer.get_top_exercises()
#         return {'data': data}
#     except ConnectionError:
#         raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# @app.get("/api/top-muscle-groups")
# def top_muscle_groups():
#     try:
#         data = workout_analyzer.get_top_muscle_groups()
#         return {'data': data}
#     except ConnectionError:
#         raise HTTPException(status_code=503, detail="Unable to connect to workout data service")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Note: /workout-history endpoint removed - use /workouts/cached instead (MCP-based caching)
    
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

@app.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat endpoint with Pydantic AI agent and session management.
    
    The agent has access to:
     - Nutrition data queries
     - Workout data queries
     - More to be added...
     """
    try:
        from backend.agents.agent import agent
        from backend.agents.dependencies import AgentDependencies

        TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

        deps = AgentDependencies(
            db=db,
            user_id=TEST_USER_ID
        )

        result = await agent.run(request.message, deps=deps)

        return ChatResponse(
            response=result.output,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)