"""
MCP service for Hevy integration.

This module provides helper functions for connecting to the locally bundled
hevy-mcp server via the Model Context Protocol (MCP).
"""

from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from backend.config import config


def get_hevy_mcp_server_path() -> Path:
    """
    Get the absolute path to the bundled hevy-mcp server.

    Returns:
        Path object pointing to the hevy-mcp dist/index.js file
    """
    # Get the backend directory (where this file is located)
    backend_dir = Path(__file__).parent.parent

    # Path to bundled MCP server
    mcp_server = backend_dir / "mcp_servers" / "hevy-mcp" / "dist" / "index.js"

    if not mcp_server.exists():
        raise FileNotFoundError(
            f"Hevy MCP server not found at {mcp_server}. "
            "Make sure the hevy-mcp server is bundled in backend/mcp_servers/"
        )

    return mcp_server


def get_hevy_mcp_server_params() -> StdioServerParameters:
    """
    Get MCP server parameters for launching the hevy-mcp server.

    Returns:
        StdioServerParameters configured to launch the bundled hevy-mcp server
    """
    server_path = get_hevy_mcp_server_path()

    return StdioServerParameters(
        command="node",
        args=[str(server_path)],
        env={
            "HEVY_API_KEY": config.HEVY_API_KEY,
        }
    )


async def get_hevy_mcp_session():
    """
    Create and yield an MCP client session connected to hevy-mcp server.

    Usage:
        async for session in get_hevy_mcp_session():
            # Discover tools
            tools = await session.list_tools()

            # Call a tool
            result = await session.call_tool("get-workouts", {"pageSize": 10})

    Yields:
        ClientSession connected to the hevy-mcp server
    """
    server_params = get_hevy_mcp_server_params()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
