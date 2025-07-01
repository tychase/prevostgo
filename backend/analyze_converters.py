import sqlite3
from collections import Counter

def analyze_converters():
    """Analyze converter data in the database"""
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    print("=== CONVERTER DATA ANALYSIS ===\n")
    
    # Get all converter values
    cursor.execute("""
        SELECT converter 
        FROM coaches 
        WHERE status = 'available' AND converter IS NOT NULL
    """)
    
    converters = [row[0].strip() for row in cursor.fetchall() if row[0]]
    converter_counter = Counter(converters)
    
    print("Top Converters in Database:")
    for converter, count in converter_counter.most_common(15):
        print(f"  - '{converter}': {count} coaches")
    
    print("\n=== TESTING CURRENT DROPDOWN VALUES ===")
    dropdown_values = ["Marathon", "Liberty Coach", "Newell Coach", "Foretravel", "Millennium", "Featherlite"]
    
    for value in dropdown_values:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM coaches 
            WHERE status = 'available' 
            AND converter LIKE ?
        """, (f"%{value}%",))
        
        count = cursor.fetchone()[0]
        print(f"  - '{value}': {count} matches")
    
    print("\n=== SUGGESTED CONVERTER DROPDOWN ===")
    print("const converters = useMemo(() => [")
    
    # Get the most common converters
    for converter, count in converter_counter.most_common(10):
        if count >= 5:  # Only include if at least 5 coaches
            print(f'  "{converter}",')
    
    print("], []);")
    
    conn.close()

if __name__ == "__main__":
    analyze_converters()
