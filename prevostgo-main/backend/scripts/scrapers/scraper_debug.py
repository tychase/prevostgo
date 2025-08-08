"""
Add debug logging to the scraper to see what database it's using
"""
import os

# At the top of scraper.py, add:
print(f"[SCRAPER DEBUG] DATABASE_URL from env: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")
print(f"[SCRAPER DEBUG] Using database: {'PostgreSQL' if 'postgres' in str(os.getenv('DATABASE_URL', '')).lower() else 'SQLite'}")

# Also add to the save_to_database method:
from app.database import DATABASE_URL, engine
print(f"[SCRAPER DEBUG] Actual DATABASE_URL being used: {DATABASE_URL[:50]}...")
print(f"[SCRAPER DEBUG] Engine URL: {engine.url}")
