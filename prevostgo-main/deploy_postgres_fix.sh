#!/bin/bash
# Deploy the complete PostgreSQL fix

echo "🚀 Deploying PostgreSQL scraper fix..."

cd /c/Users/tmcha/Dev/prevostgo

# Add the changes
git add backend/app/services/scraper.py
git add backend/app/routers/inventory.py

# Commit with descriptive message
git commit -m "Fix: Update scraper to use PostgreSQL instead of SQLite

- Replace SQLite scraper with PostgreSQL version
- Fix get_coach endpoint to use PostgreSQL
- Ensure all database operations use the configured DATABASE_URL"

# Push to trigger deployment
git push origin main

echo "✅ Changes pushed!"
echo ""
echo "Next steps:"
echo "1. Wait for Railway to complete deployment (check dashboard)"
echo "2. Run: python scripts/populate_production_db.py"
echo "3. Check https://prevostgo.com for coaches"
