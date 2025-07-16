import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Direct SQLite connection (not async for testing)
engine = create_engine("sqlite:///prevostgo.db")
Session = sessionmaker(bind=engine)

def test_direct_query():
    with Session() as session:
        # Get a coach directly
        result = session.execute(text("SELECT * FROM coaches WHERE status = 'available' LIMIT 1"))
        coach = result.fetchone()
        
        if coach:
            print("Found coach:")
            print(f"ID: {coach.id}")
            print(f"Title: {coach.title}")
            print(f"Images: {coach.images}")
            print(f"Features: {coach.features}")
            
            # Check if JSON fields need parsing
            if isinstance(coach.images, str):
                print("\nImages is a string, parsing...")
                images = json.loads(coach.images) if coach.images else []
                print(f"Parsed images: {images}")
            
            if isinstance(coach.features, str):
                print("\nFeatures is a string, parsing...")
                features = json.loads(coach.features) if coach.features else []
                print(f"Parsed features: {features}")
                
            # Check all fields
            print("\nAll columns:")
            for key, value in coach._mapping.items():
                print(f"{key}: {value} (type: {type(value).__name__})")
        else:
            print("No coaches found")

if __name__ == "__main__":
    test_direct_query()
