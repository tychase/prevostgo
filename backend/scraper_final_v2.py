"""
Final Scraper for PrevostGO v2 - Fixed deprecation warnings and improved price fetching
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import re
import hashlib
from datetime import datetime, timezone
import time

class PrevostScraper:
    def __init__(self):
        self.base_url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_db(self):
        """Get database connection"""
        conn = sqlite3.connect('prevostgo.db')
        conn.row_factory = sqlite3.Row
        return conn
        
    def generate_id(self, coach):
        """Generate unique ID for coach"""
        unique_string = f"{coach.get('year', '')}-{coach.get('converter', '')}-{coach.get('model', '')}-{coach.get('title', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
    def parse_price(self, price_str):
        """Parse price string to cents and status"""
        if not price_str:
            return None, 'contact_for_price'
            
        # Clean the price string
        price_str = str(price_str).strip()
        
        # Check for sold status
        if 'sold' in price_str.lower():
            return None, 'sold'
        
        # Extract numeric price
        price_match = re.search(r'\$\s*([\d,]+)', price_str)
        if price_match:
            price_num = price_match.group(1).replace(',', '')
            try:
                price_dollars = int(price_num)
                # Sanity check - prices should be reasonable
                if 10000 < price_dollars < 5000000:  # Between $10k and $5M
                    return price_dollars * 100, 'available'  # Convert to cents
            except:
                pass
                
        return None, 'contact_for_price'
        
    def extract_features_from_title(self, title):
        """Extract features from the title"""
        features = []
        title_lower = title.lower()
        
        # Check for slide count
        slide_match = re.search(r'(single|double|triple|quad)\s+slide', title_lower)
        if slide_match:
            slide_type = slide_match.group(1)
            slide_map = {'single': 1, 'double': 2, 'triple': 3, 'quad': 4}
            if slide_type in slide_map:
                features.append(f"{slide_map[slide_type]} Slides")
        
        # Check for bunk coach
        if 'bunk' in title_lower:
            features.append("Bunk Coach")
            
        # Check for wheelchair accessible
        if 'hc acc' in title_lower or 'wheelchair' in title_lower:
            features.append("Wheelchair Accessible")
            
        return features
        
    def scrape_listings(self):
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
        
        # Find the main content table - it contains the listings
        # Look for tables that have links to individual coach pages
        all_tables = soup.find_all('table')
        
        for table in all_tables:
            # Look for table rows that contain coach listings
            for row in table.find_all('tr'):
                try:
                    # Check if this row has a link to a coach detail page
                    link_tag = row.find('a', href=lambda x: x and '.html' in x)
                    if not link_tag:
                        continue
                    
                    # Get the title from the link
                    title = link_tag.text.strip()
                    
                    # Skip if not a Prevost listing
                    if 'Prevost' not in title:
                        continue
                    
                    # Get the URL
                    listing_url = link_tag['href']
                    if not listing_url.startswith('http'):
                        listing_url = f"https://www.prevost-stuff.com/{listing_url}"
                    
                    # Initialize coach data
                    coach = {
                        'title': title,
                        'listing_url': listing_url,
                        'source': 'prevost-stuff.com',
                        'scraped_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'images': []
                    }
                    
                    # Extract year from title
                    year_match = re.search(r'(\d{4})', title)
                    if year_match:
                        coach['year'] = int(year_match.group(1))
                    
                    # Determine condition from title
                    if '(new)' in title:
                        coach['condition'] = 'new'
                        coach['status'] = 'available'
                    elif '(sold' in title.lower():
                        coach['condition'] = 'pre-owned'
                        coach['status'] = 'sold'
                    else:
                        coach['condition'] = 'pre-owned'
                        coach['status'] = 'available'
                    
                    # Extract features from title
                    coach['features'] = self.extract_features_from_title(title)
                    
                    # Find the details table within this row
                    details_table = row.find('table', {'cellpadding': '3'})
                    if details_table:
                        # Parse all the text content
                        details_text = details_table.get_text(separator='|', strip=True)
                        
                        # Parse individual fields
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
                                    # Add to features if not already there
                                    if coach['slide_count'] > 0:
                                        slide_feature = f"{coach['slide_count']} Slides"
                                        if slide_feature not in coach['features']:
                                            coach['features'].append(slide_feature)
                                except:
                                    coach['slide_count'] = 0
                    
                    # Find image if present
                    img_tag = row.find('img')
                    if img_tag and img_tag.get('src'):
                        img_src = img_tag['src']
                        if not img_src.startswith('http'):
                            img_src = f"https://www.prevost-stuff.com/{img_src}"
                        coach['images'] = [img_src]
                    
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
                    
                    listings.append(coach)
                    
                except Exception as e:
                    # Skip problematic rows
                    continue
                    
        print(f"\nScraped {len(listings)} total listings")
        
        # Filter and count
        available = [l for l in listings if l.get('status') == 'available']
        sold = [l for l in listings if l.get('status') == 'sold']
        with_prices = [l for l in available if l.get('price')]
        
        print(f"Available coaches: {len(available)}")
        print(f"Sold coaches: {len(sold)}")
        print(f"Available with prices: {len(with_prices)}")
        
        return listings
        
    def fetch_detail_prices(self, limit=50):
        """Fetch prices from individual detail pages for coaches without prices"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get coaches without prices that have valid URLs
        cursor.execute("""
            SELECT id, listing_url, title 
            FROM coaches 
            WHERE status = 'available'
            AND (price IS NULL OR price_status = 'contact_for_price') 
            AND listing_url != '' 
            AND listing_url != '#'
            AND listing_url LIKE '%.html'
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (limit,))
        
        coaches_to_update = cursor.fetchall()
        updated_count = 0
        
        print(f"\nFetching detail pages for {len(coaches_to_update)} coaches...")
        
        for i, coach in enumerate(coaches_to_update):
            try:
                print(f"{i+1}/{len(coaches_to_update)} - {coach['title'][:50]}...")
                response = requests.get(coach['listing_url'], headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for price patterns
                    price_patterns = [
                        r'Price:\s*\$\s*([\d,]+)',
                        r'Asking\s+Price:\s*\$\s*([\d,]+)',
                        r'\$\s*([\d,]+)(?:\s*USD)?',
                    ]
                    
                    found_price = False
                    for pattern in price_patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            price_str = match.replace(',', '')
                            if price_str.isdigit():
                                price = int(price_str)
                                # Sanity check
                                if 50000 < price < 5000000:  # Between $50k and $5M
                                    cursor.execute("""
                                        UPDATE coaches 
                                        SET price = ?, price_display = ?, price_status = ?, updated_at = ?
                                        WHERE id = ?
                                    """, (price * 100, f"${price:,}", 'available', 
                                         datetime.now(timezone.utc).isoformat(), coach['id']))
                                    updated_count += 1
                                    print(f"  ✓ Updated price to ${price:,}")
                                    found_price = True
                                    break
                        if found_price:
                            break
                    
                    if not found_price:
                        print(f"  - No valid price found")
                
                # Small delay to be respectful
                time.sleep(0.5)
                        
            except Exception as e:
                print(f"  ✗ Error: {e}")
                
        conn.commit()
        conn.close()
        
        print(f"\nUpdated {updated_count} prices from detail pages")
        return updated_count
        
    def save_to_database(self, listings):
        """Save listings to database"""
        if not listings:
            print("No listings to save")
            return
            
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Ensure table exists with all columns
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
                # Convert lists to JSON strings
                coach_data = coach.copy()
                coach_data['features'] = json.dumps(coach.get('features', []))
                coach_data['images'] = json.dumps(coach.get('images', []))
                
                # Check if exists
                cursor.execute("SELECT id, status FROM coaches WHERE id = ?", (coach['id'],))
                existing = cursor.fetchone()
                
                if existing:
                    # Only update if not sold or if status changed
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
                    # Insert new
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
        
    def get_stats(self):
        """Get statistics about the scraped data"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Total coaches
        cursor.execute("SELECT COUNT(*) as total FROM coaches")
        total = cursor.fetchone()['total']
        
        # Available coaches
        cursor.execute("SELECT COUNT(*) as available FROM coaches WHERE status = 'available'")
        available = cursor.fetchone()['available']
        
        # Coaches with prices
        cursor.execute("SELECT COUNT(*) as with_prices FROM coaches WHERE status = 'available' AND price IS NOT NULL")
        with_prices = cursor.fetchone()['with_prices']
        
        # Average price
        cursor.execute("SELECT AVG(price) as avg_price FROM coaches WHERE status = 'available' AND price IS NOT NULL")
        avg_price = cursor.fetchone()['avg_price']
        
        # Price range
        cursor.execute("SELECT MIN(price) as min_price, MAX(price) as max_price FROM coaches WHERE status = 'available' AND price IS NOT NULL")
        price_range = cursor.fetchone()
        
        # Coaches by converter (top 10)
        cursor.execute("""
            SELECT converter, COUNT(*) as count 
            FROM coaches 
            WHERE status = 'available'
            GROUP BY converter 
            ORDER BY count DESC 
            LIMIT 10
        """)
        converters = cursor.fetchall()
        
        # Coaches by year range
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN year >= 2020 THEN '2020+'
                    WHEN year >= 2015 THEN '2015-2019'
                    WHEN year >= 2010 THEN '2010-2014'
                    WHEN year >= 2005 THEN '2005-2009'
                    WHEN year >= 2000 THEN '2000-2004'
                    ELSE 'Pre-2000'
                END as year_range,
                COUNT(*) as count
            FROM coaches
            WHERE status = 'available' AND year > 0
            GROUP BY year_range
            ORDER BY year_range DESC
        """)
        year_ranges = cursor.fetchall()
        
        conn.close()
        
        print("\n" + "="*50)
        print("DATABASE STATISTICS")
        print("="*50)
        print(f"\nInventory Summary:")
        print(f"  Total coaches: {total}")
        print(f"  Available: {available}")
        print(f"  With prices: {with_prices} ({with_prices/available*100:.1f}% of available)")
        
        if avg_price:
            print(f"\nPricing:")
            print(f"  Average: ${int(avg_price/100):,}")
            if price_range['min_price'] and price_range['max_price']:
                print(f"  Range: ${int(price_range['min_price']/100):,} - ${int(price_range['max_price']/100):,}")
        
        print(f"\nTop Converters:")
        for conv in converters[:5]:
            print(f"  {conv['converter']}: {conv['count']} coaches")
            
        print(f"\nCoaches by Year:")
        for yr in year_ranges:
            print(f"  {yr['year_range']}: {yr['count']} coaches")

def main():
    """Run the scraper"""
    print("PrevostGO Scraper v2.0")
    print("=" * 50)
    
    scraper = PrevostScraper()
    
    # Step 1: Scrape main listings
    print("\nStep 1: Scraping main listings page...")
    listings = scraper.scrape_listings()
    
    if listings:
        # Step 2: Save to database
        print("\nStep 2: Saving to database...")
        scraper.save_to_database(listings)
        
        # Step 3: Fetch additional prices from detail pages
        print("\nStep 3: Fetching prices from detail pages...")
        # Fetch more prices since main page doesn't have them
        scraper.fetch_detail_prices(limit=50)
        
        # Step 4: Show statistics
        scraper.get_stats()
        
        print("\n✓ Scraping complete!")
    else:
        print("\n✗ No listings found.")

if __name__ == "__main__":
    main()
