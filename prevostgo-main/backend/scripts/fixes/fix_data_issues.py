import sqlite3
import re

def fix_data_issues():
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    # Converter mappings
    converter_map = {
        'marathon': 'Marathon',
        'liberty': 'Liberty', 
        'royale': 'Royale',
        'millennium': 'Millennium',
        'millenium': 'Millennium',
        'country': 'Country Coach',
        'country coach': 'Country Coach',
        'featherlite': 'Featherlite',
        'angola': 'Angola',
        'florida': 'Florida Coach',
        'parliament': 'Parliament',
        'vantare': 'Vantare',
        'outlaw': 'Outlaw',
        'show coaches': 'Show Coaches'
    }
    
    # Model standardization
    model_map = {
        'h345': 'H3-45',
        'h3 45': 'H3-45',
        'h3-45': 'H3-45',
        'xlii': 'XLII',
        'xl2': 'XLII',
        'xl': 'XL',
        'x3': 'X3-45',
        'x345': 'X3-45',
        'x3-45': 'X3-45'
    }
    
    print("Fixing data issues...")
    
    # Fix converters
    converter_fixes = 0
    cursor.execute("SELECT id, converter FROM coaches WHERE status = 'available'")
    for coach_id, converter in cursor.fetchall():
        if converter:
            normalized = converter.lower().strip()
            if normalized in converter_map and converter_map[normalized] != converter:
                cursor.execute(
                    "UPDATE coaches SET converter = ? WHERE id = ?",
                    (converter_map[normalized], coach_id)
                )
                converter_fixes += 1
    
    # Fix models
    model_fixes = 0
    cursor.execute("SELECT id, model FROM coaches WHERE status = 'available'")
    for coach_id, model in cursor.fetchall():
        if model:
            normalized = model.lower().replace('-', '').replace(' ', '')
            if normalized in model_map and model_map[normalized] != model:
                cursor.execute(
                    "UPDATE coaches SET model = ? WHERE id = ?",
                    (model_map[normalized], coach_id)
                )
                model_fixes += 1
    
    # Fix prices (convert from dollars to cents if needed)
    price_fixes = 0
    cursor.execute("SELECT id, price FROM coaches WHERE status = 'available' AND price IS NOT NULL")
    for coach_id, price in cursor.fetchall():
        if price and price < 10000:  # Likely in dollars, not cents
            cursor.execute(
                "UPDATE coaches SET price = ? WHERE id = ?",
                (price * 100, coach_id)
            )
            price_fixes += 1
    
    # Fix empty converters by extracting from title
    empty_converter_fixes = 0
    cursor.execute("SELECT id, title, converter FROM coaches WHERE status = 'available' AND (converter = '' OR converter IS NULL)")
    for coach_id, title, converter in cursor.fetchall():
        title_lower = title.lower()
        for key, value in converter_map.items():
            if key in title_lower:
                cursor.execute(
                    "UPDATE coaches SET converter = ? WHERE id = ?",
                    (value, coach_id)
                )
                empty_converter_fixes += 1
                break
    
    conn.commit()
    
    print(f"\nFixes applied:")
    print(f"  Converter standardization: {converter_fixes}")
    print(f"  Model standardization: {model_fixes}")
    print(f"  Price corrections: {price_fixes}")
    print(f"  Empty converters fixed: {empty_converter_fixes}")
    
    # Show updated statistics
    cursor.execute("SELECT COUNT(*) FROM coaches WHERE status = 'available' AND (converter = '' OR converter IS NULL)")
    empty_converters = cursor.fetchone()[0]
    print(f"\nRemaining coaches with empty converters: {empty_converters}")
    
    conn.close()

if __name__ == "__main__":
    fix_data_issues()