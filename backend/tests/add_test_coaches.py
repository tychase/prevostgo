"""
Add test coaches to database for testing
"""
import sqlite3
import json
from datetime import datetime
import uuid

def add_test_coaches():
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    test_coaches = [
        {
            'id': str(uuid.uuid4()),
            'title': '2020 Prevost H3-45 Marathon Coach',
            'year': 2020,
            'model': 'H3-45',
            'chassis_type': 'Prevost',
            'converter': 'Marathon',
            'condition': 'pre-owned',
            'price': 150000000,  # $1.5M in cents
            'price_display': '$1,500,000',
            'price_status': 'available',
            'mileage': 25000,
            'engine': 'Volvo D13',
            'slide_count': 3,
            'features': json.dumps(['Aqua-Hot', 'Residential Refrigerator', 'Washer/Dryer']),
            'images': json.dumps(['https://example.com/coach1.jpg']),
            'dealer_name': 'Test Dealer',
            'dealer_state': 'FL',
            'listing_url': 'https://example.com/coach1',
            'source': 'test',
            'status': 'available',
            'scraped_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'views': 0,
            'inquiries': 0
        },
        {
            'id': str(uuid.uuid4()),
            'title': '2022 Prevost X3-45 Liberty Coach',
            'year': 2022,
            'model': 'X3-45',
            'chassis_type': 'Prevost',
            'converter': 'Liberty Coach',
            'condition': 'new',
            'price': 250000000,  # $2.5M in cents
            'price_display': '$2,500,000',
            'price_status': 'available',
            'mileage': 5000,
            'engine': 'Volvo D13',
            'slide_count': 4,
            'features': json.dumps(['Aqua-Hot', 'Fireplace', 'Outdoor Entertainment']),
            'images': json.dumps(['https://example.com/coach2.jpg']),
            'dealer_name': 'Test Dealer',
            'dealer_state': 'TX',
            'listing_url': 'https://example.com/coach2',
            'source': 'test',
            'status': 'available',
            'scraped_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'views': 0,
            'inquiries': 0
        },
        {
            'id': str(uuid.uuid4()),
            'title': '2019 Prevost H3-45 Millennium',
            'year': 2019,
            'model': 'H3-45',
            'chassis_type': 'Prevost',
            'converter': 'Millennium',
            'condition': 'pre-owned',
            'price': 120000000,  # $1.2M in cents
            'price_display': '$1,200,000',
            'price_status': 'available',
            'mileage': 35000,
            'engine': 'Volvo D13',
            'slide_count': 2,
            'features': json.dumps(['Bunk Beds', 'Office Space', 'Wine Cooler']),
            'images': json.dumps(['https://example.com/coach3.jpg']),
            'dealer_name': 'Test Dealer',
            'dealer_state': 'CA',
            'listing_url': 'https://example.com/coach3',
            'source': 'test',
            'status': 'available',
            'scraped_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'views': 0,
            'inquiries': 0
        }
    ]
    
    # Insert test coaches
    for coach in test_coaches:
        columns = ', '.join(coach.keys())
        placeholders = ', '.join(['?' for _ in coach])
        query = f"INSERT OR REPLACE INTO coaches ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(coach.values()))
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) as count FROM coaches WHERE source = 'test'")
    count = cursor.fetchone()[0]
    print(f"Added {count} test coaches to database")
    
    # Show the coaches
    cursor.execute("SELECT id, title, converter, price FROM coaches WHERE source = 'test'")
    coaches = cursor.fetchall()
    print("\nTest coaches added:")
    for coach in coaches:
        print(f"- {coach[1]} ({coach[2]}) - ${coach[3]/100:,.0f}")
    
    conn.close()

if __name__ == "__main__":
    add_test_coaches()
