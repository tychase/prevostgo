"""
Enhanced Railway Scraper - Combines simple deployment with advanced parsing
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
import time

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
    unique_string = f"{year}-{converter}-{model}-{title}-{index}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

def parse_price(price_str):
    """Enhanced price parsing"""
    if not price_str:
        return None, 'contact_for_price'
    
    price_str = str(price_str).strip()
    
    # Check for sold status
    if 'sold' in price_str.lower():
        return None, 'sold'
    
    # Extract numeric price
    price_match = re.search(r'\$\s*([\d,]+)', price_str)
    if price_match:
        price_num = price_match.group(1).replace(',', '')
        try:
            price_dollars = int(price_num)
            # Sanity check - prices should be reasonable
            if 10000 < price_dollars < 5000000:  # Between $10k and $5M
                return price_dollars * 100, 'available'  # Convert to cents
        except:
            pass
    
    return None, 'contact_for_price'

def extract_features_from_title(title):
    """Extract features from the title"""
    features = []
    title_lower = title.lower()
    
    # Check for slide count
    slide_match = re.search(r'(single|double|triple|quad)\s+slide', title_lower)
    if slide_match:
        slide_type = slide_match.group(1)
        slide_map = {'single': 1, 'double': 2, 'triple': 3, 'quad': 4}
        if slide_type in slide_map:
            features.append(f"{slide_map[slide_type]} Slides")
    
    # Check for bunk coach
    if 'bunk' in title_lower:
        features.append("Bunk Coach")
    
    # Check for wheelchair accessible
    if 'hc acc' in title_lower or 'wheelchair' in title_lower:
        features.append("Wheelchair Accessible")
    
    # Engine type
    if 'isx' in title_lower:
        features.append("ISX Engine")
    elif 'x15' in title_lower:
        features.append("X15 Engine")
    
    return features

def extract_model_info(title, model_str):
    """Extract model and chassis type"""
    models = ['H3-45', 'XLII', 'X3-45', 'H3-41', 'H3-40', 'XL-45', 'XL-40']
    
    # Check title first
    for m in models:
        if m in title:
            return m, m
    
    # Then check model string
    if model_str:
        for m in models:
            if m in model_str:
                return m, m
    
    # Default
    return model_str or 'Unknown', model_str or 'Unknown'

def scrape_coaches():
    """Scrape coaches with enhanced parsing"""
    print("🌐 Fetching coaches from prevost-stuff.com...")
    
    url = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=30)
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
                'features': extract_features_from_title(title),
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
                        model_raw = field.replace('Model:', '').strip()
                        coach['model'], coach['chassis_type'] = extract_model_info(title, model_raw)
                    elif field.startswith('State:'):
                        coach['dealer_state'] = field.replace('State:', '').strip()
                    elif field.startswith('Price:'):
                        price_text = field.replace('Price:', '').strip()
                        coach['price'], price_status = parse_price(price_text)
                        if coach['status'] != 'sold':
                            coach['price_status'] = price_status
                        else:
                            coach['price_status'] = 'sold'
                        coach['price_display'] = price_text if price_text and price_text != '$' else 'Contact for Price'
                    elif field.startswith('Converter:'):
                        coach['converter'] = field.replace('Converter:', '').strip()
                    elif field.startswith('Slides:'):
                        try:
                            slides_str = field.replace('Slides:', '').strip()
                            coach['slide_count'] = int(slides_str) if slides_str.isdigit() else 0
                            if coach['slide_count'] > 0:
                                slide_feature = f"{coach['slide_count']} Slides"
                                if slide_feature not in coach['features']:
                                    coach['features'].append(slide_feature)
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
            
            # Set defaults and extract model if not found
            coach['dealer_name'] = coach.get('dealer_name', 'Unknown')
            if 'model' not in coach:
                coach['model'], coach['chassis_type'] = extract_model_info(title, None)
            coach['dealer_state'] = coach.get('dealer_state', 'Unknown')
            coach['converter'] = coach.get('converter', 'Unknown')
            coach['slide_count'] = coach.get('slide_count', 0)
            coach['price_display'] = coach.get('price_display', 'Contact for Price')
            coach['price_status'] = coach.get('price_status', 'contact_for_price')
            
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
    
    # Show statistics
    available = [c for c in coaches if c['status'] == 'available']
    with_prices = [c for c in available if c.get('price')]
    
    print(f"✅ Found {len(coaches)} coaches")
    print(f"   Available: {len(available)}")
    print(f"   With prices: {len(with_prices)} ({len(with_prices)/len(available)*100:.1f}%)")
    
    return coaches

def fetch_detail_prices(coaches, limit=30):
    """Fetch prices from detail pages for coaches without prices"""
    print(f"\n🔍 Fetching prices from detail pages...")
    
    coaches_to_check = [c for c in coaches 
                       if c['status'] == 'available' 
                       and not c.get('price')
                       and c.get('listing_url', '').endswith('.html')][:limit]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    updated = 0
    
    for i, coach in enumerate(coaches_to_check):
        try:
            print(f"   {i+1}/{len(coaches_to_check)} - {coach['title'][:50]}...")
            response = requests.get(coach['listing_url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Look for price patterns
                price_patterns = [
                    r'Price:\s*\$\s*([\d,]+)',
                    r'Asking\s+Price:\s*\$\s*([\d,]+)',
                    r'\$\s*([\d,]+)(?:\s*USD)?',
                ]
                
                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        price_str = match.replace(',', '')
                        if price_str.isdigit():
                            price = int(price_str)
                            if 50000 < price < 5000000:  # Sanity check
                                coach['price'] = price * 100
                                coach['price_display'] = f"${price:,}"
                                coach['price_status'] = 'available'
                                updated += 1
                                print(f"     ✓ Found price: ${price:,}")
                                break
                    if coach.get('price'):
                        break
            
            time.sleep(0.5)  # Be respectful
            
        except Exception as e:
            print(f"     ✗ Error: {e}")
    
    print(f"   Updated {updated} prices from detail pages")
    return updated

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
        
        # Clear old data
        print("🧹 Clearing old data...")
        cur.execute("DELETE FROM coaches WHERE source = 'prevost-stuff.com'")
        
        # Insert coaches
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
                    coach.get('chassis_type'),
                    coach.get('converter'),
                    coach.get('condition', 'pre-owned'),
                    coach.get('price'),
                    coach.get('price_display'),
                    coach.get('price_status', 'contact_for_price'),
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
                    'prevost-stuff.com',
                    coach.get('status', 'available'),
                    datetime.now(),
                    datetime.now(),
                    0,  # views
                    0   # inquiries
                ))
                saved_count += 1
            except Exception as e:
                print(f"⚠️  Error saving coach {coach.get('title', 'Unknown')}: {e}")
                continue
        
        conn.commit()
        
        # Get final statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'available') as available,
                COUNT(*) FILTER (WHERE status = 'available' AND price IS NOT NULL) as with_prices,
                AVG(price) FILTER (WHERE status = 'available' AND price IS NOT NULL) as avg_price
            FROM coaches
        """)
        stats = cur.fetchone()
        
        print(f"\n✅ Database updated successfully!")
        print(f"   Saved {saved_count} coaches")
        print(f"   Total in database: {stats[0]}")
        print(f"   Available: {stats[1]}")
        print(f"   With prices: {stats[2]}")
        if stats[3]:
            print(f"   Average price: ${int(stats[3]/100):,}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=== Enhanced Prevost Coach Scraper for Railway ===\n")
    
    # Step 1: Scrape coaches
    coaches = scrape_coaches()
    
    if coaches:
        # Step 2: Fetch additional prices from detail pages
        fetch_detail_prices(coaches, limit=30)
        
        # Step 3: Save to database
        save_to_database(coaches)
        
        print("\n✅ Scraping complete!")
    else:
        print("\n❌ No coaches found to save")

if __name__ == "__main__":
    main()
