import sqlite3
import json

# Connect to database
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Get a few coaches to check their data
cursor.execute("""
    SELECT id, condition, price_status, dealer_email, features, images 
    FROM coaches 
    LIMIT 5
""")

coaches = cursor.fetchall()

print("Checking coach data format:")
print("-" * 50)

for coach in coaches:
    coach_id, condition, price_status, dealer_email, features, images = coach
    print(f"\nCoach ID: {coach_id}")
    print(f"  Condition: {condition} (type: {type(condition)})")
    print(f"  Price Status: {price_status} (type: {type(price_status)})")
    print(f"  Dealer Email: {dealer_email} (type: {type(dealer_email)})")
    
    # Check features format
    if features:
        try:
            features_list = json.loads(features) if isinstance(features, str) else features
            print(f"  Features: {len(features_list)} features")
        except:
            print(f"  Features: Error parsing - {features[:50]}...")
    
    # Check images format
    if images:
        try:
            images_list = json.loads(images) if isinstance(images, str) else images
            print(f"  Images: {len(images_list)} images")
        except:
            print(f"  Images: Error parsing - {images[:50]}...")

# Check unique condition values
print("\n" + "-" * 50)
print("Unique condition values in database:")
cursor.execute("SELECT DISTINCT condition FROM coaches")
conditions = cursor.fetchall()
for cond in conditions:
    print(f"  - '{cond[0]}'")

# Check if there's a specific coach causing issues
coach_id = "e0dad424574e"
cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
row = cursor.fetchone()

if row:
    columns = [desc[0] for desc in cursor.description]
    coach_dict = dict(zip(columns, row))
    
    print(f"\n" + "-" * 50)
    print(f"Specific coach {coach_id}:")
    print(f"  Condition: '{coach_dict.get('condition')}'")
    print(f"  Price Status: '{coach_dict.get('price_status')}'")
    print(f"  Dealer Email: '{coach_dict.get('dealer_email')}'")

conn.close()
