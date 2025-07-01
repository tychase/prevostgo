"""
Download images for existing coaches in the database
"""

import sqlite3
import requests
import json
import os
import time
from urllib.parse import urljoin

class ImageDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Create images directory
        self.images_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'coach-images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        print(f"Images will be saved to: {self.images_dir}")
        
    def download_image(self, img_url, coach_id, image_index=0):
        """Download and save image"""
        try:
            # Make URL absolute
            if not img_url.startswith('http'):
                img_url = urljoin('https://www.prevost-stuff.com/', img_url)
            
            print(f"  Downloading: {img_url}")
            
            response = requests.get(img_url, headers=self.headers, timeout=10, stream=True)
            if response.status_code == 200:
                # Determine extension
                ext = '.jpg'
                content_type = response.headers.get('content-type', '').lower()
                if 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                
                filename = f"{coach_id}_{image_index}{ext}"
                filepath = os.path.join(self.images_dir, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"  ✓ Saved: {filename}")
                return f"/coach-images/{filename}"
            else:
                print(f"  ✗ Failed: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def find_image_urls(self, listing_url, title):
        """Try to find image URLs based on listing URL patterns"""
        possible_urls = []
        
        if 'prevost-stuff.com' in listing_url and '.html' in listing_url:
            # Extract filename from URL
            filename = listing_url.split('/')[-1].replace('.html', '')
            
            # Common image patterns
            possible_urls.extend([
                f"https://www.prevost-stuff.com/forsale/{filename}.jpg",
                f"https://www.prevost-stuff.com/forsale/{filename}_1.jpg",
                f"https://www.prevost-stuff.com/forsale/{filename}_2.jpg",
                f"https://www.prevost-stuff.com/forsale/images/{filename}.jpg",
                f"https://www.prevost-stuff.com/images/{filename}.jpg"
            ])
            
            # Try year-based patterns
            import re
            year_match = re.search(r'(\d{4})', title)
            if year_match:
                year = year_match.group(1)
                possible_urls.extend([
                    f"https://www.prevost-stuff.com/forsale/{year}_{filename}.jpg",
                    f"https://www.prevost-stuff.com/forsale/{filename}_{year}.jpg"
                ])
        
        return possible_urls
    
    def download_for_existing_coaches(self, limit=None):
        """Download images for coaches already in database"""
        conn = sqlite3.connect('prevostgo.db')
        cursor = conn.cursor()
        
        # Get coaches without images
        query = """
            SELECT id, title, listing_url 
            FROM coaches 
            WHERE status = 'available' 
            AND (images = '[]' OR images IS NULL)
            AND listing_url IS NOT NULL
            AND listing_url != ''
        """
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        coaches = cursor.fetchall()
        
        print(f"\nFound {len(coaches)} coaches without images")
        updated = 0
        
        for i, (coach_id, title, listing_url) in enumerate(coaches):
            print(f"\n{i+1}/{len(coaches)} - {title[:60]}...")
            
            # Get possible image URLs
            possible_urls = self.find_image_urls(listing_url, title)
            
            # Try to download images
            downloaded_images = []
            for j, img_url in enumerate(possible_urls[:3]):  # Try first 3 possibilities
                local_path = self.download_image(img_url, coach_id, j)
                if local_path:
                    downloaded_images.append(local_path)
                    break  # Got one image, that's enough for now
            
            if downloaded_images:
                # Update database
                cursor.execute("""
                    UPDATE coaches 
                    SET images = ? 
                    WHERE id = ?
                """, (json.dumps(downloaded_images), coach_id))
                updated += 1
                print(f"  ✓ Updated with {len(downloaded_images)} image(s)")
            else:
                print(f"  ✗ No images found")
            
            # Be respectful to the server
            time.sleep(0.5)
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Downloaded images for {updated} coaches")
        return updated

def main():
    downloader = ImageDownloader()
    
    print("Image Downloader for Existing Coaches")
    print("=" * 40)
    
    print("\nOptions:")
    print("1. Download images for ALL coaches without images")
    print("2. Test with first 10 coaches")
    print("3. Test with first 50 coaches")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        downloader.download_for_existing_coaches()
    elif choice == '2':
        downloader.download_for_existing_coaches(limit=10)
    elif choice == '3':
        downloader.download_for_existing_coaches(limit=50)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
