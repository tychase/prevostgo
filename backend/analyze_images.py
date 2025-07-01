"""
Analyze the actual HTML structure to find correct image patterns
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import re

def analyze_page_structure():
    """Fetch and analyze the main listing page to understand image patterns"""
    url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Fetching main listing page...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✓ Page fetched successfully")
    except Exception as e:
        print(f"✗ Error fetching page: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all images
    all_images = soup.find_all('img')
    print(f"\nFound {len(all_images)} total images on page")
    
    # Look for coach images specifically
    coach_images = []
    for img in all_images:
        src = img.get('src', '')
        alt = img.get('alt', '')
        
        # Skip navigation/button images
        if any(skip in src.lower() for skip in ['button', 'nav', 'logo', 'icon', 'spacer']):
            continue
            
        # Look for coach-related images
        if src and (any(word in src.lower() for word in ['prevost', 'coach', 'forsale']) or 
                   any(word in alt.lower() for word in ['prevost', 'coach'])):
            
            # Get the parent row to find associated coach info
            parent_tr = img.find_parent('tr')
            coach_info = "Unknown"
            if parent_tr:
                # Try to find the coach title
                link = parent_tr.find('a', href=lambda x: x and '.html' in x)
                if link:
                    coach_info = link.text.strip()
            
            coach_images.append({
                'src': src,
                'alt': alt,
                'coach': coach_info[:60]
            })
    
    print(f"\nFound {len(coach_images)} coach-related images")
    print("\nFirst 10 coach images:")
    for i, img in enumerate(coach_images[:10]):
        print(f"\n{i+1}. Coach: {img['coach']}")
        print(f"   Image src: {img['src']}")
        print(f"   Alt text: {img['alt']}")
    
    # Analyze patterns
    print("\n\nImage URL patterns found:")
    patterns = {}
    for img in coach_images:
        src = img['src']
        if src:
            # Extract pattern
            if src.startswith('http'):
                pattern = '/'.join(src.split('/')[:-1]) + '/'
            else:
                pattern = src.rsplit('/', 1)[0] + '/' if '/' in src else ''
            
            patterns[pattern] = patterns.get(pattern, 0) + 1
    
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern} ({count} images)")
    
    # Now let's check a detail page
    print("\n\nChecking a detail page for more patterns...")
    
    # Get first available coach with a detail URL
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT listing_url, title 
        FROM coaches 
        WHERE status = 'available' 
        AND listing_url LIKE '%.html'
        LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    
    if result:
        detail_url, title = result
        print(f"\nChecking detail page: {title[:60]}")
        print(f"URL: {detail_url}")
        
        try:
            detail_response = requests.get(detail_url, headers=headers, timeout=10)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                detail_images = detail_soup.find_all('img')
                
                print(f"\nFound {len(detail_images)} images on detail page")
                for i, img in enumerate(detail_images[:5]):
                    src = img.get('src', '')
                    if src and not any(skip in src.lower() for skip in ['button', 'nav', 'logo']):
                        print(f"  {i+1}. {src}")
            else:
                print(f"✗ Failed to fetch detail page: {detail_response.status_code}")
        except Exception as e:
            print(f"✗ Error fetching detail page: {e}")

if __name__ == "__main__":
    analyze_page_structure()
