import requests
import json

print("🔍 Debugging PrevostGO Database Issue\n")

# Check the debug endpoint
try:
    print("1. Checking raw coach data via debug endpoint...")
    # Try to get a coach by ID (we'll use a common format)
    test_ids = ["1", "100", "500", "prevost-1", "coach-1"]
    
    for coach_id in test_ids:
        try:
            response = requests.get(f'https://prevostgo-production.up.railway.app/api/debug/coach/{coach_id}')
            if response.status_code == 200:
                print(f"✅ Found coach with ID: {coach_id}")
                data = response.json()
                print(f"   Title: {data.get('title', 'No title')}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                break
        except:
            continue
            
except Exception as e:
    print(f"Debug endpoint error: {e}")

print("\n2. Checking inventory summary...")
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/summary')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total coaches in summary: {data.get('total_coaches', 0)}")
        print(f"   By condition: {json.dumps(data.get('by_condition', {}), indent=2)}")
except Exception as e:
    print(f"Summary error: {e}")

print("\n3. Checking inventory with different parameters...")
# Try without any filters
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/', 
                          params={'per_page': 100})
    data = response.json()
    print(f"✅ Inventory response: {data.get('total', 0)} total coaches")
    if data.get('coaches'):
        print(f"   Returned {len(data['coaches'])} coaches")
except Exception as e:
    print(f"Inventory error: {e}")

print("\n4. Checking for coaches with different status...")
# Maybe coaches have a different status
for status in ['available', 'all', None]:
    try:
        params = {'per_page': 10}
        if status:
            params['status'] = status
        response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/', params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('total', 0) > 0:
                print(f"✅ Found {data['total']} coaches with status={status}")
                break
    except:
        continue

print("\n5. Direct database test...")
# Try the test endpoint
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/test')
    print(f"API test response: {response.json()}")
except Exception as e:
    print(f"Test endpoint error: {e}")
