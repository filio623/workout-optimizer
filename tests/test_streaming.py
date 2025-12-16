import asyncio
from backend.agents.agent import agent
from backend.agents.dependencies import AgentDependencies
from backend.db.database import AsyncSessionLocal
from pydantic_ai import Agent, AgentRunResultEvent, AgentStreamEvent, RunContext

TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"

deps = AgentDependencies(
    session_factory=AsyncSessionLocal,
    user_id=str(TEST_USER_ID),
)

test_message = "what was my average protein intake last month? and does this seem like a good protein intake for trying to build muscle?"

async def generate_stream():
    prev_text = ""
    async with agent.run_stream(test_message, deps=deps) as stream:
        async for chunk in stream.stream_text():
            new_text = chunk[len(prev_text):]
            print(new_text, end='', flush=True)
            prev_text = chunk
    print("\n")

if __name__ == "__main__":
    asyncio.run(generate_stream())