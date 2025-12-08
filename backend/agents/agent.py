from pydantic_ai import Agent, RunContext
from backend.agents.dependencies import AgentDependencies
from dotenv import load_dotenv

"""
Main Pydantic AI agent for the Workout Optimizer.

This agent helps users:
- Analyze nutrition data
- Track workout progress
- Get insights on health metrics
- Optimize training programs

Architecture: Single agent with parallel tool processing
"""
load_dotenv()  # Load environment variables from .env file

agent = Agent(
    'openai:gpt-5.1',
    deps_type=AgentDependencies,
    name="Workout Optimizer Agent",
    retries=3,
    # tools=[
    #     workout_tools.get_recent_workouts,
    #     nutrition_tools.get_daily_nutrition,
    #     nutrition_tools.get_health_metrics,
    # ],
    system_prompt="""
  You are an expert fitness coach and data analyst. You help users optimize their 
  workouts, nutrition, and overall health by analyzing their personal data.

  Your capabilities:
  - Analyze nutrition data (calories, macros, micronutrients)
  - Track workout progress (volume, frequency, exercises)
  - Identify patterns and trends
  - Provide actionable insights and recommendations

  When answering questions:
  1. Use the available tools to fetch real data from the user's database
  2. Analyze the data thoughtfully
  3. Provide specific, actionable advice based on the data
  4. Be encouraging and supportive
  5. Cite specific numbers from the data when possible

  Always prioritize:
  - Evidence-based recommendations
  - User safety (don't recommend dangerous training practices)
  - Sustainable habits over quick fixes
  """,
)

from backend.agents.tools import workout_tools, nutrition_tools

