"""
Enhanced image downloader with better pattern detection and fallback strategies
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from urllib.parse import urljoin, urlparse

class EnhancedImageDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Create images directory
        self.images_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'coach-images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Track statistics
        self.stats = {
            'total_processed': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'coaches_with_images': 0,
            'coaches_without_images': 0
        }
        
    def download_image(self, img_url, coach_id, image_index=0):
        """Download and save image with better error handling"""
        try:
            # Handle various URL formats
            if not img_url.startswith('http'):
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://www.prevost-stuff.com' + img_url
                else:
                    img_url = 'https://www.prevost-stuff.com/' + img_url
            
            response = requests.get(img_url, headers=self.headers, timeout=10, stream=True)
            if response.status_code == 200:
                # Detect file type from content
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    # Fallback to URL extension
                    url_ext = os.path.splitext(urlparse(img_url).path)[1].lower()
                    ext = url_ext if url_ext in ['.jpg', '.jpeg', '.png', '.gif'] else '.jpg'
                
                filename = f"{coach_id}_{image_index}{ext}"
                filepath = os.path.join(self.images_dir, filename)
                
                # Save image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.stats['successful_downloads'] += 1
                return f"/coach-images/{filename}"
            else:
                self.stats['failed_downloads'] += 1
                return None
                
        except Exception as e:
            self.stats['failed_downloads'] += 1
            return None
    
    def extract_all_possible_images(self, soup, base_name, detail_url):
        """Extract all possible image URLs from the page"""
        possible_images = []
        
        # Strategy 1: Find images in the content area
        content_areas = soup.find_all(['td', 'div'], class_=['content', 'main', 'listing'])
        for area in content_areas:
            imgs = area.find_all('img')
            for img in imgs:
                src = img.get('src', '')
                if src and not any(skip in src.lower() for skip in ['logo', 'banner', 'button', 'gradient']):
                    possible_images.append(src)
        
        # Strategy 2: Find all images and filter by src patterns
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            src = img.get('src', '')
            if not src:
                continue
                
            # Look for images with the base name or similar patterns
            src_lower = src.lower()
            if any(pattern in src_lower for pattern in [base_name, 'prevost', 'coach']):
                if not any(skip in src_lower for skip in ['logo', 'banner', 'epic', 'gradient', 'button']):
                    possible_images.append(src)
        
        # Strategy 3: Look for image links
        links = soup.find_all('a', href=re.compile(r'\.(jpg|jpeg|png|gif)', re.I))
        for link in links:
            href = link.get('href', '')
            if href and base_name in href.lower():
                possible_images.append(href)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in possible_images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images
    
    def scrape_detail_page_images(self, detail_url, coach_id, title):
        """Enhanced scraping with multiple strategies"""
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = []
            
            # Extract base name from URL
            url_parts = detail_url.split('/')[-1].replace('.html', '')
            base_name = url_parts.lower()
            
            # Get all possible images
            possible_images = self.extract_all_possible_images(soup, base_name, detail_url)
            
            # Try to download the most relevant images
            downloaded = 0
            for img_src in possible_images:
                if downloaded >= 5:  # Limit to 5 images
                    break
                    
                local_path = self.download_image(img_src, coach_id, downloaded)
                if local_path:
                    images.append(local_path)
                    downloaded += 1
            
            # If still no images, try common patterns
            if not images:
                # Extract year from title for pattern matching
                year_match = re.search(r'(\d{4})', title)
                year = year_match.group(1) if year_match else ''
                
                # Try various naming patterns
                patterns = [
                    f"{base_name}-01.jpg",
                    f"{base_name}_01.jpg",
                    f"{base_name}01.jpg",
                    f"{base_name}-1.jpg",
                    f"{base_name}_1.jpg",
                    f"{base_name}.jpg",
                    f"{year}{base_name}.jpg" if year else None,
                ]
                
                for pattern in [p for p in patterns if p]:
                    if downloaded >= 3:  # Try at least 3 patterns
                        break
                    local_path = self.download_image(pattern, coach_id, downloaded)
                    if local_path:
                        images.append(local_path)
                        downloaded += 1
            
            return images
            
        except Exception as e:
            return []
    
    def download_for_coaches(self, limit=None, skip_existing=True):
        """Download images for coaches with progress tracking"""
        conn = sqlite3.connect('prevostgo.db')
        cursor = conn.cursor()
        
        # Get coaches to process
        if skip_existing:
            query = """
                SELECT id, title, listing_url 
                FROM coaches 
                WHERE status = 'available' 
                AND (images = '[]' OR images IS NULL)
                AND listing_url IS NOT NULL
                AND listing_url != ''
                AND listing_url LIKE '%.html'
            """
        else:
            query = """
                SELECT id, title, listing_url 
                FROM coaches 
                WHERE status = 'available' 
                AND listing_url IS NOT NULL
                AND listing_url != ''
                AND listing_url LIKE '%.html'
            """
            
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        coaches = cursor.fetchall()
        
        print(f"\n📋 Found {len(coaches)} coaches to process")
        print("=" * 50)
        
        for i, (coach_id, title, listing_url) in enumerate(coaches):
            self.stats['total_processed'] += 1
            print(f"\n🚗 [{i+1}/{len(coaches)}] {title[:60]}...")
            
            # Scrape images
            images = self.scrape_detail_page_images(listing_url, coach_id, title)
            
            if images:
                # Update database
                cursor.execute("""
                    UPDATE coaches 
                    SET images = ? 
                    WHERE id = ?
                """, (json.dumps(images), coach_id))
                self.stats['coaches_with_images'] += 1
                print(f"   ✅ Downloaded {len(images)} images")
            else:
                self.stats['coaches_without_images'] += 1
                print(f"   ❌ No images found")
            
            # Progress indicator
            progress = (i + 1) / len(coaches) * 100
            print(f"   📊 Progress: {progress:.1f}%")
            
            # Be respectful to the server
            time.sleep(0.5)
            
            # Commit periodically
            if (i + 1) % 10 == 0:
                conn.commit()
                print(f"\n💾 Checkpoint: Saved progress for {i+1} coaches")
        
        conn.commit()
        conn.close()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 50)
        print(f"Total coaches processed: {self.stats['total_processed']}")
        print(f"Coaches with images: {self.stats['coaches_with_images']}")
        print(f"Coaches without images: {self.stats['coaches_without_images']}")
        print(f"Successful image downloads: {self.stats['successful_downloads']}")
        print(f"Failed image downloads: {self.stats['failed_downloads']}")
        
        if self.stats['coaches_with_images'] > 0:
            avg_images = self.stats['successful_downloads'] / self.stats['coaches_with_images']
            print(f"Average images per coach: {avg_images:.1f}")
        
        return self.stats

def main():
    downloader = EnhancedImageDownloader()
    
    print("🖼️  Enhanced PrevostGo Image Downloader")
    print("=" * 40)
    
    print("\n📌 Options:")
    print("1. Quick test (5 coaches)")
    print("2. Small batch (20 coaches)")
    print("3. Medium batch (50 coaches)")
    print("4. Large batch (100 coaches)")
    print("5. Process ALL remaining coaches")
    print("6. Re-process ALL coaches (including those with images)")
    
    choice = input("\n👉 Enter choice (1-6): ").strip()
    
    limits = {
        '1': 5,
        '2': 20,
        '3': 50,
        '4': 100,
        '5': None,
        '6': None
    }
    
    if choice in limits:
        limit = limits[choice]
        skip_existing = choice != '6'
        
        if choice in ['5', '6']:
            confirm = input(f"\n⚠️  This will process {'all remaining' if skip_existing else 'ALL'} coaches. Continue? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return
        
        print(f"\n🚀 Starting download process...")
        downloader.download_for_coaches(limit=limit, skip_existing=skip_existing)
        print("\n✅ Process complete! Check your frontend to see the images.")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
