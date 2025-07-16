"""
Fix for async database issues in production
This script updates the inventory router to handle both async and sync sessions properly
"""

import os
import shutil

def fix_inventory_router():
    """Create a fixed version of the inventory router"""
    
    fixed_content = '''"""
Inventory router for coach listings - Fixed for async/sync compatibility
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, String, nullslast, nullsfirst, text
from typing import List, Optional, Union
import json

from app.models.database import get_db, get_sync_db, Coach, Analytics
from app.models.schemas import (
    CoachResponse, CoachListResponse, CoachUpdate,
    SearchFilters, InventorySummary, AnalyticsEvent
)
from app.services.scraper import PrevostInventoryScraper
from app.services.scraper_enhanced import EnhancedPrevostInventoryScraper

router = APIRouter()

# Keep all other endpoints as they are...
# (pagination, summary, etc.)

@router.get("/{coach_id}")
async def get_coach(
    coach_id: str,
    session_id: Optional[str] = None,
    db: Union[AsyncSession, Session] = Depends(get_db)
):
    """Get single coach by ID - handles both async and sync sessions"""
    try:
        # Use raw SQL for maximum compatibility
        if hasattr(db, 'execute'):
            # Try async first
            try:
                # Use text() for raw SQL
                query = text("""
                    SELECT 
                        id, title, year, model, chassis_type, converter, condition,
                        price, price_display, price_status, mileage, engine, slide_count,
                        features, bathroom_config, stock_number, images, virtual_tour_url,
                        dealer_name, dealer_state, dealer_phone, dealer_email, listing_url,
                        source, status, scraped_at, updated_at, views, inquiries
                    FROM coaches 
                    WHERE id = :coach_id
                """)
                
                result = await db.execute(query, {"coach_id": coach_id})
                coach_row = result.fetchone()
                
                if not coach_row:
                    raise HTTPException(status_code=404, detail="Coach not found")
                
                # Update views
                update_query = text("UPDATE coaches SET views = COALESCE(views, 0) + 1 WHERE id = :coach_id")
                await db.execute(update_query, {"coach_id": coach_id})
                
                # Log analytics
                insert_query = text("""
                    INSERT INTO analytics (event_type, coach_id, session_id, event_data, created_at)
                    VALUES (:event_type, :coach_id, :session_id, :event_data, CURRENT_TIMESTAMP)
                """)
                await db.execute(insert_query, {
                    "event_type": "view",
                    "coach_id": coach_id,
                    "session_id": session_id,
                    "event_data": json.dumps({"source": "api"})
                })
                
                await db.commit()
                
                # Convert row to dict
                coach_dict = dict(coach_row._mapping)
                
            except Exception as async_error:
                # If async fails, try sync
                print(f"Async query failed, trying sync: {async_error}")
                db.rollback() if hasattr(db, 'rollback') else None
                
                # Sync fallback
                coach = db.query(Coach).filter(Coach.id == coach_id).first()
                if not coach:
                    raise HTTPException(status_code=404, detail="Coach not found")
                
                coach.views = (coach.views or 0) + 1
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
                    "price": coach.price,
                    "price_display": coach.price_display,
                    "price_status": coach.price_status,
                    "mileage": coach.mileage,
                    "engine": coach.engine,
                    "slide_count": coach.slide_count,
                    "features": coach.features,
                    "bathroom_config": coach.bathroom_config,
                    "stock_number": coach.stock_number,
                    "images": coach.images,
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
        else:
            # Pure sync session
            coach = db.query(Coach).filter(Coach.id == coach_id).first()
            if not coach:
                raise HTTPException(status_code=404, detail="Coach not found")
            
            coach.views = (coach.views or 0) + 1
            analytics = Analytics(
                event_type="view",
                coach_id=coach_id,
                session_id=session_id,
                event_data={"source": "api"}
            )
            db.add(analytics)
            db.commit()
            
            coach_dict = {
                "id": coach.id,
                "title": coach.title,
                "year": coach.year,
                "model": coach.model,
                "chassis_type": coach.chassis_type,
                "converter": coach.converter,
                "condition": coach.condition,
                "price": coach.price,
                "price_display": coach.price_display,
                "price_status": coach.price_status,
                "mileage": coach.mileage,
                "engine": coach.engine,
                "slide_count": coach.slide_count,
                "features": coach.features,
                "bathroom_config": coach.bathroom_config,
                "stock_number": coach.stock_number,
                "images": coach.images,
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
        
        # Parse JSON fields if they're strings
        if isinstance(coach_dict.get('features'), str):
            try:
                coach_dict['features'] = json.loads(coach_dict['features'])
            except:
                coach_dict['features'] = []
        
        if isinstance(coach_dict.get('images'), str):
            try:
                coach_dict['images'] = json.loads(coach_dict['images'])
            except:
                coach_dict['images'] = []
        
        # Convert price from cents to dollars
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
        
        # Ensure lists are not None
        coach_dict['features'] = coach_dict.get('features') or []
        coach_dict['images'] = coach_dict.get('images') or []
        
        return coach_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching coach {coach_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching coach details: {str(e)}")

# Include the rest of the router endpoints here...
'''
    
    # Backup original file
    original_path = "app/routers/inventory.py"
    backup_path = "app/routers/inventory_backup.py"
    
    if os.path.exists(original_path):
        shutil.copy(original_path, backup_path)
        print(f"Backed up {original_path} to {backup_path}")
    
    # Write the fixed content (partial - you'd need to copy other endpoints)
    print("Fix created. To apply:")
    print("1. Copy the get_coach endpoint from above")
    print("2. Replace the existing get_coach endpoint in app/routers/inventory.py")
    print("3. Deploy to Railway")

if __name__ == "__main__":
    fix_inventory_router()