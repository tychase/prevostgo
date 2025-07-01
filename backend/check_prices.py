import sqlite3

conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check price data
cursor.execute("""
    SELECT price, price_display, price_status, COUNT(*) as count
    FROM coaches
    WHERE status = 'available'
    GROUP BY price IS NULL, price_status
""")

print("Price Status Summary:")
for row in cursor.fetchall():
    print(f"Price: {row[0]}, Display: {row[1]}, Status: {row[2]}, Count: {row[3]}")

# Check some examples
cursor.execute("""
    SELECT id, title, price, price_display, price_status
    FROM coaches
    WHERE status = 'available'
    LIMIT 10
""")

print("\nExample coaches:")
for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"Title: {row[1][:50]}")
    print(f"Price (cents): {row[2]}")
    print(f"Price Display: {row[3]}")
    print(f"Price Status: {row[4]}")

conn.close()
