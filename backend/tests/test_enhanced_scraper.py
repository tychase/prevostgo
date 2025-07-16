"""
Test the enhanced scraper locally
"""

import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for local testing
os.environ['DATABASE_URL'] = 'sqlite:///prevostgo.db'

from app.services.scraper_enhanced import EnhancedPrevostInventoryScraper


async def test_scraper():
    """Test the enhanced scraper with a small limit"""
    print("Testing Enhanced Scraper")
    print("=" * 50)
    
    scraper = EnhancedPrevostInventoryScraper()
    
    # Test with just 3 listings to see if it works
    print("\nFetching 3 listings with detailed images...")
    listings = await scraper.scrape_inventory(fetch_details=True, limit=3)
    
    if listings:
        print(f"\nFound {len(listings)} listings")
        
        # Display details for each listing
        for i, listing in enumerate(listings):
            print(f"\n{i+1}. {listing['title']}")
            print(f"   Status: {listing.get('status', 'N/A')}")
            print(f"   Price: {listing.get('price_display', 'N/A')}")
            print(f"   Images: {len(listing.get('images', []))} found")
            if listing.get('images'):
                print(f"   Sample images:")
                for img in listing['images'][:3]:
                    print(f"     - {img}")
            print(f"   Features: {', '.join(listing.get('features', []))}")
            if listing.get('mileage'):
                print(f"   Mileage: {listing['mileage']:,} miles")
            if listing.get('engine'):
                print(f"   Engine: {listing['engine']}")
        
        # Save to database
        print("\nSaving to database...")
        saved = await scraper.save_to_database(listings)
        print(f"Saved/updated {saved} records")
    else:
        print("No listings found!")


if __name__ == "__main__":
    asyncio.run(test_scraper())