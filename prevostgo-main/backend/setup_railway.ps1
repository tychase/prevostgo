# Setup script for PrevostGO Database on Railway (Windows)

Write-Host "🚀 PrevostGO Database Setup for Railway" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if DATABASE_URL is set
if (-not $env:DATABASE_URL) {
    Write-Host "⚠️  DATABASE_URL not set!" -ForegroundColor Yellow
    Write-Host "   1. Add PostgreSQL to your Railway project"
    Write-Host "   2. Copy the DATABASE_URL from PostgreSQL service"
    Write-Host "   3. Add it to your backend service environment variables"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  DATABASE_URL=postgresql://user:pass@host:port/database"
    exit 1
}

Write-Host "✅ DATABASE_URL is set" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run migration if SQLite exists
if (Test-Path "prevostgo.db") {
    Write-Host ""
    Write-Host "📂 Found existing SQLite database" -ForegroundColor Yellow
    Write-Host "🔄 Running migration to PostgreSQL..." -ForegroundColor Yellow
    python migrate_to_postgres.py
} else {
    Write-Host ""
    Write-Host "📂 No existing SQLite database found" -ForegroundColor Yellow
}

# Initialize database tables
Write-Host ""
Write-Host "🏗️  Initializing database tables..." -ForegroundColor Yellow
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Run initial scraper
Write-Host ""
Write-Host "🌐 Running initial scraper to populate database..." -ForegroundColor Yellow
python init_database.py

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Deploy to Railway: git push"
Write-Host "2. Access dashboard: https://your-backend.railway.app/ (run dashboard.py)"
Write-Host "3. Check API health: https://your-backend.railway.app/api/health"
Write-Host "4. View inventory: https://your-backend.railway.app/api/inventory"
