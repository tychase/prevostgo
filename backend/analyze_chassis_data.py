import sqlite3
import json
from collections import Counter

def analyze_and_suggest_chassis():
    """Analyze chassis data and suggest frontend dropdown values"""
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    print("=== CHASSIS DATA ANALYSIS ===\n")
    
    # Get all chassis_type and model values
    cursor.execute("""
        SELECT chassis_type, model, title 
        FROM coaches 
        WHERE status = 'available'
    """)
    
    all_data = cursor.fetchall()
    chassis_types = []
    models = []
    
    for chassis_type, model, title in all_data:
        if chassis_type:
            chassis_types.append(chassis_type.strip())
        if model:
            models.append(model.strip())
    
    # Count occurrences
    chassis_counter = Counter(chassis_types)
    model_counter = Counter(models)
    
    print("Top Chassis Types:")
    for chassis, count in chassis_counter.most_common(10):
        print(f"  - '{chassis}': {count} coaches")
    
    print("\nTop Models:")
    for model, count in model_counter.most_common(10):
        print(f"  - '{model}': {count} coaches")
    
    # Extract common patterns
    prevost_models = []
    volvo_models = []
    
    for model in models + chassis_types:
        if model:
            model_upper = model.upper()
            if 'H3-45' in model_upper or 'H345' in model_upper:
                prevost_models.append('H3-45')
            elif 'X3-45' in model_upper or 'X345' in model_upper:
                prevost_models.append('X3-45')
            elif 'VOLVO' in model_upper:
                volvo_models.append(model)
    
    prevost_h345_count = prevost_models.count('H3-45')
    prevost_x345_count = prevost_models.count('X3-45')
    volvo_count = len(volvo_models)
    
    print(f"\nPattern Matching Results:")
    print(f"  - Prevost H3-45 (including variations): {prevost_h345_count} coaches")
    print(f"  - Prevost X3-45 (including variations): {prevost_x345_count} coaches")
    print(f"  - Volvo models: {volvo_count} coaches")
    
    # Generate suggested dropdown values
    print("\n=== SUGGESTED FRONTEND UPDATE ===")
    print("\nUpdate HeroSearch.jsx with these chassis options:")
    print("```javascript")
    print("const chassisTypes = useMemo(() => [")
    
    # Add the most common/standardized options
    if prevost_h345_count > 0:
        print('  "Prevost H3-45",')
    if prevost_x345_count > 0:
        print('  "Prevost X3-45",')
    
    # Add other common models from the counter
    added = set(['Prevost H3-45', 'Prevost X3-45'])
    for model, count in model_counter.most_common(10):
        if count >= 5 and model not in added and len(model) > 3:
            # Clean up the model name
            if 'prevost' in model.lower() and ('h3' in model.lower() or 'x3' in model.lower()):
                continue  # Skip variations we already added
            print(f'  "{model}",')
            added.add(model)
    
    print("], []);")
    print("```")
    
    # Test the fuzzy matching
    print("\n=== TESTING FUZZY MATCHING ===")
    test_terms = ["Prevost H3-45", "Prevost X3-45", "H3-45", "X3-45", "Volvo"]
    
    for term in test_terms:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM coaches 
            WHERE status = 'available' 
            AND (chassis_type LIKE ? OR model LIKE ?)
        """, (f"%{term}%", f"%{term}%"))
        
        count = cursor.fetchone()[0]
        print(f"  - Searching for '{term}': {count} matches")
    
    conn.close()

if __name__ == "__main__":
    analyze_and_suggest_chassis()
