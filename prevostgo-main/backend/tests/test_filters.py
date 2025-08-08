import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text, or_
from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Testing Updated Filters:")
    
    # Test converter filter (Marathon)
    print("\n1. Testing converter filter for 'Marathon':")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM coaches 
        WHERE status = 'available' 
        AND title ILIKE '%Marathon%'
    """))
    count = result.scalar()
    print(f"   Found: {count} coaches")
    
    # Show sample
    result = conn.execute(text("""
        SELECT id, title, price FROM coaches 
        WHERE status = 'available' 
        AND title ILIKE '%Marathon%'
        LIMIT 3
    """))
    for row in result:
        price = f"${row.price // 100:,}" if row.price else "Contact for Price"
        print(f"   - {row.title} - {price}")
    
    # Test model filter (H3)
    print("\n2. Testing model filter for 'H3':")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM coaches 
        WHERE status = 'available' 
        AND (model ILIKE '%H3%' OR title ILIKE '%H3%')
    """))
    count = result.scalar()
    print(f"   Found: {count} coaches")
    
    # Test combined filters
    print("\n3. Testing combined filters (price < $1M AND model contains 'H3'):")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM coaches 
        WHERE status = 'available' 
        AND price < 1000000 * 100
        AND (model ILIKE '%H3%' OR title ILIKE '%H3%')
    """))
    count = result.scalar()
    print(f"   Found: {count} coaches")
    
    # Test price ranges with actual data
    print("\n4. Coaches with actual prices (not NULL):")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM coaches 
        WHERE status = 'available' 
        AND price IS NOT NULL
    """))
    count = result.scalar()
    print(f"   Found: {count} coaches with prices")