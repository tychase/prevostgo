"""
Quick script to test if the API endpoints are working
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test health endpoint
print("Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Health status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test inventory list
print("Testing inventory list...")
try:
    response = requests.get(f"{BASE_URL}/api/inventory?per_page=3")
    print(f"Inventory list status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total coaches: {data.get('total', 0)}")
        
        coaches = data.get('coaches', [])
        if coaches:
            for i, coach in enumerate(coaches[:3]):
                print(f"\nCoach {i+1}:")
                print(f"  ID: {coach.get('id')}")
                print(f"  Title: {coach.get('title')}")
                print(f"  Price: ${coach.get('price', 'N/A')}")
            
            # Test detail endpoint with first coach
            first_id = coaches[0].get('id')
            print(f"\n\nTesting detail endpoint with ID: {first_id}")
            
            detail_response = requests.get(f"{BASE_URL}/api/inventory/{first_id}")
            print(f"Detail endpoint status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                detail = detail_response.json()
                print(f"Successfully retrieved details for: {detail.get('title')}")
                print(f"Images count: {len(detail.get('images', []))}")
                print(f"Features count: {len(detail.get('features', []))}")
            else:
                print(f"Error response: {detail_response.text}")
        else:
            print("No coaches found in inventory!")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test summary endpoint
print("Testing inventory summary...")
try:
    response = requests.get(f"{BASE_URL}/api/inventory/summary")
    print(f"Summary status: {response.status_code}")
    
    if response.status_code == 200:
        summary = response.json()
        print(f"Total coaches: {summary.get('total_coaches', 0)}")
        print(f"By condition: {summary.get('by_condition', {})}")
except Exception as e:
    print(f"Error: {e}")
