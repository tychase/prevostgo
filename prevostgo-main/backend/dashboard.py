"""
Simple web dashboard to view and manage your database
Run this locally or on Railway
"""

from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import subprocess
import sys

app = Flask(__name__)

def get_connection():
    """Get PostgreSQL connection"""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")
    
    # If using SQLite for local testing
    if DATABASE_URL.startswith("sqlite"):
        import sqlite3
        conn = sqlite3.connect('prevostgo.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    # PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        stats = {}
        
        # Total coaches
        cur.execute("SELECT COUNT(*) as total FROM coaches")
        result = cur.fetchone()
        stats['total_coaches'] = result['total'] if result else 0
        
        # By status
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM coaches 
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cur.fetchall()}
        
        # By condition
        cur.execute("""
            SELECT condition, COUNT(*) as count 
            FROM coaches 
            WHERE status = 'available'
            GROUP BY condition
        """)
        stats['by_condition'] = {row['condition']: row['count'] for row in cur.fetchall()}
        
        # Price distribution - handle both cents and dollars
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN price < 200000 OR price_cents < 20000000 THEN 1 END) as under_200k,
                COUNT(CASE WHEN (price BETWEEN 200000 AND 500000) OR (price_cents BETWEEN 20000000 AND 50000000) THEN 1 END) as range_200_500k,
                COUNT(CASE WHEN (price BETWEEN 500000 AND 1000000) OR (price_cents BETWEEN 50000000 AND 100000000) THEN 1 END) as range_500k_1m,
                COUNT(CASE WHEN price > 1000000 OR price_cents > 100000000 THEN 1 END) as over_1m,
                COUNT(CASE WHEN price IS NULL AND price_cents IS NULL THEN 1 END) as no_price
            FROM coaches
            WHERE status = 'available'
        """)
        stats['price_distribution'] = dict(cur.fetchone())
        
        # Recent activity - handle different date formats
        try:
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM coaches 
                WHERE datetime(created_at) > datetime('now', '-7 days')
            """)
        except:
            # PostgreSQL syntax
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM coaches 
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)
        
        result = cur.fetchone()
        stats['new_this_week'] = result['count'] if result else 0
        
        # Top converters
        cur.execute("""
            SELECT converter, COUNT(*) as count 
            FROM coaches 
            WHERE status = 'available' 
            GROUP BY converter 
            ORDER BY count DESC 
            LIMIT 5
        """)
        stats['top_converters'] = [dict(row) for row in cur.fetchall()]
        
        conn.close()
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({
            'error': str(e),
            'total_coaches': 0,
            'by_status': {},
            'by_condition': {},
            'price_distribution': {},
            'new_this_week': 0,
            'top_converters': []
        })

@app.route('/api/coaches')
def get_coaches():
    """Get paginated coach list"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Get coaches - try to handle both old and new schema
        try:
            cur.execute("""
                SELECT id, title, year, model, converter, condition,
                       COALESCE(price_cents, price * 100) as price_cents,
                       price_display, status, 
                       COALESCE(view_count, views, 0) as view_count,
                       dealer_state, 
                       COALESCE(created_at, scraped_at) as created_at
                FROM coaches
                ORDER BY COALESCE(created_at, scraped_at) DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
        except:
            # SQLite syntax
            cur.execute("""
                SELECT id, title, year, model, converter, condition,
                       COALESCE(price_cents, price * 100) as price_cents,
                       price_display, status, 
                       COALESCE(view_count, views, 0) as view_count,
                       dealer_state, 
                       COALESCE(created_at, scraped_at) as created_at
                FROM coaches
                ORDER BY COALESCE(created_at, scraped_at) DESC
                LIMIT ? OFFSET ?
            """, (per_page, offset))
        
        coaches = []
        for row in cur.fetchall():
            coach = dict(row)
            # Format price
            if coach.get('price_cents'):
                coach['price'] = f"${coach['price_cents'] / 100:,.0f}"
            else:
                coach['price'] = coach.get('price_display', 'Contact')
            coaches.append(coach)
        
        conn.close()
        return jsonify(coaches)
        
    except Exception as e:
        print(f"Error in get_coaches: {e}")
        return jsonify([])

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    """Trigger the scraper"""
    try:
        # Try to import and run the scraper
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from scraper_final_v2 import main as run_scraper_main
        
        # Run in a subprocess to avoid blocking
        result = subprocess.run(
            [sys.executable, 'scraper_final_v2.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Scraper completed successfully',
                'output': result.stdout[-1000:]  # Last 1000 chars
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Scraper failed',
                'error': result.stderr
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error running scraper: {str(e)}'
        })

@app.route('/api/clear-sold', methods=['POST'])
def clear_sold():
    """Remove sold coaches from database"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Count sold coaches first
        cur.execute("SELECT COUNT(*) as count FROM coaches WHERE status = 'sold'")
        count = cur.fetchone()['count']
        
        # Delete them
        cur.execute("DELETE FROM coaches WHERE status = 'sold'")
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Removed {count} sold coaches'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
