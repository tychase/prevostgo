"""
Check what's happening with the database and API connection
"""

import sqlite3
import json
import requests
import os

print("=== PrevostGO Database & API Check ===\n")

# 1. Check database
print("1. Checking Database...")
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Count coaches
cursor.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available'")
available_count = cursor.fetchone()[0]
print(f"   Available coaches in DB: {available_count}")

# Get a sample coach
cursor.execute("""
    SELECT id, title, year, model, converter, price, source, images 
    FROM coaches 
    WHERE status = 'available' 
    LIMIT 1
""")
sample = cursor.fetchone()

if sample:
    print(f"\n   Sample coach:")
    print(f"   ID: {sample[0]}")
    print(f"   Title: {sample[1]}")
    print(f"   Year: {sample[2]}")
    print(f"   Model: {sample[3]}")
    print(f"   Converter: {sample[4]}")
    print(f"   Price: ${sample[5]/100:,.0f}" if sample[5] else "Contact")
    print(f"   Source: {sample[6]}")
    print(f"   Images: {sample[7]}")

conn.close()

# 2. Check if API is running
print("\n2. Checking API...")
api_urls = [
    "http://localhost:8000/api/health",
    "http://localhost:8000/api/inventory?page=1&per_page=1"
]

for url in api_urls:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ {url} - OK")
            if 'inventory' in url:
                data = response.json()
                print(f"      Total coaches from API: {data.get('total', 0)}")
                if data.get('coaches'):
                    coach = data['coaches'][0]
                    print(f"      First coach: {coach.get('title', 'N/A')}")
        else:
            print(f"   ❌ {url} - Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {url} - Connection refused (API not running?)")
    except Exception as e:
        print(f"   ❌ {url} - Error: {e}")

# 3. Check environment
print("\n3. Environment:")
print(f"   Current directory: {os.getcwd()}")
print(f"   Database URL: {os.getenv('DATABASE_URL', 'sqlite:///prevostgo.db')}")

print("\n📋 Next Steps:")
if available_count == 0:
    print("   1. Run: python run_scraper.py")
else:
    print("   1. Make sure the API is running: python main.py")
    print("   2. Check frontend is pointing to correct API URL")
    print("   3. Look for CORS errors in browser console")
