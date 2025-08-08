"""
Quick test to see coaches without price sorting
"""
import requests

print("🔍 Testing inventory without price sorting...\n")

# Test different sort options
sort_options = [
    {'sort_by': 'year', 'sort_order': 'desc'},
    {'sort_by': 'created_at', 'sort_order': 'desc'},
    {'sort_by': 'price', 'sort_order': 'asc'},  # Ascending might work better
]

for params in sort_options:
    print(f"Testing with: {params}")
    response = requests.get(
        'https://prevostgo-production.up.railway.app/api/inventory/',
        params={**params, 'per_page': 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Total: {data.get('total', 0)}")
        print(f"  Returned: {len(data.get('coaches', []))}")
        
        if data.get('coaches'):
            coach = data['coaches'][0]
            print(f"  First coach: {coach.get('title', 'No title')}")
            print(f"  Price: {coach.get('price_display', 'No price')}")
            print("  ✅ SUCCESS - Coaches are showing!")
            break
    else:
        print(f"  Error: {response.status_code}")
    print()

# Also test the main endpoint used by the frontend
print("\nTesting frontend's actual request:")
response = requests.get(
    'https://prevostgo-production.up.railway.app/api/inventory',
    params={'per_page': 6, 'sort_by': 'price', 'sort_order': 'desc'}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total coaches: {data.get('total', 0)}")
