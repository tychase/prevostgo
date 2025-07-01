"""
PrevostGO Backend API - Minimal Synchronous Version
Works with Python 3.13 without Rust dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import sqlite3
import json
from typing import List, Dict, Optional

# Create FastAPI app
app = FastAPI(
    title="PrevostGO API",
    description="B2B/B2C digital showroom for Prevost luxury coaches",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database helper functions
def get_db():
    """Get database connection"""
    conn = sqlite3.connect('prevostgo.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create coaches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaches (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            model TEXT,
            chassis_type TEXT,
            converter TEXT,
            condition TEXT,
            price INTEGER,
            price_display TEXT,
            price_status TEXT,
            mileage INTEGER,
            engine TEXT,
            slide_count INTEGER DEFAULT 0,
            features TEXT DEFAULT '[]',
            bathroom_config TEXT,
            stock_number TEXT,
            images TEXT DEFAULT '[]',
            virtual_tour_url TEXT,
            dealer_name TEXT,
            dealer_state TEXT,
            dealer_phone TEXT,
            dealer_email TEXT,
            listing_url TEXT,
            source TEXT DEFAULT 'prevost-stuff.com',
            status TEXT DEFAULT 'available',
            scraped_at TEXT,
            updated_at TEXT,
            views INTEGER DEFAULT 0,
            inquiries INTEGER DEFAULT 0
        )
    """)
    
    # Create leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            timeframe TEXT,
            financing_status TEXT,
            preferred_models TEXT DEFAULT '[]',
            preferred_years TEXT DEFAULT '[]',
            must_have_features TEXT DEFAULT '[]',
            coaches_viewed TEXT DEFAULT '[]',
            coaches_inquired TEXT DEFAULT '[]',
            score INTEGER DEFAULT 0,
            score_factors TEXT DEFAULT '{}',
            status TEXT DEFAULT 'new',
            assigned_dealer TEXT,
            assigned_at TEXT,
            source TEXT,
            utm_campaign TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT,
            last_contacted TEXT,
            followup_date TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# API Endpoints
@app.get("/")
def root():
    return {
        "message": "Welcome to PrevostGO API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PrevostGO API"
    }

@app.get("/api/inventory")
def get_inventory(
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "price",
    sort_order: str = "asc"
):
    """Get paginated inventory"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    cursor.execute("SELECT COUNT(*) as total FROM coaches WHERE status = 'available'")
    total = cursor.fetchone()['total']
    
    # Get coaches
    query = f"""
        SELECT * FROM coaches 
        WHERE status = 'available'
        ORDER BY {sort_by} {sort_order.upper()}
        LIMIT ? OFFSET ?
    """
    
    cursor.execute(query, (per_page, offset))
    rows = cursor.fetchall()
    
    # Convert to dict and parse JSON fields
    coaches = []
    for row in rows:
        coach = dict(row)
        # Parse JSON fields
        coach['features'] = json.loads(coach.get('features', '[]'))
        coach['images'] = json.loads(coach.get('images', '[]'))
        # Convert price from cents to dollars
        if coach.get('price'):
            coach['price'] = coach['price'] / 100
        coaches.append(coach)
    
    conn.close()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "coaches": coaches
    }

@app.get("/api/inventory/{coach_id}")
def get_coach(coach_id: str):
    """Get single coach by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Coach not found")
    
    coach = dict(row)
    # Parse JSON fields
    coach['features'] = json.loads(coach.get('features', '[]'))
    coach['images'] = json.loads(coach.get('images', '[]'))
    # Convert price from cents to dollars
    if coach.get('price'):
        coach['price'] = coach['price'] / 100
    
    # Increment views
    cursor.execute("UPDATE coaches SET views = views + 1 WHERE id = ?", (coach_id,))
    conn.commit()
    conn.close()
    
    return coach

@app.get("/api/inventory/summary")
def get_inventory_summary():
    """Get inventory summary statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all available coaches
    cursor.execute("SELECT * FROM coaches WHERE status = 'available'")
    rows = cursor.fetchall()
    
    summary = {
        "total_coaches": len(rows),
        "by_condition": {},
        "by_model": {},
        "by_converter": {},
        "by_year": {},
        "price_ranges": {
            "under_200k": 0,
            "200k_500k": 0,
            "500k_1m": 0,
            "over_1m": 0,
            "contact_for_price": 0
        }
    }
    
    for row in rows:
        coach = dict(row)
        
        # By condition
        condition = coach.get('condition', 'unknown')
        summary['by_condition'][condition] = summary['by_condition'].get(condition, 0) + 1
        
        # By model
        model = coach.get('model', 'unknown')
        summary['by_model'][model] = summary['by_model'].get(model, 0) + 1
        
        # By converter
        converter = coach.get('converter', 'unknown')
        summary['by_converter'][converter] = summary['by_converter'].get(converter, 0) + 1
        
        # By year
        year = str(coach.get('year', 'unknown'))
        summary['by_year'][year] = summary['by_year'].get(year, 0) + 1
        
        # Price ranges
        price = coach.get('price')
        if price is None:
            summary['price_ranges']['contact_for_price'] += 1
        else:
            price_dollars = price / 100
            if price_dollars < 200000:
                summary['price_ranges']['under_200k'] += 1
            elif price_dollars < 500000:
                summary['price_ranges']['200k_500k'] += 1
            elif price_dollars < 1000000:
                summary['price_ranges']['500k_1m'] += 1
            else:
                summary['price_ranges']['over_1m'] += 1
    
    conn.close()
    return summary

@app.post("/api/leads")
def create_lead(lead_data: dict):
    """Create a new lead"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Set timestamps
    now = datetime.utcnow().isoformat()
    lead_data['created_at'] = now
    lead_data['updated_at'] = now
    
    # Convert lists to JSON
    for field in ['preferred_models', 'preferred_years', 'must_have_features', 'coaches_viewed', 'coaches_inquired']:
        if field in lead_data:
            lead_data[field] = json.dumps(lead_data.get(field, []))
    
    # Insert lead
    columns = ', '.join(lead_data.keys())
    placeholders = ', '.join(['?' for _ in lead_data])
    query = f"INSERT INTO leads ({columns}) VALUES ({placeholders})"
    
    cursor.execute(query, list(lead_data.values()))
    lead_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {"id": lead_id, "message": "Lead created successfully"}

@app.get("/api/featured")
def get_featured_coaches(limit: int = 6):
    """Get featured coaches for homepage"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get newest high-value coaches
    query = """
        SELECT * FROM coaches 
        WHERE status = 'available' AND price >= 100000000
        ORDER BY scraped_at DESC
        LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    
    # If not enough high-end, get newest
    if len(rows) < limit:
        additional_query = """
            SELECT * FROM coaches 
            WHERE status = 'available'
            ORDER BY scraped_at DESC
            LIMIT ?
        """
        cursor.execute(additional_query, (limit - len(rows),))
        rows.extend(cursor.fetchall())
    
    # Convert to dict and parse JSON fields
    coaches = []
    for row in rows[:limit]:
        coach = dict(row)
        coach['features'] = json.loads(coach.get('features', '[]'))
        coach['images'] = json.loads(coach.get('images', '[]'))
        if coach.get('price'):
            coach['price'] = coach['price'] / 100
        coaches.append(coach)
    
    conn.close()
    return coaches

if __name__ == "__main__":
    print("Starting PrevostGO API...")
    print("Visit http://localhost:8000/docs for API documentation")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
