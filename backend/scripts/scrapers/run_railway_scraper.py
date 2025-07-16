"""
Run the Prevost inventory scraper and save to Railway PostgreSQL
"""

import os
import sys
import asyncio

# Set the DATABASE_URL for the scraper to use
if not os.getenv("DATABASE_URL"):
    print("❌ DATABASE_URL not set!")
    print("Set it first with: $env:DATABASE_URL = 'your-postgresql-url'")
    exit(1)

# Import and run the scraper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper import PrevostInventoryScraper

async def main():
    print("=== Running Prevost Inventory Scraper ===")
    print("This will scrape coaches from prevost-stuff.com and save to Railway PostgreSQL\n")
    
    scraper = PrevostInventoryScraper()
    
    try:
        # Scrape inventory
        print("📡 Scraping inventory from prevost-stuff.com...")
        listings = await scraper.scrape_inventory(fetch_details=True, limit=None)
        
        print(f"\n✅ Found {len(listings)} coaches")
        
        # Save to database
        if listings:
            print("\n💾 Saving to Railway PostgreSQL database...")
            saved_count = await scraper.save_to_database(listings)
            print(f"\n✅ Scraping complete! Added {saved_count} new coaches to database")
        else:
            print("\n⚠️  No coaches found to save")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
