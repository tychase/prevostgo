import os
import psycopg2
from urllib.parse import urlparse

# This is what your DATABASE_URL should look like
# DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@HOST.railway.app:PORT/railway"

def test_postgres_connection():
    # Get the DATABASE_URL you should use in Railway
    database_url = input("Enter your Railway PostgreSQL URL (from the Connect dialog): ").strip()
    
    if not database_url:
        print("❌ No URL provided")
        return
    
    try:
        # Parse the URL
        result = urlparse(database_url)
        
        print(f"\n📊 Connection details:")
        print(f"  Host: {result.hostname}")
        print(f"  Port: {result.port}")
        print(f"  Database: {result.path[1:]}")
        print(f"  Username: {result.username}")
        
        # Try to connect
        print("\n🔌 Attempting to connect...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print("✅ Connected successfully!")
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check coaches count
        try:
            cursor.execute("SELECT COUNT(*) FROM coaches")
            count = cursor.fetchone()[0]
            print(f"\n🚗 Coaches in database: {count}")
        except:
            print("\n⚠️  'coaches' table not found or empty")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL connection successful!")
        print("\n📝 Add this to your Railway backend environment variables:")
        print(f"DATABASE_URL={database_url}")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nMake sure you:")
        print("1. Copied the full connection string from Railway")
        print("2. The PostgreSQL service is running")
        print("3. You're using the correct password")

if __name__ == "__main__":
    test_postgres_connection()
