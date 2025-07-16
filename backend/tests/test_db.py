import asyncio
import os
from sqlalchemy import text
from app.database import get_db, engine, DATABASE_URL
import sys

print(f"DATABASE_URL: {DATABASE_URL}")

async def test_database():
    try:
        # Test sync connection first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM coaches"))
            count = result.scalar()
            print(f"Total coaches in database: {count}")
            
            # Check some sample data
            result = conn.execute(text("SELECT id, title, price, status FROM coaches LIMIT 5"))
            print("\nSample coaches:")
            for row in result:
                print(f"  - {row.id}: {row.title} - Price: {row.price} - Status: {row.status}")
            
            # Check for available coaches
            result = conn.execute(text("SELECT COUNT(*) FROM coaches WHERE status = 'available'"))
            available_count = result.scalar()
            print(f"\nAvailable coaches: {available_count}")
            
            # Test a simple filter
            result = conn.execute(text("SELECT COUNT(*) FROM coaches WHERE status = 'available' AND price IS NOT NULL"))
            price_count = result.scalar()
            print(f"Available coaches with price: {price_count}")
            
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())