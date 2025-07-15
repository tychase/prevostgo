"""
Check the Railway PostgreSQL database schema and data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    exit(1)

# Fix URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=== Railway Database Schema Check ===\n")
    
    # Get column information for coaches table
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'coaches'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    print("📋 Coaches table columns:")
    for col in columns:
        print(f"   {col['column_name']}: {col['data_type']}")
    
    # Get the single coach to see what data we have
    print("\n📊 Current data:")
    cur.execute("SELECT COUNT(*) as total FROM coaches")
    total = cur.fetchone()['total']
    print(f"Total coaches: {total}")
    
    if total > 0:
        # Get all data from the single coach
        cur.execute("SELECT * FROM coaches LIMIT 1")
        coach = cur.fetchone()
        
        print("\n🚌 Sample coach data:")
        for key, value in coach.items():
            if value is not None and str(value).strip():
                print(f"   {key}: {value}")
    
    # Check if we need to run a scraper
    print("\n📋 Next steps:")
    print("1. The database only has 1 coach - we need to run the scraper")
    print("2. The scraper should be run on Railway, not locally")
    print("3. Or we can run it locally and it will save to the Railway database")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
