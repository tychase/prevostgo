"""
Migrate data from SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
import json
from datetime import datetime

def migrate():
    print("=== PrevostGO Database Migration ===")
    print("Migrating from SQLite to PostgreSQL...")
    
    # Check if SQLite database exists
    if not os.path.exists('prevostgo.db'):
        print("❌ SQLite database 'prevostgo.db' not found!")
        print("Make sure you're running this from the backend directory.")
        return
    
    # Get PostgreSQL URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set!")
        print("Set it to your PostgreSQL connection string.")
        return
    
    # Fix PostgreSQL URL if needed
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print(f"📁 Source: SQLite (prevostgo.db)")
    print(f"🎯 Destination: PostgreSQL")
    
    try:
        # Source: SQLite
        sqlite_conn = sqlite3.connect('prevostgo.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
        
        # Destination: PostgreSQL
        pg_conn = psycopg2.connect(DATABASE_URL)
        pg_cur = pg_conn.cursor()
        
        # Create tables in PostgreSQL
        print("\n📋 Creating PostgreSQL tables...")
        pg_cur.execute("""
            CREATE TABLE IF NOT EXISTS coaches (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                year INTEGER,
                model VARCHAR,
                chassis_type VARCHAR,
                converter VARCHAR,
                condition VARCHAR,
                price_cents INTEGER,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scraped_at TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                inquiry_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        print("📑 Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_coaches_status ON coaches(status)",
            "CREATE INDEX IF NOT EXISTS idx_coaches_price_status ON coaches(price_cents, status)",
            "CREATE INDEX IF NOT EXISTS idx_coaches_year_model ON coaches(year, model)",
            "CREATE INDEX IF NOT EXISTS idx_coaches_converter_state ON coaches(converter, dealer_state)",
            "CREATE INDEX IF NOT EXISTS idx_coaches_created_at ON coaches(created_at DESC)"
        ]
        
        for idx in indexes:
            pg_cur.execute(idx)
        
        # Get all coaches from SQLite
        sqlite_cur.execute("SELECT * FROM coaches")
        coaches = sqlite_cur.fetchall()
        
        print(f"\n🚌 Found {len(coaches)} coaches to migrate...")
        
        if len(coaches) == 0:
            print("❌ No coaches found in SQLite database!")
            print("Run the scraper first to populate the database.")
            return
        
        # Clear existing PostgreSQL data
        pg_cur.execute("DELETE FROM coaches")
        
        # Prepare data for PostgreSQL
        values = []
        for i, coach in enumerate(coaches):
            try:
                # Convert price to cents if needed
                price_cents = None
                if coach['price']:
                    # If price is already in cents (> 10000), use as is
                    # Otherwise multiply by 100
                    if coach['price'] > 10000:
                        price_cents = coach['price']
                    else:
                        price_cents = coach['price'] * 100
                
                # Parse JSON fields
                features = []
                images = []
                
                if coach['features']:
                    try:
                        features = json.loads(coach['features']) if isinstance(coach['features'], str) else coach['features']
                    except:
                        features = []
                        
                if coach['images']:
                    try:
                        images = json.loads(coach['images']) if isinstance(coach['images'], str) else coach['images']
                    except:
                        images = []
                
                # Parse dates
                created_at = coach.get('scraped_at', datetime.now().isoformat())
                updated_at = coach.get('updated_at', created_at)
                
                values.append((
                    coach['id'],
                    coach['title'],
                    coach.get('year'),
                    coach.get('model'),
                    coach.get('chassis_type'),
                    coach.get('converter'),
                    coach.get('condition', 'pre-owned'),
                    price_cents,
                    coach.get('price_display'),
                    coach.get('price_status', 'contact_for_price'),
                    coach.get('mileage'),
                    coach.get('engine'),
                    coach.get('slide_count', 0),
                    json.dumps(features),
                    coach.get('bathroom_config'),
                    coach.get('stock_number'),
                    json.dumps(images),
                    coach.get('virtual_tour_url'),
                    coach.get('dealer_name'),
                    coach.get('dealer_state'),
                    coach.get('dealer_phone'),
                    coach.get('dealer_email'),
                    coach.get('listing_url'),
                    coach.get('source', 'prevost-stuff.com'),
                    coach.get('status', 'available'),
                    created_at,
                    updated_at,
                    coach.get('views', 0),
                    coach.get('inquiries', 0)
                ))
                
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(coaches)} coaches...")
                    
            except Exception as e:
                print(f"  ⚠️  Error processing coach {coach.get('id', 'unknown')}: {e}")
                continue
        
        # Insert into PostgreSQL
        print(f"\n💾 Inserting {len(values)} coaches into PostgreSQL...")
        
        if values:
            execute_values(
                pg_cur,
                """
                INSERT INTO coaches (
                    id, title, year, model, chassis_type, converter, condition,
                    price_cents, price_display, price_status, mileage, engine,
                    slide_count, features, bathroom_config, stock_number, images,
                    virtual_tour_url, dealer_name, dealer_state, dealer_phone,
                    dealer_email, listing_url, source, status, created_at,
                    updated_at, view_count, inquiry_count
                ) VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    price_cents = EXCLUDED.price_cents,
                    price_display = EXCLUDED.price_display,
                    price_status = EXCLUDED.price_status,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                """,
                values
            )
        
        # Commit changes
        pg_conn.commit()
        
        # Verify migration
        pg_cur.execute("SELECT COUNT(*) FROM coaches")
        pg_count = pg_cur.fetchone()[0]
        
        print(f"\n✅ Migration complete!")
        print(f"   SQLite coaches: {len(coaches)}")
        print(f"   PostgreSQL coaches: {pg_count}")
        
        # Show some stats
        pg_cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'available') as available,
                COUNT(*) FILTER (WHERE status = 'sold') as sold,
                COUNT(*) FILTER (WHERE price_cents IS NOT NULL) as with_prices
            FROM coaches
        """)
        stats = pg_cur.fetchone()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Available: {stats[0]}")
        print(f"   Sold: {stats[1]}")
        print(f"   With prices: {stats[2]}")
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("\n🎉 All done! Your PostgreSQL database is ready.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

def verify_connection():
    """Test PostgreSQL connection"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set!")
        return False
        
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PrevostGO SQLite to PostgreSQL Migration Tool")
    print("-" * 50)
    
    # Verify connection first
    if verify_connection():
        migrate()
    else:
        print("\nPlease set DATABASE_URL environment variable and try again.")
        print("Example: export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
