"""
Check why coach detail pages are failing
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Check API endpoint
API_URL = "https://prevostgo-production.up.railway.app/api"  # Update this with your actual Railway backend URL

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get a sample coach
    cur.execute("SELECT id, title FROM coaches WHERE status = 'available' LIMIT 1")
    coach = cur.fetchone()
    
    if coach:
        print(f"Testing with coach ID: {coach['id']}")
        print(f"Title: {coach['title']}")
        
        # Test the API endpoint
        print(f"\nTesting API endpoint: {API_URL}/inventory/{coach['id']}")
        
        try:
            response = requests.get(f"{API_URL}/inventory/{coach['id']}", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API is working!")
                print(f"Response has keys: {list(data.keys())[:5]}...")
            else:
                print(f"❌ API returned error: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Could not reach API: {e}")
            print("\nMake sure:")
            print("1. Your backend is deployed and running on Railway")
            print("2. The API_URL in this script matches your Railway backend URL")
            print("3. Check Railway logs for any errors")
    
    conn.close()
    
except Exception as e:
    print(f"Database error: {e}")
