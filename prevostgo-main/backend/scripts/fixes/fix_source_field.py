"""
Fix the source field in the database where it contains image URLs instead of the source name
"""

import sqlite3
import json

print("=== Fixing Source Field in Database ===\n")

# Connect to database
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# First, let's see what's in the source field
print("Checking current source values...")
cursor.execute("SELECT DISTINCT source FROM coaches")
sources = cursor.fetchall()
print(f"Unique source values found: {[s[0] for s in sources]}")

# Check for coaches with image URLs in source field
cursor.execute("SELECT id, title, source FROM coaches WHERE source LIKE '%.png' OR source LIKE '%.jpg' OR source LIKE '%.gif'")
bad_sources = cursor.fetchall()

if bad_sources:
    print(f"\n❌ Found {len(bad_sources)} coaches with image URLs in source field:")
    for coach_id, title, source in bad_sources[:5]:  # Show first 5
        print(f"   ID: {coach_id}, Title: {title[:40]}...")
        print(f"   Bad source: {source}")
    
    # Fix them
    print("\n🔧 Fixing source field...")
    cursor.execute("""
        UPDATE coaches 
        SET source = 'prevost-stuff.com' 
        WHERE source LIKE '%.png' OR source LIKE '%.jpg' OR source LIKE '%.gif'
    """)
    
    fixed_count = cursor.rowcount
    print(f"✅ Fixed {fixed_count} coaches")
    
    # Commit the changes
    conn.commit()
else:
    print("\n✅ No coaches found with image URLs in source field")

# Also check for any NULL or empty sources
cursor.execute("SELECT COUNT(*) FROM coaches WHERE source IS NULL OR source = ''")
empty_count = cursor.fetchone()[0]

if empty_count > 0:
    print(f"\n🔧 Fixing {empty_count} coaches with empty source...")
    cursor.execute("""
        UPDATE coaches 
        SET source = 'prevost-stuff.com' 
        WHERE source IS NULL OR source = ''
    """)
    conn.commit()

# Verify the fix
cursor.execute("SELECT DISTINCT source FROM coaches")
sources_after = cursor.fetchall()
print(f"\n✅ Source values after fix: {[s[0] for s in sources_after]}")

# Check total coaches
cursor.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available'")
available_count = cursor.fetchone()[0]
print(f"\n📊 Total available coaches: {available_count}")

conn.close()
print("\n✅ Source field fix complete!")
