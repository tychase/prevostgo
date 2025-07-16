"""
Test the API search functionality directly
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000/api"
    
    print("Testing API endpoints...")
    
    # Test 1: Basic inventory request
    print("\n1. Testing basic inventory (no search):")
    response = requests.get(f"{base_url}/inventory?per_page=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Found {data.get('total', 0)} coaches")
        print(f"   Returned {len(data.get('coaches', []))} coaches")
    else:
        print(f"   Failed: {response.status_code} - {response.text}")
    
    # Test 2: Search for Marathon
    print("\n2. Testing search for 'Marathon':")
    response = requests.get(f"{base_url}/inventory?search=Marathon&per_page=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Found {data.get('total', 0)} coaches")
        if data.get('coaches'):
            for coach in data['coaches'][:3]:
                print(f"   - {coach.get('title', 'No title')}")
    else:
        print(f"   Failed: {response.status_code} - {response.text}")
    
    # Test 3: Search with price filter
    print("\n3. Testing search with price filter:")
    response = requests.get(f"{base_url}/inventory?min_price=100000&max_price=1000000&per_page=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Found {data.get('total', 0)} coaches")
    else:
        print(f"   Failed: {response.status_code} - {response.text}")
    
    # Test 4: Direct converter filter
    print("\n4. Testing converter filter:")
    response = requests.get(f"{base_url}/inventory?converters=Marathon&per_page=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Found {data.get('total', 0)} coaches")
    else:
        print(f"   Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
