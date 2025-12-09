"""
Dependencies for Pydantic AI agent tools.

This module defines the context that gets injected into every tool call.
Think of it as the "backpack" that tools carry - it has everything they need
to do their job (database access, user info, etc.)
"""

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

class AgentDependencies(BaseModel):
    """
    Dependencies that get passed to agent tools via RunContext.

    Why we need this:
    - Tools need to query the database (nutrition, workouts, health data)
    - Tools need to know WHICH user's data to query
    - Pydantic AI uses dependency injection to pass this safely

    Changed in Session 12:
    - Instead of sharing a single db session (causes concurrency issues),
      we now pass a session_factory that each tool uses to create its own session
    - This allows the agent to call multiple tools in parallel safely

    Attributes:
        session_factory: Factory to create new database sessions (one per tool call)
        user_id: UUID of the user asking the question
    """

    session_factory: async_sessionmaker[AsyncSession]
    user_id: str

    class Config:
        arbitrary_types_allowed = True # Allows async_sessionmaker (not a pure Pydantic type)
