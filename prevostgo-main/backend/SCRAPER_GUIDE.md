# PrevostGO Scraper Guide

## Overview

The PrevostGO scraper fetches luxury coach listings from prevost-stuff.com and populates the local database with inventory data.

## Running the Scraper

### Basic Usage

```bash
cd backend
python scraper_final.py
```

This will:
1. Fetch all listings from the main page
2. Parse coach details (year, model, price, etc.)
3. Save/update the database
4. Attempt to fetch additional prices from detail pages
5. Display statistics

### What the Scraper Collects

- **Basic Info**: Title, Year, Model, Converter
- **Pricing**: Price (in cents), Display price, Price status
- **Details**: Slide count, Condition (new/pre-owned), Status (available/sold)
- **Dealer**: Name, State
- **Features**: Extracted from title (slides, bunk coach, etc.)
- **Media**: Thumbnail images, Listing URLs

## Database Schema

The scraper populates the `coaches` table with:

```sql
id              -- Unique hash ID
title           -- Full listing title
year            -- Model year
model           -- Chassis model (H3-45, XLII, X3, etc.)
chassis_type    -- Same as model
converter       -- Converter/manufacturer name
condition       -- new or pre-owned
price           -- Price in cents (NULL if not listed)
price_display   -- Human-readable price
price_status    -- available, sold, or contact_for_price
slide_count     -- Number of slides
features        -- JSON array of features
images          -- JSON array of image URLs
dealer_name     -- Dealer/seller name
dealer_state    -- State abbreviation
listing_url     -- Link to detail page
status          -- available or sold
scraped_at      -- When first scraped
updated_at      -- Last update time
```

## Understanding the Data

### Price Status Values
- `available` - Has a listed price
- `contact_for_price` - No price shown
- `sold` - Coach has been sold

### Models
Common Prevost models scraped:
- `H3-45` - Current generation coach
- `XLII` or `XL II` - Previous generation
- `X3` - Newer model
- `XL` - Older models

### Converters
Popular converters include:
- Marathon, Millennium, Liberty, Featherlite
- Country Coach, Emerald, Florida Coach
- Royale, Parliament, Outlaw, etc.

## Scheduling Regular Updates

### Windows Task Scheduler

1. Create a batch file `run_scraper.bat`:
```batch
@echo off
cd /d C:\Users\tmcha\Dev\prevostgo\backend
call ..\venv\Scripts\activate
python scraper_final.py >> scraper_log.txt 2>&1
```

2. Schedule in Task Scheduler to run daily/weekly

### Linux/Mac Cron

Add to crontab:
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/prevostgo/backend && /path/to/venv/bin/python scraper_final.py >> scraper_log.txt 2>&1
```

## Monitoring & Maintenance

### Check Scraper Health

```python
# Quick stats check
import sqlite3
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check recent scrapes
cursor.execute("""
    SELECT DATE(scraped_at) as date, COUNT(*) as count 
    FROM coaches 
    GROUP BY DATE(scraped_at) 
    ORDER BY date DESC 
    LIMIT 7
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} coaches")

# Check price coverage
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN price IS NOT NULL THEN 1 ELSE 0 END) as with_price
    FROM coaches 
    WHERE status = 'available'
""")
result = cursor.fetchone()
print(f"Price coverage: {result[1]}/{result[0]} ({result[1]/result[0]*100:.1f}%)")
```

### Common Issues

1. **No listings found**
   - Check if the website structure changed
   - Verify internet connection
   - Check if the site is blocking the scraper

2. **Prices not updating**
   - Detail pages may have different formats
   - Some coaches legitimately don't list prices

3. **Duplicate coaches**
   - The ID generation uses title+year+model+converter
   - If these change slightly, it creates a new record

## Extending the Scraper

### Add More Sources

Create new scraper classes following the same pattern:
```python
class AnotherSiteScraper:
    def scrape_listings(self):
        # Fetch and parse listings
        return listings
    
    def save_to_database(self, listings):
        # Save with different source
        pass
```

### Extract More Features

Add to `extract_features_from_title()`:
```python
# Check for more features
if 'tag axle' in title_lower:
    features.append("Tag Axle")
if 'IFS' in title:
    features.append("Independent Front Suspension")
```

### Fetch More Details

Enhance `fetch_detail_prices()` to extract:
- Mileage
- Engine details  
- Full feature lists
- Additional images
- Detailed descriptions

## API Integration

The scraped data is served by the FastAPI backend:

- `GET /api/inventory` - List all coaches
- `GET /api/inventory/{id}` - Get specific coach
- `GET /api/inventory/search` - Search with filters

Filters supported:
- `min_price`, `max_price`
- `year_min`, `year_max`
- `model`, `converter`
- `condition`, `status`
- `min_slides`

## Best Practices

1. **Run regularly** - Daily or weekly to catch new listings
2. **Monitor logs** - Check for errors or changes in site structure
3. **Respect the source** - Don't overload with requests
4. **Backup database** - Before major updates
5. **Test locally** - Before deploying scraper changes

## Troubleshooting

### Debug Mode

Add debug output:
```python
# In scraper_final.py
DEBUG = True  # Add at top

# Then in code:
if DEBUG:
    print(f"Processing: {title}")
    print(f"Found price: {price}")
```

### Test Specific Functions

```python
from scraper_final import PrevostScraper

scraper = PrevostScraper()

# Test price parsing
price, status = scraper.parse_price("$499,000")
print(f"Price: {price}, Status: {status}")

# Test feature extraction  
features = scraper.extract_features_from_title(
    "2021 Prevost Marathon H3-45 Quad Slide Bunk Coach"
)
print(f"Features: {features}")
```

### Database Queries

Useful queries for debugging:

```sql
-- Recent updates
SELECT title, price_display, updated_at 
FROM coaches 
ORDER BY updated_at DESC 
LIMIT 10;

-- Coaches without prices
SELECT COUNT(*) 
FROM coaches 
WHERE status = 'available' 
AND price IS NULL;

-- Price distribution
SELECT 
    CASE 
        WHEN price < 20000000 THEN 'Under $200k'
        WHEN price < 50000000 THEN '$200k-$500k'
        WHEN price < 100000000 THEN '$500k-$1M'
        ELSE 'Over $1M'
    END as range,
    COUNT(*) as count
FROM coaches
WHERE price IS NOT NULL
GROUP BY range;
```

## Future Enhancements

1. **Multi-source scraping** - Add more coach listing sites
2. **Image processing** - Download and optimize images locally
3. **Price history** - Track price changes over time
4. **Notifications** - Alert users when new coaches match criteria
5. **Full-text search** - Index descriptions for better search
6. **Mileage tracking** - Extract and store mileage data
7. **VIN detection** - Extract VIN numbers when available
