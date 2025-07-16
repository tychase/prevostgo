"""
Quick fix to test if coaches exist in the database
"""
import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_database():
    # Get database URL from environment or use default
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")
    
    # Fix for SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print(f"Database URL: {DATABASE_URL[:30]}...")
    
    # For async
    if "postgresql" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    elif "sqlite" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    
    try:
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.connect() as conn:
            # Check coaches table
            result = await conn.execute(text("SELECT COUNT(*) FROM coaches"))
            count = result.scalar()
            print(f"\n✅ Total coaches in database: {count}")
            
            # Check available coaches
            result = await conn.execute(text("SELECT COUNT(*) FROM coaches WHERE status = 'available'"))
            available = result.scalar()
            print(f"✅ Available coaches: {available}")
            
            # Get sample coaches
            result = await conn.execute(text("SELECT id, title, status FROM coaches LIMIT 5"))
            coaches = result.fetchall()
            
            if coaches:
                print("\n📋 Sample coaches:")
                for coach in coaches:
                    print(f"  ID: {coach[0]}, Title: {coach[1]}, Status: {coach[2]}")
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Set the Railway DATABASE_URL here for testing
    # os.environ["DATABASE_URL"] = "postgresql://..."
    asyncio.run(check_database())
