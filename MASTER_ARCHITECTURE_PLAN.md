# Workout Optimizer - Master Architecture & Implementation Plan
**Last Updated:** 2025-12-20 (Phase 3 Complete - MVP Candidate)
**Status:** Implementation - Phase 3 Complete, Phase 4 Ready
**Learning Mode**: Step-by-step guidance for developer building first major application

---

## Project Structure

```
Workout_Optimizer/
├── backend/           # FastAPI REST API (renamed from app/)
│   ├── hevy/         # Hevy API client (will be replaced by MCP)
│   ├── llm/          # AI agent, tools, session management
│   ├── services/     # Business logic, analyzers, sync services
│   ├── models.py     # Pydantic data models
│   ├── config.py     # Configuration management
│   └── main.py       # FastAPI application entry point
│
├── web/              # React web app (renamed from frontend/)
│   ├── src/          # React components, hooks, services
│   └── ...
│
├── mobile/           # Expo app (web + iOS + Android) - TO BE CREATED
│   ├── app/          # Expo Router file-based routing
│   ├── components/   # Shared React Native components
│   └── ...
│
├── tests/            # Backend tests
├── user_data/        # User profiles, goals, preferences (JSON files)
├── docs/             # Documentation
├── .env              # Environment variables (NOT in git)
├── requirements.txt  # Python dependencies
└── MASTER_ARCHITECTURE_PLAN.md  # This file!
```

**Why this structure?**
- ✅ **Clarity**: `backend/`, `web/`, and `mobile/` are self-explanatory
- ✅ **Scales**: Easy to add more frontends or services
- ✅ **Learning-friendly**: No ambiguity for future reference
- ✅ **Monorepo-ready**: Standard structure for multi-part projects

---

## Table of Contents
1. [Project Vision & Goals](#project-vision--goals)
2. [Complete Tech Stack](#complete-tech-stack)
3. [Architecture Overview](#architecture-overview)
4. [Database Design](#database-design)
5. [Data Ingestion & Automation](#data-ingestion--automation)
6. [LLM Integration & Agentic Framework](#llm-integration--agentic-framework)
7. [Frontend Development](#frontend-development)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Learning Path & Resources](#learning-path--resources)
10. [Code Examples & Patterns](#code-examples--patterns)

---

## Project Vision & Goals

### What We're Building

An intelligent AI-powered fitness coach application that:
- **Connects to Hevy** (workout tracking app) to analyze training data
- **Integrates nutrition data** from MyNetDiary (CSV exports)
- **Incorporates health metrics** from Apple Health (steps, weight, sleep, etc.)
- **Uses AI** to analyze patterns, detect plateaus, and provide personalized coaching
- **Creates workout programs** tailored to user goals (strength, hypertrophy, aesthetics)
- **Runs on multiple platforms** (iOS, Android, Web) from a single codebase

### Core Use Cases

**Example 1: Muscle Growth Troubleshooting**
```
User: "I'm working out 4x/week but not gaining muscle. What's wrong?"

AI Agent:
1. Analyzes recent workouts (volume, intensity, frequency)
2. Checks nutrition data (protein intake, calorie surplus)
3. Reviews health metrics (sleep quality, recovery)
4. Identifies issue: "You're averaging 80g protein/day but need 150g for your bodyweight"
5. Provides actionable recommendations
```

**Example 2: Intelligent Program Design**
```
User: "Create me a 4-day program to build a surfer physique"

AI Agent:
1. Loads user profile (experience level, available equipment)
2. Analyzes current training patterns
3. Generates Upper/Lower split with emphasis on shoulders, chest, back
4. Creates 4 complete routines in Hevy
5. Explains the programming logic and progression plan
```

**Example 3: Performance Analysis**
```
User: "My bench press has stalled for 3 weeks"

AI Agent:
1. Detects plateau in bench press data
2. Analyzes frequency, volume, technique variations
3. Checks recovery indicators (sleep, training frequency)
4. Suggests deload week + variation exercises
5. Can automatically update routine with suggestions
```

---

## Complete Tech Stack

### Backend Technologies

```yaml
Core Framework:
  - Python 3.11+
  - FastAPI 0.115+ (async web framework)
  - Uvicorn (ASGI server)
  - Pydantic V2 (data validation)

Database Stack:
  - PostgreSQL 15+ (main database)
  - TimescaleDB extension (time-series optimization)
  - pgvector extension (optional: vector embeddings for RAG)
  - SQLAlchemy 2.0 (async ORM)
  - Alembic (database migrations)
  - psycopg3 (async PostgreSQL driver)

AI & LLM:
  - Pydantic AI (agentic framework - model agnostic)
  - OpenAI SDK (GPT models)
  - Anthropic SDK (Claude models)
  - MCP Python SDK (Model Context Protocol)

Data Processing:
  - Polars (fast dataframe operations)
  - Pandas (backup for complex operations)
  - NumPy (statistical analysis)
  - PyArrow (efficient data interchange)

Data Parsing:
  - lxml (fast XML parsing for Apple Health)
  - openpyxl (Excel files)
  - csv (built-in, for CSV nutrition logs)

Web Automation:
  - Playwright (browser automation for MyNetDiary scraping)

Background Jobs & Scheduling:
  - APScheduler (task scheduling)
  - FastAPI BackgroundTasks (simple async tasks)
  - Optional: Dramatiq + Redis (complex job queues)

Caching:
  - Redis (query caching, session storage)
  - @lru_cache (Python in-memory caching)

Observability:
  - Logfire (tracing, logging, metrics)
  - Sentry (error tracking - optional)

Development Tools:
  - pytest + pytest-asyncio (testing)
  - Black (code formatting)
  - Ruff (linting)
  - mypy (type checking)
```

### Frontend Technologies

```yaml
Framework:
  - Expo SDK 50+
  - React Native
  - TypeScript 5+

Styling:
  - NativeWind (Tailwind for React Native)
  - React Native StyleSheet (fallback)

Navigation:
  - Expo Router (file-based routing)

State Management:
  - React Context (theme, user state)
  - TanStack Query (server state - optional)
  - Zustand (global state - if needed)

HTTP & API:
  - Axios (HTTP client)
  - React Native fetch (fallback)

UI Components:
  - React Native core components
  - Expo Vector Icons
  - Custom components

Data Visualization:
  - Victory Native (charts)
  - React Native Chart Kit
```

### DevOps & Deployment

```yaml
Containerization:
  - Docker (backend + PostgreSQL + Redis)
  - Docker Compose (local development)

Backend Hosting Options:
  - Railway.app (easiest - PostgreSQL + FastAPI)
  - Render.com
  - Fly.io
  - AWS (more control, more complex)

Frontend Deployment:
  - Expo Application Services (EAS) - mobile builds
  - Vercel/Netlify (web deployment)

Database Hosting:
  - Railway (managed PostgreSQL + TimescaleDB)
  - Supabase (PostgreSQL + auth + storage)
  - AWS RDS (production scale)
```

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                 Expo App (Web + iOS + Android)                  │
│  - Chat interface                                               │
│  - Workout analytics visualizations                             │
│  - File upload (CSV, XML)                                       │
│  - Profile & goals management                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API (HTTPS)
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI Backend                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Pydantic AI Agent Layer                       │ │
│  │  - System Prompt: "Elite AI Fitness Coach"                │ │
│  │  - Model: OpenAI GPT-4o OR Anthropic Claude 3.5           │ │
│  │  - Session Management: PostgreSQL chat history            │ │
│  └──────────┬────────────────────────┬────────────────────────┘ │
│             │                        │                          │
│  ┌──────────▼──────────┐  ┌─────────▼──────────────────────┐  │
│  │   MCP Manager       │  │  Custom AI Tools               │  │
│  │                     │  │                                 │  │
│  │  • Hevy MCP Server  │  │  • analyze_nutrition_vs_       │  │
│  │    - get_workouts   │  │    training()                  │  │
│  │    - get_routines   │  │  • detect_plateaus()           │  │
│  │    - create_routine │  │  • generate_workout_program()  │  │
│  │    - update_routine │  │  • assess_muscle_balance()     │  │
│  │                     │  │  • get_holistic_snapshot()     │  │
│  │  • Future MCPs:     │  │  • recall_past_conversation()  │  │
│  │    - Strava         │  │  • correlation_engine()        │  │
│  │    - Whoop          │  │                                 │  │
│  └─────────────────────┘  └────────────┬───────────────────┘  │
│                                         │                      │
│  ┌──────────────────────────────────────▼────────────────────┐ │
│  │              Data Access Layer                            │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │         PostgreSQL + TimescaleDB Database            │ │ │
│  │  │                                                       │ │ │
│  │  │  Tables:                                              │ │ │
│  │  │  • users - User profiles                             │ │ │
│  │  │  • chat_sessions - Conversation sessions             │ │ │
│  │  │  • chat_messages - All chat history                  │ │ │
│  │  │  • health_metrics_raw - Raw Apple Health data        │ │ │
│  │  │  • health_metrics_daily - Daily aggregates           │ │ │
│  │  │  • health_weekly_summary - Weekly summaries          │ │ │
│  │  │  • nutrition_daily - Daily nutrition logs            │ │ │
│  │  │  • workout_cache - Cached Hevy workouts              │ │ │
│  │  │  • user_goals - Fitness goals & targets              │ │ │
│  │  │  • user_preferences - Training preferences           │ │ │
│  │  │  • sync_metadata - Sync status tracking              │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │      Health Data Ingestion Service                   │ │ │
│  │  │  • AppleHealthStreamingParser (XML)                  │ │ │
│  │  │  • NutritionParser (CSV/XLS)                         │ │ │
│  │  │  • DuplicateHandler (incremental sync)               │ │ │
│  │  │  • DataAggregator (daily/weekly summaries)           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │      Analysis Services (Polars/Pandas)               │ │ │
│  │  │  • WorkoutAnalyzer - Training pattern analysis       │ │ │
│  │  │  • NutritionAnalyzer - Diet pattern analysis         │ │ │
│  │  │  • CorrelationEngine - Multi-source correlations     │ │ │
│  │  │  • PlateauDetector - Performance stagnation          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │      Sync Automation Service                         │ │ │
│  │  │  • MyNetDiaryScraper (Playwright automation)         │ │ │
│  │  │  • APScheduler (daily 2 AM sync)                     │ │ │
│  │  │  • iOS Shortcut endpoint (Apple Health upload)       │ │ │
│  │  │  • SyncMonitor (health checks, alerts)               │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

External Services:
  • Hevy API (via MCP server)
  • OpenAI API (GPT models)
  • Anthropic API (Claude models)
  • MyNetDiary.com (automated scraping)
  • iOS HealthKit (via Shortcuts or companion app)
```

### Key Architectural Decisions

**1. Why Pydantic AI over OpenAI Agents?**
- ✅ **Model agnostic**: Switch between GPT, Claude, Gemini without code changes
- ✅ **Type-safe**: Full Pydantic validation throughout
- ✅ **Logfire integration**: Already using Logfire - Pydantic AI has native support
- ✅ **Simpler API**: Less boilerplate than LangGraph, more flexible than OpenAI Agents
- ✅ **MCP compatible**: Works seamlessly with Model Context Protocol

**2. Why PostgreSQL + TimescaleDB?**
- ✅ **Multi-modal data**: Handles workouts, nutrition, health metrics, chat history
- ✅ **Time-series optimization**: TimescaleDB for efficient time-based queries
- ✅ **JSONB support**: Flexible metadata without losing query performance
- ✅ **Production-ready**: Better than SQLite for multi-user, deployed apps
- ✅ **Vector support**: pgvector extension for future RAG capabilities

**3. Why Expo for Frontend?**
- ✅ **Single codebase**: Web + iOS + Android (90-95% code sharing)
- ✅ **React knowledge transfers**: Same hooks, patterns, components
- ✅ **NativeWind**: Tailwind syntax works almost identically
- ✅ **Native features**: Camera, notifications, HealthKit access
- ✅ **Easy deployment**: EAS for mobile, Vercel/Netlify for web

**4. Why MCP (Model Context Protocol)?**
- ✅ **Community maintenance**: Hevy MCP server maintained by community
- ✅ **Standardization**: Industry standard for AI-tool integration
- ✅ **Extensibility**: Easy to add new MCPs (Strava, Whoop, etc.)
- ✅ **Code reduction**: Delete custom Hevy client (~30% less code)

**5. Why "Direct-Access" Agent Architecture?**
- ✅ **Real-time consistency**: Agent reads "live" data from MCP (e.g., just-finished workout) to avoid stale cache.
- ✅ **Write capabilities**: Agent can *act* (create routines) via MCP, not just analyze.
- ✅ **Hybrid approach**: 
  - **Live Data**: Uses MCP Tools directly (low latency, high freshness).
  - **Deep Analysis**: Uses SQL Tools (high speed, aggregation power).

---

## Database Design

### Complete Schema with Rationale

```sql
-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hevy_user_id VARCHAR UNIQUE,  -- Link to Hevy account
    email VARCHAR UNIQUE,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'  -- Flexible for additional fields
);

CREATE INDEX idx_users_hevy_id ON users(hevy_user_id);

-- ============================================================================
-- CHAT HISTORY (Enhanced from SQLite)
-- ============================================================================

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    session_name VARCHAR,  -- Optional: "Plateau troubleshooting", etc.
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, last_activity DESC);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    token_count INT,
    tool_calls JSONB,  -- Store tool call details for debugging
    metadata JSONB DEFAULT '{}',

    -- For future vector search (RAG)
    embedding vector(1536)  -- OpenAI text-embedding-3-small dimension
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, timestamp DESC);
CREATE INDEX idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- HEALTH METRICS (Apple Health, Wearables)
-- ============================================================================

-- Raw detailed records (for drill-down analysis)
CREATE TABLE health_metrics_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_date TIMESTAMPTZ NOT NULL,  -- Full timestamp with timezone
    metric_type VARCHAR(50) NOT NULL,   -- 'steps', 'weight', 'heart_rate', etc.
    value NUMERIC NOT NULL,
    unit VARCHAR(20),
    source VARCHAR(50),  -- 'apple_health', 'fitbit', 'manual', etc.
    metadata JSONB DEFAULT '{}'
);

-- Convert to TimescaleDB hypertable (automatic time-based partitioning)
SELECT create_hypertable('health_metrics_raw', 'metric_date');

-- Compression for older data (90% space savings)
ALTER TABLE health_metrics_raw SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'user_id,metric_type'
);

-- Automatically compress data older than 30 days
SELECT add_compression_policy('health_metrics_raw', INTERVAL '30 days');

-- Daily aggregates (for LLM tool queries)
CREATE TABLE health_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    steps INT,
    weight_kg NUMERIC,
    active_calories INT,
    resting_heart_rate INT,
    sleep_hours NUMERIC,
    distance_meters NUMERIC,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, metric_date)
);

CREATE INDEX idx_health_daily_user_date ON health_metrics_daily(user_id, metric_date DESC);

-- Weekly summaries (even more aggregated for LLM)
CREATE TABLE health_weekly_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,  -- Monday of the week
    avg_daily_steps INT,
    avg_weight_kg NUMERIC,
    weight_change_kg NUMERIC,  -- Change from previous week
    avg_sleep_hours NUMERIC,
    total_active_days INT,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, week_start)
);

CREATE INDEX idx_health_weekly_user ON health_weekly_summary(user_id, week_start DESC);

-- ============================================================================
-- NUTRITION TRACKING
-- ============================================================================

CREATE TABLE nutrition_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    calories INT,
    protein_g NUMERIC,
    carbs_g NUMERIC,
    fat_g NUMERIC,
    fiber_g NUMERIC,
    meal_count INT,

    -- Computed fields (calculated at insert)
    protein_per_kg_bodyweight NUMERIC,  -- Based on user weight that day
    calorie_surplus_deficit INT,        -- vs TDEE (if available)

    meals JSONB,  -- Detailed meal breakdown if available
    source VARCHAR(50) DEFAULT 'mynetdiary',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, log_date)
);

CREATE INDEX idx_nutrition_user_date ON nutrition_daily(user_id, log_date DESC);

-- ============================================================================
-- WORKOUT CACHE (from Hevy via MCP)
-- ============================================================================

CREATE TABLE workout_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workout_id VARCHAR UNIQUE NOT NULL,  -- Hevy workout ID
    workout_date DATE NOT NULL,
    title VARCHAR,
    duration_minutes INT,
    total_volume_kg NUMERIC,  -- Sum of all weight * reps
    total_sets INT,

    -- Store full JSON for flexibility
    workout_data JSONB NOT NULL,

    synced_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_workout_cache_user_date (user_id, workout_date DESC),
    INDEX idx_workout_cache_id (workout_id)
);

-- ============================================================================
-- USER GOALS & PREFERENCES
-- ============================================================================

CREATE TABLE user_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    goal_type VARCHAR(50) NOT NULL,  -- 'strength', 'hypertrophy', 'aesthetics', 'endurance'
    description TEXT,
    target_physique VARCHAR(100),  -- 'surfer', 'powerlifter', 'athletic', etc.
    target_metrics JSONB,  -- { "bench_press_kg": 100, "target_weight_kg": 80 }
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    training_frequency INT,  -- Days per week
    available_equipment JSONB,  -- ['barbell', 'dumbbells', 'pullup_bar']
    preferred_split VARCHAR(50),  -- 'ppl', 'upper_lower', 'full_body'
    disliked_exercises JSONB,  -- ['overhead_press', 'lunges']
    injury_history JSONB,  -- [{ "injury": "shoulder", "exercises_to_avoid": [...] }]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id)
);

-- ============================================================================
-- SYNC METADATA (track automation status)
-- ============================================================================

CREATE TABLE sync_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL,  -- 'mynetdiary', 'apple_health', 'hevy'
    last_sync_time TIMESTAMP,
    last_sync_status VARCHAR(20),  -- 'success', 'failed', 'partial'
    records_synced INT DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',

    UNIQUE(user_id, source)
);

CREATE INDEX idx_sync_meta_user_source ON sync_metadata(user_id, source);

-- ============================================================================
-- CONTINUOUS AGGREGATES (TimescaleDB - Auto-updating materialized views)
-- ============================================================================

-- Automatically maintain daily health summaries from raw data
CREATE MATERIALIZED VIEW health_daily_auto
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', metric_date) AS day,
    user_id,
    metric_type,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value,
    COUNT(*) as measurement_count
FROM health_metrics_raw
GROUP BY day, user_id, metric_type
WITH NO DATA;

-- Auto-refresh policy (refresh every hour for last 7 days)
SELECT add_continuous_aggregate_policy('health_daily_auto',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

### Database Migrations Strategy

```bash
# Using Alembic for migrations

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "create users and health tables"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Data Ingestion & Automation

### Problem Statement

Currently, health data requires manual exports:
- **MyNetDiary**: Export CSV yearly, manually download
- **Apple Health**: Export from iPhone, AirDrop to computer
- **Tedious**: Must repeat for every update
- **Stale data**: No real-time information

### Solution: Automated Sync

#### 1. MyNetDiary Automation (Playwright Web Scraper)

**File**: `backend/services/sync/mynetdiary_scraper.py`

```python
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import polars as pl
import os

class MyNetDiaryScraper:
    """
    Automate CSV download from MyNetDiary web portal.
    Runs daily to fetch last 7 days of data.
    """

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.download_dir = "data/downloads/mynetdiary"

    async def login_and_download_recent(self, days_back: int = 7):
        """
        Headless browser automation to download nutrition data.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # 1. Navigate to login page
            await page.goto("https://www.mynetdiary.com/login.do")

            # 2. Fill credentials and login
            await page.fill('input[name="email"]', self.email)
            await page.fill('input[name="password"]', self.password)
            await page.click('button[type="submit"]')

            # 3. Wait for dashboard to load
            await page.wait_for_url("**/home.do")

            # 4. Navigate to export page
            await page.goto("https://www.mynetdiary.com/exportData.do")

            # 5. Set date range (last 7 days to minimize duplicates)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            await page.fill('input[name="startDate"]', start_date.strftime('%Y-%m-%d'))
            await page.fill('input[name="endDate"]', end_date.strftime('%Y-%m-%d'))

            # 6. Select CSV format
            await page.select_option('select[name="format"]', 'csv')

            # 7. Download file
            async with page.expect_download() as download_info:
                await page.click('button#exportButton')

            download = await download_info.value
            file_path = os.path.join(
                self.download_dir,
                f"nutrition_{datetime.now().date()}.csv"
            )
            await download.save_as(file_path)

            await browser.close()

            return file_path

    async def sync_to_database(self, user_id: str, db):
        """
        Complete sync workflow:
        1. Download CSV
        2. Parse with Polars
        3. Filter duplicates
        4. Insert new records
        """
        try:
            # Download
            csv_path = await self.login_and_download_recent(days_back=7)

            # Parse CSV
            df = pl.read_csv(csv_path)

            # Normalize columns (adjust based on MyNetDiary CSV format)
            df = df.rename({
                'Date': 'log_date',
                'Calories': 'calories',
                'Protein (g)': 'protein_g',
                'Carbs (g)': 'carbs_g',
                'Fat (g)': 'fat_g'
            })

            # Get existing dates to avoid duplicates
            existing_dates = await db.get_existing_nutrition_dates(
                user_id,
                days_back=7
            )

            # Filter to new records only
            new_records = df.filter(
                ~pl.col('log_date').is_in(existing_dates)
            )

            if len(new_records) == 0:
                return {
                    "status": "up_to_date",
                    "new_records": 0,
                    "message": "No new data to sync"
                }

            # Insert new records
            await db.bulk_insert_nutrition(user_id, new_records.to_dicts())

            # Update sync metadata
            await db.update_sync_metadata(
                user_id=user_id,
                source='mynetdiary',
                status='success',
                records_synced=len(new_records)
            )

            return {
                "status": "synced",
                "new_records": len(new_records),
                "date_range": f"{new_records['log_date'].min()} to {new_records['log_date'].max()}"
            }

        except Exception as e:
            # Log error and update sync metadata
            await db.update_sync_metadata(
                user_id=user_id,
                source='mynetdiary',
                status='failed',
                error_message=str(e)
            )
            raise
```

**Scheduled Execution**:

File: `backend/services/sync/scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(hour=2, minute=0))
async def daily_mynetdiary_sync():
    """Run at 2 AM daily"""
    scraper = MyNetDiaryScraper(
        email=os.getenv("MYNETDIARY_EMAIL"),
        password=os.getenv("MYNETDIARY_PASSWORD")
    )

    result = await scraper.sync_to_database(
        user_id="default_user",
        db=database
    )

    logger.info(f"MyNetDiary sync completed: {result}")

# Start scheduler on app startup
def start_scheduler():
    scheduler.start()
```

**Add to FastAPI**:

```python
# backend/main.py
from backend.services.sync.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
```

#### 2. Apple Health Automation (iOS Shortcut)

**Why iOS Shortcut?**
- ✅ No separate app needed
- ✅ Native HealthKit access
- ✅ Can run automatically (daily trigger)
- ✅ Quick to set up (30 minutes)

**iOS Shortcut Workflow**:

```
Trigger: Time of Day (11 PM daily)

Actions:
1. Find Health Samples
   - Type: Steps
   - Start Date: 7 days ago
   - End Date: Today

2. Get Health Samples (for each type)
   - Steps
   - Body Mass (Weight)
   - Active Energy Burned
   - Sleep Analysis

3. Create Dictionary
   Format:
   {
     "metrics": [
       {
         "type": "steps",
         "value": 8500,
         "unit": "count",
         "date": "2024-01-15"
       },
       ...
     ],
     "user_id": "your_user_id",
     "sync_date": "2024-01-15T23:00:00Z"
   }

4. Get Contents of URL
   - URL: https://your-api.com/upload/apple-health-json
   - Method: POST
   - Headers: {"Content-Type": "application/json"}
   - Body: JSON from step 3
```

**Backend Endpoint**:

```python
# backend/main.py

class AppleHealthData(BaseModel):
    metrics: List[dict]
    user_id: str
    sync_date: datetime

@app.post("/upload/apple-health-json")
async def upload_apple_health_json(data: AppleHealthData):
    """
    Receive Apple Health data from iOS Shortcut.
    Handles duplicate detection and upserts.
    """
    # Parse incoming data
    new_metrics = []
    for metric in data.metrics:
        new_metrics.append({
            'user_id': data.user_id,
            'metric_type': metric['type'],
            'value': float(metric['value']),
            'unit': metric['unit'],
            'metric_date': metric['date'],
            'source': 'apple_health_shortcut'
        })

    # Get existing metrics to detect duplicates
    existing = await db.get_existing_health_metrics(
        user_id=data.user_id,
        dates=[m['metric_date'] for m in new_metrics],
        types=[m['metric_type'] for m in new_metrics]
    )

    existing_keys = {
        (e['metric_date'], e['metric_type'])
        for e in existing
    }

    # Separate new vs updates
    new_records = []
    update_records = []

    for record in new_metrics:
        key = (record['metric_date'], record['metric_type'])
        if key in existing_keys:
            update_records.append(record)  # Will upsert
        else:
            new_records.append(record)

    # Insert new records
    if new_records:
        await db.bulk_insert_health_metrics_daily(new_records)

    # Update existing records (newer data overwrites)
    if update_records:
        await db.bulk_upsert_health_metrics_daily(update_records)

    # Update sync metadata
    await db.update_sync_metadata(
        user_id=data.user_id,
        source='apple_health',
        status='success',
        records_synced=len(new_records) + len(update_records)
    )

    return {
        "status": "success",
        "new_records": len(new_records),
        "updated_records": len(update_records),
        "duplicates_skipped": len(new_metrics) - len(new_records) - len(update_records)
    }
```

#### 3. Duplicate Handling Strategy

**File**: `backend/services/sync/duplicate_handler.py`

```python
from typing import List, Set, Tuple
from datetime import datetime

class DuplicateHandler:
    """
    Smart duplicate detection for incremental syncs.

    Key Insight: Use unique constraints in DB + check before insert
    """

    async def filter_new_nutrition_records(
        self,
        db,
        user_id: str,
        new_records: List[dict]
    ) -> List[dict]:
        """
        Filter nutrition records that don't exist yet.
        Duplicate key: (user_id, log_date)
        """
        # Extract dates from new records
        dates = [r['log_date'] for r in new_records]

        # Query existing dates
        existing = await db.execute("""
            SELECT log_date
            FROM nutrition_daily
            WHERE user_id = $1
              AND log_date = ANY($2)
        """, user_id, dates)

        existing_dates = {row['log_date'] for row in existing}

        # Filter to new only
        new_only = [
            r for r in new_records
            if r['log_date'] not in existing_dates
        ]

        return new_only

    async def filter_new_health_metrics(
        self,
        db,
        user_id: str,
        new_records: List[dict]
    ) -> Tuple[List[dict], List[dict]]:
        """
        Filter health metrics.
        Returns: (new_records, update_records)

        Duplicate key: (user_id, metric_date, metric_type)
        """
        # Create composite keys
        new_keys = {
            (r['metric_date'], r['metric_type'])
            for r in new_records
        }

        # Query existing
        dates = list({r['metric_date'] for r in new_records})
        types = list({r['metric_type'] for r in new_records})

        existing = await db.execute("""
            SELECT metric_date, metric_type
            FROM health_metrics_daily
            WHERE user_id = $1
              AND metric_date = ANY($2)
              AND metric_type = ANY($3)
        """, user_id, dates, types)

        existing_keys = {
            (row['metric_date'], row['metric_type'])
            for row in existing
        }

        # Separate into new vs updates
        new_records_filtered = []
        update_records = []

        for record in new_records:
            key = (record['metric_date'], record['metric_type'])
            if key in existing_keys:
                update_records.append(record)  # Will upsert
            else:
                new_records_filtered.append(record)

        return new_records_filtered, update_records
```

#### 4. Sync Monitoring & Alerts

```python
# backend/services/sync/monitor.py

async def check_sync_health(db, user_id: str):
    """
    Monitor sync status and alert if data is stale.
    Run daily to ensure automation is working.
    """
    syncs = await db.execute("""
        SELECT source, last_sync_time, last_sync_status
        FROM sync_metadata
        WHERE user_id = $1
    """, user_id)

    alerts = []
    for sync in syncs:
        hours_since_sync = (
            datetime.now() - sync['last_sync_time']
        ).total_seconds() / 3600

        if hours_since_sync > 48:  # No sync in 2 days
            alerts.append({
                'source': sync['source'],
                'issue': 'STALE_DATA',
                'last_sync': sync['last_sync_time'],
                'hours_since': hours_since_sync
            })

        if sync['last_sync_status'] == 'failed':
            alerts.append({
                'source': sync['source'],
                'issue': 'SYNC_FAILED',
                'last_sync': sync['last_sync_time']
            })

    if alerts:
        # Send notifications (email, Slack, push notification)
        await send_alert_notification(alerts)

    return alerts
```

---

## LLM Integration & Agentic Framework

### Why Pydantic AI?

**Comparison with Alternatives**:

| Feature | Pydantic AI | OpenAI Agents | LangGraph |
|---------|-------------|---------------|-----------|
| Model Agnostic | ✅ Yes | ❌ OpenAI only | ✅ Yes |
| Type Safety | ✅ Full Pydantic | ⚠️ Partial | ⚠️ Partial |
| Learning Curve | ⭐⭐ Easy | ⭐⭐ Easy | ⭐⭐⭐⭐ Hard |
| Logfire Integration | ✅ Native | ⚠️ Manual | ⚠️ Manual |
| MCP Support | ✅ Yes | ⚠️ Limited | ✅ Yes |
| Documentation | ⭐⭐⭐⭐ Good | ⭐⭐⭐ OK | ⭐⭐⭐⭐ Good |
| Maintenance | ✅ Active | ✅ Active | ✅ Active |

**Decision: Pydantic AI** - Best balance of simplicity, flexibility, and type safety.

### Pydantic AI Setup

**Installation**:

```bash
pip install pydantic-ai
pip install anthropic  # For Claude
pip install openai     # For GPT
```

**Basic Agent Structure**:

File: `backend/llm/agent.py`

```python
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from typing import Optional

# Define dependencies (injected into tools)
@dataclass
class AppContext:
    """
    Application context available to all tools.
    Think of this as "what the agent needs to do its job".
    """
    db: Any  # Database connection
    hevy_client: Any  # MCP client for Hevy
    user_id: str

# Create agent (can switch models easily)
agent = Agent(
    'openai:gpt-4o',  # OR 'anthropic:claude-3-5-sonnet-20241022'
    deps_type=AppContext,
    system_prompt="""
    You are an elite AI fitness coach with expertise in:
    - Program design and periodization
    - Exercise science and biomechanics
    - Nutrition for muscle growth and fat loss
    - Performance analysis and plateau detection

    You have access to the user's:
    - Complete workout history (from Hevy)
    - Daily nutrition logs (from MyNetDiary)
    - Health metrics (from Apple Health: steps, weight, sleep)
    - Past conversation history

    Your goal: Provide personalized, data-driven coaching.

    Always:
    1. Start by understanding user context (load profile, goals)
    2. Analyze relevant data before giving advice
    3. Provide specific, actionable recommendations
    4. Explain the "why" behind your suggestions

    When asked to create programs:
    - Generate complete, structured workout plans
    - Consider user's experience, equipment, and goals
    - Create actual routines in Hevy (don't just describe)
    """
)

# Define tools (this is where the magic happens)
@agent.tool
async def analyze_nutrition_vs_training(
    ctx: RunContext[AppContext],
    days_back: int = 30
) -> dict:
    """
    Analyze relationship between nutrition and workout performance.

    Use this when user asks about muscle growth, recovery, or
    performance issues.

    Args:
        days_back: Number of days to analyze (default 30)

    Returns:
        Analysis with insights on protein intake, calorie balance,
        and correlations with training performance
    """
    # Get nutrition data (aggregated daily summaries, not raw meals)
    nutrition = await ctx.deps.db.get_nutrition_summary(
        user_id=ctx.deps.user_id,
        days_back=days_back
    )

    # Get workout data
    workouts = await ctx.deps.db.get_workout_summary(
        user_id=ctx.deps.user_id,
        days_back=days_back
    )

    # Get health metrics
    health = await ctx.deps.db.get_health_metrics_summary(
        user_id=ctx.deps.user_id,
        days_back=days_back
    )

    # Perform analysis
    avg_protein = sum(d['protein_g'] for d in nutrition) / len(nutrition)
    avg_calories = sum(d['calories'] for d in nutrition) / len(nutrition)
    avg_weight = sum(h['weight_kg'] for h in health) / len(health)

    protein_per_kg = avg_protein / avg_weight

    # Generate insights
    insights = []

    if protein_per_kg < 1.6:
        insights.append({
            'type': 'INSUFFICIENT_PROTEIN',
            'severity': 'high',
            'message': f'Protein intake ({avg_protein:.0f}g/day, {protein_per_kg:.1f}g/kg) is below recommended 1.6-2.2g/kg for muscle growth',
            'recommendation': f'Increase daily protein to {int(avg_weight * 1.8)}g (1.8g/kg bodyweight)'
        })

    if len(workouts) < 12:  # Less than 3x/week for 4 weeks
        insights.append({
            'type': 'LOW_TRAINING_FREQUENCY',
            'severity': 'medium',
            'message': f'Only {len(workouts)} workouts in {days_back} days',
            'recommendation': 'Aim for 3-5 workouts per week for optimal progress'
        })

    return {
        'period_analyzed': f'{days_back} days',
        'nutrition_summary': {
            'avg_daily_protein_g': round(avg_protein, 1),
            'avg_daily_calories': round(avg_calories, 0),
            'protein_per_kg_bodyweight': round(protein_per_kg, 2)
        },
        'training_summary': {
            'total_workouts': len(workouts),
            'workouts_per_week': round(len(workouts) / (days_back / 7), 1)
        },
        'health_summary': {
            'avg_weight_kg': round(avg_weight, 1),
            'avg_daily_steps': round(sum(h['steps'] for h in health) / len(health), 0)
        },
        'insights': insights,
        'assessment': 'NEEDS_IMPROVEMENT' if insights else 'ON_TRACK'
    }

@agent.tool
async def get_workout_history(
    ctx: RunContext[AppContext],
    days_back: int = 7
) -> dict:
    """
    Get recent workout history from Hevy.

    Use this when user asks about recent training or wants
    to review what they've done.

    Args:
        days_back: Number of days to retrieve (default 7)

    Returns:
        List of recent workouts with exercises and performance
    """
    # Query via MCP (will be implemented later)
    workouts = await ctx.deps.hevy_client.get_workouts(
        page_size=20  # Get enough to cover days_back
    )

    # Filter to requested time range
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days_back)

    recent_workouts = [
        w for w in workouts
        if w['start_time'] >= cutoff_date
    ]

    return {
        'workouts': recent_workouts,
        'total': len(recent_workouts),
        'date_range': f'Last {days_back} days'
    }

@agent.tool
async def detect_plateaus(
    ctx: RunContext[AppContext],
    exercise_name: Optional[str] = None
) -> dict:
    """
    Detect performance plateaus in exercises.

    Use this when user mentions stagnation, not progressing,
    or asks for help breaking through.

    Args:
        exercise_name: Specific exercise to check (optional)

    Returns:
        List of exercises with plateaus and recommended solutions
    """
    # Get exercise progression data
    if exercise_name:
        exercises = [exercise_name]
    else:
        # Get user's top 10 exercises
        exercises = await ctx.deps.db.get_top_exercises(
            user_id=ctx.deps.user_id,
            limit=10
        )

    plateaus = []

    for exercise in exercises:
        progression = await ctx.deps.db.get_exercise_progression(
            user_id=ctx.deps.user_id,
            exercise_name=exercise,
            weeks_back=8
        )

        # Simple plateau detection: no improvement in last 3 sessions
        if len(progression) >= 3:
            recent_3 = progression[-3:]
            weights = [s['max_weight'] for s in recent_3]

            if max(weights) == min(weights):  # No change
                plateaus.append({
                    'exercise': exercise,
                    'plateau_duration_weeks': 3,
                    'current_weight': weights[0],
                    'recommendations': [
                        'Try a deload week (reduce weight by 10-20%)',
                        'Add variation exercises (e.g., incline bench if flat bench)',
                        'Increase frequency (train this exercise more often)',
                        'Check nutrition and recovery'
                    ]
                })

    return {
        'plateaus_detected': len(plateaus),
        'exercises_analyzed': len(exercises),
        'plateaus': plateaus
    }

# More tools to be added...
```

**Running the Agent**:

```python
# In FastAPI endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    # Create context with dependencies
    ctx = AppContext(
        db=database,
        hevy_client=hevy_mcp_client,
        user_id=request.user_id
    )

    # Run agent with user message
    result = await agent.run(
        request.message,
        deps=ctx
    )

    return {"response": result.data}
```

### MCP Integration

**Hevy MCP Server Setup**:

```bash
# Using Docker (easiest)
docker run -d \
  --name hevy-mcp \
  -e HEVY_API_KEY=$HEVY_API_KEY \
  -p 3000:3000 \
  ghcr.io/chrisdoc/hevy-mcp:latest
```

**MCP Client Utility**:

File: `backend/mcp_client.py`

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from backend.config import config
from pathlib import Path
import json

async def call_hevy_tool(tool_name: str, arguments: dict = None) -> dict:
    """
    Execute a tool on the Hevy MCP server.
    Creates an ephemeral connection for each call to ensure reliability.
    """
    # Path to your local MCP server implementation
    server_script = Path(__file__).parent / "mcp_servers/hevy-mcp/dist/index.js"
    
    server_params = StdioServerParameters(
        command="node",
        args=[str(server_script)],
        env={"HEVY_API_KEY": config.HEVY_API_KEY}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(tool_name, arguments or {})
            
            if result.isError:
                raise RuntimeError(f"MCP Tool Error: {result.content}")
                
            # Parse result content (usually JSON string inside text)
            if not result.content:
                return {}
                
            text_content = result.content[0].text
            try:
                return json.loads(text_content)
            except json.JSONDecodeError:
                return {"raw_text": text_content}
```

**Agent Tools Wrapper**:

File: `backend/agents/tools/hevy_mcp_tools.py`

```python
from backend.mcp_client import call_hevy_tool

async def get_recent_workouts_live(limit: int = 5):
    """Get the most recent workouts directly from Hevy (real-time)"""
    return await call_hevy_tool("get-workouts", {"pageSize": limit})

async def create_routine(title: str, exercises: list):
    """Create a new routine in Hevy"""
    return await call_hevy_tool("create-routine", {
        "title": title, 
        "exercises": exercises
    })
```

### LLM Context Management (Critical!)

**Problem**: Can't load 3 years of data into LLM context (would be 100,000+ tokens)

**Solution**: Smart aggregation + time windowing

```python
# backend/services/data_access/llm_optimized_queries.py

class LLMOptimizedDataAccess:
    """
    Queries designed to fit in LLM context window.

    Key principle: Aggregate before returning.
    Never return raw records to LLM.
    """

    async def get_nutrition_for_llm(
        self,
        user_id: str,
        scenario: str = 'default'
    ) -> dict:
        """
        Get nutrition data optimized for LLM context.

        Scenarios:
        - 'quick_check': Last 7 days only (~100 tokens)
        - 'default': Last 30 days daily + 12 weeks summary (~500 tokens)
        - 'troubleshooting': Detailed recent + long-term trends (~1000 tokens)
        - 'historical': Monthly aggregates for comparisons (~200 tokens)
        """

        if scenario == 'quick_check':
            # Just last week's daily data
            return await self.db.execute("""
                SELECT
                    log_date,
                    calories,
                    protein_g,
                    carbs_g,
                    fat_g
                FROM nutrition_daily
                WHERE user_id = $1
                  AND log_date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY log_date DESC
            """, user_id)

        elif scenario == 'troubleshooting':
            # Detailed recent + trends
            last_7_days = await self.db.execute("""
                SELECT * FROM nutrition_daily
                WHERE user_id = $1
                  AND log_date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY log_date DESC
            """, user_id)

            last_12_weeks = await self.db.execute("""
                SELECT
                    week_start,
                    AVG(calories) as avg_calories,
                    AVG(protein_g) as avg_protein,
                    AVG(weight_kg) as avg_weight
                FROM health_weekly_summary
                WHERE user_id = $1
                ORDER BY week_start DESC
                LIMIT 12
            """, user_id)

            return {
                'last_7_days_detail': last_7_days,  # 7 records
                'last_12_weeks_summary': last_12_weeks,  # 12 records
                'total_data_points': 19  # Only 19 records total!
            }

        # ... other scenarios
```

**Result**: LLM receives <1000 tokens of data instead of 100,000+ tokens.

---

## Frontend Development

### Expo Setup

```bash
# Create Expo project in mobile/ directory
npx create-expo-app@latest mobile --template tabs

cd mobile

# Install dependencies
npx expo install react-native-web react-dom
npm install nativewind
npm install --save-dev tailwindcss@3.3.2

# Navigation
npx expo install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens react-native-safe-area-context

# UI libraries
npm install axios
npm install react-native-markdown-display
npm install victory-native  # Charts
```

### NativeWind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./backend/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Your theme colors (from existing app)
        ocean: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          // ... etc
        }
      }
    }
  },
  plugins: []
}

// babel.config.js
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['nativewind/babel']
  };
};
```

### Component Migration Example

```typescript
// BEFORE: React Web (web/src/components/ChatArea.tsx)
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

export const ChatArea: React.FC = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map(msg => (
          <div key={msg.id} className="mb-4">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}
      </div>

      <div className="p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full px-4 py-2 border rounded"
        />
      </div>
    </div>
  );
};

// AFTER: Expo (mobile/components/ChatArea.tsx)
import React, { useState } from 'react';
import { View, ScrollView, TextInput } from 'react-native';
import Markdown from 'react-native-markdown-display';

export const ChatArea: React.FC = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Same logic, different components!

  return (
    <View className="flex-1">
      <ScrollView className="flex-1 p-4">
        {messages.map(msg => (
          <View key={msg.id} className="mb-4">
            <Markdown>{msg.content}</Markdown>
          </View>
        ))}
      </ScrollView>

      <View className="p-4 border-t">
        <TextInput
          value={input}
          onChangeText={setInput}
          className="w-full px-4 py-2 border rounded"
        />
      </View>
    </View>
  );
};
```

**Changes**:
- `<div>` → `<View>`
- `<input>` → `<TextInput>`
- `onChange` → `onChangeText`
- `ReactMarkdown` → `react-native-markdown-display`
- Tailwind classes work the same!

### API Service (No Changes!)

```typescript
// services/api.ts - IDENTICAL for web, iOS, Android

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async sendMessage(message: string, sessionId: string) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    return response.json();
  },

  async uploadNutritionCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload/nutrition`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }

  // ... more methods
};
```

---

## Implementation Roadmap

### Phase 1: Database & Backend Foundation (Week 1)

**Learning Focus**: PostgreSQL, SQLAlchemy, Database design

**Tasks**:
1. ✅ Set up PostgreSQL locally (Docker)
2. ✅ Install TimescaleDB extension
3. ✅ Create database schema with Alembic migrations
4. ✅ Set up SQLAlchemy models
5. ✅ Test database connections
6. ✅ **Phase 1.5 COMPLETE (2025-11-11):** Created FastAPI + PostgreSQL integration
   - Created `backend/db/database.py` with async session management
   - Added user profile endpoints (POST/GET)
   - Verified full stack working (FastAPI → SQLAlchemy → PostgreSQL)

**Success Criteria**:
- PostgreSQL running and accessible
- All tables created with proper indexes
- Can insert and query test data
- Alembic migrations working
- ✅ FastAPI endpoints can use PostgreSQL (Phase 1.5)

**Important Note on Chat History (Decision 2025-11-11):**
- Chat history tables (`chat_sessions`, `chat_messages`) are created in PostgreSQL but NOT YET IN USE
- Currently using `agents.SQLiteSession` for chat history (temporary)
- Will migrate chat to PostgreSQL in Phase 2 or Phase 3
- This phased approach allows focusing on new features (nutrition, health data) first
- PostgreSQL chat models are ready when we're ready to migrate

**Resources**:
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [TimescaleDB Docs](https://docs.timescale.com/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

**Checkpoints**:
```bash
# Verify PostgreSQL
psql -U postgres -d workout_optimizer -c "SELECT version();"

# Verify TimescaleDB
psql -U postgres -d workout_optimizer -c "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"

# Test migration
alembic upgrade head

# Test query
python -m app.test_db_connection
```

---

### Phase 2: Data Ingestion & Automation (Week 2)

**Learning Focus**: Playwright, Polars, Background tasks

**Tasks**:
1. ✅ Build Apple Health XML parser (streaming)
2. ✅ Build MyNetDiary CSV parser
3. ✅ Create manual upload endpoints
4. ✅ Test with real export files
5. ✅ Build MyNetDiary Playwright scraper
6. ✅ Set up APScheduler for daily automation
7. ✅ Implement duplicate detection
8. ✅ Create iOS Shortcut for Apple Health

**Success Criteria**:
- Can parse and import Apple Health export
- Can parse and import MyNetDiary CSV
- Duplicate detection working (no re-imports)
- Automated daily sync running
- iOS Shortcut successfully uploads data

**Resources**:
- [Playwright Python Docs](https://playwright.dev/python/)
- [Polars User Guide](https://pola-rs.github.io/polars/user-guide/)
- [APScheduler Docs](https://apscheduler.readthedocs.io/)

**Test Data**:
```bash
# Export your Apple Health data (iPhone)
# Health app → Profile → Export All Health Data

# Export MyNetDiary data
# MyNetDiary.com → Account → Export Data

# Test import
curl -X POST http://localhost:8000/upload/apple-health \
  -F "file=@export.xml"

curl -X POST http://localhost:8000/upload/nutrition \
  -F "file=@nutrition_2024.csv"
```

---

### Phase 3: Pydantic AI & MCP Integration (Week 3) - UPDATED 2025-12-08

**Learning Focus**: Pydantic AI, Agent architecture patterns, Tool orchestration

**Architectural Decision (Session 10):**
- **Framework:** Pydantic AI (type-safe, model-agnostic, MCP-native)
- **Pattern:** Single Agent with Parallel Tool Processing
- **Rationale:** Start simple for learning, iterate to complex (supervisor pattern) in Phase 5+ if needed

**Tasks**:
1. ✅ **Session 10:** Cleanup legacy code (backend/hevy, old agents library)
2. ✅ **Session 10:** Install Pydantic AI and dependencies (already installed)
3. ✅ **Session 10:** Create backend/agents/ structure (agent.py, dependencies.py, tools/)
4. ✅ **Session 10:** Build first agent with core tools (2 tools: nutrition_stats, recent_workouts)
5. ✅ **Session 10:** Add /chat endpoint to FastAPI (POST /chat)
6. ✅ **Session 10:** Test with real data (140 days nutrition, agent working!)
7. ⏳ **Session 11:** Port 8-12 additional tools from backend/llm/tools/
8. ⏳ **Session 12:** Integrate Hevy MCP tools with agent
9. ⏳ **Session 13:** Implement streaming responses
10. ✅ **Session 13:** Test agent with complex multi-source queries
11. ✅ **Session 14:** Optimize context management and session persistence
12. ✅ **Session 16:** Implement Logfire monitoring for full observability

**Session 10 Accomplishments:**
- ✅ Legacy code removed (`backend/hevy/`, commented out `workout_analyzer`)
- ✅ Agent responds to queries with type-safe tools
- ✅ Can call custom database tools (nutrition ✓, workouts ✓)
- ✅ Parallel tool execution working (async tools with RunContext)
- ✅ HTTP endpoint functional (`/chat`)
- ✅ Tested with real queries ("average protein last 7 days" → "131.3g/day")

**Remaining Success Criteria**:
- ⏳ Port more tools from backend/llm/tools/
- ⏳ Can call MCP tools (get workouts from Hevy via MCP)
- ⏳ Conversation history persists in PostgreSQL (currently using temp session)
- ⏳ Can switch between Claude and GPT-4 (currently hardcoded to Claude)

**Resources**:
- [Pydantic AI Docs](https://ai.pydantic.dev/)
- [Pydantic AI GitHub Examples](https://github.com/pydantic/pydantic-ai/tree/main/examples)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Hevy MCP Server](https://github.com/chrisdoc/hevy-mcp)

**Test Queries** (Progressive complexity):
```
Session 10-11:
"What was my average protein intake last week?"
"Show me my total workout volume for November"

Session 12:
"Show me my workouts from last week" (uses MCP)
"Analyze my nutrition for the past month"

Session 13:
"I'm not gaining muscle, what's wrong?" (multi-domain analysis)
"Has my bench press plateaued?" (needs plateau detection)
"Create a 4-day upper/lower split for me" (program generation)
```

**Implementation Notes**:
- Start with 3-5 tools, test thoroughly, then expand
- Tools organized by domain (Nutrition, Workout, Health, Analysis)
- Use RunContext[Dependencies] for DB session injection
- Parallel execution with asyncio.gather() for multi-source queries
- May migrate to Hierarchical Supervisor pattern in Phase 5 if agent struggles with 20+ tools

---

### Phase 4: Advanced Analysis Tools (Week 4)

**Learning Focus**: Data analysis, Pandas/Polars, Statistical methods

**Tasks**:
1. ✅ Build CorrelationEngine
2. ✅ Implement nutrition vs training analysis
3. ✅ Build PlateauDetector
4. ✅ Create holistic health snapshot tool
5. ✅ Add historical context retrieval (RAG - optional)
6. ✅ Optimize LLM context management
7. ✅ Test multi-source analysis

**Success Criteria**:
- Can correlate nutrition with performance
- Detects plateaus in exercises
- Provides actionable insights
- LLM context stays under 10,000 tokens

**Test Scenarios**:
```
"Why am I not gaining muscle despite training hard?"
→ Should analyze: training volume, protein intake, calorie balance

"My bench press hasn't improved in 6 weeks"
→ Should detect plateau, suggest deload or variations

"Compare my current diet to 3 months ago"
→ Should provide before/after comparison
```

---

### Phase 5: Expo Frontend Migration (Week 5-6)

**Learning Focus**: React Native, Expo, Mobile development

**Tasks**:
1. ✅ Create Expo project with TypeScript
2. ✅ Set up NativeWind (Tailwind)
3. ✅ Configure file-based routing
4. ✅ Port ChatArea component
5. ✅ Port analytics components
6. ✅ Port API service (no changes needed)
7. ✅ Add file upload UI
8. ✅ Test on web, iOS simulator, Android emulator
9. ✅ Build responsive layouts

**Success Criteria**:
- App runs on web (localhost)
- App runs on iOS simulator
- App runs on Android emulator
- Chat functionality working
- File uploads working
- UI looks good on all platforms

**Resources**:
- [Expo Docs](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/)
- [NativeWind Docs](https://www.nativewind.dev/)

**Testing Commands**:
```bash
# Web
npx expo start --web

# iOS
npx expo start --ios

# Android
npx expo start --android

# Physical device
npx expo start
# Scan QR code with Expo Go app
```

---

### Phase 6: Deployment & Production (Week 7)

**Learning Focus**: Docker, CI/CD, Deployment platforms

**Tasks**:
1. ✅ Create Docker Compose setup
2. ✅ Deploy backend to Railway/Render
3. ✅ Deploy PostgreSQL to Railway
4. ✅ Deploy web frontend to Vercel
5. ✅ Build iOS app with EAS
6. ✅ Build Android app with EAS
7. ✅ Set up environment variables
8. ✅ Configure production database
9. ✅ Test end-to-end

**Success Criteria**:
- Backend accessible at public URL
- Database persistent and backed up
- Web app accessible online
- iOS app installable via TestFlight
- Android app installable (internal testing)

**Deployment Commands**:
```bash
# Build Docker image
docker build -t workout-optimizer-backend .

# Deploy to Railway
railway up

# Build mobile apps
eas build --platform ios
eas build --platform android

# Deploy web
vercel deploy
```

---

## Learning Path & Resources

### For Someone Learning to Code

**Your Background**: Learning to code, want to build this yourself with guidance

**Teaching Approach**:
- Start with fundamentals
- Build incrementally
- Understand *why*, not just *how*
- Real code examples with explanations
- No copy-paste without understanding

### Week 1: Database Fundamentals

**Concepts to Learn**:
1. **What is a database?**
   - Think of it as organized Excel sheets with relationships
   - PostgreSQL = the software that manages these sheets
   - Tables = individual sheets
   - Rows = records (one workout, one user, etc.)
   - Columns = fields (name, date, calories, etc.)

2. **Why SQL?**
   ```sql
   -- Human-readable way to ask for data

   -- Get all workouts from last week
   SELECT * FROM workout_cache
   WHERE workout_date >= CURRENT_DATE - INTERVAL '7 days';

   -- Get average protein per day
   SELECT AVG(protein_g) FROM nutrition_daily
   WHERE user_id = 'your_id';
   ```

3. **Why SQLAlchemy (ORM)?**
   ```python
   # Instead of writing SQL strings:
   query = "SELECT * FROM users WHERE id = ?"

   # Write Python:
   user = session.query(User).filter(User.id == user_id).first()

   # Safer, type-checked, easier to maintain
   ```

**Hands-On Exercise**:
```python
# Create your first table and insert data

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define what a "user" looks like
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)

# 2. Create database connection
engine = create_engine('postgresql://user:pass@localhost/workout_db')

# 3. Create table
Base.metadata.create_all(engine)

# 4. Insert a user
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(name="James", email="james@example.com")
session.add(new_user)
session.commit()

# 5. Query it back
user = session.query(User).filter(User.email == "james@example.com").first()
print(f"Found user: {user.name}")
```

**Understanding Check**:
- Can you explain what a "primary key" is?
- Why do we use `unique=True` on email?
- What does `session.commit()` do?

---

### Week 2: Python Async & Data Processing

**Concepts to Learn**:
1. **Async/Await (Why FastAPI uses it)**
   ```python
   # Synchronous (blocking)
   def get_workouts():
       data = fetch_from_api()  # Waits here, blocks everything
       return data

   # Asynchronous (non-blocking)
   async def get_workouts():
       data = await fetch_from_api()  # Waits, but others can run
       return data

   # Why? Handle multiple users simultaneously
   ```

2. **Pandas vs Polars**
   ```python
   import polars as pl

   # Load CSV
   df = pl.read_csv('nutrition.csv')

   # Filter
   high_protein_days = df.filter(pl.col('protein_g') > 150)

   # Aggregate
   avg_calories = df.select(pl.col('calories').mean())

   # Think: Excel formulas, but in code
   ```

**Hands-On Exercise**:
```python
# Parse your actual MyNetDiary CSV

import polars as pl
from datetime import datetime

# 1. Load your real CSV
df = pl.read_csv('your_nutrition_export.csv')

# 2. See what's in it
print(df.head())
print(df.columns)

# 3. Calculate average protein
avg_protein = df.select(pl.col('Protein (g)').mean()).item()
print(f"Your average protein: {avg_protein}g/day")

# 4. Find highest protein day
max_protein_day = df.sort('Protein (g)', descending=True).head(1)
print(f"Best protein day: {max_protein_day}")

# 5. Group by week
weekly = df.groupby_dynamic('Date', every='1w').agg(
    pl.col('Protein (g)').mean().alias('avg_protein'),
    pl.col('Calories').mean().alias('avg_calories')
)
print(weekly)
```

**Understanding Check**:
- What's the difference between `async` and regular functions?
- When would you use Polars vs just Python loops?
- How would you find all days where protein > 150g AND calories < 2000?

---

### Week 3: LLM Agents Demystified

**Concepts to Learn**:
1. **What is an AI Agent?**
   ```
   Regular chatbot:
   User: "Show me workouts"
   Bot: "I don't have access to your workouts"

   Agent:
   User: "Show me workouts"
   Agent: *calls get_workouts() tool*
   Agent: "Here are your last 5 workouts: [shows data]"

   Key: Agent can USE TOOLS to get information
   ```

2. **How Pydantic AI Works**
   ```python
   # 1. Define a tool (function the AI can call)
   @agent.tool
   async def get_workout_count(ctx: RunContext, days: int) -> int:
       """Count workouts in last N days"""
       workouts = await ctx.deps.db.query(...)
       return len(workouts)

   # 2. User asks question
   user_message = "How many workouts did I do this month?"

   # 3. AI agent:
   #    - Reads question
   #    - Decides: "I need get_workout_count tool"
   #    - Calls tool with days=30
   #    - Gets result: 12
   #    - Responds: "You did 12 workouts this month"
   ```

3. **Tool Design Principles**
   ```python
   # ❌ BAD: Too vague
   @agent.tool
   def analyze_stuff(ctx, data):
       """Analyze stuff"""
       pass

   # ✅ GOOD: Clear purpose and return value
   @agent.tool
   async def detect_bench_press_plateau(
       ctx: RunContext[AppContext],
       weeks_back: int = 8
   ) -> dict:
       """
       Detect if bench press has plateaued.

       Returns:
           {
               'is_plateau': bool,
               'weeks_stagnant': int,
               'current_max_kg': float,
               'recommendation': str
           }
       """
       # Implementation...
   ```

**Hands-On Exercise**:
```python
# Build your first agent tool

from pydantic_ai import Agent, RunContext
from dataclasses import dataclass

@dataclass
class MyContext:
    user_name: str

agent = Agent('openai:gpt-4o-mini', deps_type=MyContext)

@agent.tool
async def get_favorite_exercise(ctx: RunContext[MyContext]) -> str:
    """Get user's favorite exercise"""
    # For now, hardcode
    favorites = {
        'james': 'bench press',
        'default': 'squats'
    }
    return favorites.get(ctx.deps.user_name.lower(), 'unknown')

# Test it
ctx = MyContext(user_name="James")
result = await agent.run(
    "What's my favorite exercise?",
    deps=ctx
)
print(result.data)
# Output: "Your favorite exercise is bench press"
```

**Understanding Check**:
- What makes an agent different from a regular chatbot?
- Why do we pass `RunContext` to tools?
- How does the AI know which tool to call?

---

### Week 4-5: Frontend (React Native/Expo)

**Concepts to Learn**:
1. **React Components**
   ```typescript
   // Component = reusable piece of UI

   function WorkoutCard({ title, date, sets }) {
       return (
           <View className="p-4 bg-white rounded">
               <Text className="font-bold">{title}</Text>
               <Text className="text-gray-500">{date}</Text>
               <Text>{sets} sets</Text>
           </View>
       );
   }

   // Use it:
   <WorkoutCard title="Push Day" date="2024-01-15" sets={24} />
   ```

2. **State Management (useState)**
   ```typescript
   function ChatInput() {
       // State: data that can change
       const [message, setMessage] = useState('');

       return (
           <TextInput
               value={message}
               onChangeText={setMessage}  // Update state
           />
       );
   }
   ```

3. **API Calls (useEffect)**
   ```typescript
   function WorkoutList() {
       const [workouts, setWorkouts] = useState([]);

       useEffect(() => {
           // Runs when component loads
           fetch('https://api.example.com/workouts')
               .then(res => res.json())
               .then(data => setWorkouts(data));
       }, []);  // Empty array = run once

       return (
           <ScrollView>
               {workouts.map(w => <WorkoutCard {...w} />)}
           </ScrollView>
       );
   }
   ```

**Hands-On Exercise**:
```typescript
// Build a simple chat input

import React, { useState } from 'react';
import { View, TextInput, Pressable, Text } from 'react-native';

export function SimpleChatInput() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const sendMessage = async () => {
        // Call your API
        const res = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                session_id: 'test'
            })
        });

        const data = await res.json();
        setResponse(data.response);
        setMessage('');  // Clear input
    };

    return (
        <View className="p-4">
            <TextInput
                value={message}
                onChangeText={setMessage}
                placeholder="Ask about your workouts..."
                className="border p-2 rounded"
            />
            <Pressable onPress={sendMessage} className="bg-blue-500 p-2 rounded mt-2">
                <Text className="text-white text-center">Send</Text>
            </Pressable>
            {response && (
                <Text className="mt-4">{response}</Text>
            )}
        </View>
    );
}
```

---

## Code Examples & Patterns

### Pattern 1: Repository Pattern (Clean Data Access)

```python
# backend/repositories/nutrition_repository.py

class NutritionRepository:
    """
    Handles all nutrition data access.
    Keeps database queries separate from business logic.
    """

    def __init__(self, db):
        self.db = db

    async def get_daily_summary(
        self,
        user_id: str,
        days_back: int = 30
    ) -> List[dict]:
        """Get daily nutrition summary"""
        query = """
            SELECT
                log_date,
                calories,
                protein_g,
                carbs_g,
                fat_g
            FROM nutrition_daily
            WHERE user_id = $1
              AND log_date >= CURRENT_DATE - $2
            ORDER BY log_date DESC
        """

        results = await self.db.fetch(query, user_id, days_back)
        return [dict(r) for r in results]

    async def get_weekly_averages(
        self,
        user_id: str,
        weeks: int = 12
    ) -> List[dict]:
        """Get weekly averages"""
        # Implementation...

    async def insert_daily_logs(
        self,
        user_id: str,
        logs: List[dict]
    ):
        """Bulk insert nutrition logs"""
        # Implementation...
```

**Usage**:
```python
# In your agent tool
nutrition_repo = NutritionRepository(ctx.deps.db)
data = await nutrition_repo.get_daily_summary(user_id, days_back=30)
```

### Pattern 2: Service Layer (Business Logic)

```python
# backend/services/analysis/plateau_detector.py

class PlateauDetector:
    """
    Detects performance plateaus in exercises.
    Business logic separate from data access.
    """

    def __init__(self, workout_repo):
        self.workout_repo = workout_repo

    async def detect_exercise_plateau(
        self,
        user_id: str,
        exercise_name: str,
        weeks_back: int = 8
    ) -> dict:
        """
        Detect if exercise has plateaued.

        Plateau definition:
        - No improvement in last 3 consecutive sessions
        - Or weight decreased by >10%
        """
        # Get progression data
        progression = await self.workout_repo.get_exercise_progression(
            user_id, exercise_name, weeks_back
        )

        if len(progression) < 3:
            return {'insufficient_data': True}

        # Analyze last 3 sessions
        recent_3 = progression[-3:]
        weights = [s['max_weight'] for s in recent_3]

        # Check for stagnation
        if max(weights) == min(weights):
            return {
                'is_plateau': True,
                'plateau_type': 'stagnant',
                'weeks_stagnant': self._calculate_stagnant_weeks(progression),
                'current_max_kg': weights[-1],
                'recommendation': self._get_plateau_recommendation('stagnant')
            }

        # Check for regression
        if weights[-1] < weights[0] * 0.9:
            return {
                'is_plateau': True,
                'plateau_type': 'regression',
                'weight_loss_pct': ((weights[0] - weights[-1]) / weights[0]) * 100,
                'recommendation': self._get_plateau_recommendation('regression')
            }

        return {'is_plateau': False}

    def _get_plateau_recommendation(self, plateau_type: str) -> str:
        """Generate recommendation based on plateau type"""
        recommendations = {
            'stagnant': [
                "Try a deload week (reduce weight by 10-20%)",
                "Increase training frequency for this exercise",
                "Add variation exercises (e.g., incline bench if flat bench)",
                "Check nutrition and recovery (sleep, protein intake)"
            ],
            'regression': [
                "Take a full deload week immediately",
                "Check for overtraining (reduce volume)",
                "Ensure adequate sleep (8+ hours)",
                "Check nutrition (protein, calorie intake)"
            ]
        }
        return recommendations.get(plateau_type, [])
```

### Pattern 3: Dependency Injection

```python
# backend/dependencies.py

class AppDependencies:
    """
    Container for all app dependencies.
    Makes testing easier (can mock dependencies).
    """

    def __init__(self):
        self.db = Database()
        self.hevy_client = HevyMCPClient()

        # Repositories
        self.nutrition_repo = NutritionRepository(self.db)
        self.workout_repo = WorkoutRepository(self.db)

        # Services
        self.plateau_detector = PlateauDetector(self.workout_repo)
        self.correlation_engine = CorrelationEngine(
            self.nutrition_repo,
            self.workout_repo
        )

# Initialize once
app_deps = AppDependencies()

# Use in agent
@dataclass
class AppContext:
    deps: AppDependencies
    user_id: str

# In FastAPI
@app.post("/chat")
async def chat(request: ChatRequest):
    ctx = AppContext(
        deps=app_deps,
        user_id=request.user_id
    )

    result = await agent.run(request.message, deps=ctx)
    return {"response": result.data}
```

---

## Environment Variables & Configuration

```bash
# .env file (NEVER commit this!)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/workout_optimizer

# LLM APIs (choose one or both)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# External Services
HEVY_API_KEY=hevy_...
MYNETDIARY_EMAIL=your_email@example.com
MYNETDIARY_PASSWORD=your_password

# Observability
LOGFIRE_TOKEN=your_logfire_token

# App Config
DEBUG=true
ENVIRONMENT=development
```

**Load in Python**:
```python
# backend/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # LLM
    openai_api_key: str
    anthropic_api_key: str

    # Services
    hevy_api_key: str
    mynetdiary_email: str
    mynetdiary_password: str

    # Observability
    logfire_token: str = ""

    # App
    debug: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Testing Strategy

```python
# tests/test_nutrition_repository.py

import pytest
from backend.repositories.nutrition_repository import NutritionRepository

@pytest.fixture
async def test_db():
    """Create test database"""
    # Use pytest-asyncio for async tests
    db = await create_test_database()
    yield db
    await db.cleanup()

@pytest.fixture
def sample_nutrition_data():
    return [
        {'log_date': '2024-01-01', 'protein_g': 150, 'calories': 2500},
        {'log_date': '2024-01-02', 'protein_g': 140, 'calories': 2400},
    ]

@pytest.mark.asyncio
async def test_get_daily_summary(test_db, sample_nutrition_data):
    """Test getting daily summary"""
    repo = NutritionRepository(test_db)

    # Insert test data
    await repo.insert_daily_logs('test_user', sample_nutrition_data)

    # Query it back
    result = await repo.get_daily_summary('test_user', days_back=7)

    # Assert
    assert len(result) == 2
    assert result[0]['protein_g'] == 150
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Loading Too Much Data into LLM Context

**Problem**:
```python
# ❌ BAD: Returns 1000+ records (100,000 tokens!)
@agent.tool
async def get_all_nutrition(ctx):
    return await ctx.deps.db.get_all_nutrition_ever()
```

**Solution**:
```python
# ✅ GOOD: Returns aggregated summary (500 tokens)
@agent.tool
async def get_nutrition_summary(ctx, days_back: int = 30):
    """Get aggregated nutrition summary"""
    return await ctx.deps.db.get_daily_summary(days_back)
```

### Pitfall 2: Forgetting Async/Await

**Problem**:
```python
# ❌ BAD: Missing await
async def get_data():
    result = db.query()  # Returns a coroutine, not data!
    return result
```

**Solution**:
```python
# ✅ GOOD: Proper await
async def get_data():
    result = await db.query()  # Actually waits for data
    return result
```

### Pitfall 3: SQL Injection

**Problem**:
```python
# ❌ BAD: SQL injection vulnerability!
user_input = "1; DROP TABLE users;--"
query = f"SELECT * FROM users WHERE id = {user_input}"
```

**Solution**:
```python
# ✅ GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = $1"
result = await db.execute(query, user_id)
```

---

## Next Steps & Questions

**Before Starting Implementation**:
1. Read through this entire plan
2. Set up development environment (Python, PostgreSQL, Docker)
3. Fork/clone the existing repo
4. Ask questions about anything unclear

**When You Start Coding**:
1. Follow the roadmap phases sequentially
2. Complete "Understanding Check" sections
3. Ask for code reviews at each checkpoint
4. Don't skip testing!

**How to Get Help**:
```
Format:
"I'm working on [Phase X: Task Y]
I tried [what you did]
I expected [expected result]
But I got [actual result]
Here's my code: [code snippet]
Question: [specific question]"

Example:
"I'm working on Phase 1: Database setup
I tried creating the users table with SQLAlchemy
I expected the table to be created
But I got: 'relation users already exists'
Here's my code: [code]
Question: How do I handle existing tables in migrations?"
```

---

## Glossary

**Agent**: AI that can use tools to accomplish tasks
**API**: Application Programming Interface (how programs talk to each other)
**Async/Await**: Way to handle multiple operations simultaneously
**CORS**: Security feature for web browsers
**Docker**: Tool to package software in containers
**FastAPI**: Python web framework (builds APIs)
**LLM**: Large Language Model (GPT, Claude, etc.)
**MCP**: Model Context Protocol (standard way for AI to use tools)
**ORM**: Object-Relational Mapping (database ↔ Python objects)
**PostgreSQL**: Powerful open-source database
**Pydantic**: Python library for data validation
**RAG**: Retrieval Augmented Generation (AI looks up relevant info)
**Repository Pattern**: Code organization (separate data access from logic)
**REST API**: Standard way for web services to communicate
**SQLAlchemy**: Python library to work with databases
**TimescaleDB**: PostgreSQL extension for time-series data
**Tool**: Function the AI agent can call
**Type Safety**: Catching errors before code runs

---

## Final Notes

This plan is a living document. As you implement, you'll:
- Discover edge cases
- Find better ways to do things
- Need to adjust priorities

**That's normal and expected!**

The goal isn't perfection—it's a working app that helps optimize your workouts using AI and data.

**Key Principles**:
1. **Incremental progress**: Small working pieces > big non-working system
2. **Test as you go**: Don't wait until the end
3. **Ask questions**: No question is too simple
4. **Understand before moving on**: Don't cargo-cult code

**You've got this!** 🏋️💪

---

**Revision History**:
- v1.0 (2025-11-10): Initial comprehensive plan
