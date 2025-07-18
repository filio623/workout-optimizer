# Workout Optimizer - Minimal Viable Architecture Plan (MVP)

## Executive Overview

This project is a learning-focused, solo-developer AI-powered workout optimizer that integrates with the Hevy fitness app. The goal is to analyze, improve, and personalize your workout routines using your Hevy data, with a simple backend and room for future growth.

---

## Core Principles
- **Simplicity:** Only essential features for solo use and learning
- **Extensibility:** Easy to add features later (frontend, database, etc.)
- **Robustness:** Clean, maintainable code with clear separation of concerns
- **Backend-First:** All logic and endpoints in Python (FastAPI)
- **No Unnecessary Complexity:** No user auth, no database, no advanced infra
- **Performance:** Optimize critical paths for fast user experience

---

## Current State (Updated)

### ✅ **What We Have Built:**
- **Hevy API Integration** - Complete client with all CRUD operations
- **LLM Interface** - OpenAI Agents SDK with 8 function tools
- **Exercise Templates Caching** - Static file approach (0.00s vs 12s API calls)
- **Routine Creation** - Successfully creates and posts routines to Hevy
- **Performance Optimization** - Instant exercise access via static JSON file
- **Organized File Structure** - Clean project organization with `app/data/`
- **Configuration Management** - Centralized config with environment variables
- **Data Models** - Pydantic models for all data structures
- **Error Handling** - Basic error handling throughout the system
- **Logging** - Comprehensive logging for debugging

### 🔄 **What We're Working On:**
- **Smart Exercise Selection** - Muscle group analysis and intelligent selection
- **Interactive Conversation** - Multi-turn dialogue capabilities
- **Workout Analysis Tools** - Data analysis with pandas

### 📋 **What's Planned:**
- **Multi-Routine Creation** - Create multiple routines and organize in folders
- **Frontend Development** - Web/mobile interface
- **Database Integration** - Data persistence for history and analysis

---

## Minimal Component List

### 1. API Integration ✅
- `hevy_client.py`: Handles all Hevy API calls (GET/POST/PUT as needed)
- `config.py`: Loads API keys from `.env`

### 2. Data Layer ✅
- `models.py`: Pydantic models for workouts, routines, exercises
- `app/data/exercise_templates.json`: Static exercise data (432 exercises)
- **No database** (unless you want to persist analysis/history later)

### 3. AI/LLM Integration ✅
- `llm_interface.py`: Connects to OpenAI, wraps prompt/response logic
- OpenAI Agents SDK integration with 8 function tools
- Agent instructions for fitness coaching

### 4. Business Logic 🔄
- `workout_analyzer.py`: Functions to analyze workouts, routines, and generate summaries
- `exercise_cache.py`: Static file management for exercise templates
- `exercise_analyzer.py`: Smart exercise selection (in progress)
- `recommendation_engine.py` (optional): For suggestions/improvements

### 5. API Layer 📋
- `main.py`: FastAPI app with endpoints for:
  - `/chat` (POST): Send a question, get an AI answer
  - `/workouts` (GET): List workouts
  - `/analyze` (GET/POST): Get analysis or recommendations

### 6. Utilities ✅
- `config.py`: Loads environment variables/settings
- `logger.py`: Simple logging throughout the system

### 7. Testing 🔄
- `tests/`: Basic unit tests for core logic
- `test_cache.py`: Exercise cache functionality testing

---

## Minimal System Diagrams

### 1. System Overview (Updated)

```
+-------------------+
|      User         |
| (CLI or HTTP Req) |
+---------+---------+
          |
          v
+---------------------------+
|     FastAPI App (main.py) |
+---------------------------+
   |         |         |
   v         v         v
+--------+ +--------+ +--------------+
| Hevy   | |  LLM   | |  Analyzer    |
| Client | |Interface| | (workout_...|
+--------+ +--------+ +--------------+
   |         |         |
   v         v         v
+------------------------------------+
|      Hevy API   |   OpenAI API     |
+------------------------------------+
```

### 2. File/Module Relationships (Updated)

```
+-------------------+
|    main.py        |
+-------------------+
   |     |     |
   v     v     v
+--------+ +--------+ +-------------------+
| hevy_  | | llm_   | | workout_analyzer  |
| client | |interface| +------------------+
+--------+ +--------+      |
   |         |             v
   v         v         +--------+
+--------+ +--------+ | models |
|config.py| |models.py| +--------+
+--------+ +--------+      |
                          v
                    +------------------+
                    | exercise_cache   |
                    +------------------+
                          |
                          v
                    +------------------+
                    | app/data/        |
                    | exercise_templates.json |
                    +------------------+
```

### 3. API Endpoint Flow (Updated)

```
User (CLI/HTTP)
      |
      v
+-------------------+
|   FastAPI App     |
+-------------------+
      |
      |-- /chat (POST) --> LLM Interface --> OpenAI API
      |                    |
      |                    v
      |              Exercise Cache (0.00s)
      |
      |-- /workouts (GET) --> Hevy Client --> Hevy API
      |
      |-- /analyze (GET/POST) --> Hevy Client
      |                          |
      |                          v
      |                    Workout Analyzer
      |                          |
      |                          v
      |                    (returns analysis)
      v
(response to user)
```

---

## Minimal File Structure (Updated)

```
app/
  ├── data/
  │   └── exercise_templates.json  # Static exercise data (432 exercises)
  ├── hevy/
  │   └── client.py                # Hevy API integration
  ├── llm/
  │   └── interface.py             # OpenAI Agents SDK integration
  ├── services/
  │   ├── exercise_cache.py        # Static file management
  │   ├── exercise_analyzer.py     # Smart exercise selection (in progress)
  │   └── workout_analyzer.py      # Workout analysis
  ├── models.py                    # Pydantic data models
  ├── config.py                    # Configuration management
  └── main.py                      # FastAPI application entry point

tests/
  ├── __init__.py
  └── test_cache.py                # Exercise cache testing

.env                               # Environment variables
requirements.txt                   # Dependencies
README.md                          # Documentation
```

---

## Performance Achievements

### Exercise Template Loading:
- **Before:** 12+ seconds (API calls)
- **After:** 0.00 seconds (static file)
- **Improvement:** 100% faster ⚡

### Routine Creation:
- **Total Time:** ~3 seconds (including LLM processing)
- **Exercise Selection:** Instant
- **API Post:** ~0.2 seconds

### File Organization:
- **Static File:** `app/data/exercise_templates.json` (432 exercises)
- **Cache Service:** `app/services/exercise_cache.py`
- **Clean Structure:** Organized and maintainable

---

## What's NOT Included (for now)
- No user management/authentication (just your API keys in .env)
- No database (unless you want to persist data)
- No caching, rate limiting, or advanced logging
- No frontend (yet)
- No Docker/Kubernetes/CI/CD
- No notification/email system

---

## Frontend Considerations

- **Future Frontend with Flutter:**
    - You are considering Flutter for frontend development (web and/or mobile).
    - The backend API is designed to be frontend-agnostic and exposes standard HTTP/JSON endpoints, making it easy to consume from a Flutter app (using packages like `http`, `dio`, or `chopper`).
    - When ready, you can build a Flutter app that interacts with your FastAPI backend for chat, workout data, and analysis features.
    - Authentication, CORS, and API versioning can be added to support a production-grade Flutter frontend.

---

## How to Extend Later
- Add a database (SQLite/Postgres) for history, user data, etc.
- Add a frontend (React, Flutter, etc.) when ready.
- Add more advanced AI tools, caching, or user management as needed.
- Add workout analysis with pandas for data insights.
- Add multi-routine creation and folder organization.

---

## Implementation Steps
1. **Set up the minimal file structure.** ✅
2. **Implement Hevy API client and test fetching data.** ✅
3. **Add LLM integration and basic analysis functions.** ✅
4. **Optimize performance with exercise caching.** ✅
5. **Add smart exercise selection.** 🔄
6. **Add interactive conversation capabilities.** 📋
7. **Expose endpoints via FastAPI.** 📋
8. **Test with CLI or Postman.** 📋
9. **Iterate and add features as you learn and need them.** 📋

---

## Success Criteria

### MVP Complete ✅
- [x] Hevy API integration works correctly
- [x] AI chat functionality works
- [x] Exercise templates load instantly
- [x] Routine creation works end-to-end
- [x] All core modules are functional
- [x] Performance optimization achieved

### Enhanced Features Complete When:
- [ ] Smart exercise selection with muscle group analysis
- [ ] Interactive conversation capabilities
- [ ] Workout analysis tools with pandas
- [ ] Multi-routine creation and organization
- [ ] Frontend interface (optional)

---

## Summary
This plan keeps things simple, focused, and easy to build/maintain for a solo developer. We've successfully built a robust, extensible backend that meets your goals and is ready for future growth. The foundation is solid with excellent performance, and we're now focusing on making the exercise selection more intelligent and adding interactive conversation capabilities. Frontend development is deferred until the backend is solid and your learning goals are met. 