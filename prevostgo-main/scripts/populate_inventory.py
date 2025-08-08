"""
Quick script to populate database with test coaches or run the scraper
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.scraper import PrevostInventoryScraper
import asyncio

async def main():
    print("🚀 Starting PrevostGO Inventory Scraper...")
    
    scraper = PrevostInventoryScraper()
    
    # Run the scraper
    print("📡 Fetching coaches from prevost-stuff.com...")
    listings = await scraper.scrape_inventory(fetch_details=True, limit=10)
    
    print(f"✅ Found {len(listings)} coaches")
    
    # Save to database
    saved_count = await scraper.save_to_database(listings)
    print(f"💾 Saved {saved_count} new coaches to database")
    
    # Show summary
    if listings:
        print("\n📊 Sample coaches:")
        for coach in listings[:3]:
            print(f"  - {coach.get('title', 'No title')}")
            print(f"    Price: {coach.get('price_display', 'Contact for price')}")
            print(f"    Converter: {coach.get('converter', 'Unknown')}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
