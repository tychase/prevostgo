"""
Check for data quality issues in coaches
"""
import requests

print("🔍 Checking Coach Data Quality\n")

# Get all coaches without pagination limit
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/', 
                       params={'per_page': 100})
data = response.json()

print(f"Total coaches returned: {len(data.get('coaches', []))}")
print(f"Total in database: {data.get('total', 0)}")

if data.get('coaches'):
    # Analyze the coaches
    coaches = data['coaches']
    
    # Check for problematic data
    generic_titles = 0
    no_year = 0
    no_model = 0
    no_converter = 0
    
    for coach in coaches:
        if coach.get('title') == 'Prevost':
            generic_titles += 1
        if not coach.get('year') or coach.get('year') == 0:
            no_year += 1
        if not coach.get('model') or coach.get('model') == 'Unknown':
            no_model += 1
        if not coach.get('converter') or coach.get('converter') == 'Unknown':
            no_converter += 1
    
    print(f"\nData quality issues:")
    print(f"  Generic titles: {generic_titles}")
    print(f"  Missing year: {no_year}")
    print(f"  Missing model: {no_model}")
    print(f"  Missing converter: {no_converter}")
    
    # Show sample of good coaches
    print(f"\nSample coaches with good data:")
    good_coaches = [c for c in coaches if c.get('year', 0) > 0 and c.get('title') != 'Prevost']
    for coach in good_coaches[:5]:
        print(f"  - {coach.get('title')}")
        print(f"    Year: {coach.get('year')}, Model: {coach.get('model')}, Converter: {coach.get('converter')}")

# Also check featured coaches endpoint
print("\n\nChecking featured coaches endpoint...")
response = requests.get('https://prevostgo-production.up.railway.app/api/inventory/featured/listings')
if response.status_code == 200:
    featured = response.json()
    print(f"Featured coaches: {len(featured)}")
