# Backend Cleanup Plan

## Current State
- 23 test/scraper/utility files in backend root directory
- Multiple scraper implementations with overlapping functionality
- Test files mixed with production code

## Files to Organize

### 1. Test Files → Move to `tests/` directory
- test_api.py
- test_api_endpoints.py
- test_api_search.py
- test_coach_api.py
- test_database_connection.py
- test_db.py
- test_db_direct.py
- test_enhanced_scraper.py
- test_filters.py
- test_search.py
- test_search_sql.py
- add_test_coaches.py

### 2. Utility Scripts → Move to `scripts/` directory
- run_scraper.py
- run_railway_scraper.py
- scraper_debug.py
- download_images.py
- enhanced_image_downloader.py
- fetch_images_only.py
- smart_image_downloader.py

### 3. Scrapers to Remove (redundant)
- enhanced_railway_scraper.py (use enhanced scraper instead)
- simple_railway_scraper.py (use enhanced scraper instead)
- simple_railway_scraper_v2.py (use enhanced scraper instead)
- scraper_final_v2.py (migrate dashboard to use service scrapers)

### 4. Production Scrapers to Keep
- app/services/scraper.py (basic scraper)
- app/services/scraper_enhanced.py (PRIMARY - best features)
- app/services/scraper_postgres.py (remove - redundant)

## Action Plan

1. **Create directory structure:**
   ```
   backend/
   ├── tests/
   │   ├── __init__.py
   │   ├── api/
   │   ├── database/
   │   └── scrapers/
   ├── scripts/
   │   ├── __init__.py
   │   ├── scrapers/
   │   └── utilities/
   ```

2. **Update imports** in files that reference moved scripts

3. **Consolidate scraper functionality:**
   - Make enhanced scraper the default
   - Add missing converter extraction logic
   - Improve price parsing
   - Remove redundant scrapers

4. **Update documentation** to reflect new structure