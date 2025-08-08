import requests
import json
import time

print("🚀 Populating PrevostGO Production Database...\n")

# First, check current inventory
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory')
    data = response.json()
    print(f"📦 Current inventory: {data['total']} coaches\n")
except Exception as e:
    print(f"❌ Error checking inventory: {e}\n")

# Trigger the scraper
print("📡 Triggering scraper to fetch real coaches from prevost-stuff.com...")
try:
    response = requests.post(
        'https://prevostgo-production.up.railway.app/api/inventory/scrape',
        params={
            'fetch_details': True,
            'limit': None  # Get all coaches
        },
        timeout=300  # 5 minute timeout for large scrape
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Scraper completed!")
        print(f"   Total found: {data['total_found']}")
        print(f"   New saved: {data['new_saved']}")
    else:
        print(f"❌ Scraper failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("⏱️  Scraper is taking longer than expected. This is normal for first run.")
    print("Check Railway logs for progress...")
except Exception as e:
    print(f"❌ Error triggering scraper: {e}")

# Wait and check again
print("\n⏳ Waiting 10 seconds for database to update...")
time.sleep(10)

# Final check
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory')
    data = response.json()
    print(f"\n📦 Final inventory count: {data['total']} coaches")
    
    if data['total'] > 0:
        print("✅ Success! Database populated with real coaches.")
        print("\n🌐 Check https://prevostgo.com - coaches should now be visible!")
        
        # Show sample coaches
        if data['coaches']:
            print("\n📋 Sample coaches in database:")
            for coach in data['coaches'][:3]:
                print(f"  - {coach.get('title', 'No title')}")
                print(f"    Price: {coach.get('price_display', 'Contact for price')}")
    else:
        print("⚠️  Database still empty. Check Railway logs for errors.")
        print("\nTroubleshooting:")
        print("1. Check Railway logs for any error messages")
        print("2. Verify DATABASE_URL is set correctly")
        print("3. Make sure PostgreSQL service is running")
        
except Exception as e:
    print(f"❌ Error checking final inventory: {e}")
