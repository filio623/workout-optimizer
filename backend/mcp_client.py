"""
MCP client for interacting with the Hevy MCP server.
Provides a reusable utility for calling Hevy tools via stdio transport.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from backend.config import settings

async def call_hevy_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
    """
    Execute a tool on the Hevy MCP server.
    Creates an ephemeral connection for each call to ensure reliability.
    
    Args:
        tool_name: Name of the tool to call (e.g., 'get-workouts')
        arguments: Dict of arguments for the tool
        
    Returns:
        The parsed JSON result from the tool
        
    Raises:
        ValueError: If the tool call fails or returns an error
        RuntimeError: If the MCP server cannot be started or communicated with
    """
    # Path to the Hevy MCP server implementation
    # backend/mcp_client.py -> backend/mcp_servers/hevy-mcp/dist/index.js
    server_script = Path(__file__).parent / "mcp_servers" / "hevy-mcp" / "dist" / "index.js"
    
    if not server_script.exists():
        raise RuntimeError(f"Hevy MCP server not found at {server_script}. Please run backend/mcp_servers/setup_mcp_servers.sh")

    server_params = StdioServerParameters(
        command="node",
        args=[str(server_script)],
        env={"HEVY_API_KEY": settings.HEVY_API_KEY}
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(tool_name, arguments or {})
                
                # Check for MCP errors
                if result.isError:
                    error_msg = result.content[0].text if result.content else "Unknown MCP error"
                    raise ValueError(f"Hevy MCP Error ({tool_name}): {error_msg}")
                
                if not result.content or not result.content[0].text:
                    return None
                
                # Parse result content
                text_content = result.content[0].text
                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    return text_content
                    
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise RuntimeError(f"Failed to communicate with Hevy MCP server: {str(e)}")
