"""
Inventory router for coach listings
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, String, nullslast, nullsfirst
from typing import List, Optional

from app.models.database import get_db, Coach, Analytics
from app.models.schemas import (
    CoachResponse, CoachListResponse, CoachUpdate,
    SearchFilters, InventorySummary, AnalyticsEvent
)
from app.services.scraper import PrevostInventoryScraper

router = APIRouter()

@router.get("/", response_model=CoachListResponse)
async def get_coaches(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    mileage_max: Optional[int] = None,
    model: Optional[str] = None,
    chassis: Optional[str] = None,
    converter: Optional[str] = None,
    slide_count: Optional[int] = None,
    condition: Optional[str] = None,
    dealer_state: Optional[str] = None,
    sort_by: str = Query("price", regex="^(price|year|mileage|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of coaches with filters"""
    
    # Build query
    query = select(Coach).where(Coach.status == "available")
    
    # Apply text search if provided
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Coach.title.ilike(search_term),
                Coach.model.ilike(search_term),
                Coach.converter.ilike(search_term)
                # Removed features search as it might cause issues with JSON column
            )
        )
    
    # Apply filters
    if price_min is not None:
        query = query.where(Coach.price >= price_min * 100)  # Convert to cents
    if price_max is not None:
        query = query.where(Coach.price <= price_max * 100)
        
    if year_min is not None:
        query = query.where(Coach.year >= year_min)
    if year_max is not None:
        query = query.where(Coach.year <= year_max)
        
    if mileage_max is not None:
        query = query.where(Coach.mileage <= mileage_max)
        
    if model:
        # Use partial matching for model
        model_term = f"%{model}%"
        query = query.where(Coach.model.ilike(model_term))
    
    if chassis:
        # Use partial matching for chassis types
        # Check both chassis_type and model columns as chassis info might be in either
        chassis_term = f"%{chassis}%"
        query = query.where(
            or_(
                Coach.chassis_type.ilike(chassis_term),
                Coach.model.ilike(chassis_term)
            )
        )
    
    if converter:
        # Use partial matching for converter to handle variations
        converter_term = f"%{converter}%"
        query = query.where(Coach.converter.ilike(converter_term))
        
    if slide_count is not None:
        query = query.where(Coach.slide_count == slide_count)
        
    if condition:
        query = query.where(Coach.condition == condition)
        
    if dealer_state:
        query = query.where(Coach.dealer_state == dealer_state)
        
    # Apply sorting with special handling for price
    if sort_by == "price":
        # Sort by price, but put NULL prices (Contact for Price) at the end
        sort_column = Coach.price
        if sort_order == "desc":
            # For descending, we want high prices first, then NULL at the end
            query = query.order_by(nullslast(sort_column.desc()))
        else:
            # For ascending, we want low prices first, then NULL at the end
            query = query.order_by(nullslast(sort_column))
    else:
        # Regular sorting for other columns
        sort_column = getattr(Coach, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column)
        
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    coaches = result.scalars().all()
    
    # Convert prices from cents to dollars for response
    coach_responses = []
    for coach in coaches:
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
        try:
            coach_responses.append(CoachResponse(**coach_dict))
        except Exception as e:
            print(f"Error converting coach {coach.id}: {e}")
            # Skip coaches that can't be converted
            continue
    
    return CoachListResponse(
        total=total,
        page=page,
        per_page=per_page,
        coaches=coach_responses
    )

@router.get("/summary", response_model=InventorySummary)
async def get_inventory_summary(db: AsyncSession = Depends(get_db)):
    """Get inventory summary statistics"""
    
    # Get all available coaches
    result = await db.execute(
        select(Coach).where(Coach.status == "available")
    )
    coaches = result.scalars().all()
    
    # Calculate statistics
    summary = {
        "total_coaches": len(coaches),
        "by_condition": {},
        "by_model": {},
        "by_converter": {},
        "by_year": {},
        "price_ranges": {
            "under_200k": 0,
            "200k_500k": 0,
            "500k_1m": 0,
            "over_1m": 0,
            "contact_for_price": 0
        }
    }
    
    for coach in coaches:
        # By condition
        condition = coach.condition or "unknown"
        summary["by_condition"][condition] = summary["by_condition"].get(condition, 0) + 1
        
        # By model
        model = coach.model or "unknown"
        summary["by_model"][model] = summary["by_model"].get(model, 0) + 1
        
        # By converter
        converter = coach.converter or "unknown"
        summary["by_converter"][converter] = summary["by_converter"].get(converter, 0) + 1
        
        # By year
        year = str(coach.year) if coach.year else "unknown"
        summary["by_year"][year] = summary["by_year"].get(year, 0) + 1
        
        # Price ranges (convert from cents)
        if coach.price is None:
            summary["price_ranges"]["contact_for_price"] += 1
        else:
            price_dollars = coach.price // 100
            if price_dollars < 200000:
                summary["price_ranges"]["under_200k"] += 1
            elif price_dollars < 500000:
                summary["price_ranges"]["200k_500k"] += 1
            elif price_dollars < 1000000:
                summary["price_ranges"]["500k_1m"] += 1
            else:
                summary["price_ranges"]["over_1m"] += 1
                
    return InventorySummary(**summary)

@router.get("/{coach_id}")
def get_coach(
    coach_id: str,
    session_id: Optional[str] = None
):
    """Get single coach by ID - using synchronous SQLite for now"""
    import sqlite3
    import json
    
    try:
        # Use direct SQLite connection to avoid async issues
        conn = sqlite3.connect('prevostgo.db')
        cursor = conn.cursor()
        
        # Get coach
        cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        coach_dict = dict(zip(columns, row))
        
        # Update views
        cursor.execute("UPDATE coaches SET views = views + 1 WHERE id = ?", (coach_id,))
        
        # Log analytics event (simplified for now)
        cursor.execute(
            "INSERT INTO analytics (event_type, coach_id, session_id, event_data) VALUES (?, ?, ?, ?)",
            ("view", coach_id, session_id, json.dumps({"source": "api"}))
        )
        
        conn.commit()
        conn.close()
        
        # Parse JSON fields
        for field in ['images', 'features']:
            if coach_dict.get(field):
                try:
                    coach_dict[field] = json.loads(coach_dict[field])
                except:
                    coach_dict[field] = []
            else:
                coach_dict[field] = []
        
        # Convert price from cents to dollars
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
        
        # Normalize fields
        coach_dict['price_status'] = coach_dict.get('price_status') or 'contact_for_price'
        coach_dict['slide_count'] = coach_dict.get('slide_count') or 0
        
        # Validate email
        if coach_dict.get('dealer_email') and '@' not in str(coach_dict['dealer_email']):
            coach_dict['dealer_email'] = None
        
        # Normalize condition
        condition = str(coach_dict.get('condition', '')).lower()
        if 'new' in condition and 'pre' not in condition:
            coach_dict['condition'] = 'new'
        else:
            coach_dict['condition'] = 'pre-owned'
        
        # Create response
        response = {
            "id": coach_dict['id'],
            "title": coach_dict['title'],
            "year": coach_dict['year'],
            "model": coach_dict.get('model'),
            "chassis_type": coach_dict.get('chassis_type'),
            "converter": coach_dict.get('converter'),
            "condition": coach_dict['condition'],
            "price": coach_dict.get('price'),
            "price_display": coach_dict.get('price_display'),
            "price_status": coach_dict['price_status'],
            "mileage": coach_dict.get('mileage'),
            "engine": coach_dict.get('engine'),
            "slide_count": coach_dict['slide_count'],
            "features": coach_dict['features'],
            "bathroom_config": coach_dict.get('bathroom_config'),
            "stock_number": coach_dict.get('stock_number'),
            "images": coach_dict['images'],
            "virtual_tour_url": coach_dict.get('virtual_tour_url'),
            "dealer_name": coach_dict.get('dealer_name'),
            "dealer_state": coach_dict.get('dealer_state'),
            "dealer_phone": coach_dict.get('dealer_phone'),
            "dealer_email": coach_dict.get('dealer_email'),
            "listing_url": coach_dict.get('listing_url'),
            "source": coach_dict.get('source', 'prevost-stuff.com'),
            "status": coach_dict.get('status', 'available'),
            "scraped_at": coach_dict.get('scraped_at'),
            "updated_at": coach_dict.get('updated_at'),
            "views": coach_dict.get('views', 0),
            "inquiries": coach_dict.get('inquiries', 0)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching coach {coach_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching coach details: {str(e)}")

@router.put("/{coach_id}", response_model=CoachResponse)
async def update_coach(
    coach_id: str,
    update_data: CoachUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update coach listing (admin only - add auth later)"""
    
    result = await db.execute(
        select(Coach).where(Coach.id == coach_id)
    )
    coach = result.scalar_one_or_none()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
        
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    if 'price' in update_dict and update_dict['price'] is not None:
        update_dict['price'] = update_dict['price'] * 100  # Convert to cents
        
    for field, value in update_dict.items():
        setattr(coach, field, value)
        
    await db.commit()
    await db.refresh(coach)
    
    # Convert to response model
    coach_response = {
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
        
    return CoachResponse(**coach_response)

@router.get("/featured/listings", response_model=List[CoachResponse])
async def get_featured_coaches(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get featured coaches for homepage"""
    
    # For now, get newest high-end coaches
    # In production, you'd have a featured flag or algorithm
    query = select(Coach).where(
        and_(
            Coach.status == "available",
            Coach.price >= 100000000  # $1M+ in cents
        )
    ).order_by(Coach.scraped_at.desc()).limit(limit)
    
    result = await db.execute(query)
    coaches = result.scalars().all()
    
    # If not enough high-end, get newest
    if len(coaches) < limit:
        additional_query = select(Coach).where(
            Coach.status == "available"
        ).order_by(Coach.scraped_at.desc()).limit(limit - len(coaches))
        
        additional_result = await db.execute(additional_query)
        coaches.extend(additional_result.scalars().all())
        
    # Convert prices
    coach_responses = []
    for coach in coaches:
        coach_dict = coach.__dict__.copy()
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
        coach_responses.append(CoachResponse(**coach_dict))
        
    return coach_responses

@router.post("/track-event")
async def track_analytics_event(
    event: AnalyticsEvent,
    db: AsyncSession = Depends(get_db)
):
    """Track analytics events"""
    
    analytics = Analytics(
        event_type=event.event_type,
        coach_id=event.coach_id,
        lead_id=event.lead_id,
        event_data=event.event_data,
        session_id=event.session_id
    )
    
    db.add(analytics)
    await db.commit()
    
    return {"success": True, "message": "Event tracked"}

@router.post("/scrape")
async def trigger_scrape(
    fetch_details: bool = Query(True, description="Fetch detailed info for each listing"),
    limit: Optional[int] = Query(None, description="Limit number of coaches to scrape"),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger inventory scraper"""
    try:
        scraper = PrevostInventoryScraper()
        
        # Run the scraper
        listings = await scraper.scrape_inventory(fetch_details=fetch_details, limit=limit)
        
        # Save to database
        saved_count = await scraper.save_to_database(listings)
        
        return {
            "success": True,
            "message": f"Scraping completed successfully",
            "total_found": len(listings),
            "new_saved": saved_count,
            "details": {
                "fetch_details": fetch_details,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )
