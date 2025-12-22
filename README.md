# Workout Optimizer

**Status:** MVP Ready (Phase 3 Complete)  
**Version:** 1.0.0

An intelligent, self-hosted AI fitness coach that aggregates data from **Hevy** (workouts), **Apple Health** (biometrics), and **MyNetDiary** (nutrition) to provide personalized, data-driven coaching via an autonomous agent.

## 🚀 Features

- **🧠 Pydantic AI Agent**: A sovereign AI coach (Claude 3.5 Sonnet) that autonomously uses tools to analyze your data.
- **📊 Multi-Modal Analysis**: Correlates workout volume with nutrition (protein/calories) and health metrics (sleep/recovery).
- **🔄 Sovereign Cloud Architecture**: Self-hosted PostgreSQL + TimescaleDB database (Dockerized) ensuring total data privacy.
- **🔌 Hevy Integration (MCP)**: Uses the **Model Context Protocol** to sync workouts and create routines directly in Hevy.
- **🍎 Apple Health & Nutrition**: Ingests comprehensive health exports and MyNetDiary logs for holistic analysis.
- **💬 Persistent Chat**: Context-aware chat history stored in PostgreSQL, allowing for long-term coaching conversations.
- **📈 Real-Time Dashboard**: Visualization of muscle splits, weekly progress, and training heatmaps.
- **🔬 Full Observability**: Integrated with **Logfire** for deep tracing of Agent reasoning and API performance.

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic AI
- **Database**: PostgreSQL 16 + TimescaleDB (Time-series optimization)
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **AI/LLM**: Anthropic Claude 3.5 Sonnet (via Pydantic AI)
- **Integrations**: 
  - **Hevy**: via MCP (Model Context Protocol)
  - **Apple Health**: JSON Export Parser
  - **MyNetDiary**: XLS/CSV Parser

### System Diagram

```mermaid
graph TD
    User[User] --> Web[React Web App]
    Web --> API[FastAPI Backend]
    
    subgraph "Backend Core"
        API --> Agent[Pydantic AI Agent]
        API --> Services[Business Logic]
    end
    
    subgraph "Data Layer"
        Services --> DB[(PostgreSQL + TimescaleDB)]
        Agent --> HevyMCP[Hevy MCP Server]
    end
    
    HevyMCP --> HevyAPI[Hevy API]
```

## 📁 Project Structure

```
Workout_Optimizer/
├── backend/                # FastAPI Application
│   ├── agents/            # Pydantic AI Agent & Tools
│   ├── db/                # SQLAlchemy Models & Session
│   ├── mcp_servers/       # Hevy MCP Integration
│   ├── parsers/           # Apple Health/MyNetDiary Parsers
│   ├── routes/            # API Endpoints
│   ├── services/          # Core Business Logic
│   └── main.py            # Entry Point
├── web/                    # React Frontend
│   ├── src/
│   │   ├── components/    # UI Components
│   │   └── services/      # API Client
├── docker-compose.yml      # Database Orchestration
├── requirements.txt        # Python Dependencies
└── MASTER_ARCHITECTURE_PLAN.md
```

## 🛠️ Setup & Installation

### Prerequisites

- **Docker Desktop** (for the database)
- **Python 3.11+**
- **Node.js 18+**

### 1. Database Setup
Start the PostgreSQL + TimescaleDB container:
```bash
docker compose up -d
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Database Migrations
alembic upgrade head
```

Create a `.env` file in the root directory:
```env
# AI Keys
ANTHROPIC_API_KEY=your_key_here
LOGFIRE_TOKEN=your_token_here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/workout_optimizer

# Hevy Integration
HEVY_API_KEY=your_hevy_key_here
```

### 3. Frontend Setup
```bash
cd web
npm install
```

## 🚀 Running the Application

### Start the Backend
```bash
# From the root directory
source .venv/bin/activate
python -m backend.main
```
*Backend runs on http://localhost:8005*

### Start the Frontend
```bash
# From the web/ directory
npm run dev
```
*Frontend runs on http://localhost:5173*

## 🧪 Usage Guide

1. **Sync Data**: The dashboard will automatically pull recent workouts from Hevy.
2. **Upload Nutrition**: Click the 📎 icon in Chat to upload MyNetDiary Excel files.
3. **Ask Questions**: 
   - *"Why is my bench press stalling?"*
   - *"Am I eating enough protein for my training volume?"*
   - *"Create a new Push Day routine for me."*

## 📚 Documentation
- [Master Architecture Plan](MASTER_ARCHITECTURE_PLAN.md) - Deep dive into design decisions.
- [Technical Guide](TECHNICAL_GUIDE.md) - For developers contributing to the code.
- [Progress Log](PROGRESS.md) - History of development sessions.

## 📄 License
MIT
