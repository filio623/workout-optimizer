"""
Database session management for FastAPI.

This module provides:
- Async engine (connection pool)
- Session factory (creates database sessions)
- get_db() dependency (provides sessions to FastAPI endpoints)
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from backend.db.models import Base


DATABASE_URL = "postgresql+asyncpg://postgres:workout_dev_password@localhost/workout_optimizer"

#create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

# create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# dependency function for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session to FastAPI endpoints.
    Usage in FastAPI:
        @app.post("/endpoint")
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            # Use db here
            result = await db.execute(select(User))
            return result.scalars().all()
    
    The session is automatically closed after the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session # provide session to endpoint
            await session.commit() # commit if no errors
        except Exception:
            await session.rollback() # rollback on error
            raise
        finally:
            await session.close() # always ensure session is closed