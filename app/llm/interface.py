from agents import Agent, Runner, function_tool
from app.services.workout_analyzer import get_yesterdays_workout, get_workout_duration, get_current_program, get_all_program_routines
from app.services.program_analyzer import aggregate_program_exercises
from app.config import config

OPENAI_MODEL = config.OPENAI_MODEL
OPENAI_API_KEY = config.OPENAI_API_KEY


tools = [
    function_tool(get_yesterdays_workout),
    function_tool(get_current_program),
]

agent = Agent(
    name="Fitness Assistant",
    instructions="You are a helpful workout and fitness assistant that provides advice on workout routines, nutrition, and fitness tracking.",
    model=OPENAI_MODEL,
    tools=tools,
    )

result = Runner.run_sync(agent, "Can you tell me the name of my current program and what routines are in it?")
print(result.final_output)
