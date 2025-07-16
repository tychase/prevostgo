"""
Test database connection and async setup
"""

import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")
print(f"Original DATABASE_URL: {DATABASE_URL}")

# Fix PostgreSQL URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"Fixed DATABASE_URL: {DATABASE_URL}")

# Create async URL
if "postgresql" in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif "sqlite" in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

print(f"ASYNC_DATABASE_URL: {ASYNC_DATABASE_URL}")

async def test_connection():
    """Test database connection"""
    try:
        # Test sync connection first
        print("\n1. Testing sync engine...")
        if "sqlite" in DATABASE_URL:
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"   Sync connection successful: {result.scalar()}")
        
        # Test async connection
        print("\n2. Testing async engine...")
        try:
            async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
            async with async_engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                print(f"   Async connection successful: {result.scalar()}")
            
            # Test async session
            print("\n3. Testing async session...")
            AsyncSessionLocal = sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False
            )
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                print(f"   Async session successful: {result.scalar()}")
            
            await async_engine.dispose()
            
        except Exception as e:
            print(f"   Async engine error: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"Connection error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())