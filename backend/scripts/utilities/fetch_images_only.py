import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_images_only():
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    # Get coaches with valid listing URLs but no images
    cursor.execute("""
        SELECT id, listing_url, title 
        FROM coaches 
        WHERE status = 'available'
        AND (images = '[]' OR images IS NULL)
        AND listing_url != '' 
        AND listing_url LIKE 'http%'
        LIMIT 50
    """)
    
    coaches = cursor.fetchall()
    updated = 0
    
    print(f"Fetching images for {len(coaches)} coaches...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for i, (coach_id, url, title) in enumerate(coaches):
        print(f"\n{i+1}/{len(coaches)} - {title[:50]}...")
        
        # For prevost-stuff.com, images are typically in the listing page
        # Let's try to extract from the main listing page pattern
        if 'prevost-stuff.com' in url:
            # The image URL pattern is usually based on the listing URL
            # Convert listing URL to image URL
            # Example: /forsale/2024_liberty_1234.html -> /forsale/2024_liberty_1234.jpg
            base_url = url.replace('.html', '.jpg')
            
            # Also try without the full path
            filename = url.split('/')[-1].replace('.html', '')
            possible_images = [
                base_url,
                f"https://www.prevost-stuff.com/forsale/{filename}.jpg",
                f"https://www.prevost-stuff.com/forsale/{filename}_1.jpg",
                f"https://www.prevost-stuff.com/forsale/images/{filename}.jpg"
            ]
            
            # Test which URLs work
            working_images = []
            for img_url in possible_images:
                try:
                    resp = requests.head(img_url, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        working_images.append(img_url)
                        print(f"  ✓ Found image: {img_url}")
                        break  # Just take the first working one
                except:
                    pass
            
            if working_images:
                cursor.execute("""
                    UPDATE coaches 
                    SET images = ? 
                    WHERE id = ?
                """, (json.dumps(working_images), coach_id))
                updated += 1
            else:
                print(f"  ✗ No images found")
        
        # Small delay to be respectful
        time.sleep(0.2)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {updated} coaches with images")

if __name__ == "__main__":
    fetch_images_only()
