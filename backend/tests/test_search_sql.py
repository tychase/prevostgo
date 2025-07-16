"""
Test search queries directly on SQLite
"""
import sqlite3

def test_search_queries():
    conn = sqlite3.connect('prevostgo.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test 1: Basic search for Marathon
    print("Test 1: Search for 'Marathon' in converter field")
    query = """
    SELECT id, title, converter, model 
    FROM coaches 
    WHERE status = 'available' 
    AND converter LIKE '%Marathon%'
    LIMIT 5
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"Found {len(results)} results:")
    for row in results:
        print(f"  - {row['title']} (Converter: {row['converter']})")
    
    # Test 2: Search across multiple fields
    print("\n\nTest 2: Search for 'Marathon' across multiple fields")
    search_term = '%Marathon%'
    query = """
    SELECT id, title, converter, model 
    FROM coaches 
    WHERE status = 'available' 
    AND (
        title LIKE ? OR 
        model LIKE ? OR 
        converter LIKE ?
    )
    LIMIT 5
    """
    cursor.execute(query, (search_term, search_term, search_term))
    results = cursor.fetchall()
    print(f"Found {len(results)} results:")
    for row in results:
        print(f"  - {row['title']} (Converter: {row['converter']})")
    
    # Test 3: Case-insensitive search
    print("\n\nTest 3: Case-insensitive search for 'marathon'")
    query = """
    SELECT id, title, converter, model 
    FROM coaches 
    WHERE status = 'available' 
    AND LOWER(converter) LIKE LOWER('%marathon%')
    LIMIT 5
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"Found {len(results)} results:")
    for row in results:
        print(f"  - {row['title']} (Converter: {row['converter']})")
    
    conn.close()

if __name__ == "__main__":
    test_search_queries()
