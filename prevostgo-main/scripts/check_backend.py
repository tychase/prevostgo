import requests
import json

# Check local backend
try:
    response = requests.get('http://localhost:8000/api/health')
    print("✅ Local backend is running!")
    print(f"Response: {response.json()}")
except Exception as e:
    print("❌ Local backend is not running")
    print(f"Error: {e}")

# Check production backend
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/health')
    print("\n✅ Production backend is running!")
    print(f"Response: {response.json()}")
except Exception as e:
    print("\n❌ Production backend is not accessible")
    print(f"Error: {e}")

# Check inventory
try:
    response = requests.get('http://localhost:8000/api/inventory')
    data = response.json()
    print(f"\n📦 Local inventory: {data['total']} coaches")
except Exception as e:
    print(f"\n❌ Could not check local inventory: {e}")

try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory')
    data = response.json()
    print(f"\n📦 Production inventory: {data['total']} coaches")
except Exception as e:
    print(f"\n❌ Could not check production inventory: {e}")
