"""
Clean up invalid coach entries from the database
"""
import requests
import json

print("🧹 Cleaning up invalid coach entries...\n")

# This will trigger the scraper which now includes cleanup
print("Triggering scraper with cleanup...")
response = requests.post(
    'https://prevostgo-production.up.railway.app/api/inventory/scrape',
    params={'fetch_details': True, 'limit': None}
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Scraper completed")
    print(f"   Total found: {data['total_found']}")
    print(f"   New saved: {data['new_saved']}")
else:
    print(f"❌ Error: {response.status_code}")

# Check the inventory after cleanup
print("\n📦 Checking inventory after cleanup...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/')
data = response.json()
print(f"   Total coaches: {data.get('total', 0)}")

if data.get('coaches'):
    print("\n📋 Sample coaches (first 5):")
    for coach in data['coaches'][:5]:
        print(f"   - {coach.get('title')}")
        print(f"     Year: {coach.get('year')}, Price: {coach.get('price_display')}")
