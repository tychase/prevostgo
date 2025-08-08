"""
Test scraper to see what it's actually parsing
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("Fetching prevost-stuff.com...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print("\nLooking for coach listings...")

# Find all links that might be coach listings
coach_links = soup.find_all('a', href=lambda x: x and '.html' in x and 'prevost' in x.lower())
print(f"Found {len(coach_links)} potential coach links")

# Show first 5 links
print("\nFirst 5 coach links:")
for i, link in enumerate(coach_links[:5]):
    print(f"\n{i+1}. Link text: {link.text.strip()}")
    print(f"   URL: {link.get('href')}")
    
    # Try to find the parent row to get more details
    parent = link.find_parent('tr')
    if parent:
        text = parent.get_text(separator=' | ', strip=True)
        print(f"   Row text: {text[:200]}...")

# Also look for tables with coach data
print("\n\nLooking for data tables...")
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Find tables that contain coach information
for i, table in enumerate(tables):
    text = table.get_text(strip=True)
    if 'Prevost' in text and ('Price' in text or 'Converter' in text):
        print(f"\nTable {i} appears to contain coach data")
        # Show first row
        first_row = table.find('tr')
        if first_row:
            print(f"First row: {first_row.get_text(separator=' | ', strip=True)[:200]}...")
        break
