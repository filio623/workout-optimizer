"""
Test script to verify MCP connection to hevy-mcp server.

This script demonstrates:
1. How to connect to an MCP server via stdio
2. How to initialize the session
3. How to list available tools
4. How to call a tool and get data

Run: python backend/test_mcp_connection.py
"""

import asyncio
import json
from backend.services.mcp_hevy import get_hevy_mcp_session


async def test_hevy_mcp():
    """Test connection to hevy-mcp server and fetch workouts."""

    print("🔧 Step 1: Connecting to bundled hevy-mcp server...")
    print("   - Using locally bundled hevy-mcp (patched version)")
    print()

    # Use the helper function to get MCP session
    async for session in get_hevy_mcp_session():
        print("   ✅ Connected to MCP server!")
        print()

        print("🔍 Step 2: Discovering available tools...")
        tools_list = await session.list_tools()
        print(f"   ✅ Found {len(tools_list.tools)} tools:")
        for tool in tools_list.tools:
            print(f"      - {tool.name}: {tool.description}")
        print()

        print("📞 Step 3: Calling 'get-workouts' tool...")
        print("   - Requesting 3 most recent workouts")

        # Call the get-workouts tool
        result = await session.call_tool(
            "get-workouts",
            arguments={"pageSize": 3}
        )

        print("   ✅ Tool call successful!")
        print()

        print("📦 Step 4: Parsing MCP response...")
        # MCP returns content as a list of content items
        # For hevy-mcp, it returns JSON as text
        if result.content:
            first_content = result.content[0]
            print(f"   - Content type: {first_content.type}")

            # Parse the JSON string
            workouts_data = json.loads(first_content.text)

            # Handle both list and dict responses
            if isinstance(workouts_data, list):
                workouts = workouts_data
                print(f"   - Total workouts in response: {len(workouts)}")
            else:
                workouts = workouts_data.get('workouts', [])
                print(f"   - Total workouts in response: {len(workouts)}")
                print(f"   - Page: {workouts_data.get('page')}/{workouts_data.get('page_count')}")
            print()

            print("🏋️ Step 5: Displaying workout data...")
            for i, workout in enumerate(workouts, 1):
                print(f"   Workout {i}:")
                print(f"      - ID: {workout.get('id')}")
                print(f"      - Title: {workout.get('title')}")
                # hevy-mcp uses camelCase (startTime), raw Hevy API uses snake_case (start_time)
                start_time = workout.get('startTime') or workout.get('start_time')
                print(f"      - Date: {start_time[:10] if start_time else 'N/A'}")
                print(f"      - Exercises: {len(workout.get('exercises', []))}")
            print()

            print("✅ SUCCESS! MCP integration is working!")
            print()
            print("📝 What just happened:")
            print("   1. Launched bundled hevy-mcp server (backend/mcp_servers/hevy-mcp)")
            print("   2. Connected via stdio (stdin/stdout pipes)")
            print("   3. Discovered 18 available tools dynamically")
            print("   4. Called the 'get-workouts' tool")
            print("   5. Received workout data from Hevy API")
            print("   6. All without writing any HTTP request code!")

        else:
            print("   ⚠️  No content in response")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing MCP Connection to hevy-mcp Server")
    print("=" * 70)
    print()

    try:
        asyncio.run(test_hevy_mcp())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
