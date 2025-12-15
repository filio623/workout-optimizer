from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager
from backend.config import settings
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import User
from uuid import UUID
from backend.routes import nutrition, apple_health, workouts
import asyncio



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
    name: str = Field(..., json_schema_extra={"example": "John Doe"})
    email: str

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Allows SQLAlchemy model to Pydantic model conversion

    id: str
    name: str
    email: str
    created_at: str
    updated_at: str


    
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



@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with Pydantic AI agent and session management.

    The agent has access to:
     - Nutrition data queries
     - Workout data queries
     - Health metrics queries
     - Exercise progression tracking
     - More to be added...
     """
    try:
        from backend.agents.agent import agent
        from backend.agents.dependencies import AgentDependencies
        from backend.db.database import AsyncSessionLocal

        TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

        # Pass session factory instead of a single session
        # This allows tools to create their own sessions for parallel execution
        deps = AgentDependencies(
            session_factory=AsyncSessionLocal,
            user_id=TEST_USER_ID
        )

        result = await agent.run(request.message, deps=deps)

        return ChatResponse(
            response=result.output,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
    
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        from backend.agents.agent import agent
        from backend.agents.dependencies import AgentDependencies
        from backend.db.database import AsyncSessionLocal

        TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

        deps = AgentDependencies(
            session_factory=AsyncSessionLocal,
            user_id=TEST_USER_ID,
        )

        async def generate():
            try:
                # Set 60 second timeout to prevent infinite hanging
                async with asyncio.timeout(60):
                    prev_text = ""
                    async with agent.run_stream(request.message, deps=deps) as stream:
                        async for chunk in stream.stream_text():
                            new_text = chunk[len(prev_text):]
                            yield new_text
                            prev_text = chunk
                    yield "\n"
            except asyncio.TimeoutError:
                yield "\n\n❌ Error: Request timed out after 60 seconds. Please try a simpler query.\n"
            except ConnectionError as e:
                yield f"\n\n❌ Error: Lost connection to AI service. {str(e)}\n"
            except Exception as e:
                yield f"\n\n❌ Error: {str(e)}\n"

        return StreamingResponse(generate(), media_type="text/plain")


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)