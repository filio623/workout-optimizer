"""
Dependencies for Pydantic AI agent tools.

This module defines the context that gets injected into every tool call.
Think of it as the "backpack" that tools carry - it has everything they need
to do their job (database access, user info, etc.)
"""

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class AgentDependencies(BaseModel):
    """
    Dependencies that get passed to agent tools via RunContext.
    
    Why we need this:
    - Tools need to query the database (nutrition, workouts, health data)
    - Tools need to know WHICH user's data to query
    - Pydantic AI uses dependency injection to pass this safely
    
    Attributes:
        db: SQLAlchemy async session for database queries
        user_id: UUID of the user asking the question
    """

    db: AsyncSession
    user_id: str

    class Config:
        arbitrary_types_allowed = True # Allows AsyncSession (not a pure Pydantic type)
