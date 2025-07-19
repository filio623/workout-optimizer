from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.config import config
from app.hevy.client import HevyClient
from app.llm.interface import LLMInterface

# Initialize clients
hevy_client = HevyClient()
llm_interface = LLMInterface()

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

@app.post("/chat")
async def chat(message: str):
    # TODO: Call llm_interface to get AI response
    return {"message": message}

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