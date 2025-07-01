"""
PrevostGO Inventory Scraper Service
Synchronous version using requests (compatible with Python 3.13)
"""

import requests
import asyncio
from bs4 import BeautifulSoup
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.database import Coach, async_session
from app.models.schemas import CoachCreate

logger = logging.getLogger(__name__)

class PrevostInventoryScraper:
    """Scraper for Prevost coach inventory"""
    
    def __init__(self):
        self.base_url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
        self.headers = {
            'User-Agent': 'PrevostGO-Bot/1.0 (Compatible with FastAPI)'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Advertisement domains to avoid
        self.ad_domains = [
            'googleads.com', 'googlesyndication.com', 'doubleclick.net',
            'amazon-adsystem.com', 'facebook.com', 'adsrvr.org'
        ]
        
    def generate_listing_id(self, listing: Dict) -> str:
        """Generate unique ID for listing"""
        unique_string = f"{listing.get('year', '')}-{listing.get('converter', '')}-{listing.get('model', '')}-{listing.get('stock_number', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
    def is_advertisement(self, url: str) -> bool:
        """Check if URL is likely an advertisement"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for ad_domain in self.ad_domains:
            if ad_domain in domain:
                return True
                
        if any(pattern in url.lower() for pattern in ['banner', 'advertisement', 'sponsor']):
            return True
            
        return False
        
    def normalize_price(self, price_str: str) -> Tuple[Optional[int], str]:
        """Normalize price to cents and status"""
        if not price_str or price_str.strip() == '$':
            return None, 'contact_for_price'
            
        price_clean = re.sub(r'[$,]', '', price_str)
        
        try:
            price_dollars = int(price_clean)
            price_cents = price_dollars * 100  # Store in cents
            return price_cents, 'available'
        except:
            return None, 'contact_for_price'
            
    def parse_listing_block(self, block_text: str) -> Dict[str, any]:
        """Parse a single listing block"""
        listing = {
            'source': 'prevost-stuff.com',
            'scraped_at': datetime.utcnow(),
            'images': [],
            'features': [],
            'status': 'available'
        }
        
        # Extract title
        title_match = re.search(r'^(.*?)\]', block_text)
        if title_match:
            title = title_match.group(1).strip()
            listing['title'] = title
            
            # Parse year
            year_match = re.search(r'(\d{4})', title)
            if year_match:
                listing['year'] = int(year_match.group(1))
                
            # Extract converter
            converter_match = re.search(r'Prevost\s+(\w+)', title)
            if converter_match:
                listing['converter'] = converter_match.group(1)
                
        # Extract URL
        url_match = re.search(r'\((https://[^)]+)\)', block_text)
        if url_match:
            listing['listing_url'] = url_match.group(1)
            
        # Parse structured fields
        lines = block_text.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('Seller:'):
                listing['dealer_name'] = line.replace('Seller:', '').strip()
                
            elif line.startswith('Model:'):
                model = line.replace('Model:', '').strip()
                listing['model'] = model
                listing['chassis_type'] = model
                
            elif line.startswith('State:'):
                listing['dealer_state'] = line.replace('State:', '').strip()
                
            elif line.startswith('Price:'):
                price_str = line.replace('Price:', '').strip()
                listing['price'], listing['price_status'] = self.normalize_price(price_str)
                listing['price_display'] = price_str
                
            elif line.startswith('Slides:'):
                slides_str = line.replace('Slides:', '').strip()
                try:
                    listing['slide_count'] = int(slides_str) if slides_str.isdigit() else 0
                except:
                    listing['slide_count'] = 0
                    
        # Extract condition
        listing['condition'] = 'new' if '(new)' in block_text else 'pre-owned'
        
        # Add slide configuration to features
        if listing.get('slide_count', 0) > 0:
            slide_text = f"{listing['slide_count']} Slide{'s' if listing['slide_count'] > 1 else ''}"
            listing['features'].append(slide_text)
            
        # Generate ID
        listing['id'] = self.generate_listing_id(listing)
        
        return listing
        
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Error fetching {url}: Status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
            
    def fetch_listing_details(self, listing: Dict) -> Dict:
        """Fetch additional details from individual listing page"""
        if not listing.get('listing_url'):
            return listing
            
        html = self.fetch_url(listing['listing_url'])
        if not html:
            return listing
            
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Extract mileage
        mileage_match = re.search(r'([\d,]+)\s*Miles', text_content)
        if mileage_match:
            listing['mileage'] = int(mileage_match.group(1).replace(',', ''))
            
        # Extract engine
        engine_patterns = [
            r'(Volvo\s+\d+HP)',
            r'(Caterpillar\s+[^\n]+)',
            r'(Detroit\s+[^\n]+)',
            r'(\d+HP\s+[^\n]+)'
        ]
        for pattern in engine_patterns:
            engine_match = re.search(pattern, text_content, re.IGNORECASE)
            if engine_match:
                listing['engine'] = engine_match.group(1).strip()
                listing['features'].append(f"Engine: {listing['engine']}")
                break
                
        # Extract bathroom configuration
        if 'Bath and a Half' in text_content:
            listing['bathroom_config'] = 'Bath and a Half'
            listing['features'].append('Bath and a Half')
        elif 'Full Bath' in text_content:
            listing['bathroom_config'] = 'Full Bath'
            listing['features'].append('Full Bath')
            
        # Extract stock number
        stock_match = re.search(r'#(\d+)', text_content)
        if stock_match:
            listing['stock_number'] = stock_match.group(1)
            
        # Extract virtual tour
        if 'matterport.com' in text_content:
            tour_match = re.search(r'(https://[^\s]+matterport\.com[^\s]+)', text_content)
            if tour_match:
                listing['virtual_tour_url'] = tour_match.group(1)
                
        # Extract images
        for img in soup.find_all('img'):
            img_src = img.get('src', '')
            if img_src:
                img_url = urljoin(listing['listing_url'], img_src)
                
                if not self.is_advertisement(img_url):
                    if img.get('width'):
                        try:
                            width = int(img.get('width'))
                            if width < 100:
                                continue
                        except:
                            pass
                            
                    listing['images'].append(img_url)
                    
        # Extract dealer contact
        phone_match = re.search(r'(\d{3}-\d{3}-\d{4})', text_content)
        if phone_match:
            listing['dealer_phone'] = phone_match.group(1)
            
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text_content)
        if email_match:
            listing['dealer_email'] = email_match.group(0).lower()
            
        return listing
        
    def scrape_inventory_sync(self, fetch_details: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Synchronous method to scrape all inventory"""
        logger.info(f"Starting inventory scrape from {self.base_url}")
        
        # Fetch main page
        html = self.fetch_url(self.base_url)
        if not html:
            logger.error("Failed to fetch main listing page")
            return []
            
        # Parse listings
        listings = []
        listing_blocks = re.split(r'\n\s*\[', html)
        
        for i, block in enumerate(listing_blocks[1:]):
            if limit and i >= limit:
                break
                
            block = '[' + block
            listing = self.parse_listing_block(block)
            
            if listing.get('title') and listing.get('year'):
                logger.info(f"Parsed listing {i+1}: {listing.get('title')}")
                
                if fetch_details and listing.get('listing_url'):
                    listing = self.fetch_listing_details(listing)
                    # Rate limiting
                    import time
                    time.sleep(0.5)
                    
                listings.append(listing)
                
        logger.info(f"Scraped {len(listings)} listings successfully")
        return listings
        
    async def scrape_inventory(self, fetch_details: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Async wrapper for compatibility"""
        # Run synchronous scraping in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.scrape_inventory_sync, 
            fetch_details, 
            limit
        )
        
    async def save_to_database(self, listings: List[Dict]) -> int:
        """Save listings to database"""
        saved_count = 0
        
        async with async_session() as session:
            for listing_data in listings:
                try:
                    # Check if coach already exists
                    result = await session.execute(
                        select(Coach).where(Coach.id == listing_data['id'])
                    )
                    existing_coach = result.scalar_one_or_none()
                    
                    if existing_coach:
                        # Update existing coach
                        for key, value in listing_data.items():
                            if hasattr(existing_coach, key):
                                setattr(existing_coach, key, value)
                        existing_coach.updated_at = datetime.utcnow()
                    else:
                        # Create new coach
                        coach = Coach(**listing_data)
                        session.add(coach)
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Error saving coach {listing_data.get('id')}: {str(e)}")
                    continue
                    
            await session.commit()
            
        logger.info(f"Saved {saved_count} new coaches to database")
        return saved_count
        
    async def run_initial_scrape(self):
        """Run initial scrape and save to database"""
        listings = await self.scrape_inventory(fetch_details=True)
        if listings:
            await self.save_to_database(listings)
            return len(listings)
        return 0
        
    async def run_incremental_update(self):
        """Run incremental update (only new/changed listings)"""
        # For now, this is the same as initial scrape
        # In production, you'd implement logic to check for changes
        return await self.run_initial_scrape()
