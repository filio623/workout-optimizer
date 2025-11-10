from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from app.config import config
from app.hevy.client import HevyClient
from app.llm.interface import run_agent_with_session
from app.services.workout_analyzer import WorkoutAnalyzer
from datetime import datetime
import logfire

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


# Note: /analyze endpoint removed - analysis is now handled through AI chat interface



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)