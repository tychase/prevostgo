"""
Emergency diagnostic script to find where the coaches are
"""
import requests
import json

print("🚨 Emergency Coach Diagnostic\n")

# 1. Check if scraper is still using SQLite
print("1. Triggering a small test scrape...")
response = requests.post(
    'https://prevostgo-production.up.railway.app/api/inventory/scrape',
    params={'fetch_details': False, 'limit': 1}
)
if response.status_code == 200:
    data = response.json()
    print(f"   Scraper response: {json.dumps(data, indent=2)}")

# 2. Check health endpoint to confirm API is running
print("\n2. Checking API health...")
response = requests.get('https://prevostgo-production.up.railway.app/api/health')
print(f"   Health: {response.json()}")

# 3. Check for database connection errors in a different way
print("\n3. Testing database connection...")
# Try to trigger an error to see the real issue
response = requests.get(
    'https://prevostgo-production.up.railway.app/api/inventory/',
    params={'sort_by': 'invalid_column'}  # This should cause an error
)
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error response: {response.text[:500]}")

# 4. Check the raw debug endpoint
print("\n4. Checking debug endpoint...")
response = requests.get('https://prevostgo-production.up.railway.app/api/debug/coach/test')
print(f"   Debug status: {response.status_code}")
if response.status_code == 500:
    print(f"   Debug error: {response.text[:200]}")
