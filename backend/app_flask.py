"""
PrevostGO API - Ultra Simple Flask Version
No compatibility issues!
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db():
    """Get database connection"""
    conn = sqlite3.connect('prevostgo.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite row to dict"""
    return dict(row) if row else None

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to PrevostGO API",
        "endpoints": {
            "inventory": "/api/inventory",
            "coach_detail": "/api/inventory/<id>",
            "summary": "/api/inventory/summary",
            "featured": "/api/featured"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/inventory')
def get_inventory():
    """Get all coaches with pagination and search"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sort_by = request.args.get('sort_by', 'price')
    sort_order = request.args.get('sort_order', 'asc')
    search = request.args.get('search', '')
    
    # Get filter parameters
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    converter = request.args.get('converter')
    model = request.args.get('model')
    min_slides = request.args.get('min_slides', type=int)
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    
    # Validate sort column
    valid_columns = ['price', 'year', 'mileage', 'scraped_at']
    if sort_by not in valid_columns:
        sort_by = 'price'
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Build WHERE clause for search
    where_clause = "WHERE status = 'available'"
    params = []
    
    if search:
        where_clause += """ AND (
            title LIKE ? OR 
            model LIKE ? OR 
            converter LIKE ? OR 
            features LIKE ?
        )"""
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    # Apply filters
    if min_price is not None:
        where_clause += " AND price >= ?"
        params.append(min_price * 100)  # Convert to cents
    
    if max_price is not None:
        where_clause += " AND price <= ?"
        params.append(max_price * 100)  # Convert to cents
    
    if converter:
        where_clause += " AND converter = ?"
        params.append(converter)
    
    if model:
        where_clause += " AND model = ?"
        params.append(model)
    
    if min_slides is not None:
        where_clause += " AND slide_count >= ?"
        params.append(min_slides)
    
    if year_min is not None:
        where_clause += " AND year >= ?"
        params.append(year_min)
    
    if year_max is not None:
        where_clause += " AND year <= ?"
        params.append(year_max)
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM coaches {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get coaches
    query = f"""
        SELECT * FROM coaches 
        {where_clause}
        ORDER BY {sort_by} {sort_order.upper()}
        LIMIT ? OFFSET ?
    """
    
    params.extend([per_page, offset])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    coaches = []
    for row in rows:
        coach = dict(row)
        # Parse JSON fields
        try:
            coach['features'] = json.loads(coach.get('features', '[]'))
            coach['images'] = json.loads(coach.get('images', '[]'))
        except:
            coach['features'] = []
            coach['images'] = []
        # Convert price from cents to dollars
        if coach.get('price'):
            coach['price'] = coach['price'] / 100
        coaches.append(coach)
    
    conn.close()
    
    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "coaches": coaches
    })

@app.route('/api/inventory/<coach_id>')
def get_coach(coach_id):
    """Get single coach by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Coach not found"}), 404
    
    coach = dict(row)
    # Parse JSON fields
    try:
        coach['features'] = json.loads(coach.get('features', '[]'))
        coach['images'] = json.loads(coach.get('images', '[]'))
    except:
        coach['features'] = []
        coach['images'] = []
    # Convert price from cents to dollars
    if coach.get('price'):
        coach['price'] = coach['price'] / 100
    
    # Increment views
    cursor.execute("UPDATE coaches SET views = views + 1 WHERE id = ?", (coach_id,))
    conn.commit()
    conn.close()
    
    return jsonify(coach)

@app.route('/api/inventory/summary')
def get_summary():
    """Get inventory summary"""
    conn = get_db()
    cursor = conn.cursor()
    
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
        if model:
            summary['by_model'][model] = summary['by_model'].get(model, 0) + 1
        
        # By converter
        converter = coach.get('converter', 'unknown')
        if converter:
            summary['by_converter'][converter] = summary['by_converter'].get(converter, 0) + 1
        
        # By year
        year = str(coach.get('year', 'unknown'))
        if year != '0':
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
    return jsonify(summary)

@app.route('/api/featured')
def get_featured():
    """Get featured coaches"""
    limit = int(request.args.get('limit', 6))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get high-value coaches first
    query = """
        SELECT * FROM coaches 
        WHERE status = 'available' AND price >= 100000000
        ORDER BY scraped_at DESC
        LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    
    # If not enough, get newest
    if len(rows) < limit:
        query2 = """
            SELECT * FROM coaches 
            WHERE status = 'available'
            ORDER BY scraped_at DESC
            LIMIT ?
        """
        cursor.execute(query2, (limit - len(rows),))
        rows.extend(cursor.fetchall())
    
    coaches = []
    for row in rows[:limit]:
        coach = dict(row)
        try:
            coach['features'] = json.loads(coach.get('features', '[]'))
            coach['images'] = json.loads(coach.get('images', '[]'))
        except:
            coach['features'] = []
            coach['images'] = []
        if coach.get('price'):
            coach['price'] = coach['price'] / 100
        coaches.append(coach)
    
    conn.close()
    return jsonify(coaches)

@app.route('/api/leads', methods=['POST'])
def create_lead():
    """Create a new lead"""
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Set timestamps
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO leads (first_name, last_name, email, phone, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get('first_name', ''),
        data.get('last_name', ''),
        data.get('email', ''),
        data.get('phone', ''),
        now, now
    ))
    
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({"id": lead_id, "message": "Lead created successfully"})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting PrevostGO Flask API...")
    print("API will be available at http://localhost:8000")
    print("Test endpoints:")
    print("  - http://localhost:8000/api/inventory")
    print("  - http://localhost:8000/api/inventory/summary")
    app.run(host='0.0.0.0', port=8000, debug=True)
