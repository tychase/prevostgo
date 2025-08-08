import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Now we can import database stuff
from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

print(f"DATABASE_URL: {DATABASE_URL}")

def test_search():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT COUNT(*) FROM coaches"))
            total = result.scalar()
            print(f"\nTotal coaches in database: {total}")
            
            # Check available coaches
            result = conn.execute(text("SELECT COUNT(*) FROM coaches WHERE status = 'available'"))
            available = result.scalar()
            print(f"Available coaches: {available}")
            
            # Test filters
            print("\nTesting filters:")
            
            # Price filter test
            result = conn.execute(text("""
                SELECT COUNT(*) FROM coaches 
                WHERE status = 'available' 
                AND price >= 50000 * 100 
                AND price <= 500000 * 100
            """))
            price_filtered = result.scalar()
            print(f"- Coaches between $50k-$500k: {price_filtered}")
            
            # Model filter test
            result = conn.execute(text("""
                SELECT model, COUNT(*) as count 
                FROM coaches 
                WHERE status = 'available' 
                GROUP BY model 
                ORDER BY count DESC 
                LIMIT 5
            """))
            print("\n- Top 5 models:")
            for row in result:
                print(f"  {row.model}: {row.count}")
            
            # Converter filter test
            result = conn.execute(text("""
                SELECT converter, COUNT(*) as count 
                FROM coaches 
                WHERE status = 'available' 
                GROUP BY converter 
                ORDER BY count DESC 
                LIMIT 5
            """))
            print("\n- Top 5 converters:")
            for row in result:
                print(f"  {row.converter}: {row.count}")
                
            # Test a specific filter combination
            result = conn.execute(text("""
                SELECT id, title, price, model, converter 
                FROM coaches 
                WHERE status = 'available' 
                AND model ILIKE '%H3%'
                LIMIT 3
            """))
            print("\n- Sample H3 coaches:")
            for row in result:
                price_display = f"${row.price // 100:,}" if row.price else "Contact for Price"
                print(f"  {row.id}: {row.title} - {price_display}")
                
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()