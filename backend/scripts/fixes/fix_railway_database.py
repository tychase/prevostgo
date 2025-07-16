"""
Check and fix the production PostgreSQL database on Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

print("=== Railway PostgreSQL Database Check & Fix ===\n")

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set!")
    print("\nTo fix this:")
    print("1. Get your DATABASE_URL from Railway dashboard")
    print("2. Set it: export DATABASE_URL='your-postgresql-url'")
    print("3. Run this script again")
    exit(1)

# Fix PostgreSQL URL if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # Connect to PostgreSQL
    print("Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("✅ Connected successfully!")
    
    # Check if coaches table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'coaches'
        );
    """)
    
    if not cur.fetchone()['exists']:
        print("❌ 'coaches' table not found!")
        print("Run the migration script first.")
        exit(1)
    
    # Check total coaches
    cur.execute("SELECT COUNT(*) as total FROM coaches")
    total = cur.fetchone()['total']
    print(f"\n📊 Total coaches in database: {total}")
    
    # Check coaches by status
    cur.execute("""
        SELECT status, COUNT(*) as count 
        FROM coaches 
        GROUP BY status
    """)
    status_counts = cur.fetchall()
    print("\n📈 Coaches by status:")
    for row in status_counts:
        print(f"   {row['status']}: {row['count']}")
    
    # Check for the source field issue
    print("\n🔍 Checking source field for issues...")
    
    # Check unique source values
    cur.execute("SELECT DISTINCT source FROM coaches")
    sources = [row['source'] for row in cur.fetchall()]
    print(f"Unique source values: {sources}")
    
    # Check for image URLs in source field
    cur.execute("""
        SELECT id, title, source 
        FROM coaches 
        WHERE source LIKE '%.png' 
           OR source LIKE '%.jpg' 
           OR source LIKE '%.gif'
           OR source LIKE 'http%'
        LIMIT 5
    """)
    bad_sources = cur.fetchall()
    
    if bad_sources:
        print(f"\n❌ Found coaches with image URLs in source field:")
        for coach in bad_sources:
            print(f"   ID: {coach['id']}")
            print(f"   Title: {coach['title'][:50]}...")
            print(f"   Bad source: {coach['source']}")
        
        # Count total bad sources
        cur.execute("""
            SELECT COUNT(*) as count
            FROM coaches 
            WHERE source LIKE '%.png' 
               OR source LIKE '%.jpg' 
               OR source LIKE '%.gif'
               OR source LIKE 'http%'
        """)
        bad_count = cur.fetchone()['count']
        
        print(f"\n🔧 Total coaches with bad source field: {bad_count}")
        
        # Fix them
        print("Fixing source field...")
        cur.execute("""
            UPDATE coaches 
            SET source = 'prevost-stuff.com' 
            WHERE source LIKE '%.png' 
               OR source LIKE '%.jpg' 
               OR source LIKE '%.gif'
               OR source LIKE 'http%'
        """)
        
        fixed_count = cur.rowcount
        print(f"✅ Fixed {fixed_count} coaches")
        
        # Also fix NULL or empty sources
        cur.execute("""
            UPDATE coaches 
            SET source = 'prevost-stuff.com' 
            WHERE source IS NULL OR source = ''
        """)
        
        fixed_null = cur.rowcount
        if fixed_null > 0:
            print(f"✅ Fixed {fixed_null} coaches with empty source")
        
        # Commit changes
        conn.commit()
        print("✅ Changes committed to database")
    else:
        print("✅ No coaches found with image URLs in source field")
    
    # Verify the fix
    cur.execute("SELECT DISTINCT source FROM coaches")
    sources_after = [row['source'] for row in cur.fetchall()]
    print(f"\n✅ Source values after fix: {sources_after}")
    
    # Check available coaches
    cur.execute("SELECT COUNT(*) as count FROM coaches WHERE status = 'available'")
    available = cur.fetchone()['count']
    print(f"\n📊 Available coaches: {available}")
    
    # Get a sample coach to verify data structure
    cur.execute("""
        SELECT id, title, year, model, converter, price_cents, source, images
        FROM coaches 
        WHERE status = 'available' 
        LIMIT 1
    """)
    sample = cur.fetchone()
    
    if sample:
        print(f"\n📋 Sample coach:")
        print(f"   ID: {sample['id']}")
        print(f"   Title: {sample['title']}")
        print(f"   Year: {sample['year']}")
        print(f"   Model: {sample['model']}")
        print(f"   Price: ${sample['price_cents']/100:,.0f}" if sample['price_cents'] else "Contact")
        print(f"   Source: {sample['source']}")
        print(f"   Images: {len(sample['images']) if sample['images'] else 0} images")
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\n✅ Database check and fix complete!")
    print("\n📋 Next steps:")
    print("1. Check if the backend API is deployed and running on Railway")
    print("2. Verify the frontend is pointing to the correct Railway backend URL")
    print("3. Check for any CORS errors in the browser console")
    
except psycopg2.OperationalError as e:
    print(f"❌ Could not connect to database: {e}")
    print("\nMake sure:")
    print("1. DATABASE_URL is set correctly")
    print("2. The Railway database service is running")
    print("3. You have network access to Railway")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
