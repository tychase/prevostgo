from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from typing import List, Optional, Dict, Any
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/coaches", tags=["coaches"])

@router.get("/search", response_model=List[schemas.CoachOut])
def search_coaches(
    q: Optional[str] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    chassis: Optional[str] = None,
    converter: Optional[str] = None,
    sort: str = "relevance",
    page: int = 1,
    page_size: int = 24,
    db: Session = Depends(get_db),
):
    stmt = select(models.Coach).where(models.Coach.is_active == True)

    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(
            models.Coach.title.ilike(like),
            models.Coach.model.ilike(like),
            func.cast(models.Coach.year, models.String).ilike(like),
        ))

    if min_year is not None:
        stmt = stmt.where(models.Coach.year >= min_year)
    if max_year is not None:
        stmt = stmt.where(models.Coach.year <= max_year)
    if min_price is not None:
        stmt = stmt.where(models.Coach.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(models.Coach.price <= max_price)

    # facets from specs JSONB (chassis, converter)
    if chassis:
        stmt = stmt.where(func.lower(func.cast(models.Coach.specs["chassis"], models.String)) == chassis.lower())
    if converter:
        stmt = stmt.where(func.lower(func.cast(models.Coach.specs["converter"], models.String)) == converter.lower())

    # sorting
    if sort == "price_asc":
        stmt = stmt.order_by(models.Coach.price.asc().nullslast())
    elif sort == "price_desc":
        stmt = stmt.order_by(models.Coach.price.desc().nullslast())
    elif sort == "year_desc":
        stmt = stmt.order_by(models.Coach.year.desc().nullslast())
    elif sort == "year_asc":
        stmt = stmt.order_by(models.Coach.year.asc().nullslast())
    else:
        # "relevance": basic heuristic: newer + priced items first
        stmt = stmt.order_by(models.Coach.year.desc().nullslast(), models.Coach.price.desc().nullslast())

    # pagination
    stmt = stmt.offset((page-1)*page_size).limit(page_size)

    items = db.scalars(stmt).all()
    return items
