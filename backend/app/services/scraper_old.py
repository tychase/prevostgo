"""
PrevostGO Inventory Scraper Service - PostgreSQL Version
Direct integration with PostgreSQL database
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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.models.database import Coach, get_db, SessionLocal

# Debug: Check database configuration
import os
print(f"[SCRAPER] DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT SET')[:50] if os.getenv('DATABASE_URL') else 'NOT SET'}...")
print(f"[SCRAPER] Current working directory: {os.getcwd()}")

logger = logging.getLogger(__name__)

class PrevostInventoryScraper:
    """Scraper that works directly with PostgreSQL"""
    
    def __init__(self):
        self.base_url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
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
        
    async def scrape_inventory(self, fetch_details: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Scrape inventory from prevost-stuff.com"""
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
                        'scraped_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow(),
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
                    
                    img_tag = row.find('img')
                    if img_tag and img_tag.get('src'):
                        img_src = img_tag['src']
                        if not img_src.startswith('http'):
                            img_src = f"https://www.prevost-stuff.com/{img_src}"
                        coach['images'] = [img_src]
                    
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
                    
                    coach['id'] = self.generate_id(coach)
                    
                    listings.append(coach)
                    
                except Exception as e:
                    continue
                    
        print(f"\nScraped {len(listings)} total listings")
        
        available = [l for l in listings if l.get('status') == 'available']
        sold = [l for l in listings if l.get('status') == 'sold']
        with_prices = [l for l in available if l.get('price')]
        
        print(f"Available coaches: {len(available)}")
        print(f"Sold coaches: {len(sold)}")
        print(f"Available with prices: {len(with_prices)}")
        
        if limit:
            listings = listings[:limit]
            
        return listings
        
    async def save_to_database(self, listings: List[Dict]) -> int:
        """Save listings to PostgreSQL database"""
        if not listings:
            print("No listings to save")
            return 0
            
        saved_count = 0
        updated_count = 0
        
        # Use synchronous session for now due to async issues
        db = SessionLocal()
        
        # Debug: Check what database we're actually connected to
        from app.database import DATABASE_URL, engine
        print(f"[SCRAPER SAVE] DATABASE_URL: {DATABASE_URL[:50] if DATABASE_URL else 'None'}...")
        print(f"[SCRAPER SAVE] Engine URL: {engine.url}")
        print(f"[SCRAPER SAVE] Saving {len(listings)} coaches to database...")
        
        try:
            for coach_data in listings:
                try:
                    # Check if exists
                    existing = db.query(Coach).filter(Coach.id == coach_data['id']).first()
                    
                    if existing:
                        # Update existing
                        if existing.status != 'sold' or coach_data['status'] != existing.status:
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
                            updated_count += 1
                    else:
                        # Create new
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
                            inquiries=0
                        )
                        db.add(new_coach)
                        saved_count += 1
                        
                except Exception as e:
                    print(f"Error saving coach {coach_data.get('title')}: {e}")
                    continue
                    
            db.commit()
            
        except Exception as e:
            print(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
        print(f"\nDatabase update complete:")
        print(f"  - New coaches added: {saved_count}")
        print(f"  - Existing coaches updated: {updated_count}")
        
        return saved_count
