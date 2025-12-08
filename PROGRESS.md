# Workout Optimizer - Progress Log

**Last Updated:** 2025-12-08 (Session 10 Complete)
**Current Phase:** Phase 3 - In Progress (Pydantic AI Agent Implementation)
**Status:** First Pydantic AI agent working! Agent can query nutrition and workout data, respond intelligently via /chat endpoint.

---

## 🎓 LEARNING MODE - READ THIS FIRST

**IMPORTANT FOR CLAUDE CODE SESSIONS:**

This is a **learning project** where the developer (James) is building their first major application. The approach must be:

- ✅ **Teach, don't just code** - Explain the "why" behind every decision
- ✅ **Step-by-step guidance** - Break complex tasks into small, understandable pieces
- ✅ **Understanding checks** - Ask questions to verify comprehension before moving on
- ✅ **Build incrementally** - Small working pieces over big non-working systems
- ✅ **Hands-on learning** - Guide the developer to write code themselves when possible

**Reference Document:** `MASTER_ARCHITECTURE_PLAN.md`
- See section: "Learning Mode: Step-by-step guidance for developer building first major application"
- See section: "Learning Path & Resources" (starting line 1909)

**Teaching Philosophy:**
> "The goal isn't perfection—it's a working app that helps optimize workouts using AI and data."
> "Understand before moving on: Don't cargo-cult code"

---

## 📚 Master Plan Reference Guide

**For Implementation Details, See:** `MASTER_ARCHITECTURE_PLAN.md`

| Topic | Section in Master Plan | Line # |
|-------|----------------------|--------|
| Complete Tech Stack | "Complete Tech Stack" | ~74 |
| Database Schema Design | "Database Design" | ~314 |
| Phase Roadmap | "Implementation Roadmap" | ~1666 |
| Phase 2 Details | "Phase 2: Data Ingestion & Automation" | ~1710 |
| Phase 3 Details | "Phase 3: Pydantic AI & MCP Integration" | ~1752 |
| LLM Context Management | "LLM Context Management (Critical!)" | ~1418 |

---

## 🚀 Quick Start for New Sessions

### Verify System is Working

```bash
# 1. Check if database is running
docker compose ps

# 2. If not running, start it:
docker compose up -d

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Start FastAPI server (port 8005)
python backend/main.py

# 5. Check migration status
alembic current

# 6. View tables in database
docker exec -it workout_optimizer_db psql -U postgres -d workout_optimizer
# Then: \dt
# Exit: \q
```

---

## 📊 Current System State

### What's Working Right Now

**✅ Database (PostgreSQL + TimescaleDB)**
- Running in Docker at `localhost:5432`
- 7 tables created: users, chat_sessions, chat_messages, nutrition_daily, health_metrics_raw, health_metrics_daily, workout_cache
- 2 migrations applied (initial tables + nutrition schema updates)

**✅ FastAPI Backend (Port 8005)**
- `/nutrition/upload` - Upload MyNetDiary Excel files
- `/workouts/sync` - Sync Hevy workouts via MCP
- `/workouts/cached` - Get cached workouts
- `/user/profile` - Create/retrieve user profiles
- **`/chat`** - Chat with Pydantic AI agent (NEW in Session 10!)

**✅ Data Ingestion Pipeline**
- MyNetDiary parser: Extracts 117 nutrition columns from Excel
- Service layer: Bulk insert with UPSERT (handles duplicates)
- **279 days** of nutrition data across 2023-2025
- Complete raw data preservation in JSONB

**✅ Hevy Integration**
- MCP server connected via `hevy_api_key` environment variable
- Can fetch workouts, routines, and exercise templates

---

## 🎯 Phase 2 - Data Ingestion (IN PROGRESS)

### Completed Components

| Component | Status | Description |
|-----------|--------|-------------|
| MyNetDiary Parser | ✅ Complete | Parses Excel exports, aggregates daily nutrition |
| Upload Endpoint | ✅ Complete | `/nutrition/upload` receives files, saves to DB |
| Service Layer | ✅ Complete | `nutrition_service.py` with UPSERT logic |
| Raw Data Storage | ✅ Complete | JSONB column preserves all 117 nutrition fields |
| Multi-year Support | ✅ Complete | Handles 2023-2025 data, prevents duplicates |

### Current Data in Database

**Nutrition Data:**
- **140 days** logged for 2025 (Jan 18 - Dec 8, 2025)
- **Recent average (last 6 days):** 1,526 cal/day, 131.3g protein/day
- **100% raw data coverage** (all 117 columns preserved)

**Apple Health Data:**
- **740 daily metrics** (steps, weight, heart rate, activity time)
- **55,139 raw time-series metrics** (workout heart rate, energy, recovery)
- **466 workouts** from Apple Health (strength training sessions)
- **70+ additional metrics** in JSONB (VO2 max, sleep analysis, nutrition)

**Test User ID:** `2ae24e52-8440-4551-836b-7e2cd9ec45d5`

### Key Technical Decisions Made

**1. UPSERT Strategy**
- Unique constraint on `(user_id, log_date)` enables conflict detection
- `ON CONFLICT DO UPDATE` handles re-uploads gracefully
- Idempotent operations: uploading same file multiple times = same result

**2. Hybrid Data Storage**
- **Indexed columns:** calories, protein_g, carbs_g, fats_g, fiber_g (fast queries)
- **JSONB column:** raw_data with all 117 fields (complete preservation)
- Best of both: speed for common queries + flexibility for any nutrient

**3. Service Layer Pattern**
- Routes (HTTP) → Services (business logic) → Database
- Separation of concerns improves testability and reusability

---

## 🔧 Architecture Decisions & Learnings

### Key Concepts Learned

**Database Design:**
- Unique constraints enable UPSERT operations
- JSONB for flexible schema (future-proof)
- Bulk inserts for performance (131 records in one transaction)

**Data Serialization:**
- Pandas/NumPy types must be converted for PostgreSQL
- NaN → None, Timestamps → ISO strings
- Recursive cleaning for nested structures

**FastAPI Patterns:**
- Dependency injection with `Depends(get_db)`
- Async file handling with `UploadFile`
- Router organization with prefixes (`/nutrition`)

**Testing Approach:**
- Upload → verify → fix → re-upload → verify UPSERT
- Test with real data to catch edge cases early
- Database queries to verify data integrity

---

## 📁 Project Structure

```
Workout_Optimizer/
├── backend/
│   ├── agents/                # NEW! Pydantic AI agent system
│   │   ├── agent.py           # Main agent (Claude 3.5 Sonnet)
│   │   ├── dependencies.py    # Dependency injection
│   │   └── tools/
│   │       ├── nutrition_tools.py  # Nutrition query tools
│   │       └── workout_tools.py    # Workout query tools
│   ├── db/
│   │   ├── models.py          # SQLAlchemy models (7 tables)
│   │   ├── database.py        # Session management
│   │   └── test_connection.py # Connection test script
│   ├── parsers/
│   │   ├── mynetdiary.py      # Excel → Dict parser (with raw_data)
│   │   └── apple_health.py    # JSON → Dict parser (3 methods)
│   ├── services/
│   │   ├── nutrition_service.py      # UPSERT logic for nutrition data
│   │   ├── apple_health_service.py   # UPSERT + batching + deduplication
│   │   └── workout_service.py        # Hevy workout caching with UPSERT
│   ├── routes/
│   │   ├── nutrition.py       # Nutrition upload endpoint
│   │   ├── apple_health.py    # Apple Health upload endpoint
│   │   └── workouts.py        # Workout sync/cache endpoints
│   ├── llm/                   # Legacy (OpenAI Agents SDK - keeping for reference)
│   ├── mcp_servers/           # Hevy MCP server bundle
│   ├── alembic/
│   │   └── versions/          # 5 migrations applied
│   ├── main.py                # FastAPI app (port 8005) with /chat endpoint
│   ├── config.py              # Environment variables
│   ├── test_agent.py          # Test script for Pydantic AI agent
│   └── create_test_user.py    # Test user creation script
├── sample_data/
│   ├── my_net_diary/          # Excel files (2023-2025)
│   └── apple_health/          # JSON export (2023-2025)
├── docker-compose.yml         # PostgreSQL + TimescaleDB
├── requirements.txt           # Python dependencies
└── MASTER_ARCHITECTURE_PLAN.md # Full system design
```

---

## 🎓 Session History Summary

### Session 1-3: Foundation (Complete)
- Docker + PostgreSQL setup
- Alembic migrations configured
- SQLAlchemy models created (7 tables)
- Hevy MCP integration working
- FastAPI skeleton with basic endpoints

### Session 4: MyNetDiary Parser (Complete)
- Built parser class with pandas
- Excel → DataFrame → Dict transformation
- `/nutrition/upload` endpoint working
- Tested with 131 days of real data
- **Key Learning:** Feature-based architecture, DataFrame aggregation

### Session 5: Database Insertion & UPSERT (Complete)
- Added unique constraint to enable UPSERT
- Built service layer with bulk insert
- Implemented `ON CONFLICT DO UPDATE` logic
- Added raw_data JSONB column (117 fields)
- Fixed pandas type serialization (Timestamp, NaN handling)
- Tested with 3 years of data (279 days total)
- **Key Learning:** UPSERT patterns, JSONB flexibility, service layer design

### Session 6: Apple Health Integration (Complete ✅)
- Built AppleHealthParser for JSON exports (not XML)
- Created 3 parsing methods: daily metrics, raw metrics, workouts
- Updated `health_metrics_daily` schema (weight_lbs, exercise_minutes, stand_minutes)
- Added unique constraints for deduplication (user_id + metric_type + date)
- Implemented batch inserts (4000 rows/batch) for PostgreSQL param limits
- Fixed timezone handling (aware → naive UTC)
- **Debugged and solved:** Cardinality violation error from duplicate timestamps within batches
- **Solution:** Added deduplication logic to remove duplicate (metric_type, timestamp) pairs before insert
- **Successfully loaded:**
  - 740 days of daily health metrics (25+ additional metrics in JSONB)
  - 55,139 raw time-series metrics (deduplicated from 58,422)
  - 466 Apple Health workouts
- **Key Learning:** Large-scale data processing, PostgreSQL limits, timezone gotchas, batching strategies, ON CONFLICT constraints within single INSERT

### Session 7: Hevy Workout Caching System (Complete ✅)
- **Goal:** Build local cache of Hevy workouts for fast queries and offline access
- Added unique constraints to `workout_cache` (user_id, source, source_workout_id)
- Added unique constraints to `health_metrics_raw` (user_id, source, metric_type, metric_date)
- Added `bodyweight_reps` column to separately track bodyweight exercise volume
- Built `workout_service.py` with metric calculation and UPSERT sync logic
- **Metric calculations (industry best practices):**
  - Total volume = weight × reps (weighted exercises only)
  - Bodyweight reps = separate tracking (not included in volume)
  - Duration, sets, exercise count from Hevy API data
- Created `/workouts/sync`, `/workouts/cached`, `/workouts/stats` endpoints
- **Successfully synced:** 10 Hevy workouts with deduplication working
- **Current cache:** 475 total workouts (10 Hevy + 465 Apple Health)
- Fixed timezone issues (aware → naive UTC for PostgreSQL compatibility)
- **Key Learning:** Caching patterns, volume calculation standards, UPSERT for idempotent operations, weighted vs bodyweight exercise tracking
- **Note:** Initially used custom HevyClient (REST API), replaced with MCP in Session 9

### Session 8: MCP (Model Context Protocol) - Setup & Learning (Complete ✅)
- **Goal:** Replace custom REST client with standardized MCP protocol for Hevy integration
- **Deep dive learning session:** MCP fundamentals, stdio communication, JSON-RPC protocol
- **Discovered issue:** hevy-mcp server has stdout pollution (dotenvx + console.log statements)
- **Solution:** Forked hevy-mcp, removed 3 lines causing pollution, submitted PR to upstream
- **What we learned:**
  - MCP is "USB for AI apps" - standardizes data source connections
  - MCP servers run as local subprocesses, not remote services
  - stdio transport uses pipes (stdin/stdout) for JSON-RPC messages
  - Tool discovery happens at runtime via `list_tools`
  - Clean stdout is critical for stdio protocol
- **Implementation:**
  - Bundled patched hevy-mcp server in `backend/mcp_servers/hevy-mcp/`
  - Created `mcp_hevy.py` service helper for easy integration
  - Created `test_mcp_connection.py` to verify functionality
  - Added setup script for node_modules installation
  - Documented everything in README files
- **Testing results:**
  - ✅ Successfully connected to MCP server via stdio
  - ✅ Discovered 18 tools dynamically
  - ✅ Called `get-workouts` tool and retrieved real data
  - ✅ Field name difference: camelCase (MCP) vs snake_case (REST API)
- **Open source contribution:**
  - Forked chrisdoc/hevy-mcp on GitHub
  - Created feature branch: `fix/stdio-stdout-pollution`
  - Submitted PR with detailed explanation and testing notes
  - **✅ PR MERGED!** Fixes now in official hevy-mcp package
- **Key Learning:** MCP protocol architecture, stdio debugging, open source contribution workflow, subprocess management, JSON-RPC communication

### Session 9: MCP Production Migration (Complete ✅)
- **Goal:** Complete the refactoring of workout_service.py to use MCP in production
- **Challenges encountered:**
  1. **Async context issues** - FastAPI + MCP async generators incompatible
     - Solution: Use direct `async with` context managers instead of generator pattern
  2. **Page size validation** - MCP server max is 10, not 100
     - Solution: Changed default from 100 → 10, added `isError` flag checking
  3. **Import organization** - MCP imports needed at module level
     - Solution: Moved imports to top of file for proper async/await handling
- **Production implementation:**
  - Refactored `sync_hevy_workouts()` to use stdio_client and ClientSession directly
  - Added proper error handling for MCP validation errors (`result.isError`)
  - Maintained backward compatibility for field names (camelCase and snake_case)
  - Removed deprecated `mcp_hevy.py` helper (using direct integration instead)
  - Cleaned up debug code and traceback prints
- **Testing & Verification:**
  - ✅ Successfully synced 10 workouts via MCP
  - ✅ UPSERT logic working (8 duplicates updated, 2 new inserted)
  - ✅ Database verified: 477 total workouts, 6,754 kg volume
  - ✅ `/workouts/sync`, `/workouts/cached`, `/workouts/stats` all working
- **Architecture improvements:**
  - Subprocess spawned per request (isolated, no state leaks)
  - Standardized protocol replaces custom REST client
  - Community-maintained hevy-mcp server handles API changes
  - All 18 MCP tools available for future features
- **Key Learning:** FastAPI async context management, MCP error handling, subprocess lifecycle, production integration patterns
- **Outcome:** Phase 2 (Data Ingestion & MCP Integration) fully complete!

---

## 🎯 Phase 3 - Pydantic AI Agent (STARTING - Session 10)

### Architectural Decisions (2025-12-07)

**Framework Choice: Pydantic AI** ✅
- **Why not OpenAI Agents SDK:** Vendor lock-in to OpenAI, less flexible
- **Why not LangGraph:** Too complex for initial implementation, steeper learning curve
- **Why Pydantic AI:**
  - ✅ Model-agnostic (Claude, GPT-4, Gemini)
  - ✅ Native MCP support (works with our existing Hevy integration)
  - ✅ Type-safe with Pydantic (matches our FastAPI stack)
  - ✅ Built-in streaming for better UX
  - ✅ Dependency injection for database sessions

**Agent Architecture: Single Agent with Parallel Tool Processing** ✅
- **Pattern:** One coordinating agent with organized tools, parallel execution
- **Why not Hierarchical Supervisor (yet):**
  - Start simple for learning phase
  - Most queries need multiple domains (nutrition + workout + health)
  - Faster to implement and debug
  - Can migrate to supervisor pattern in Phase 5 if needed
- **Future Evolution:** May refactor to Hierarchical Agent Teams when we have 20+ tools

**Implementation Approach:**
1. **Incremental learning** - Start simple, iterate to complex
2. **Phase 3a-3b:** Cleanup legacy code, install Pydantic AI
3. **Phase 3c-3d:** Build single agent with 5-8 core tools
4. **Phase 3e:** Port remaining tools as needed
5. **Phase 4+:** Consider supervisor pattern if complexity increases

### Session 10: Pydantic AI Agent Foundation (Complete ✅)

**Goal:** Build the first working Pydantic AI agent with tool calling and FastAPI integration

**What We Built:**
1. ✅ **Cleaned up legacy code:**
   - Removed `backend/hevy/` (old REST client)
   - Removed `tests/legacy/` directory
   - Commented out old `workout_analyzer` endpoints in main.py
   - Identified legacy `backend/llm/` code (keeping for reference)

2. ✅ **Installed Pydantic AI:**
   - Pydantic AI v1.0.1 with OpenAI + Anthropic support
   - Already installed (discovered during setup)

3. ✅ **Created agent architecture:**
   - `backend/agents/agent.py` - Main agent with Claude 3.5 Sonnet
   - `backend/agents/dependencies.py` - Dependency injection (db, user_id)
   - `backend/agents/tools/nutrition_tools.py` - Nutrition queries
   - `backend/agents/tools/workout_tools.py` - Workout queries

4. ✅ **Built 2 working tools:**
   - `get_nutrition_stats(days)` - Queries nutrition_daily table, calculates averages
   - `get_recent_workouts(limit)` - Queries workout_cache table

5. ✅ **Created `/chat` endpoint:**
   - FastAPI endpoint at POST `/chat`
   - Accepts: `{"message": "...", "session_id": "..."}`
   - Returns: `{"response": "...", "session_id": "..."}`
   - Integrates with Pydantic AI agent via dependency injection

6. ✅ **Tested with real data:**
   - Uploaded 140 days of new MyNetDiary nutrition data (Jan-Dec 2025)
   - Agent successfully queried database and returned accurate averages
   - Test query: "What was my average protein intake over the last 7 days?"
   - Result: "131.3 g per day" (from 6 logged days)

**Key Technical Learnings:**

**Pydantic AI Concepts:**
- `@agent.tool` decorator registers functions with the agent
- `RunContext[AgentDependencies]` provides dependency injection
- Tools receive context automatically, agent decides which tools to call
- Docstrings are critical - agent reads them to understand tool usage
- `await agent.run(message, deps=deps)` executes the agent

**Architecture Pattern:**
- Single agent with parallel tool processing (simpler than hierarchical)
- Tools organized by domain (nutrition, workout, health)
- Agent powered by Claude 3.5 Sonnet (better reasoning than GPT-4)
- Database session injected via FastAPI `Depends(get_db)`

**Debugging Wins:**
- Fixed `datetime.now(UTC)` for Python 3.11+ (modern best practice)
- Fixed async/await in tools (must be async def, must await db queries)
- Fixed typo in label access (`row.day_count` not `row.day.count`)
- Remembered to restart server after adding endpoint! 😄

**Success Metrics:**
- ✅ Agent responds intelligently to natural language queries
- ✅ Parallel tool calling working (can query multiple sources)
- ✅ Type-safe tools with Pydantic validation
- ✅ Real database queries with proper async handling
- ✅ HTTP endpoint working for frontend integration

---

## 🚀 Upcoming Sessions (Phase 3 Roadmap)

### Session 11: Expand Agent Tools
- Port 8-12 additional tools from `backend/llm/tools/`
- Add analysis tools (plateau detection, correlation analysis)
- Implement proper context management

### Session 12: MCP Integration with Agent
- Connect agent to Hevy MCP tools
- Enable queries like "Show my workouts from last week"
- Test multi-source data queries

### Session 13: Streaming & UX
- Implement streaming responses
- Add typing indicators
- Optimize response times

### Later: Consider Supervisor Pattern (if needed)
- Evaluate if single agent struggles with 20+ tools
- Implement hierarchical architecture if accuracy issues appear

---

## 🐛 Known Issues / Tech Debt

1. **Legacy Code Present** - `backend/hevy/`, `backend/llm/` use old agents library (Session 10 cleanup)
2. **Test User Hardcoded** - Need proper authentication (Phase 4)
3. **No Error Handling for Malformed Excel** - Parser assumes correct format
4. **No File Size Limits** - Upload endpoint accepts any size file
5. **No Data Validation** - Trust parser output without validation
6. **Timezone Handling** - Dates assume UTC, no timezone conversion

---

## 💡 Quick Reference: Common Commands

**Database:**
```bash
# Connect to database
docker exec -it workout_optimizer_db psql -U postgres -d workout_optimizer

# View nutrition data
SELECT log_date, calories, protein_g FROM nutrition_daily LIMIT 5;

# Check raw_data
SELECT log_date, jsonb_array_length(raw_data) FROM nutrition_daily LIMIT 3;

# Query specific nutrient from JSONB
SELECT log_date, raw_data->0->>'Calcium, mg' FROM nutrition_daily LIMIT 3;
```

**Alembic:**
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

**FastAPI:**
```bash
# Start server
python backend/main.py

# Upload nutrition file
curl -X POST http://localhost:8005/nutrition/upload \
  -F "file=@sample_data/my_net_diary/MyNetDiary_Year_2024.xls"
```

---

## 📈 Progress Metrics

**Total Sessions:** 10 (in progress)
**Total Time:** ~32-37 hours (including learning, design discussions, debugging)
**Code Written:** ~1000 lines of production code
**Tests Passed:** End-to-end pipeline working with real data from multiple sources
**Data Ingested:**
- 279 days of nutrition data (3 years)
- 740 days of health metrics
- 55,139 time-series data points
- **475 workouts cached** (10 Hevy + 465 Apple Health)
- **38,064 kg total volume** tracked

**Files Created:** 23+ (models, parsers, services, routes, migrations, configs)
**Dependencies Added:** 8 (FastAPI, SQLAlchemy, Alembic, pandas, xlrd, etc.)
**Database Tables:** 7 (users, chat, nutrition, health metrics daily/raw, workouts)
**Migrations Applied:** 5 (initial schema, nutrition updates, Apple Health constraints, workout constraints, bodyweight_reps)

---

**Current Status:** 🟡 **Phase 3 Starting!** Multi-source data pipeline operational. Now building Pydantic AI agent with single-agent + parallel tool processing architecture. Starting with cleanup and foundation work in Session 10.
