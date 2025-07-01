"""
Minimal FastAPI app to test the inventory endpoint
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select, or_, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List
import json

Base = declarative_base()

# Import the Coach model
from app.models.database import Coach

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create sync engine for testing
engine = create_engine("sqlite:///prevostgo.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test/inventory")
def test_inventory(
    search: Optional[str] = None,
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: Session = next(get_db())
):
    """Simple sync endpoint to test inventory"""
    try:
        # Build query
        query = db.query(Coach).filter(Coach.status == "available")
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Coach.title.ilike(search_term),
                    Coach.model.ilike(search_term),
                    Coach.converter.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        coaches = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict
        coaches_data = []
        for coach in coaches:
            coach_dict = {
                "id": coach.id,
                "title": coach.title,
                "year": coach.year,
                "model": coach.model,
                "converter": coach.converter,
                "price": coach.price // 100 if coach.price else None,
                "price_display": coach.price_display,
                "condition": coach.condition,
                "status": coach.status
            }
            coaches_data.append(coach_dict)
        
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "coaches": coaches_data
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/test/health")
def test_health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal test server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
