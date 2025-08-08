import requests
import json

print("🔍 Checking PrevostGO Production Status...\n")

# Check production backend
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/health')
    print("✅ Production backend is running!")
    print(f"Response: {response.json()}")
except Exception as e:
    print("❌ Production backend is not accessible")
    print(f"Error: {e}")

# Check inventory
try:
    response = requests.get('https://prevostgo-production.up.railway.app/api/inventory')
    data = response.json()
    print(f"\n📦 Production inventory: {data['total']} coaches")
    
    if data['total'] == 0:
        print("⚠️  No coaches in production database!")
        print("Need to run the scraper to populate with real data from prevost-stuff.com")
    else:
        print(f"✅ Found {data['total']} coaches")
        if data['coaches']:
            print("\nSample coaches:")
            for coach in data['coaches'][:3]:
                print(f"  - {coach.get('title', 'No title')}")
except Exception as e:
    print(f"\n❌ Could not check production inventory: {e}")

# Check if frontend can reach backend
print("\n🌐 Checking frontend connectivity...")
try:
    response = requests.get('https://prevostgo.com')
    print("✅ Frontend is accessible")
except Exception as e:
    print(f"❌ Frontend error: {e}")

# Check CORS
print("\n🔐 Checking CORS configuration...")
try:
    response = requests.options('https://prevostgo-production.up.railway.app/api/inventory', 
                               headers={'Origin': 'https://prevostgo.com'})
    print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
except Exception as e:
    print(f"CORS check error: {e}")
