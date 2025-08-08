import requests
import json
import time

print("🚀 Triggering PrevostGO Production Scraper...\n")

# Trigger the scraper on production
try:
    print("📡 Sending scrape request to production API...")
    response = requests.post(
        'https://prevostgo-production.up.railway.app/api/inventory/scrape',
        params={
            'fetch_details': True,
            'limit': None  # Get all coaches
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Scraper triggered successfully!")
        print(f"Total found: {data['total_found']}")
        print(f"New saved: {data['new_saved']}")
    else:
        print(f"❌ Scraper failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error triggering scraper: {e}")

# Wait a bit then check inventory
print("\n⏳ Waiting 5 seconds then checking inventory...")
time.sleep(5)

try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory')
    data = response.json()
    print(f"\n📦 Current inventory: {data['total']} coaches")
    
    if data['total'] > 0:
        print("✅ Database populated successfully!")
    else:
        print("⚠️  Database still empty. Check Railway logs for errors.")
        
except Exception as e:
    print(f"❌ Error checking inventory: {e}")
