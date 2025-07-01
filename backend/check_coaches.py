"""
Quick database check for coaches
"""
import sqlite3
import json

def check_database():
    conn = sqlite3.connect('prevostgo.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Count total coaches
    cursor.execute("SELECT COUNT(*) as total FROM coaches")
    total = cursor.fetchone()['total']
    print(f"Total coaches in database: {total}")
    
    # Count available coaches
    cursor.execute("SELECT COUNT(*) as available FROM coaches WHERE status = 'available'")
    available = cursor.fetchone()['available']
    print(f"Available coaches: {available}")
    
    # Check for Marathon coaches
    cursor.execute("SELECT COUNT(*) as total FROM coaches WHERE converter LIKE '%Marathon%'")
    marathon = cursor.fetchone()['total']
    print(f"Marathon coaches: {marathon}")
    
    # Get sample coaches
    cursor.execute("SELECT id, title, model, converter, price, status FROM coaches LIMIT 5")
    coaches = cursor.fetchall()
    
    print("\nSample coaches:")
    for coach in coaches:
        coach_dict = dict(coach)
        print(f"- {coach_dict['id']}: {coach_dict['title']}")
        print(f"  Model: {coach_dict['model']}, Converter: {coach_dict['converter']}")
        print(f"  Price: ${coach_dict['price']/100 if coach_dict['price'] else 'Contact'}")
        print(f"  Status: {coach_dict['status']}")
        print()
    
    # Check unique statuses
    cursor.execute("SELECT DISTINCT status FROM coaches")
    statuses = cursor.fetchall()
    print("Unique statuses in database:")
    for status in statuses:
        print(f"- {status['status']}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
