"""
Emergency fix for inventory router to use PostgreSQL instead of SQLite
This replaces the get_coach function that's hardcoded to use SQLite
"""

from fastapi import HTTPException
from sqlalchemy import select
from app.models.database import Coach, Analytics, SessionLocal
import json
from datetime import datetime

async def get_coach_fixed(coach_id: str, session_id: str = None):
    """Fixed version that uses PostgreSQL"""
    db = SessionLocal()
    try:
        # Get coach using SQLAlchemy
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Update views
        coach.views = (coach.views or 0) + 1
        
        # Log analytics event
        analytics = Analytics(
            event_type="view",
            coach_id=coach_id,
            session_id=session_id,
            event_data={"source": "api"}
        )
        db.add(analytics)
        db.commit()
        
        # Convert to dict
        coach_dict = {
            "id": coach.id,
            "title": coach.title,
            "year": coach.year,
            "model": coach.model,
            "chassis_type": coach.chassis_type,
            "converter": coach.converter,
            "condition": coach.condition,
            "price": coach.price // 100 if coach.price else None,
            "price_display": coach.price_display,
            "price_status": coach.price_status or 'contact_for_price',
            "mileage": coach.mileage,
            "engine": coach.engine,
            "slide_count": coach.slide_count or 0,
            "features": coach.features or [],
            "bathroom_config": coach.bathroom_config,
            "stock_number": coach.stock_number,
            "images": coach.images or [],
            "virtual_tour_url": coach.virtual_tour_url,
            "dealer_name": coach.dealer_name,
            "dealer_state": coach.dealer_state,
            "dealer_phone": coach.dealer_phone,
            "dealer_email": coach.dealer_email,
            "listing_url": coach.listing_url,
            "source": coach.source or 'prevost-stuff.com',
            "status": coach.status or 'available',
            "scraped_at": coach.scraped_at,
            "updated_at": coach.updated_at,
            "views": coach.views or 0,
            "inquiries": coach.inquiries or 0
        }
        
        return coach_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching coach {coach_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching coach details: {str(e)}")
    finally:
        db.close()

# Add this to the router file to replace the broken function
