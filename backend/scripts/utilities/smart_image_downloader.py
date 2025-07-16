"""
Updated image downloader that fetches from detail pages
Based on the actual prevost-stuff.com structure
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from urllib.parse import urljoin

class SmartImageDownloader:
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
            # Make URL absolute if needed
            if not img_url.startswith('http'):
                # Handle relative URLs
                if img_url.startswith('/'):
                    img_url = 'https://www.prevost-stuff.com' + img_url
                else:
                    img_url = 'https://www.prevost-stuff.com/' + img_url
            
            print(f"  Downloading: {img_url}")
            
            response = requests.get(img_url, headers=self.headers, timeout=10, stream=True)
            if response.status_code == 200:
                # Determine extension
                ext = '.jpg'
                if '.png' in img_url.lower():
                    ext = '.png'
                elif '.gif' in img_url.lower():
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
    
    def scrape_detail_page_images(self, detail_url, coach_id):
        """Scrape images from the detail page"""
        try:
            print(f"  Fetching detail page: {detail_url}")
            response = requests.get(detail_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"  ✗ Failed to fetch detail page: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = []
            
            # Extract the base filename from the URL
            # Example: https://prevost-stuff.com/2021PrevostMillenniumH_TMS2616062725.html
            # Base name: 2021prevostmillenniumh_tms2616062725
            url_parts = detail_url.split('/')[-1].replace('.html', '')
            base_name = url_parts.lower()
            
            print(f"  Looking for images with base name: {base_name}")
            
            # Find all img tags
            img_tags = soup.find_all('img')
            found_count = 0
            
            for img in img_tags:
                src = img.get('src', '')
                
                # Skip ads, logos, buttons
                if any(skip in src.lower() for skip in ['logo', 'button', 'banner', 'epic', 'coach%20pro', 
                                                         'building', 'gradient', 'desert', 'aqua_air']):
                    continue
                
                # Look for images that match our coach
                # Pattern: base_name-01.jpg, base_name-02.jpg, etc.
                if base_name in src.lower() or url_parts in src:
                    local_path = self.download_image(src, coach_id, found_count)
                    if local_path:
                        images.append(local_path)
                        found_count += 1
                        
                        # Limit to 5 images per coach
                        if found_count >= 5:
                            break
            
            # If no images found with exact match, try pattern matching
            if not images:
                print(f"  No exact matches, trying pattern matching...")
                
                # Try common patterns based on what we saw
                possible_patterns = [
                    f"{base_name}-01.jpg",
                    f"{base_name}-02.jpg",
                    f"{base_name}-03.jpg",
                    f"{base_name}-04.jpg",
                    f"{base_name}_01.jpg",
                    f"{base_name}_02.jpg",
                ]
                
                for pattern in possible_patterns[:3]:  # Try first 3
                    local_path = self.download_image(pattern, coach_id, found_count)
                    if local_path:
                        images.append(local_path)
                        found_count += 1
            
            print(f"  Found {len(images)} images")
            return images
            
        except Exception as e:
            print(f"  ✗ Error scraping detail page: {e}")
            return []
    
    def download_for_coaches(self, limit=None):
        """Download images for coaches from their detail pages"""
        conn = sqlite3.connect('prevostgo.db')
        cursor = conn.cursor()
        
        # Get coaches without images but with detail URLs
        query = """
            SELECT id, title, listing_url 
            FROM coaches 
            WHERE status = 'available' 
            AND (images = '[]' OR images IS NULL)
            AND listing_url IS NOT NULL
            AND listing_url != ''
            AND listing_url LIKE '%.html'
        """
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        coaches = cursor.fetchall()
        
        print(f"\nFound {len(coaches)} coaches to process")
        updated = 0
        
        for i, (coach_id, title, listing_url) in enumerate(coaches):
            print(f"\n{i+1}/{len(coaches)} - {title[:60]}...")
            
            # Scrape images from detail page
            images = self.scrape_detail_page_images(listing_url, coach_id)
            
            if images:
                # Update database
                cursor.execute("""
                    UPDATE coaches 
                    SET images = ? 
                    WHERE id = ?
                """, (json.dumps(images), coach_id))
                updated += 1
                print(f"  ✓ Updated with {len(images)} image(s)")
            else:
                print(f"  ✗ No images found")
            
            # Be respectful to the server
            time.sleep(1)
            
            # Commit every 10 coaches
            if (i + 1) % 10 == 0:
                conn.commit()
                print(f"\n💾 Saved progress: {i+1} coaches processed")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Downloaded images for {updated} coaches")
        return updated

def main():
    downloader = SmartImageDownloader()
    
    print("Smart Image Downloader for PrevostGo")
    print("=" * 40)
    print("This will fetch images from coach detail pages")
    
    print("\nOptions:")
    print("1. Test with first 5 coaches")
    print("2. Process first 20 coaches")
    print("3. Process first 50 coaches")
    print("4. Process ALL coaches (may take a while)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        downloader.download_for_coaches(limit=5)
    elif choice == '2':
        downloader.download_for_coaches(limit=20)
    elif choice == '3':
        downloader.download_for_coaches(limit=50)
    elif choice == '4':
        confirm = input("\nThis will process all coaches. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            downloader.download_for_coaches()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
