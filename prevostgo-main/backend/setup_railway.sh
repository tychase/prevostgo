#!/bin/bash
# Setup script for PrevostGO Database on Railway

echo "🚀 PrevostGO Database Setup for Railway"
echo "======================================"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set!"
    echo "   1. Add PostgreSQL to your Railway project"
    echo "   2. Copy the DATABASE_URL from PostgreSQL service"
    echo "   3. Add it to your backend service environment variables"
    echo ""
    echo "Example:"
    echo "  DATABASE_URL=postgresql://user:pass@host:port/database"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migration if SQLite exists
if [ -f "prevostgo.db" ]; then
    echo ""
    echo "📂 Found existing SQLite database"
    echo "🔄 Running migration to PostgreSQL..."
    python migrate_to_postgres.py
else
    echo ""
    echo "📂 No existing SQLite database found"
fi

# Initialize database tables
echo ""
echo "🏗️  Initializing database tables..."
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Run initial scraper
echo ""
echo "🌐 Running initial scraper to populate database..."
python init_database.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Deploy to Railway: git push"
echo "2. Access dashboard: https://your-backend.railway.app/ (run dashboard.py)"
echo "3. Check API health: https://your-backend.railway.app/api/health"
echo "4. View inventory: https://your-backend.railway.app/api/inventory"
