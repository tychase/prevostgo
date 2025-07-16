"""Quick database check script"""
import sqlite3
import sys
import os

db_path = "prevostgo.db"

if not os.path.exists(db_path):
    print(f"Database file not found: {db_path}")
    sys.exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("=== Database Tables ===")
    for table in tables:
        print(f"  {table[0]}")
    
    # Check coaches table structure
    cursor.execute("PRAGMA table_info(coaches)")
    columns = cursor.fetchall()
    print("\n=== Coaches Table Structure ===")
    print("  Columns:", [col[1] for col in columns])
    
    # Count coaches
    cursor.execute("SELECT COUNT(*) FROM coaches")
    total = cursor.fetchone()[0]
    print(f"\n=== Total Coaches: {total} ===")
    
    if total > 0:
        # Get sample data
        cursor.execute("""
            SELECT id, title, year, converter, model, price, dealer_name, condition 
            FROM coaches 
            LIMIT 5
        """)
        coaches = cursor.fetchall()
        
        print("\n=== Sample Coaches ===")
        for coach in coaches:
            price = f"${coach[5]/100:,.0f}" if coach[5] else "Contact"
            print(f"  {coach[1]}")
            print(f"    Year: {coach[2]}, Converter: {coach[3]}, Model: {coach[4]}")
            print(f"    Price: {price}, Dealer: {coach[6]}, Condition: {coach[7]}")
            print()
            
        # Get price distribution
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN price < 20000000 THEN 1 END) as under_200k,
                COUNT(CASE WHEN price >= 20000000 AND price < 50000000 THEN 1 END) as _200k_500k,
                COUNT(CASE WHEN price >= 50000000 AND price < 100000000 THEN 1 END) as _500k_1m,
                COUNT(CASE WHEN price >= 100000000 THEN 1 END) as over_1m,
                COUNT(CASE WHEN price IS NULL THEN 1 END) as no_price
            FROM coaches
        """)
        dist = cursor.fetchone()
        
        print("=== Price Distribution ===")
        print(f"  Under $200k: {dist[0]}")
        print(f"  $200k-$500k: {dist[1]}")
        print(f"  $500k-$1M: {dist[2]}")
        print(f"  Over $1M: {dist[3]}")
        print(f"  No price: {dist[4]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()

print("\nRun this check from: C:\\Users\\tmcha\\Dev\\prevostgo\\backend")
print("Command: python check_db_status.py")
