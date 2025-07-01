import sqlite3
import json

conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Check coaches with images
cursor.execute("SELECT COUNT(*) FROM coaches WHERE images != '[]' AND images IS NOT NULL")
with_images = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available'")
total = cursor.fetchone()[0]

print(f"Coaches with images: {with_images} out of {total}")

# Show sample of image data
cursor.execute("SELECT id, title, images FROM coaches WHERE images != '[]' AND images IS NOT NULL LIMIT 5")
print("\nSample image data:")
for row in cursor.fetchall():
    images = json.loads(row[2]) if row[2] else []
    print(f"\nID: {row[0]}")
    print(f"Title: {row[1][:50]}...")
    print(f"Images: {images}")

# Check for empty images
cursor.execute("SELECT COUNT(*) FROM coaches WHERE (images = '[]' OR images IS NULL) AND status = 'available'")
no_images = cursor.fetchone()[0]
print(f"\nCoaches without images: {no_images}")

conn.close()
