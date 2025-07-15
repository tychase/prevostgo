"""
Direct PostgreSQL query to check coaches in production
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

print("🔍 Direct PostgreSQL Database Check\n")

# You'll need to provide your DATABASE_URL here
database_url = input("Enter your Railway PostgreSQL URL: ").strip()

if not database_url:
    print("No URL provided. Exiting.")
    exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Count all coaches
    cursor.execute("SELECT COUNT(*) as total FROM coaches")
    result = cursor.fetchone()
    print(f"✅ Total coaches in database: {result['total']}")
    
    # 2. Count by status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM coaches 
        GROUP BY status
    """)
    print("\n📊 Coaches by status:")
    for row in cursor.fetchall():
        print(f"   {row['status']}: {row['count']}")
    
    # 3. Check a sample coach
    cursor.execute("""
        SELECT id, title, status, price_status, year, condition
        FROM coaches 
        LIMIT 5
    """)
    print("\n📋 Sample coaches:")
    for row in cursor.fetchall():
        print(f"   ID: {row['id']}")
        print(f"   Title: {row['title']}")
        print(f"   Status: {row['status']}")
        print(f"   Condition: {row['condition']}")
        print(f"   Price Status: {row['price_status']}")
        print()
    
    # 4. Check if there are any with status='available'
    cursor.execute("SELECT COUNT(*) as available FROM coaches WHERE status = 'available'")
    result = cursor.fetchone()
    print(f"✅ Coaches with status='available': {result['available']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
