"""
Initialize database with coach data
Run this on Railway to populate the database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper_final_v2 import PrevostScraper

def main():
    print("Initializing PrevostGO database...")
    
    scraper = PrevostScraper()
    
    # Scrape listings
    print("Scraping listings...")
    listings = scraper.scrape_listings()
    
    if listings:
        # Save to database
        print("Saving to database...")
        scraper.save_to_database(listings)
        
        # Fetch additional prices
        print("Fetching additional prices...")
        scraper.fetch_detail_prices(limit=30)
        
        # Show stats
        scraper.get_stats()
        
        print("\nDatabase initialization complete!")
    else:
        print("No listings found!")

if __name__ == "__main__":
    main()
