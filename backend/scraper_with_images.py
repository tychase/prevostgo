"""
Enhanced Scraper with Local Image Download
Downloads images and saves them locally with coach IDs
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import re
import hashlib
from datetime import datetime, timezone
import time
import os
from urllib.parse import urljoin, urlparse

class PrevostScraperWithImages:
    def __init__(self):
        self.base_url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Create images directory structure
        self.images_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'coach-images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Also create a directory in the backend for reference
        self.backend_images_dir = os.path.join(os.path.dirname(__file__), 'coach-images')
        os.makedirs(self.backend_images_dir, exist_ok=True)
        
        print(f"Images will be saved to: {self.images_dir}")
        
    def get_db(self):
        """Get database connection"""
        conn = sqlite3.connect('prevostgo.db')
        conn.row_factory = sqlite3.Row
        return conn
        
    def generate_id(self, coach):
        """Generate unique ID for coach"""
        unique_string = f"{coach.get('year', '')}-{coach.get('converter', '')}-{coach.get('model', '')}-{coach.get('title', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
    def download_image(self, img_url, coach_id, image_index=0):
        """Download image and save locally with coach ID"""
        try:
            # Make image URL absolute
            if not img_url.startswith('http'):
                img_url = urljoin('https://www.prevost-stuff.com/', img_url)
            
            print(f"  Downloading image from: {img_url}")
            
            response = requests.get(img_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # Determine file extension
                content_type = response.headers.get('content-type', '').lower()
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    # Try to get from URL
                    ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                
                # Create filename with coach ID
                filename = f"{coach_id}_{image_index}{ext}"
                filepath = os.path.join(self.images_dir, filename)
                
                # Save the image
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"  ✓ Saved as: {filename}")
                
                # Return the public URL path (relative to frontend public directory)
                return f"/coach-images/{filename}"
            else:
                print(f"  ✗ Failed to download (status: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"  ✗ Error downloading image: {e}")
            return None
            
    def scrape_coach_detail_page(self, url, coach_id):
        """Scrape individual coach page for more images"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            images = []
            
            # Look for all images on the detail page
            img_tags = soup.find_all('img')
            for i, img in enumerate(img_tags):
                src = img.get('src', '')
                # Filter for relevant images (skip navigation, logos, etc.)
                if src and any(keyword in src.lower() for keyword in ['coach', 'prevost', 'forsale', coach_id[:6]]):
                    local_path = self.download_image(src, coach_id, i)
                    if local_path:
                        images.append(local_path)
                        
                    # Limit to 5 images per coach
                    if len(images) >= 5:
                        break
                        
            return images
            
        except Exception as e:
            print(f"  Error scraping detail page: {e}")
            return []
        
    def parse_price(self, price_str):
        """Parse price string to cents and status"""
        if not price_str:
            return None, 'contact_for_price'
            
        price_str = str(price_str).strip()
        
        if 'sold' in price_str.lower():
            return None, 'sold'
        
        price_match = re.search(r'\$\s*([\d,]+)', price_str)
        if price_match:
            price_num = price_match.group(1).replace(',', '')
            try:
                price_dollars = int(price_num)
                if 10000 < price_dollars < 5000000:
                    return price_dollars * 100, 'available'
            except:
                pass
                
        return None, 'contact_for_price'
        
    def extract_features_from_title(self, title):
        """Extract features from the title"""
        features = []
        title_lower = title.lower()
        
        slide_match = re.search(r'(single|double|triple|quad)\s+slide', title_lower)
        if slide_match:
            slide_type = slide_match.group(1)
            slide_map = {'single': 1, 'double': 2, 'triple': 3, 'quad': 4}
            if slide_type in slide_map:
                features.append(f"{slide_map[slide_type]} Slides")
        
        if 'bunk' in title_lower:
            features.append("Bunk Coach")
            
        if 'hc acc' in title_lower or 'wheelchair' in title_lower:
            features.append("Wheelchair Accessible")
            
        return features
        
    def scrape_listings(self, download_images=True, limit=None):
        """Scrape the main listing page"""
        print("Fetching listings from prevost-stuff.com...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            print(f"Successfully fetched page (status: {response.status_code})")
        except Exception as e:
            print(f"Error fetching page: {e}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        
        all_tables = soup.find_all('table')
        
        for table in all_tables:
            for row in table.find_all('tr'):
                try:
                    link_tag = row.find('a', href=lambda x: x and '.html' in x)
                    if not link_tag:
                        continue
                    
                    title = link_tag.text.strip()
                    
                    if 'Prevost' not in title:
                        continue
                    
                    listing_url = link_tag['href']
                    if not listing_url.startswith('http'):
                        listing_url = f"https://www.prevost-stuff.com/{listing_url}"
                    
                    coach = {
                        'title': title,
                        'listing_url': listing_url,
                        'source': 'prevost-stuff.com',
                        'scraped_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'images': []
                    }
                    
                    year_match = re.search(r'(\d{4})', title)
                    if year_match:
                        coach['year'] = int(year_match.group(1))
                    
                    if '(new)' in title:
                        coach['condition'] = 'new'
                        coach['status'] = 'available'
                    elif '(sold' in title.lower():
                        coach['condition'] = 'pre-owned'
                        coach['status'] = 'sold'
                    else:
                        coach['condition'] = 'pre-owned'
                        coach['status'] = 'available'
                    
                    coach['features'] = self.extract_features_from_title(title)
                    
                    # Parse details
                    details_table = row.find('table', {'cellpadding': '3'})
                    if details_table:
                        details_text = details_table.get_text(separator='|', strip=True)
                        
                        for field in details_text.split('|'):
                            field = field.strip()
                            
                            if field.startswith('Seller:'):
                                coach['dealer_name'] = field.replace('Seller:', '').strip()
                            elif field.startswith('Model:'):
                                coach['model'] = field.replace('Model:', '').strip()
                            elif field.startswith('Year:') and 'year' not in coach:
                                try:
                                    coach['year'] = int(field.replace('Year:', '').strip())
                                except:
                                    pass
                            elif field.startswith('State:'):
                                coach['dealer_state'] = field.replace('State:', '').strip()
                            elif field.startswith('Price:'):
                                price_text = field.replace('Price:', '').strip()
                                coach['price'], price_status = self.parse_price(price_text)
                                if coach['status'] != 'sold':
                                    coach['price_status'] = price_status
                                else:
                                    coach['price_status'] = 'sold'
                                coach['price_display'] = price_text if price_text and price_text != '$' else 'Contact for Price'
                            elif field.startswith('Converter:'):
                                coach['converter'] = field.replace('Converter:', '').strip()
                            elif field.startswith('Slides:'):
                                slides_str = field.replace('Slides:', '').strip()
                                try:
                                    coach['slide_count'] = int(slides_str) if slides_str.isdigit() else 0
                                    if coach['slide_count'] > 0:
                                        slide_feature = f"{coach['slide_count']} Slides"
                                        if slide_feature not in coach['features']:
                                            coach['features'].append(slide_feature)
                                except:
                                    coach['slide_count'] = 0
                    
                    # Set defaults
                    coach.setdefault('dealer_name', 'Unknown')
                    coach.setdefault('model', 'Unknown')
                    coach.setdefault('year', 0)
                    coach.setdefault('dealer_state', 'Unknown')
                    coach.setdefault('price', None)
                    coach.setdefault('price_display', 'Contact for Price')
                    coach.setdefault('price_status', 'contact_for_price')
                    coach.setdefault('converter', 'Unknown')
                    coach.setdefault('slide_count', 0)
                    coach.setdefault('chassis_type', coach.get('model', 'Unknown'))
                    
                    # Generate ID
                    coach['id'] = self.generate_id(coach)
                    
                    # Download images if enabled
                    if download_images and coach['status'] == 'available':
                        print(f"\nProcessing images for: {coach['title'][:60]}...")
                        
                        # First, try to download the main image from the listing
                        img_tag = row.find('img')
                        if img_tag and img_tag.get('src'):
                            img_src = img_tag['src']
                            local_path = self.download_image(img_src, coach['id'], 0)
                            if local_path:
                                coach['images'].append(local_path)
                        
                        # Then try to get more images from the detail page
                        if coach['listing_url'] and '.html' in coach['listing_url']:
                            detail_images = self.scrape_coach_detail_page(coach['listing_url'], coach['id'])
                            coach['images'].extend(detail_images)
                            
                        # Small delay between downloads
                        time.sleep(0.5)
                    
                    listings.append(coach)
                    
                    # Apply limit if specified
                    if limit and len(listings) >= limit:
                        break
                        
                except Exception as e:
                    continue
                    
            if limit and len(listings) >= limit:
                break
                
        print(f"\nScraped {len(listings)} total listings")
        
        available = [l for l in listings if l.get('status') == 'available']
        sold = [l for l in listings if l.get('status') == 'sold']
        with_prices = [l for l in available if l.get('price')]
        with_images = [l for l in available if l.get('images')]
        
        print(f"Available coaches: {len(available)}")
        print(f"Sold coaches: {len(sold)}")
        print(f"Available with prices: {len(with_prices)}")
        print(f"Available with images: {len(with_images)}")
        
        return listings
        
    def save_to_database(self, listings):
        """Save listings to database"""
        if not listings:
            print("No listings to save")
            return
            
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coaches (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                year INTEGER,
                model TEXT,
                chassis_type TEXT,
                converter TEXT,
                condition TEXT,
                price INTEGER,
                price_display TEXT,
                price_status TEXT,
                mileage INTEGER,
                engine TEXT,
                slide_count INTEGER DEFAULT 0,
                features TEXT DEFAULT '[]',
                bathroom_config TEXT,
                stock_number TEXT,
                images TEXT DEFAULT '[]',
                virtual_tour_url TEXT,
                dealer_name TEXT,
                dealer_state TEXT,
                dealer_phone TEXT,
                dealer_email TEXT,
                listing_url TEXT,
                source TEXT DEFAULT 'prevost-stuff.com',
                status TEXT DEFAULT 'available',
                scraped_at TEXT,
                updated_at TEXT,
                views INTEGER DEFAULT 0,
                inquiries INTEGER DEFAULT 0
            )
        """)
        
        saved = 0
        updated = 0
        
        for coach in listings:
            try:
                coach_data = coach.copy()
                coach_data['features'] = json.dumps(coach.get('features', []))
                coach_data['images'] = json.dumps(coach.get('images', []))
                
                cursor.execute("SELECT id, status FROM coaches WHERE id = ?", (coach['id'],))
                existing = cursor.fetchone()
                
                if existing:
                    if existing['status'] != 'sold' or coach['status'] != existing['status']:
                        cursor.execute("""
                            UPDATE coaches SET 
                            title = ?, price = ?, price_display = ?,
                            price_status = ?, status = ?, 
                            scraped_at = ?, updated_at = ?,
                            listing_url = ?, images = ?, features = ?,
                            slide_count = ?
                            WHERE id = ?
                        """, (
                            coach_data['title'], coach_data['price'], 
                            coach_data['price_display'], coach_data['price_status'],
                            coach_data['status'], coach_data['scraped_at'], 
                            coach_data['updated_at'], coach_data.get('listing_url', ''),
                            coach_data['images'], coach_data['features'],
                            coach_data.get('slide_count', 0),
                            coach_data['id']
                        ))
                        updated += 1
                else:
                    cursor.execute("""
                        INSERT INTO coaches 
                        (id, title, year, model, converter, condition, price, price_display,
                         price_status, slide_count, dealer_name, dealer_state, source, 
                         status, scraped_at, updated_at, features, images, listing_url, chassis_type)
                        VALUES 
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        coach_data['id'], coach_data['title'], coach_data.get('year', 0),
                        coach_data.get('model', ''), coach_data.get('converter', ''), 
                        coach_data['condition'], coach_data['price'], coach_data['price_display'], 
                        coach_data['price_status'], coach_data.get('slide_count', 0), 
                        coach_data.get('dealer_name', ''), coach_data.get('dealer_state', ''),
                        coach_data['source'], coach_data['status'], coach_data['scraped_at'],
                        coach_data['updated_at'], coach_data['features'], coach_data['images'],
                        coach_data.get('listing_url', ''), coach_data.get('chassis_type', '')
                    ))
                    saved += 1
                    
            except Exception as e:
                print(f"Error saving coach {coach.get('title')}: {e}")
                continue
                
        conn.commit()
        conn.close()
        
        print(f"\nDatabase update complete:")
        print(f"  - New coaches added: {saved}")
        print(f"  - Existing coaches updated: {updated}")

def main():
    """Run the enhanced scraper"""
    print("PrevostGO Enhanced Scraper with Image Download")
    print("=" * 50)
    
    scraper = PrevostScraperWithImages()
    
    # Ask user for options
    print("\nOptions:")
    print("1. Scrape with image download (slower but complete)")
    print("2. Scrape without images (faster)")
    print("3. Test with 10 coaches only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        listings = scraper.scrape_listings(download_images=True)
    elif choice == '2':
        listings = scraper.scrape_listings(download_images=False)
    elif choice == '3':
        listings = scraper.scrape_listings(download_images=True, limit=10)
    else:
        print("Invalid choice")
        return
    
    if listings:
        print("\nSaving to database...")
        scraper.save_to_database(listings)
        print("\n✓ Scraping complete!")
        
        # Show where images are saved
        print(f"\nImages saved to: {scraper.images_dir}")
        print("Images are accessible at: /coach-images/[coach_id]_[index].jpg")
    else:
        print("\n✗ No listings found.")

if __name__ == "__main__":
    main()
