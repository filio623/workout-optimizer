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

---

## Minimal Component List

### 1. API Integration
- `hevy_client.py`: Handles all Hevy API calls (GET/POST/PUT as needed)
- `auth.py` (optional): Loads API keys from `.env`

### 2. Data Layer
- `models.py`: Pydantic models for workouts, routines, exercises
- **No database** (unless you want to persist analysis/history later)

### 3. AI/LLM Integration
- `llm_interface.py`: Connects to OpenAI, wraps prompt/response logic
- `prompt_templates.py` (optional): For reusable prompt patterns

### 4. Business Logic
- `workout_analyzer.py`: Functions to analyze workouts, routines, and generate summaries
- `recommendation_engine.py` (optional): For suggestions/improvements

### 5. API Layer
- `main.py`: FastAPI app with endpoints for:
  - `/chat` (POST): Send a question, get an AI answer
  - `/workouts` (GET): List workouts
  - `/analyze` (GET/POST): Get analysis or recommendations

### 6. Utilities
- `config.py`: Loads environment variables/settings
- `logger.py` (optional): Simple logging

### 7. Testing
- `tests/`: Basic unit tests for core logic

---

## Minimal System Diagrams

### 1. System Overview

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

### 2. File/Module Relationships

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
+--------+ +--------+
```

### 3. API Endpoint Flow

```
User (CLI/HTTP)
      |
      v
+-------------------+
|   FastAPI App     |
+-------------------+
      |
      |-- /chat (POST) --> LLM Interface --> OpenAI API
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

## Minimal File Structure

```
app/
  hevy_client.py
  llm_interface.py
  workout_analyzer.py
  models.py
  main.py
  config.py
  # (optional) logger.py, prompt_templates.py, recommendation_engine.py

tests/
  test_workout_analyzer.py
.env
requirements.txt
README.md
```

---

## What’s NOT Included (for now)
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
- Add a frontend (React, etc.) when ready.
- Add more advanced AI tools, caching, or user management as needed.

---

## Implementation Steps
1. **Set up the minimal file structure.**
2. **Implement Hevy API client and test fetching data.**
3. **Add LLM integration and basic analysis functions.**
4. **Expose endpoints via FastAPI.**
5. **Test with CLI or Postman.**
6. **Iterate and add features as you learn and need them.**

---

## Summary
This plan keeps things simple, focused, and easy to build/maintain for a solo developer. You’ll have a robust, extensible backend that meets your goals and is ready for future growth. Frontend development is deferred until the backend is solid and your learning goals are met. 