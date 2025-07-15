import requests
import json

print("🔍 Debugging Coach Data in Production\n")

# 1. Check inventory endpoint
print("1. Checking main inventory endpoint...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/')
data = response.json()
print(f"   Total coaches: {data.get('total', 0)}")
print(f"   Coaches returned: {len(data.get('coaches', []))}")

# 2. Check without status filter
print("\n2. Checking inventory summary...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/summary')
if response.status_code == 200:
    summary = response.json()
    print(f"   Total coaches in summary: {summary.get('total_coaches', 0)}")
    print(f"   By condition: {json.dumps(summary.get('by_condition', {}), indent=6)}")
    print(f"   By status: {json.dumps(summary.get('by_status', {}), indent=6)}")

# 3. Try debug endpoint with a coach ID from the logs
print("\n3. Checking specific coach by ID...")
test_ids = ['8ea93f4c3dcd', '4a76344110fa', 'bea41cec53bc']  # IDs from your logs
for coach_id in test_ids:
    try:
        response = requests.get(f'https://prevostgo-production.up.railway.app/api/debug/coach/{coach_id}')
        if response.status_code == 200:
            coach = response.json()
            print(f"\n   ✅ Found coach {coach_id}:")
            print(f"      Title: {coach.get('title')}")
            print(f"      Status: {coach.get('status')}")
            print(f"      Year: {coach.get('year')}")
            print(f"      Price: {coach.get('price_display')}")
            break
    except Exception as e:
        continue

# 4. Check if the issue is with the status filter
print("\n4. Testing different query parameters...")
params_to_test = [
    {},  # No filters
    {'per_page': 100},  # More results
    {'sort_by': 'year', 'sort_order': 'desc'},  # Different sort
]

for params in params_to_test:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/', params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('total', 0) > 0:
            print(f"   ✅ Found {data['total']} coaches with params: {params}")
            if data.get('coaches'):
                print(f"      First coach: {data['coaches'][0].get('title')}")
            break
        else:
            print(f"   ❌ No coaches with params: {params}")
