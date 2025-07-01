import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check chassis_type values
cursor.execute("SELECT DISTINCT chassis_type FROM coaches WHERE chassis_type IS NOT NULL")
chassis_types = cursor.fetchall()

print("Unique chassis types in database:")
for chassis in chassis_types:
    cursor.execute("SELECT COUNT(*) FROM coaches WHERE chassis_type = ?", (chassis[0],))
    count = cursor.fetchone()[0]
    print(f"  - '{chassis[0]}': {count} coaches")

# Check model column too
print("\nUnique models in database:")
cursor.execute("SELECT DISTINCT model FROM coaches WHERE model IS NOT NULL")
models = cursor.fetchall()
for model in models:
    cursor.execute("SELECT COUNT(*) FROM coaches WHERE model = ?", (model[0],))
    count = cursor.fetchone()[0]
    print(f"  - '{model[0]}': {count} coaches")

# Check for any coaches with the specific chassis types from the dropdown
test_chassis = ["Prevost H3-45", "Prevost X3-45", "Volvo B13R", "Custom"]
print("\nChecking for specific chassis types:")
for chassis in test_chassis:
    cursor.execute("SELECT COUNT(*) FROM coaches WHERE chassis_type = ? OR model = ?", (chassis, chassis))
    count = cursor.fetchone()[0]
    print(f"  - '{chassis}': {count} coaches")

# Show a sample of what's actually stored
print("\nSample of actual chassis_type and model values:")
cursor.execute("SELECT chassis_type, model, title FROM coaches LIMIT 10")
samples = cursor.fetchall()
for sample in samples:
    print(f"  chassis_type: '{sample[0]}', model: '{sample[1]}', title: '{sample[2]}'")

conn.close()
