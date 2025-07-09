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
from app.models.database import Coach, get_db

# Import SessionLocal and use it synchronously since we're having async issues
from app.database import SessionLocal

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
        """Save listings to database using sync operations"""
        # Run the synchronous save in an executor
        loop = asyncio.get_event_loop()
        saved_count = await loop.run_in_executor(
            None,
            self._save_to_database_sync,
            listings
        )
        return saved_count
        
    def _save_to_database_sync(self, listings: List[Dict]) -> int:
        """Synchronous database save"""
        saved_count = 0
        updated_count = 0
        
        # Use the original scraper's save method which works
        self.scraper.save_to_database(listings)
        
        # Count how many were saved
        for listing in listings:
            saved_count += 1
            
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
