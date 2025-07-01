"""
Generate placeholder images for coaches without images
Uses coach information to create unique, branded placeholder images
"""

import sqlite3
import json
import os
from PIL import Image, ImageDraw, ImageFont
import colorsys
import hashlib

class PlaceholderGenerator:
    def __init__(self):
        # Create images directory
        self.images_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'coach-images')
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Try to use a nice font, fallback to default
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        try:
            # Try Windows fonts
            self.font_large = ImageFont.truetype("arial.ttf", 48)
            self.font_medium = ImageFont.truetype("arial.ttf", 32)
            self.font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            # Use default font
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def generate_color_from_text(self, text):
        """Generate a consistent color based on text"""
        # Use hash to get consistent color
        hash_value = int(hashlib.md5(text.encode()).hexdigest()[:6], 16)
        hue = (hash_value % 360) / 360.0
        
        # Use pleasant saturation and lightness
        saturation = 0.6 + (hash_value % 20) / 100.0  # 0.6-0.8
        lightness = 0.3 + (hash_value % 20) / 100.0   # 0.3-0.5
        
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        return tuple(int(c * 255) for c in rgb)
    
    def create_placeholder(self, coach_id, title, year, converter, model):
        """Create a placeholder image for a coach"""
        # Image dimensions
        width, height = 800, 600
        
        # Create image with gradient background
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Generate color based on converter
        primary_color = self.generate_color_from_text(converter or 'default')
        secondary_color = self.generate_color_from_text(title)
        
        # Draw gradient background
        for y in range(height):
            ratio = y / height
            r = int(primary_color[0] * (1 - ratio) + secondary_color[0] * ratio)
            g = int(primary_color[1] * (1 - ratio) + secondary_color[1] * ratio)
            b = int(primary_color[2] * (1 - ratio) + secondary_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add semi-transparent overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        img.paste(overlay, (0, 0), overlay)
        
        # Draw content
        draw = ImageDraw.Draw(img)
        
        # Add "PREVOST" text at top
        draw.text((width//2, 50), "PREVOST", font=self.font_large, fill='white', anchor='mt')
        
        # Add converter and model
        if converter and converter != 'Unknown':
            draw.text((width//2, 120), converter.upper(), font=self.font_medium, fill='white', anchor='mt')
        
        if model and model != 'Unknown':
            draw.text((width//2, 170), model, font=self.font_small, fill='lightgray', anchor='mt')
        
        # Add year in large text
        if year and year > 0:
            draw.text((width//2, height//2), str(year), font=self.font_large, fill='white', anchor='mm')
        
        # Add "Image Coming Soon" at bottom
        draw.text((width//2, height - 80), "Image Coming Soon", font=self.font_small, fill='lightgray', anchor='mb')
        
        # Add coach ID in corner
        draw.text((10, height - 10), f"ID: {coach_id}", font=self.font_small, fill='gray', anchor='lb')
        
        # Save image
        filename = f"{coach_id}_placeholder.jpg"
        filepath = os.path.join(self.images_dir, filename)
        img.save(filepath, 'JPEG', quality=85)
        
        return f"/coach-images/{filename}"
    
    def generate_for_all_coaches(self):
        """Generate placeholders for all coaches without images"""
        conn = sqlite3.connect('prevostgo.db')
        cursor = conn.cursor()
        
        # Get all coaches without images
        cursor.execute("""
            SELECT id, title, year, converter, model 
            FROM coaches 
            WHERE status = 'available'
            AND (images = '[]' OR images IS NULL)
        """)
        
        coaches = cursor.fetchall()
        print(f"Generating placeholders for {len(coaches)} coaches...")
        
        updated = 0
        for i, (coach_id, title, year, converter, model) in enumerate(coaches):
            try:
                # Generate placeholder
                placeholder_path = self.create_placeholder(coach_id, title, year, converter, model)
                
                # Update database
                cursor.execute("""
                    UPDATE coaches 
                    SET images = ? 
                    WHERE id = ?
                """, (json.dumps([placeholder_path]), coach_id))
                
                updated += 1
                
                if (i + 1) % 10 == 0:
                    print(f"  Generated {i + 1}/{len(coaches)} placeholders...")
                    
            except Exception as e:
                print(f"  Error generating placeholder for {coach_id}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Generated {updated} placeholder images")
        return updated

def main():
    # Check if PIL is installed
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ERROR: Pillow library not installed!")
        print("Install it with: pip install Pillow")
        return
    
    generator = PlaceholderGenerator()
    
    print("Placeholder Image Generator")
    print("=" * 40)
    print("\nThis will create placeholder images for coaches without photos.")
    print("Placeholders will be unique based on coach information.")
    
    confirm = input("\nGenerate placeholders for all coaches? (y/n): ").strip().lower()
    
    if confirm == 'y':
        generator.generate_for_all_coaches()
        print("\nPlaceholders have been created!")
        print("Refresh your frontend to see them.")
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()
