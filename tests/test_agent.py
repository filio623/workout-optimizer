"""
Quick test script to verify the Pydantic AI agent works.
"""

import asyncio
from backend.agents.agent import agent
from backend.agents.dependencies import AgentDependencies
from backend.db.database import get_db
from backend.config import config

# Your test user ID
TEST_USER_ID = "2ae24e52-8440-4551-836b-7e2cd9ec45d5"


async def test_agent():
    """Test the agent with a simple nutrition query."""

    print("🧪 Testing Pydantic AI Agent...\n")

    # Get database session
    async for db in get_db():
        # Create dependencies
        deps = AgentDependencies(
            db=db,
            user_id=TEST_USER_ID
        )

        # Test query
        user_message = "What was my average protein intake over the last 7 days?"

        print(f"User: {user_message}\n")
        print("Agent is thinking...\n")

        # Run the agent
        result = await agent.run(user_message, deps=deps)

        print(f"Agent: {result.output}\n")
        print("✅ Agent test complete!")

        break  # Only need first session


if __name__ == "__main__":
    asyncio.run(test_agent())