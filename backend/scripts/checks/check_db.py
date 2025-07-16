import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check coach count
try:
    cursor.execute("SELECT COUNT(*) FROM coaches")
    count = cursor.fetchone()[0]
    print(f"\nTotal coaches in database: {count}")
    
    # Get a sample of coaches
    cursor.execute("SELECT id, title, year, price, dealer_name FROM coaches LIMIT 5")
    coaches = cursor.fetchall()
    print("\nSample coaches:")
    for coach in coaches:
        price_display = f"${coach[3]/100:,.0f}" if coach[3] else "Contact for price"
        print(f"  - {coach[1]} ({coach[2]}) - {price_display} - {coach[4]}")
        
except Exception as e:
    print(f"Error reading coaches: {e}")

conn.close()
