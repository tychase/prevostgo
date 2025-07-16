"""
One-time setup script to initialize the database
Run this ONCE when deploying to Railway
"""

import os
import sys

print("🚀 Running one-time database setup...")

# Check if we should run setup
if os.getenv("RUN_DB_SETUP") != "true":
    print("Skipping setup (RUN_DB_SETUP not set to 'true')")
else:
    print("Setting up database...")
    
    # First try migration if SQLite exists
    if os.path.exists('prevostgo.db'):
        print("Found SQLite database, migrating to PostgreSQL...")
        try:
            from migrate_to_postgres import migrate
            migrate()
        except Exception as e:
            print(f"Migration failed: {e}")
    
    # Then run scraper to ensure we have data
    print("Running scraper to populate database...")
    try:
        from init_database import main as init_main
        init_main()
    except Exception as e:
        print(f"Scraper failed: {e}")
    
    print("✅ Setup complete!")

# Now start the main app
print("Starting main application...")
import main
