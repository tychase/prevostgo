import sqlite3
import re

conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check current slide counts
cursor.execute("""
    SELECT slide_count, COUNT(*) as count
    FROM coaches
    WHERE status = 'available'
    GROUP BY slide_count
    ORDER BY slide_count
""")

print("Current slide count distribution:")
for row in cursor.fetchall():
    print(f"  {row[0]} slides: {row[1]} coaches")

# Let's fix slide counts by extracting from title/features
print("\nFixing slide counts from titles...")

cursor.execute("""
    SELECT id, title, features, slide_count
    FROM coaches
    WHERE status = 'available'
""")

coaches = cursor.fetchall()
fixed_count = 0

slide_patterns = {
    'non slide': 0,
    'no slide': 0,
    'single slide': 1,
    'double slide': 2,
    'triple slide': 3,
    'quad slide': 4,
    '1 slide': 1,
    '2 slide': 2,
    '3 slide': 3,
    '4 slide': 4,
}

for coach_id, title, features_json, current_slide_count in coaches:
    title_lower = title.lower()
    detected_slides = None
    
    # Check title for slide patterns
    for pattern, count in slide_patterns.items():
        if pattern in title_lower:
            detected_slides = count
            break
    
    # Also check for "# 123" pattern which often indicates slide count
    if detected_slides is None:
        match = re.search(r'#\s*(\d+)', title)
        if match:
            # Sometimes the # is a stock number, but if title has "slide" it might be slide count
            if 'slide' in title_lower:
                try:
                    num = int(match.group(1))
                    if 0 <= num <= 5:  # Reasonable slide count
                        detected_slides = num
                except:
                    pass
    
    # Update if we found a different slide count
    if detected_slides is not None and detected_slides != current_slide_count:
        cursor.execute("""
            UPDATE coaches
            SET slide_count = ?
            WHERE id = ?
        """, (detected_slides, coach_id))
        fixed_count += 1

conn.commit()

# Check the results
cursor.execute("""
    SELECT slide_count, COUNT(*) as count
    FROM coaches
    WHERE status = 'available'
    GROUP BY slide_count
    ORDER BY slide_count
""")

print(f"\nFixed {fixed_count} slide counts")
print("\nUpdated slide count distribution:")
for row in cursor.fetchall():
    print(f"  {row[0]} slides: {row[1]} coaches")

conn.close()
