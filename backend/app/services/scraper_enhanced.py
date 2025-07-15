"""
Enhanced PrevostGO Inventory Scraper Service with Detail Page Fetching
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re
import hashlib
import requests
from bs4 import BeautifulSoup
import time
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

logger = logging.getLogger(__name__)

class EnhancedPrevostInventoryScraper:
    """Enhanced scraper that fetches all images from detail pages"""
    
    def __init__(self):
        self.base_url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_database_session(self):
        """Get a database session with proper configuration"""
        database_url = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")
        
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            
        print(f"[SCRAPER] Connecting to database: {database_url[:50]}...")
        
        if "sqlite" in database_url:
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(database_url)
            
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal(), engine
        
    def generate_id(self, coach):
        """Generate unique ID for coach"""
        unique_string = f"{coach.get('year', '')}-{coach.get('converter', '')}-{coach.get('model', '')}-{coach.get('title', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
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
        
    def is_valid_coach_listing(self, title, url):
        """Check if this is a real coach listing"""
        skip_patterns = [
            'Coach_Dealers.html',
            'index.html',
            'about.html',
            'contact.html',
            'services.html'
        ]
        
        for pattern in skip_patterns:
            if pattern in url:
                return False
                
        if not re.search(r'19\d{2}|20\d{2}', title + url):
            return False
            
        if 'Prevost' not in title:
            return False
            
        if title.strip() == 'Prevost':
            return False
            
        return True
        
    def fetch_listing_details(self, listing_url):
        """Fetch detailed information including all images from listing page"""
        try:
            print(f"  Fetching details from: {listing_url}")
            response = requests.get(listing_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            details = {
                'images': [],
                'description': '',
                'additional_info': {},
                'price_info': None
            }
            
            # Extract price from detail page
            text = soup.get_text()
            price_patterns = [
                r'Price:\s*\$\s*([\d,]+)',
                r'Asking\s+Price:\s*\$\s*([\d,]+)',
                r'\$\s*([\d,]+)(?:\s*USD)?',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    price_str = match.replace(',', '')
                    if price_str.isdigit():
                        price = int(price_str)
                        if 50000 < price < 5000000:  # Between $50k and $5M
                            details['price_info'] = {
                                'price': price * 100,  # Convert to cents
                                'price_display': f"${price:,}",
                                'price_status': 'available'
                            }
                            break
                if details['price_info']:
                    break
            
            # Find all images
            seen_images = set()
            
            # Look for image tags
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src:
                    # Skip thumbnails, logos, icons
                    if any(skip in src.lower() for skip in ['thumb', 'logo', 'icon', 'banner', 'button', 'spacer']):
                        continue
                    
                    # Make URL absolute
                    if not src.startswith('http'):
                        src = f"https://www.prevost-stuff.com/{src.lstrip('/')}"
                    
                    # Check if it's likely a coach image
                    if any(pattern in src.lower() for pattern in ['.jpg', '.jpeg', '.png']) and src not in seen_images:
                        details['images'].append(src)
                        seen_images.add(src)
            
            # Also check for links to full-size images
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    if not href.startswith('http'):
                        href = f"https://www.prevost-stuff.com/{href.lstrip('/')}"
                    if href not in seen_images:
                        details['images'].append(href)
                        seen_images.add(href)
            
            # Extract description - look for main content blocks
            content_blocks = soup.find_all(['div', 'td'], text=re.compile(r'.{100,}'))
            for block in content_blocks:
                text = block.get_text(strip=True)
                if not any(skip in text.lower() for skip in ['copyright', 'all rights reserved', 'privacy policy', 'navigation']):
                    if len(text) > len(details['description']):
                        details['description'] = text
            
            # Extract additional info from tables
            for table in soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map common fields
                        if 'mileage' in label and value:
                            mileage_match = re.search(r'([\d,]+)', value)
                            if mileage_match:
                                details['additional_info']['mileage'] = int(mileage_match.group(1).replace(',', ''))
                        elif 'engine' in label:
                            details['additional_info']['engine'] = value
                        elif 'transmission' in label:
                            details['additional_info']['transmission'] = value
                        elif 'length' in label:
                            details['additional_info']['length'] = value
                        elif 'vin' in label:
                            details['additional_info']['vin'] = value
            
            print(f"    Found {len(details['images'])} images")
            return details
            
        except Exception as e:
            print(f"    Error fetching details: {e}")
            return None
        
    async def scrape_inventory(self, fetch_details: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Scrape inventory from prevost-stuff.com with enhanced detail fetching"""
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
                    listing_url = link_tag['href']
                    
                    if not listing_url.startswith('http'):
                        listing_url = f"https://www.prevost-stuff.com/{listing_url}"
                    
                    if not self.is_valid_coach_listing(title, listing_url):
                        continue
                    
                    coach = {
                        'title': title,
                        'listing_url': listing_url,
                        'source': 'prevost-stuff.com',
                        'scraped_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow(),
                        'images': []
                    }
                    
                    # Extract year from title or URL
                    year_match = re.search(r'(19\d{2}|20\d{2})', title + listing_url)
                    if year_match:
                        coach['year'] = int(year_match.group(1))
                    else:
                        coach['year'] = 0
                        continue
                    
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
                    
                    # Parse listing page info
                    details_table = row.find('table', {'cellpadding': '3'})
                    if details_table:
                        details_text = details_table.get_text(separator='|', strip=True)
                        
                        for field in details_text.split('|'):
                            field = field.strip()
                            
                            if field.startswith('Seller:'):
                                coach['dealer_name'] = field.replace('Seller:', '').strip()
                            elif field.startswith('Model:'):
                                coach['model'] = field.replace('Model:', '').strip()
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
                    
                    # Get thumbnail from listing page
                    img_tag = row.find('img')
                    if img_tag and img_tag.get('src'):
                        img_src = img_tag['src']
                        if not img_src.startswith('http'):
                            img_src = f"https://www.prevost-stuff.com/{img_src}"
                        if 'logo' not in img_src.lower():
                            coach['images'] = [img_src]
                    
                    # Set defaults
                    coach.setdefault('dealer_name', 'Unknown')
                    coach.setdefault('model', 'Unknown')
                    coach.setdefault('dealer_state', 'Unknown')
                    coach.setdefault('price', None)
                    coach.setdefault('price_display', 'Contact for Price')
                    coach.setdefault('price_status', 'contact_for_price')
                    coach.setdefault('converter', 'Unknown')
                    coach.setdefault('slide_count', 0)
                    coach.setdefault('chassis_type', coach.get('model', 'Unknown'))
                    
                    coach['id'] = self.generate_id(coach)
                    
                    listings.append(coach)
                    
                except Exception as e:
                    continue
                    
        print(f"\nScraped {len(listings)} total listings")
        
        # Fetch details for each listing if enabled
        if fetch_details:
            print("\nFetching detail pages for all listings...")
            for i, coach in enumerate(listings):
                if coach['status'] == 'available' and coach.get('listing_url'):
                    print(f"\n{i+1}/{len(listings)} - {coach['title'][:50]}...")
                    details = self.fetch_listing_details(coach['listing_url'])
                    
                    if details:
                        # Update images
                        if details['images']:
                            coach['images'] = details['images']
                        
                        # Update price if found
                        if details['price_info'] and not coach.get('price'):
                            coach['price'] = details['price_info']['price']
                            coach['price_display'] = details['price_info']['price_display']
                            coach['price_status'] = details['price_info']['price_status']
                        
                        # Add additional info
                        if details['additional_info'].get('mileage'):
                            coach['mileage'] = details['additional_info']['mileage']
                        if details['additional_info'].get('engine'):
                            coach['engine'] = details['additional_info']['engine']
                        
                        # Add description to features if meaningful
                        if details['description'] and len(details['description']) > 200:
                            coach['description'] = details['description'][:1000]  # Limit length
                    
                    # Be respectful with delay
                    time.sleep(0.5)
                    
                    if limit and i >= limit:
                        break
        
        available = [l for l in listings if l.get('status') == 'available']
        sold = [l for l in listings if l.get('status') == 'sold']
        with_prices = [l for l in available if l.get('price')]
        
        print(f"\nFinal stats:")
        print(f"Available coaches: {len(available)}")
        print(f"Sold coaches: {len(sold)}")
        print(f"Available with prices: {len(with_prices)}")
        
        return listings
        
    async def save_to_database(self, listings: List[Dict]) -> int:
        """Save listings to PostgreSQL database"""
        if not listings:
            print("No listings to save")
            return 0
            
        saved_count = 0
        updated_count = 0
        
        db, engine = self.get_database_session()
        
        from app.models.database import Coach
        
        try:
            from app.database import Base
            Base.metadata.create_all(bind=engine)
            
            # Clean up invalid entries first
            bad_coaches = db.query(Coach).filter(
                and_(
                    Coach.title == 'Prevost',
                    Coach.year == 0
                )
            ).all()
            
            if bad_coaches:
                print(f"[CLEANUP] Removing {len(bad_coaches)} invalid coach entries...")
                for bad_coach in bad_coaches:
                    db.delete(bad_coach)
                db.commit()
            
            for coach_data in listings:
                try:
                    existing = db.query(Coach).filter(Coach.id == coach_data['id']).first()
                    
                    if existing:
                        # Update if not sold or if status changed or if we have more images
                        if (existing.status != 'sold' or coach_data['status'] != existing.status or 
                            len(coach_data.get('images', [])) > len(existing.images or [])):
                            
                            existing.title = coach_data['title']
                            existing.price = coach_data.get('price')
                            existing.price_display = coach_data.get('price_display')
                            existing.price_status = coach_data.get('price_status')
                            existing.status = coach_data.get('status')
                            existing.scraped_at = coach_data.get('scraped_at')
                            existing.updated_at = coach_data.get('updated_at')
                            existing.listing_url = coach_data.get('listing_url')
                            existing.images = coach_data.get('images', [])
                            existing.features = coach_data.get('features', [])
                            existing.slide_count = coach_data.get('slide_count', 0)
                            
                            # Update additional fields if present
                            if 'mileage' in coach_data:
                                existing.mileage = coach_data['mileage']
                            if 'engine' in coach_data:
                                existing.engine = coach_data['engine']
                            if 'description' in coach_data:
                                existing.description = coach_data['description']
                            
                            updated_count += 1
                    else:
                        # Insert new
                        new_coach = Coach(
                            id=coach_data['id'],
                            title=coach_data['title'],
                            year=coach_data.get('year', 0),
                            model=coach_data.get('model', ''),
                            chassis_type=coach_data.get('chassis_type', ''),
                            converter=coach_data.get('converter', ''),
                            condition=coach_data.get('condition', 'pre-owned'),
                            price=coach_data.get('price'),
                            price_display=coach_data.get('price_display'),
                            price_status=coach_data.get('price_status', 'contact_for_price'),
                            slide_count=coach_data.get('slide_count', 0),
                            features=coach_data.get('features', []),
                            images=coach_data.get('images', []),
                            dealer_name=coach_data.get('dealer_name', ''),
                            dealer_state=coach_data.get('dealer_state', ''),
                            listing_url=coach_data.get('listing_url', ''),
                            source=coach_data.get('source', 'prevost-stuff.com'),
                            status=coach_data.get('status', 'available'),
                            scraped_at=coach_data.get('scraped_at'),
                            updated_at=coach_data.get('updated_at'),
                            views=0,
                            inquiries=0,
                            mileage=coach_data.get('mileage'),
                            engine=coach_data.get('engine'),
                            description=coach_data.get('description')
                        )
                        db.add(new_coach)
                        saved_count += 1
                        
                except Exception as e:
                    print(f"Error saving coach {coach_data.get('title')}: {e}")
                    continue
                    
            db.commit()
            
            total_coaches = db.query(Coach).count()
            available_coaches = db.query(Coach).filter(Coach.status == 'available').count()
            print(f"\n[VERIFY] Total coaches in database: {total_coaches}")
            print(f"[VERIFY] Available coaches: {available_coaches}")
            
        except Exception as e:
            print(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
        print(f"\nDatabase update complete:")
        print(f"  - New coaches added: {saved_count}")
        print(f"  - Existing coaches updated: {updated_count}")
        
        return saved_count + updated_count


async def run_enhanced_scraper(limit: Optional[int] = None):
    """Run the enhanced scraper"""
    print("Running Enhanced PrevostGO Scraper")
    print("=" * 50)
    
    scraper = EnhancedPrevostInventoryScraper()
    
    # Scrape with detail fetching enabled
    listings = await scraper.scrape_inventory(fetch_details=True, limit=limit)
    
    if listings:
        # Save to database
        await scraper.save_to_database(listings)
        print("\n✓ Enhanced scraping complete!")
    else:
        print("\n✗ No listings found.")


if __name__ == "__main__":
    asyncio.run(run_enhanced_scraper())