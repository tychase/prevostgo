#!/bin/bash
# Deploy the SQLite fix to production

echo "🚀 Deploying SQLite fix to Railway..."

cd /c/Users/tmcha/Dev/prevostgo

# Add and commit the fix
git add backend/app/routers/inventory.py
git commit -m "Fix: Replace SQLite with PostgreSQL in get_coach endpoint"

# Push to trigger Railway deployment
git push origin main

echo "✅ Fix pushed. Railway will automatically redeploy."
echo "⏳ Wait for deployment to complete (check Railway dashboard)"
echo "🔄 Then run: python scripts/populate_production_db.py"
