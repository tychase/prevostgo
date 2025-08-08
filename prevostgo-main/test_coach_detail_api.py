import requests
import json

# Test the inventory list endpoint first
print("Testing inventory list endpoint...")
response = requests.get("http://localhost:8000/api/inventory?per_page=5")
if response.status_code == 200:
    data = response.json()
    print(f"Total coaches: {data.get('total', 0)}")
    coaches = data.get('coaches', [])
    
    if coaches:
        # Get the first coach ID
        first_coach = coaches[0]
        coach_id = first_coach.get('id')
        print(f"\nFirst coach ID: {coach_id}")
        print(f"Title: {first_coach.get('title')}")
        
        # Now test the detail endpoint
        print(f"\nTesting detail endpoint for coach {coach_id}...")
        detail_response = requests.get(f"http://localhost:8000/api/inventory/{coach_id}")
        
        print(f"Status code: {detail_response.status_code}")
        
        if detail_response.status_code == 200:
            coach_detail = detail_response.json()
            print("Coach details retrieved successfully!")
            print(f"Title: {coach_detail.get('title')}")
            print(f"Price: {coach_detail.get('price')}")
            print(f"Images: {len(coach_detail.get('images', []))} images")
        else:
            print(f"Error: {detail_response.text}")
    else:
        print("No coaches found in inventory")
else:
    print(f"Error fetching inventory: {response.status_code}")
    print(response.text)
