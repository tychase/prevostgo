"""
Quick diagnostic script to check your current setup
"""

import os
import sys

print("🔍 PrevostGO Setup Diagnostic")
print("=" * 40)

# Check Python version
print(f"\n✅ Python version: {sys.version}")

# Check current directory
print(f"\n📁 Current directory: {os.getcwd()}")

# Check for database files
print("\n📊 Database files:")
if os.path.exists('prevostgo.db'):
    size = os.path.getsize('prevostgo.db') / 1024 / 1024
    print(f"  ✅ SQLite database found: {size:.2f} MB")
else:
    print("  ❌ No SQLite database found")

# Check environment variables
print("\n🔐 Environment variables:")
db_url = os.getenv('DATABASE_URL')
if db_url:
    # Hide password
    if '@' in db_url:
        parts = db_url.split('@')
        safe_url = parts[0].split('//')[0] + '//***:***@' + parts[1]
        print(f"  ✅ DATABASE_URL is set: {safe_url}")
    else:
        print(f"  ✅ DATABASE_URL is set")
else:
    print("  ❌ DATABASE_URL not set")

# Check Railway environment
railway_env = os.getenv('RAILWAY_ENVIRONMENT')
if railway_env:
    print(f"  ✅ Running on Railway: {railway_env}")
else:
    print("  ℹ️  Not running on Railway (local development)")

# Try to import required modules
print("\n📦 Python packages:")
packages = [
    'fastapi',
    'sqlalchemy', 
    'psycopg2',
    'flask',
    'requests',
    'bs4'
]

for package in packages:
    try:
        __import__(package)
        print(f"  ✅ {package}")
    except ImportError:
        print(f"  ❌ {package} (not installed)")

# Quick database check
print("\n💾 Database connectivity:")
try:
    if db_url and 'postgresql' in db_url:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM coaches")
        count = cur.fetchone()[0]
        conn.close()
        print(f"  ✅ PostgreSQL connected: {count} coaches")
    elif os.path.exists('prevostgo.db'):
        import sqlite3
        conn = sqlite3.connect('prevostgo.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM coaches")
        count = cur.fetchone()[0]
        conn.close()
        print(f"  ✅ SQLite connected: {count} coaches")
    else:
        print("  ❌ No database connection available")
except Exception as e:
    print(f"  ❌ Database error: {e}")

print("\n" + "=" * 40)
print("📝 Next steps:")
if not db_url:
    print("1. Set DATABASE_URL environment variable")
    print("2. Run: python setup_railway.ps1 (Windows) or ./setup_railway.sh (Linux/Mac)")
elif db_url and 'postgresql' in db_url:
    print("1. Run migration: python migrate_to_postgres.py")
    print("2. Run scraper: python init_database.py")
    print("3. Start dashboard: python dashboard.py")
else:
    print("1. Everything looks good!")
    print("2. Start the API: python main.py")
    print("3. Start dashboard: python dashboard.py")
