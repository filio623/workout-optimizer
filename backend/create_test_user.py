"""
Create a test user for development.
Run this once to create a user, then use their ID for nutrition uploads.
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.db.models import User, Base

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

DATABASE_URL = "postgresql+asyncpg://postgres:workout_dev_password@localhost:5432/workout_optimizer"


async def create_test_user():

    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:

        test_user = User(
            name="Test User",
            email="test@workoutoptimizer.com"
        )

        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

        print(f"Created test user with ID: {test_user.id}")
        print(f" Name: {test_user.name}")
        print(f" Email: {test_user.email}")
        print("Copy this user ID for nutrition uploads.")

        return str(test_user.id)
    
if __name__ == "__main__":
    asyncio.run(create_test_user())