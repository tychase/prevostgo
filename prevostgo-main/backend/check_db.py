import asyncio
from app.database import engine
from sqlalchemy import text

async def check_database():
    try:
        async with engine.connect() as conn:
            # Check coaches table
            result = await conn.execute(text("SELECT COUNT(*) FROM coaches"))
            count = result.scalar()
            print(f"Coaches in database: {count}")
            
            # Get sample data
            sample = await conn.execute(text("SELECT id, title, price, year FROM coaches LIMIT 5"))
            print("\nSample coaches:")
            for row in sample:
                print(f"  - {row[1]} | Price: ${row[2]} | Year: {row[3]}")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())