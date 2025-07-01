"""
Debug script to test database and API routes
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.models.database import Coach, Base

async def test_database():
    """Test database connection and data"""
    print("Testing database connection...")
    
    # Create engine
    engine = create_async_engine(
        "sqlite+aiosqlite:///prevostgo.db",
        echo=True
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Count coaches
        result = await session.execute(select(func.count(Coach.id)))
        count = result.scalar()
        print(f"\nTotal coaches in database: {count}")
        
        # Get sample coaches
        result = await session.execute(
            select(Coach).limit(5)
        )
        coaches = result.scalars().all()
        
        print("\nSample coaches:")
        for coach in coaches:
            print(f"- {coach.id}: {coach.title} - ${coach.price/100 if coach.price else 'Contact'}")
        
        # Check for available coaches
        result = await session.execute(
            select(func.count(Coach.id)).where(Coach.status == "available")
        )
        available_count = result.scalar()
        print(f"\nAvailable coaches: {available_count}")
        
    await engine.dispose()

# Test the routes directly
async def test_routes():
    """Test API routes directly"""
    from main import app
    from fastapi.testclient import TestClient
    
    print("\n\nTesting API routes...")
    
    # Initialize the database
    from app.models.database import init_db
    await init_db()
    
    with TestClient(app) as client:
        # Test health
        response = client.get("/api/health")
        print(f"\n/api/health: {response.status_code}")
        
        # Test inventory
        response = client.get("/api/inventory")
        print(f"\n/api/inventory: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('total', 0)} coaches found")
        else:
            print(f"Error: {response.text}")
        
        # Test inventory with limit
        response = client.get("/api/inventory?limit=5")
        print(f"\n/api/inventory?limit=5: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Starting database test...")
    asyncio.run(test_database())
    
    print("\n" + "="*50)
    asyncio.run(test_routes())
