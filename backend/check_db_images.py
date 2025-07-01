import sqlite3
import json

conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check total coaches with non-empty images
cursor.execute("SELECT COUNT(*) FROM coaches WHERE images != '[]' AND images IS NOT NULL")
total_with_images = cursor.fetchone()[0]

# Check all coaches
cursor.execute("SELECT COUNT(*) FROM coaches")
total_all = cursor.fetchone()[0]

print(f"Total coaches in database: {total_all}")
print(f"Coaches with images: {total_with_images}")

# Sample some image data
cursor.execute("SELECT id, title, images, listing_url FROM coaches WHERE images IS NOT NULL LIMIT 10")
print("\nFirst 10 coaches - image data:")
for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"Title: {row[1][:50]}...")
    print(f"Images JSON: {row[2]}")
    print(f"Listing URL: {row[3]}")

# Check if ANY coach has images
cursor.execute("SELECT id, title, images FROM coaches WHERE images NOT IN ('[]', '', NULL) LIMIT 5")
results = cursor.fetchall()
if results:
    print("\nCoaches with actual images:")
    for row in results:
        print(f"ID: {row[0]}, Images: {row[2]}")
else:
    print("\nNO coaches have images in the database!")

conn.close()
