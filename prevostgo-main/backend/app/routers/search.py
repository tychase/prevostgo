"""
Search and filtering router with search alerts
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Dict, Any
import json

from app.models.database import get_db, Coach, Lead, SearchAlert
from app.models.schemas import (
    SearchFilters, CoachResponse, SearchAlertCreate, 
    SearchAlertResponse, CoachListResponse
)

router = APIRouter()

def build_search_query(filters: SearchFilters, base_query=None):
    """Build SQLAlchemy query from search filters"""
    if base_query is None:
        query = select(Coach).where(Coach.status == "available")
    else:
        query = base_query
        
    # Price filters (convert dollars to cents)
    if filters.price_min is not None:
        query = query.where(Coach.price >= filters.price_min * 100)
    if filters.price_max is not None:
        query = query.where(Coach.price <= filters.price_max * 100)
        
    # Year filters
    if filters.year_min is not None:
        query = query.where(Coach.year >= filters.year_min)
    if filters.year_max is not None:
        query = query.where(Coach.year <= filters.year_max)
        
    # Mileage filter
    if filters.mileage_max is not None:
        query = query.where(Coach.mileage <= filters.mileage_max)
        
    # Model filters
    if filters.models:
        query = query.where(Coach.model.in_(filters.models))
        
    # Converter filters
    if filters.converters:
        query = query.where(Coach.converter.in_(filters.converters))
        
    # Slide count filters
    if filters.slide_counts:
        query = query.where(Coach.slide_count.in_(filters.slide_counts))
        
    # Condition filters
    if filters.conditions:
        query = query.where(Coach.condition.in_(filters.conditions))
        
    # Dealer state filters
    if filters.dealer_states:
        query = query.where(Coach.dealer_state.in_(filters.dealer_states))
        
    # Feature filters (using JSON contains)
    if filters.must_have_features:
        for feature in filters.must_have_features:
            query = query.where(Coach.features.contains([feature]))
            
    # Sorting
    sort_column = getattr(Coach, filters.sort_by, Coach.price)
    if filters.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column)
        
    return query

@router.post("/coaches", response_model=CoachListResponse)
async def search_coaches(
    filters: SearchFilters,
    db: AsyncSession = Depends(get_db)
):
    """Search coaches with advanced filters"""
    
    # Build query
    query = build_search_query(filters)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page)
    
    # Execute query
    result = await db.execute(query)
    coaches = result.scalars().all()
    
    # Convert prices from cents to dollars
    coach_responses = []
    for coach in coaches:
        coach_dict = coach.__dict__.copy()
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
        coach_responses.append(CoachResponse(**coach_dict))
        
    return CoachListResponse(
        total=total,
        page=filters.page,
        per_page=filters.per_page,
        coaches=coach_responses
    )

@router.get("/suggestions")
async def get_search_suggestions(
    q: str,
    field: str = "all",  # all, model, converter, location
    db: AsyncSession = Depends(get_db)
):
    """Get search suggestions for autocomplete"""
    
    suggestions = []
    
    if field in ["all", "model"]:
        # Get model suggestions
        model_query = select(Coach.model).distinct().where(
            and_(
                Coach.model.ilike(f"%{q}%"),
                Coach.model.isnot(None)
            )
        ).limit(5)
        model_result = await db.execute(model_query)
        models = model_result.scalars().all()
        suggestions.extend([{"type": "model", "value": m} for m in models])
        
    if field in ["all", "converter"]:
        # Get converter suggestions
        converter_query = select(Coach.converter).distinct().where(
            and_(
                Coach.converter.ilike(f"%{q}%"),
                Coach.converter.isnot(None)
            )
        ).limit(5)
        converter_result = await db.execute(converter_query)
        converters = converter_result.scalars().all()
        suggestions.extend([{"type": "converter", "value": c} for c in converters])
        
    if field in ["all", "location"]:
        # Get location suggestions
        location_query = select(Coach.dealer_state).distinct().where(
            and_(
                Coach.dealer_state.ilike(f"%{q}%"),
                Coach.dealer_state.isnot(None)
            )
        ).limit(5)
        location_result = await db.execute(location_query)
        locations = location_result.scalars().all()
        suggestions.extend([{"type": "location", "value": l} for l in locations])
        
    return {"suggestions": suggestions[:10]}  # Limit total suggestions

@router.get("/facets")
async def get_search_facets(
    db: AsyncSession = Depends(get_db)
):
    """Get available facets for search filters"""
    
    # Get all available coaches
    coaches_query = select(Coach).where(Coach.status == "available")
    result = await db.execute(coaches_query)
    coaches = result.scalars().all()
    
    # Build facets
    facets = {
        "models": {},
        "converters": {},
        "years": {},
        "slide_counts": {},
        "conditions": {},
        "dealer_states": {},
        "price_ranges": {
            "under_200k": 0,
            "200k_500k": 0,
            "500k_1m": 0,
            "over_1m": 0
        },
        "features": {}
    }
    
    for coach in coaches:
        # Models
        if coach.model:
            facets["models"][coach.model] = facets["models"].get(coach.model, 0) + 1
            
        # Converters
        if coach.converter:
            facets["converters"][coach.converter] = facets["converters"].get(coach.converter, 0) + 1
            
        # Years
        if coach.year:
            year_str = str(coach.year)
            facets["years"][year_str] = facets["years"].get(year_str, 0) + 1
            
        # Slide counts
        slide_str = str(coach.slide_count)
        facets["slide_counts"][slide_str] = facets["slide_counts"].get(slide_str, 0) + 1
        
        # Conditions
        if coach.condition:
            facets["conditions"][coach.condition] = facets["conditions"].get(coach.condition, 0) + 1
            
        # Dealer states
        if coach.dealer_state:
            facets["dealer_states"][coach.dealer_state] = facets["dealer_states"].get(coach.dealer_state, 0) + 1
            
        # Price ranges
        if coach.price:
            price_dollars = coach.price // 100
            if price_dollars < 200000:
                facets["price_ranges"]["under_200k"] += 1
            elif price_dollars < 500000:
                facets["price_ranges"]["200k_500k"] += 1
            elif price_dollars < 1000000:
                facets["price_ranges"]["500k_1m"] += 1
            else:
                facets["price_ranges"]["over_1m"] += 1
                
        # Features
        if coach.features:
            for feature in coach.features:
                facets["features"][feature] = facets["features"].get(feature, 0) + 1
                
    return facets

@router.post("/alerts", response_model=SearchAlertResponse)
async def create_search_alert(
    alert_data: SearchAlertCreate,
    lead_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create search alert for a lead"""
    
    # Verify lead exists
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id)
    )
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Create alert
    alert = SearchAlert(
        lead_id=lead_id,
        criteria=alert_data.criteria.model_dump(),
        frequency=alert_data.frequency
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return SearchAlertResponse.model_validate(alert)

@router.get("/alerts/{alert_id}", response_model=SearchAlertResponse)
async def get_search_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get search alert by ID"""
    
    result = await db.execute(
        select(SearchAlert).where(SearchAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    return SearchAlertResponse.model_validate(alert)

@router.put("/alerts/{alert_id}/toggle")
async def toggle_search_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Toggle search alert active status"""
    
    result = await db.execute(
        select(SearchAlert).where(SearchAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.active = not alert.active
    await db.commit()
    
    return {
        "success": True,
        "active": alert.active,
        "message": f"Alert {'activated' if alert.active else 'deactivated'}"
    }

@router.delete("/alerts/{alert_id}")
async def delete_search_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete search alert"""
    
    result = await db.execute(
        select(SearchAlert).where(SearchAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    await db.delete(alert)
    await db.commit()
    
    return {"success": True, "message": "Alert deleted"}

@router.get("/alerts/lead/{lead_id}", response_model=List[SearchAlertResponse])
async def get_lead_alerts(
    lead_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts for a lead"""
    
    query = select(SearchAlert).where(SearchAlert.lead_id == lead_id)
    
    if active_only:
        query = query.where(SearchAlert.active == True)
        
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return [SearchAlertResponse.model_validate(alert) for alert in alerts]

@router.post("/similar/{coach_id}", response_model=List[CoachResponse])
async def find_similar_coaches(
    coach_id: str,
    limit: int = 6,
    db: AsyncSession = Depends(get_db)
):
    """Find similar coaches based on characteristics"""
    
    # Get the reference coach
    ref_result = await db.execute(
        select(Coach).where(Coach.id == coach_id)
    )
    ref_coach = ref_result.scalar_one_or_none()
    
    if not ref_coach:
        raise HTTPException(status_code=404, detail="Coach not found")
        
    # Build similarity query
    # Priority: same model > same converter > similar price > similar year
    query = select(Coach).where(
        and_(
            Coach.status == "available",
            Coach.id != coach_id  # Exclude the reference coach
        )
    )
    
    # Score-based ordering
    # Same model: +10 points
    # Same converter: +8 points
    # Similar price (±20%): +6 points
    # Similar year (±3 years): +4 points
    # Same slide count: +2 points
    
    # For now, simple approach - prioritize same model/converter
    similar_coaches = []
    
    # First, same model and converter
    exact_match_query = query.where(
        and_(
            Coach.model == ref_coach.model,
            Coach.converter == ref_coach.converter
        )
    ).limit(limit)
    
    exact_result = await db.execute(exact_match_query)
    similar_coaches.extend(exact_result.scalars().all())
    
    if len(similar_coaches) < limit:
        # Then, same model
        model_match_query = query.where(
            and_(
                Coach.model == ref_coach.model,
                Coach.converter != ref_coach.converter
            )
        ).limit(limit - len(similar_coaches))
        
        model_result = await db.execute(model_match_query)
        similar_coaches.extend(model_result.scalars().all())
        
    if len(similar_coaches) < limit:
        # Then, same converter
        converter_match_query = query.where(
            and_(
                Coach.converter == ref_coach.converter,
                Coach.model != ref_coach.model
            )
        ).limit(limit - len(similar_coaches))
        
        converter_result = await db.execute(converter_match_query)
        similar_coaches.extend(converter_result.scalars().all())
        
    # Convert prices
    coach_responses = []
    for coach in similar_coaches[:limit]:
        coach_dict = coach.__dict__.copy()
        if coach_dict.get('price'):
            coach_dict['price'] = coach_dict['price'] // 100
        coach_responses.append(CoachResponse(**coach_dict))
        
    return coach_responses
