"""
Inventory router with sync database operations for compatibility
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import json

from app.models.database import get_sync_db, Coach, Analytics
from app.models.schemas import CoachResponse

router = APIRouter()

@router.get("/{coach_id}")
def get_coach(
    coach_id: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """Get single coach by ID using sync operations"""
    try:
        # Get coach
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
        
        # Create response
        response = {
            "id": coach.id,
            "title": coach.title,
            "year": coach.year,
            "model": coach.model,
            "chassis_type": coach.chassis_type,
            "converter": coach.converter,
            "condition": coach.condition,
            "price": coach.price // 100 if coach.price else None,
            "price_display": coach.price_display,
            "price_status": coach.price_status,
            "mileage": coach.mileage,
            "engine": coach.engine,
            "slide_count": coach.slide_count,
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
            "source": coach.source,
            "status": coach.status,
            "scraped_at": coach.scraped_at,
            "updated_at": coach.updated_at,
            "views": coach.views,
            "inquiries": coach.inquiries
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching coach {coach_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching coach details: {str(e)}")