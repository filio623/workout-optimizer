# Hevy MCP Server (Patched)

This is a locally bundled and patched version of [chrisdoc/hevy-mcp](https://github.com/chrisdoc/hevy-mcp).

## Why Patched?

The original hevy-mcp server has stdout pollution issues that break stdio-based MCP communication:

1. **dotenvx import** - Prints colored status messages to stdout
2. **console.log statements** - Two debug messages that pollute the JSON-RPC stream

## Changes Made

### `src/index.ts`

**Line 1-2:** Removed dotenvx import
```typescript
// PATCHED: Removed dotenvx import to prevent stdout pollution in stdio mode
// import "@dotenvx/dotenvx/config";
```

**Line 35-36:** Removed console.log
```typescript
// PATCHED: Removed console.log to prevent stdout pollution in stdio mode
// console.log("Hevy client initialized with API key");
```

**Line 60-61:** Removed console.log
```typescript
// PATCHED: Removed console.log to prevent stdout pollution in stdio mode
// console.log("Starting MCP server in stdio mode");
```

## Why Bundled Locally?

- ✅ **Reliable** - Doesn't depend on npm registry or network
- ✅ **Fast** - No download/install step
- ✅ **Portable** - Works on any machine with Node.js
- ✅ **Controlled** - We know exactly what version we're running

## Version Info

- **Original Package:** hevy-mcp v1.12.5
- **Patched:** 2025-11-28
- **Node.js Required:** v20 or higher

## Pull Request Status

A PR has been submitted to the upstream repository to fix these issues:
- PR Link: [To be added]

Once merged, we can switch back to the official npm package.

## Setup Instructions

### First Time Setup (or After Cloning Repo)

The `node_modules` directory is not committed to git. After cloning the repo, you need to install dependencies:

```bash
# From the Workout_Optimizer directory
cd backend/mcp_servers
chmod +x setup_mcp_servers.sh
./setup_mcp_servers.sh
```

Or manually:

```bash
cd backend/mcp_servers/hevy-mcp
npm install
```

**Requirements:**
- Node.js v20 or higher

## Usage in Code

See `backend/services/mcp_hevy.py` for how this server is used in the application.

Example:
```python
from backend.services.mcp_hevy import get_hevy_mcp_session

async for session in get_hevy_mcp_session():
    # Discover tools
    tools = await session.list_tools()

    # Call a tool
    result = await session.call_tool("get-workouts", {"pageSize": 10})
```
