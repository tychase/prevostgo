"""
Simple scraper for Prevost coaches - with duplicate handling
"""

import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
import re
import hashlib
from datetime import datetime
import json

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL environment variable not set!")
    print("Set it with: $env:DATABASE_URL = 'your-postgresql-public-url'")
    exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def generate_coach_id(year, converter, model, title, index=0):
    """Generate unique ID for a coach"""
    # Include index to handle duplicates
    unique_string = f"{year}-{converter}-{model}-{title}-{index}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

def parse_price(price_str):
    """Extract price in cents from price string"""
    if not price_str or price_str.strip() == '':
        return None
    
    # Look for dollar amounts
    price_match = re.search(r'\$\s*([\d,]+)', price_str)
    if price_match:
        price_num = price_match.group(1).replace(',', '')
        try:
            return int(price_num) * 100  # Convert to cents
        except:
            pass
    return None

def scrape_coaches():
    """Scrape coaches from prevost-stuff.com"""
    print("🌐 Fetching coaches from prevost-stuff.com...")
    
    url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    coaches = []
    seen_ids = set()
    
    # Find all coach listings
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            link = row.find('a', href=lambda x: x and '.html' in x)
            if not link:
                continue
                
            title = link.text.strip()
            
            # Skip non-coach pages
            if 'Prevost' not in title or title == 'Prevost':
                continue
                
            # Extract year
            year_match = re.search(r'(19\d{2}|20\d{2})', title)
            if not year_match:
                continue
                
            coach = {
                'title': title,
                'year': int(year_match.group(1)),
                'listing_url': f"https://www.prevost-stuff.com/{link['href']}" if not link['href'].startswith('http') else link['href'],
                'condition': 'new' if '(new)' in title.lower() else 'pre-owned',
                'status': 'sold' if 'sold' in title.lower() else 'available',
                'source': 'prevost-stuff.com',
                'features': [],
                'images': []
            }
            
            # Extract details from the listing
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
                        coach['price'] = parse_price(price_text)
                        coach['price_display'] = price_text if price_text else 'Contact for Price'
                    elif field.startswith('Converter:'):
                        coach['converter'] = field.replace('Converter:', '').strip()
                    elif field.startswith('Slides:'):
                        try:
                            coach['slide_count'] = int(field.replace('Slides:', '').strip())
                        except:
                            coach['slide_count'] = 0
            
            # Get image if available
            img = row.find('img')
            if img and img.get('src'):
                img_url = img['src']
                if not img_url.startswith('http'):
                    img_url = f"https://www.prevost-stuff.com/{img_url}"
                if 'logo' not in img_url.lower():
                    coach['images'] = [img_url]
            
            # Set defaults
            coach['dealer_name'] = coach.get('dealer_name', 'Unknown')
            coach['model'] = coach.get('model', 'Unknown')
            coach['dealer_state'] = coach.get('dealer_state', 'Unknown')
            coach['converter'] = coach.get('converter', 'Unknown')
            coach['slide_count'] = coach.get('slide_count', 0)
            coach['price_display'] = coach.get('price_display', 'Contact for Price')
            
            # Generate unique ID
            index = 0
            while True:
                coach_id = generate_coach_id(
                    coach['year'], 
                    coach['converter'], 
                    coach['model'], 
                    coach['title'],
                    index
                )
                if coach_id not in seen_ids:
                    coach['id'] = coach_id
                    seen_ids.add(coach_id)
                    break
                index += 1
            
            coaches.append(coach)
    
    print(f"✅ Found {len(coaches)} coaches")
    return coaches

def save_to_database(coaches):
    """Save coaches to Railway PostgreSQL database"""
    if not coaches:
        print("No coaches to save")
        return
        
    print(f"\n💾 Saving {len(coaches)} coaches to Railway database...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS coaches (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                year INTEGER,
                model VARCHAR,
                chassis_type VARCHAR,
                converter VARCHAR,
                condition VARCHAR,
                price INTEGER,
                price_display VARCHAR,
                price_status VARCHAR,
                mileage INTEGER,
                engine VARCHAR,
                slide_count INTEGER DEFAULT 0,
                features JSONB DEFAULT '[]'::jsonb,
                bathroom_config VARCHAR,
                stock_number VARCHAR,
                images JSONB DEFAULT '[]'::jsonb,
                virtual_tour_url VARCHAR,
                dealer_name VARCHAR,
                dealer_state VARCHAR,
                dealer_phone VARCHAR,
                dealer_email VARCHAR,
                listing_url VARCHAR,
                source VARCHAR DEFAULT 'prevost-stuff.com',
                status VARCHAR DEFAULT 'available',
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0,
                inquiries INTEGER DEFAULT 0
            )
        """)
        
        # First, let's clear out old data to avoid conflicts
        print("🧹 Clearing old data...")
        cur.execute("DELETE FROM coaches WHERE source = 'prevost-stuff.com'")
        
        # Insert coaches one by one to handle any remaining issues
        saved_count = 0
        for coach in coaches:
            try:
                cur.execute("""
                    INSERT INTO coaches (
                        id, title, year, model, chassis_type, converter, condition,
                        price, price_display, price_status, mileage, engine,
                        slide_count, features, bathroom_config, stock_number, images,
                        virtual_tour_url, dealer_name, dealer_state, dealer_phone,
                        dealer_email, listing_url, source, status, scraped_at,
                        updated_at, views, inquiries
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    coach['id'],
                    coach['title'],
                    coach['year'],
                    coach.get('model'),
                    coach.get('model'),  # chassis_type same as model for now
                    coach.get('converter'),
                    coach.get('condition', 'pre-owned'),
                    coach.get('price'),
                    coach.get('price_display'),
                    'available' if coach.get('price') else 'contact_for_price',
                    None,  # mileage
                    None,  # engine
                    coach.get('slide_count', 0),
                    json.dumps(coach.get('features', [])),
                    None,  # bathroom_config
                    None,  # stock_number
                    json.dumps(coach.get('images', [])),
                    None,  # virtual_tour_url
                    coach.get('dealer_name'),
                    coach.get('dealer_state'),
                    None,  # dealer_phone
                    None,  # dealer_email
                    coach.get('listing_url'),
                    'prevost-stuff.com',  # source - hardcoded to avoid issues
                    coach.get('status', 'available'),
                    datetime.now(),  # scraped_at
                    datetime.now(),  # updated_at
                    0,  # views
                    0   # inquiries
                ))
                saved_count += 1
            except psycopg2.IntegrityError:
                # Skip duplicates silently
                continue
            except Exception as e:
                print(f"⚠️  Error saving coach {coach.get('title', 'Unknown')}: {e}")
                continue
        
        conn.commit()
        
        # Get final counts
        cur.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available'")
        available_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM coaches")
        total_count = cur.fetchone()[0]
        
        print(f"\n✅ Database updated successfully!")
        print(f"   Saved {saved_count} coaches")
        print(f"   Total coaches in database: {total_count}")
        print(f"   Available coaches: {available_count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=== Prevost Coach Scraper for Railway ===\n")
    
    # Scrape coaches
    coaches = scrape_coaches()
    
    # Save to database
    if coaches:
        save_to_database(coaches)
        print("\n✅ Scraping complete!")
    else:
        print("\n❌ No coaches found to save")

if __name__ == "__main__":
    main()
