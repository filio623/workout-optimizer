from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from app.config import config
from app.hevy.client import HevyClient
from app.llm.interface import run_agent_with_session

# Initialize clients
hevy_client = HevyClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Load config, validate API keys, initialize clients here
    print("App starting up...")
    yield
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with session management for conversation history."""
    try:
        response = await run_agent_with_session(request.message, request.session_id)
        return ChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/workouts")
async def workouts():
    # TODO: Call hevy_client to fetch workouts from Hevy API
    return {"message": "Workouts"}

@app.get("/analyze")
async def analyze(workout: dict):
    # TODO: Call workout_analyzer to analyze the workout data
    return {"message": "Analyze"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)