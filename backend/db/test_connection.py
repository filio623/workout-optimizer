"""
Test database connection to PostgreSQL.
This script verifies that we can connect to the database.
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = "postgresql://postgres:workout_dev_password@localhost:5432/workout_optimizer"

ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:workout_dev_password@localhost:5432/workout_optimizer"

def test_sync_connection():
    """Test synchronous database connection."""
    print("Testing synchronous database connection...")

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f" Connected to PostgreSQL version: {version}")

            result = connection.execute(text(
                "SELECT extname FROM pg_extension WHERE extname = 'timescaledb';"
            ))
            timescale = result.fetchone()
            if timescale:
                print("timescaledb extension found.")
            else:
                print("timescaledb extension NOT found.")

            engine.dispose()
            return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
async def test_async_connection():
    """Test asynchronous database connection."""
    print("Testing asynchronous database connection...")

    try:
        engine = create_async_engine(ASYNC_DATABASE_URL)

        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f" Connected to database: {db_name}")

            await engine.dispose()
            return True
    except Exception as e:
        print(f"Async connection failed: {e}")
        return False
        
def main():

    """Run all connection tests."""
    print("=" * 60)
    print("PostgreSQL Connection Test")
    print("=" * 60)

    sync_result = test_sync_connection()
    async_result = test_async_connection()

    print("\n" + "=" * 60)
    if sync_result and async_result:
        print("All connection tests passed successfully!")
    else:
        print("Some connection tests failed.")
        print(f"Sunchronous test result: {sync_result}")
        print(f"Asynchronous test result: {async_result}")
    print("=" * 60)

if __name__ == "__main__":
    main()



                                         
            