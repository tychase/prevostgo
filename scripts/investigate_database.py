"""
Check what's actually in the database
"""
import requests
import json

print("🔍 Detailed Database Investigation\n")

# 1. Check inventory with no filters
print("1. Raw inventory endpoint...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/')
data = response.json()
print(f"   Total: {data.get('total', 0)}")
if data.get('coaches'):
    coach = data['coaches'][0]
    print(f"   First coach:")
    print(f"     ID: {coach.get('id')}")
    print(f"     Title: {coach.get('title')}")
    print(f"     Status: {coach.get('status')}")
    print(f"     Year: {coach.get('year')}")

# 2. Check summary to see distribution
print("\n2. Inventory summary...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/summary')
if response.status_code == 200:
    summary = response.json()
    print(f"   Total coaches: {summary.get('total_coaches', 0)}")
    print(f"   By condition: {json.dumps(summary.get('by_condition', {}), indent=6)}")

# 3. Try to get more coaches with different parameters
print("\n3. Testing pagination...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/', 
                       params={'per_page': 50, 'page': 1})
data = response.json()
print(f"   With per_page=50: {len(data.get('coaches', []))} coaches returned")

# 4. Check if it's a year filter issue (year=0 coaches)
print("\n4. Testing year filters...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/',
                       params={'year_min': 1})
data = response.json()
print(f"   With year_min=1: {data.get('total', 0)} coaches")

# 5. Direct coach fetch
print("\n5. Testing direct coach fetch...")
# Try the coach ID from logs
test_ids = ['8ea93f4c3dcd', '4a76344110fa', 'bea41cec53bc']
for coach_id in test_ids:
    response = requests.get(f'https://prevostgo-production.up.railway.app/api/inventory/{coach_id}')
    if response.status_code == 200:
        coach = response.json()
        print(f"   ✅ Found coach {coach_id}:")
        print(f"      Title: {coach.get('title')}")
        print(f"      Status: {coach.get('status')}")
        break
    elif response.status_code == 404:
        print(f"   ❌ Coach {coach_id} not found")
