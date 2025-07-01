import requests
import json

# Test coach detail endpoint
coach_id = "e0dad424574e"  # Using the ID from the screenshot
url = f"http://localhost:8000/api/inventory/{coach_id}"

print(f"Testing coach detail endpoint: {url}")
print("-" * 50)

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\nCoach Data:")
        print(f"ID: {data.get('id')}")
        print(f"Title: {data.get('title')}")
        print(f"Year: {data.get('year')}")
        print(f"Model: {data.get('model')}")
        print(f"Converter: {data.get('converter')}")
        print(f"Price: ${data.get('price'):,}" if data.get('price') else "Price: N/A")
        print(f"Mileage: {data.get('mileage')}")
        print(f"Condition: {data.get('condition')}")
        print(f"Slides: {data.get('slide_count')}")
        print(f"Stock #: {data.get('stock_number')}")
        print(f"Images: {len(data.get('images', []))} images")
        print(f"Features: {len(data.get('features', []))} features")
        
        print("\nFull Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
