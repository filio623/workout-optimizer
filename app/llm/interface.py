from agents import Agent, Runner, function_tool

from dotenv import load_dotenv
import os
from app.services.workout_analyzer import get_yesterdays_workout, get_workout_duration, get_current_program, get_all_program_routines
from app.services.program_analyzer import aggregate_program_exercises

# Load environment variables from .env file
load_dotenv()

tools = [
    function_tool(get_yesterdays_workout),
    function_tool(get_current_program),
]

agent = Agent(
    name="Fitness Assistant",
    instructions="You are a helpful workout and fitness assistant that provides advice on workout routines, nutrition, and fitness tracking.",
    model="gpt-4o-mini",
    tools=tools,
    )

result = Runner.run_sync(agent, "Can you tell me the name of my current program and what routines are in it?")
print(result.final_output)
