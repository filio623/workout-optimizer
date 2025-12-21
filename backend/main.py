from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager
from backend.config import settings
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db, AsyncSessionLocal
from backend.db.models import User
from uuid import UUID
from backend.routes import nutrition, apple_health, workouts, dashboard
from backend.services.chat_service import (
    get_or_create_session,
    save_message,
    get_user_sessions,
    get_session_messages,
    delete_session,
    update_session_title
)
import asyncio
import logfire


# Configure Logfire
logfire.configure(token=settings.LOGFIRE_TOKEN)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up...")
    yield
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

# Instrument FastAPI with Logfire
logfire.instrument_fastapi(app)

# Instrument Pydantic (for validation tracing)
if hasattr(logfire, "instrument_pydantic"):
    logfire.instrument_pydantic()

# Instrument Pydantic AI (for agent tracing)
if hasattr(logfire, "instrument_pydantic_ai"):
    logfire.instrument_pydantic_ai()

# Instrument OpenAI (for LLM call tracing - prompts, tokens, etc.)
if hasattr(logfire, "instrument_openai"):
    logfire.instrument_openai()

# Instrument Google GenAI (if using Gemini)
if hasattr(logfire, "instrument_google_genai"):
    logfire.instrument_google_genai()

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
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # Optional, creates new if None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ChatSessionResponse(BaseModel):
    id: str
    session_name: str
    created_at: datetime
    last_activity: datetime

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

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

# --- Chat History Endpoints ---

TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

@app.get("/chat/history", response_model=list[ChatSessionResponse])
async def get_history(db: AsyncSession = Depends(get_db)):
    """Get all chat sessions for the current user."""
    sessions = await get_user_sessions(db, TEST_USER_ID)
    return [
        ChatSessionResponse(
            id=str(s.id),
            session_name=s.session_name or "New Conversation",
            created_at=s.created_at,
            last_activity=s.last_activity
        ) for s in sessions
    ]

@app.get("/chat/{session_id}", response_model=list[ChatMessageResponse])
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get messages for a specific session."""
    messages = await get_session_messages(db, session_id, TEST_USER_ID)
    if not messages and session_id:
        # Check if session exists but is empty, or doesn't exist
        # For now just return empty list
        pass
        
    return [
        ChatMessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            timestamp=m.timestamp
        ) for m in messages
    ]

@app.delete("/chat/{session_id}")
async def delete_chat_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a chat session."""
    success = await delete_session(db, session_id, TEST_USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}

# --- Main Chat Endpoints ---

@app.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat endpoint with Pydantic AI agent and session management."""
    try:
        from backend.agents.agent import agent
        from backend.agents.dependencies import AgentDependencies

        # 1. Get or Create Session
        session = await get_or_create_session(db, TEST_USER_ID, request.session_id)
        session_id_str = str(session.id)

        # 2. Save User Message
        await save_message(db, session.id, "user", request.message)

        # 3. Run Agent
        deps = AgentDependencies(
            session_factory=AsyncSessionLocal,
            user_id=TEST_USER_ID
        )

        result = await agent.run(request.message, deps=deps)
        
        # 4. Save Agent Response
        await save_message(db, session.id, "assistant", result.output)

        return ChatResponse(
            response=result.output,
            session_id=session_id_str
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
    
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint with persistence."""
    try:
        from backend.agents.agent import agent
        from backend.agents.dependencies import AgentDependencies

        # We need to manually manage DB session here since StreamingResponse runs in background
        async with AsyncSessionLocal() as db:
            session = await get_or_create_session(db, TEST_USER_ID, request.session_id)
            session_id_str = str(session.id)
            
            # Save User Message immediately
            await save_message(db, session.id, "user", request.message)

        deps = AgentDependencies(
            session_factory=AsyncSessionLocal,
            user_id=TEST_USER_ID,
        )

        async def generate():
            full_response = ""
            try:
                # Emit session ID as the first chunk (custom format or just header?)
                # For simplicity, we just stream text. Client handles session ID separately?
                # Actually, standard is to return session ID in a header or separate event.
                # For this MVP, let's assume client keeps using the ID we sent back or knows it.
                # To be robust, we should probably send it first.
                yield f"SESSION_ID:{session_id_str}\n"

                async with asyncio.timeout(60):
                    prev_text = ""
                    async with agent.run_stream(request.message, deps=deps) as stream:
                        async for chunk in stream.stream_text():
                            new_text = chunk[len(prev_text):]
                            full_response += new_text
                            yield new_text
                            prev_text = chunk
                    yield "\n"
            except asyncio.TimeoutError:
                yield "\n\n❌ Error: Request timed out after 60 seconds. Please try a simpler query.\n"
                full_response += "\n[Error: Request timed out]"
            except ConnectionError as e:
                yield f"\n\n❌ Error: Lost connection to AI service. {str(e)}\n"
                full_response += f"\n[Error: Connection lost: {str(e)}]"
            except Exception as e:
                yield f"\n\n❌ Error: {str(e)}\n"
                full_response += f"\n[Error: {str(e)}]"
            finally:
                # Save Assistant Message
                try:
                    async with AsyncSessionLocal() as db_final:
                        await save_message(db_final, session.id, "assistant", full_response)
                        
                        # Auto-title if it's the first message
                        # (Simplistic check: if session name is default)
                        if session.session_name == "New Conversation":
                            # Generate a title (mock for now, or use first few words)
                            title = request.message[:30] + "..."
                            await update_session_title(db_final, session.id, title)
                except Exception as db_err:
                    print(f"Error saving chat history: {db_err}")

        return StreamingResponse(generate(), media_type="text/plain")


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)