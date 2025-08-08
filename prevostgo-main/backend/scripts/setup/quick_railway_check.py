"""
Quick script to check Railway database without making changes
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    print("\nWindows PowerShell:")
    print('$env:DATABASE_URL = "your-postgresql-url-from-railway"')
    print("\nWindows CMD:")
    print('set DATABASE_URL=your-postgresql-url-from-railway')
    print("\nLinux/Mac:")
    print('export DATABASE_URL="your-postgresql-url-from-railway"')
    exit(1)

# Fix URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Quick stats
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'available') as available,
            COUNT(*) FILTER (WHERE source LIKE 'http%' OR source LIKE '%.png') as bad_sources
        FROM coaches
    """)
    
    stats = cur.fetchone()
    print(f"Total coaches: {stats['total']}")
    print(f"Available: {stats['available']}")
    print(f"Bad sources: {stats['bad_sources']}")
    
    if stats['bad_sources'] > 0:
        print("\n⚠️  Found coaches with image URLs in source field!")
        print("Run fix_railway_database.py to fix this issue")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
