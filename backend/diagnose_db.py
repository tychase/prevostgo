"""
Diagnostic script to check database and API status
"""

import sqlite3
import json
import os

print("=== PrevostGO Database Diagnostic ===\n")

# Check if database exists
db_path = "prevostgo.db"
if not os.path.exists(db_path):
    print(f"❌ Database file not found: {db_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    exit(1)

print(f"✅ Database found: {db_path}")
print(f"   Size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"\n📊 Tables in database: {[t[0] for t in tables]}")

# Check if coaches table exists
if 'coaches' not in [t[0] for t in tables]:
    print("❌ 'coaches' table not found!")
    print("\n💡 Run 'python init_database.py' to create the database schema")
    conn.close()
    exit(1)

# Count coaches
cursor.execute("SELECT COUNT(*) FROM coaches")
total = cursor.fetchone()[0]
print(f"\n🚌 Total coaches in database: {total}")

if total == 0:
    print("❌ No coaches found in database!")
    print("\n💡 Run 'python run_scraper.py' to populate the database")
    conn.close()
    exit(1)

# Count by status
cursor.execute("SELECT status, COUNT(*) FROM coaches GROUP BY status")
status_counts = cursor.fetchall()
print("\n📈 Coaches by status:")
for status, count in status_counts:
    print(f"   {status}: {count}")

# Count with prices
cursor.execute("SELECT COUNT(*) FROM coaches WHERE price IS NOT NULL AND status = 'available'")
with_prices = cursor.fetchone()[0]
print(f"\n💰 Available coaches with prices: {with_prices}")

# Sample coaches
cursor.execute("""
    SELECT id, title, year, converter, price, price_display, status 
    FROM coaches 
    LIMIT 5
""")
samples = cursor.fetchall()

print("\n📋 Sample coaches:")
for coach in samples:
    price_str = f"${coach[4]/100:,.0f}" if coach[4] else coach[5] or "Contact"
    print(f"   [{coach[6]}] {coach[2]} {coach[1][:50]}...")
    print(f"      Converter: {coach[3]}, Price: {price_str}")

# Check for recent scrapes
cursor.execute("""
    SELECT MAX(scraped_at) as last_scrape 
    FROM coaches
""")
last_scrape = cursor.fetchone()[0]
print(f"\n🕐 Last scrape: {last_scrape}")

conn.close()

print("\n✅ Database diagnostic complete!")
print("\nIf the database has coaches but they're not showing in the UI:")
print("1. Check that the backend API is running (python main.py)")
print("2. Check for CORS issues in the browser console")
print("3. Verify the API URL in the frontend is correct")
