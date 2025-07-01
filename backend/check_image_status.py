import sqlite3
import json
import os

# Check current status
conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

# Count coaches with images
cursor.execute("SELECT COUNT(*) FROM coaches WHERE images != '[]' AND images IS NOT NULL AND status = 'available'")
with_images = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available'")
total = cursor.fetchone()[0]

print(f"📊 Current Status:")
print(f"   Total available coaches: {total}")
print(f"   Coaches with images: {with_images}")
print(f"   Coaches without images: {total - with_images}")
print(f"   Percentage with images: {(with_images/total*100):.1f}%")

# Check image directory
images_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'coach-images')
if os.path.exists(images_dir):
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    print(f"\n📁 Image files on disk: {len(image_files)}")
    
    # Show file size
    total_size = sum(os.path.getsize(os.path.join(images_dir, f)) for f in image_files)
    print(f"   Total size: {total_size / 1024 / 1024:.1f} MB")

conn.close()
