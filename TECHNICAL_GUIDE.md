# Workout Optimizer - Technical Guide & System Architecture

**Last Updated:** December 21, 2025
**Version:** 1.2 (Persistent Chat Implemented)

This document provides a deep technical dive into the Workout Optimizer codebase. It is designed for engineers and developers to understand the system's internal mechanics, architectural decisions, and data flows.

---

## 1. High-Level Architecture

The Workout Optimizer is a **Vertical AI Application** designed to aggregate scattered health data and provide personalized coaching via an autonomous agent.

### System Context Diagram

```mermaid
graph TD
    User((User))
    
    subgraph "Frontend Layer (React)"
        Web[React Web App]
        Dashboard[Analytics Dashboard]
        Upload[File Upload UI]
    end
    
    subgraph "Application Layer (FastAPI)"
        API[FastAPI Backend]
        Agent[Pydantic AI Agent]
        DashRoute[Dashboard Stats Route]
        ChatService[Chat Service]
    end
    
    subgraph "Data Integration Layer"
        Parsers[Data Parsers]
        Services[Business Logic Services]
        MCP[MCP Client]
    end
    
    subgraph "External Systems"
        HevyAPI[Hevy API]
        AppleHealth[Apple Health Export]
        MND[MyNetDiary Export]
    end
    
    subgraph "Persistence Layer"
        DB[(PostgreSQL + TimescaleDB)]
        HevyMCP[Hevy MCP Server]
    end

    User <--> Web
    Web <-->|HTTP/Streaming| API
    Dashboard <-->|GET /dashboard/stats| DashRoute
    Upload <-->|POST /upload| API
    
    API --> Agent
    API --> ChatService
    Agent -->|Uses Tools| Services
    Agent -->|Uses Tools| MCP
    DashRoute -->|Aggregates| DB
    ChatService -->|Persists History| DB
    
    MCP <-->|Stdio/JSON-RPC| HevyMCP
    HevyMCP <-->|REST| HevyAPI
    
    Services -->|Read/Write| DB
    Parsers -->|Transform| Services
    
    AppleHealth -->|JSON| Parsers
    MND -->|Excel| Parsers
```

---

## 2. The "Brain": AI Agent Architecture

The core of the system is a **Single Agent with Parallel Tool Processing**, built on **Pydantic AI**.

### Tool Categorization
Tools are organized into domain-specific modules in `backend/agents/tools/`:

*   **`workout_tools.py`**: Queries history, PRs, and performs **Plateau Detection** (`detect_plateaus`).
*   **`nutrition_tools.py`**: Calculates macro averages and caloric trends.
*   **`health_tools.py`**: Retrieves sleep, steps, and weight metrics.
*   **`analysis_tools.py`**: Performs cross-domain correlation (e.g., `analyze_nutrition_vs_training`).

### Execution Flow

When a user asks a complex question like *"Why is my bench press stuck?"*, the agent:
1.  **Analyzes Intent**: Recognizes a performance issue.
2.  **Parallel Tool Call**: Simultaneously triggers `detect_plateaus("Bench Press")`, `get_nutrition_stats(days=30)`, and `get_health_metrics(days=30)`.
3.  **Synthesis**: Correlates the findings (e.g., "Weight stalled while protein intake dropped 20%").
4.  **Action**: Streams a response with specific, data-backed recommendations.

---

## 3. Data Layer: PostgreSQL + TimescaleDB

We use a hybrid relational/time-series database design to handle high-frequency health data and complex relationship data.

### Key Tables

| Table | Type | Purpose |
|-------|------|---------|
| `nutrition_daily` | Relational | Daily macro totals + full fidelity `raw_data` JSONB. |
| `workout_cache` | Relational | Synced summaries of workouts from Hevy/Apple Health. |
| `health_metrics_raw` | **Hypertable** | High-frequency time-series data (Heart Rate, Energy). |
| `chat_sessions` | Relational | Container for conversation threads with metadata. |
| `chat_messages` | Relational | Individual messages linked to sessions. |

---

## 4. Dashboard & Visualization

The app provides a real-time analytics dashboard via the `/dashboard/stats` endpoint.

### Aggregation Logic (`backend/routes/dashboard.py`)
This route bypasses the AI Agent for speed and performs direct SQL aggregations:
*   **Weekly Progress**: Normalized workout scores based on duration/intensity.
*   **Muscle Split**: Percentage distribution extracted from `workout_data` JSONB.
*   **Heatmap**: 28-day activity grid calculated from workout timestamps.

---

## 5. Data Ingestion Pipelines

### Web-Based Uploads
Users can now ingest data directly through the UI via the "Paperclip" button in the chat.
1.  **Frontend**: Triggers a file picker, wraps the file in `FormData`, and sends to `/nutrition/upload`.
2.  **Backend**: Identifies the parser, validates the schema, performs an **UPSERT** to prevent duplicates, and returns a summary message.

---

## 6. Frontend Architecture

### Component Guide
*   **`ChatInterface.tsx`**: Manages streaming LLM state, real-time session updates, and file upload triggers.
*   **`ChartsSection.tsx`**: Fetches and renders dashboard visualizations using Tailwind-based progress bars and grids.
*   **`Sidebar.tsx`**: Orchestrates the layout of stats, workout history, and now manages the **Chat History** list.
*   **`Layout.tsx`**: Lifts state (`currentSessionId`) to coordinate between Sidebar and ChatInterface.

---

## 7. Persistent Chat Architecture

We implemented a robust persistent chat system using PostgreSQL (`chat_sessions`, `chat_messages`).

### Data Flow (Streaming)
The `/chat/stream` endpoint handles the complex lifecycle of a streaming response:

1.  **Initialization**: Creates/Retrieves a `chat_session`.
2.  **User Message**: Immediately saves the user's input to `chat_messages`.
3.  **Handshake**: Sends the `SESSION_ID: <uuid>` as the first chunk to the frontend (allowing the URL to update instantly).
4.  **Streaming**: Generators text chunks from the AI Agent (no DB writes during stream).
5.  **Finalization**: In a `finally` block, aggregates the full response and saves it as a single `chat_message` record.

### State Management
*   **Backend**: `backend/services/chat_service.py` handles all DB interactions (CRUD for sessions/messages).
*   **Frontend**: `ChatInterface.tsx` re-fetches message history whenever `sessionId` changes.

---

## 9. Monitoring & Observability (Logfire)

We use **Pydantic Logfire** for end-to-end observability. This provides a "waterfall" view of the entire request lifecycle, from the FastAPI endpoint down to individual LLM tool calls.

### Integration
*   **FastAPI Instrumentation:** Tracks HTTP requests, latency, and status codes.
*   **Pydantic AI Instrumentation:** Traces agent execution, tool usage, and prompt/response flows.
*   **OpenAI/Google GenAI Instrumentation:** Logs raw LLM calls, token usage, and costs.

**Configuration:**
Logfire is configured in `backend/main.py` using the `LOGFIRE_TOKEN` environment variable.

---

## 10. Directory Structure Guide

```
/
├── backend/
│   ├── agents/
│   │   ├── agent.py          # Main agent definition
│   │   ├── dependencies.py    # Session factory injection
│   │   └── tools/             # AI tools (SQL/MCP wrappers)
│   ├── routes/
│   │   ├── dashboard.py       # Analytics aggregation
│   │   ├── nutrition.py       # File upload handling
│   │   └── workouts.py        # Hevy sync handling
│   ├── services/
│   │   ├── chat_service.py    # Persistent chat logic
│   ├── db/
│   │   └── models.py          # SQLAlchemy schema
│   └── main.py                # FastAPI entry & chat routes
├── web/
│   └── src/
│       ├── components/        # UI Layer
│       └── services/          # API Client (api.ts)
└── TECHNICAL_GUIDE.md         # You are here
```

---

## 8. Development Workflows

### Creating an Analysis Tool
1.  Add logic to `backend/agents/tools/analysis_tools.py`.
2.  Use `ctx.deps.session_factory()` for parallel-safe DB access.
3.  Ensure the docstring clearly explains *when* the agent should use the tool.

### Testing the "Full Loop"
1.  Upload a `MyNetDiary` Excel file via the UI.
2.  Verify the Dashboard updates instantly.
3.  Ask the Chat: *"Analyze my nutrition from that upload."*