"""
PrevostGO Inventory Scraper Service
Wrapper around the working scraper_final_v2.py for FastAPI integration
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
import sys
import os

# Add parent directory to path to import scraper_final_v2
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scraper_final_v2 import PrevostScraper

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Coach, async_session

logger = logging.getLogger(__name__)

class PrevostInventoryScraper:
    """Wrapper class for the working PrevostScraper to integrate with FastAPI"""
    
    def __init__(self):
        self.scraper = PrevostScraper()
        
    async def scrape_inventory(self, fetch_details: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Async wrapper to run the synchronous scraper"""
        loop = asyncio.get_event_loop()
        
        # Run the scraper in a thread pool
        listings = await loop.run_in_executor(
            None,
            self._scrape_sync,
            fetch_details,
            limit
        )
        
        return listings
        
    def _scrape_sync(self, fetch_details: bool, limit: Optional[int]) -> List[Dict]:
        """Synchronous scraping method"""
        try:
            # Get listings from the main page
            listings = self.scraper.scrape_listings()
            
            # Apply limit if specified
            if limit:
                listings = listings[:limit]
                
            # If fetch_details is True, we could fetch additional details
            # but the main scraper already gets most info we need
            
            return listings
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []
            
    async def save_to_database(self, listings: List[Dict]) -> int:
        """Save listings to the async database"""
        saved_count = 0
        updated_count = 0
        
        async with async_session() as session:
            for listing_data in listings:
                try:
                    # Prepare data for database
                    coach_data = listing_data.copy()
                    
                    # Ensure datetime objects are properly formatted
                    if isinstance(coach_data.get('scraped_at'), str):
                        coach_data['scraped_at'] = datetime.fromisoformat(coach_data['scraped_at'].replace('Z', '+00:00'))
                    if isinstance(coach_data.get('updated_at'), str):
                        coach_data['updated_at'] = datetime.fromisoformat(coach_data['updated_at'].replace('Z', '+00:00'))
                    
                    # Ensure features and images are JSON strings
                    if isinstance(coach_data.get('features'), list):
                        coach_data['features'] = json.dumps(coach_data['features'])
                    if isinstance(coach_data.get('images'), list):
                        coach_data['images'] = json.dumps(coach_data['images'])
                    
                    # Check if coach exists
                    result = await session.execute(
                        select(Coach).where(Coach.id == coach_data['id'])
                    )
                    existing_coach = result.scalar_one_or_none()
                    
                    if existing_coach:
                        # Update existing coach
                        if existing_coach.status != 'sold' or coach_data['status'] != existing_coach.status:
                            for key, value in coach_data.items():
                                if hasattr(existing_coach, key):
                                    setattr(existing_coach, key, value)
                            updated_count += 1
                    else:
                        # Create new coach
                        coach = Coach(**coach_data)
                        session.add(coach)
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Error saving coach {listing_data.get('id')}: {str(e)}")
                    continue
                    
            await session.commit()
            
        logger.info(f"Saved {saved_count} new coaches, updated {updated_count} existing coaches")
        return saved_count
        
    async def run_initial_scrape(self):
        """Run initial scrape and save to database"""
        listings = await self.scrape_inventory(fetch_details=True)
        if listings:
            saved = await self.save_to_database(listings)
            
            # Also run the price fetching in the background
            # This updates the SQLite database directly
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.scraper.fetch_detail_prices,
                30  # Fetch prices for 30 coaches
            )
            
            return len(listings)
        return 0
        
    async def run_incremental_update(self):
        """Run incremental update"""
        return await self.run_initial_scrape()
