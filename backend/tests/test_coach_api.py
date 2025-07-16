import requests
import sqlite3

# First, get a valid coach ID from the database
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM coaches WHERE status = 'available' LIMIT 1")
coach_id = cursor.fetchone()[0]
conn.close()

print(f"Testing with coach ID: {coach_id}")

# Test the API endpoint
try:
    response = requests.get(f"http://localhost:8000/api/inventory/{coach_id}")
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Response:")
        print(response.json())
    else:
        print("Error Response:")
        print(response.text)
except Exception as e:
    print(f"Error connecting to API: {e}")
    print("\nMake sure your backend is running!")
