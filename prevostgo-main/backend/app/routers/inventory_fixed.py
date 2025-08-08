"""
Fixed inventory router with proper JSON handling
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, String, text
from typing import List, Optional
import json

from app.models.database import get_db, Coach, Analytics
from app.models.schemas import (
    CoachResponse, CoachListResponse, CoachUpdate,
    SearchFilters, InventorySummary, AnalyticsEvent
)

router = APIRouter()

def parse_json_field(value):
    """Parse JSON field that might be stored as string"""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            return []
    return value

@router.get("/{coach_id}")
async def get_coach(
    coach_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get single coach by ID"""
    
    # Use raw SQL for better control
    query = text("""
        SELECT * FROM coaches WHERE id = :coach_id
    """)
    
    result = await db.execute(query, {"coach_id": coach_id})
    coach_row = result.fetchone()
    
    if not coach_row:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    # Convert row to dict
    coach_data = dict(coach_row._mapping)
    
    # Parse JSON fields
    coach_data['images'] = parse_json_field(coach_data.get('images'))
    coach_data['features'] = parse_json_field(coach_data.get('features'))
    
    # Convert price from cents to dollars
    if coach_data.get('price'):
        coach_data['price'] = coach_data['price'] // 100
    
    # Track view
    await db.execute(
        text("UPDATE coaches SET views = views + 1 WHERE id = :coach_id"),
        {"coach_id": coach_id}
    )
    await db.commit()
    
    return coach_data
