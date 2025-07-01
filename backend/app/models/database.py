"""
Database models and configuration for PrevostGO
Using SQLAlchemy with async support
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
import os

# Database URL - using SQLite for simplicity, can switch to PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./prevostgo.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

class Coach(Base):
    """Coach inventory model"""
    __tablename__ = "coaches"
    
    id = Column(String, primary_key=True)  # Generated hash ID
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    model = Column(String)  # H3-45, XLII, X3, XL
    chassis_type = Column(String)
    converter = Column(String)  # Marathon, Liberty, Millennium, etc.
    condition = Column(String)  # new, pre-owned
    
    # Pricing
    price = Column(Integer)  # Stored in cents for precision
    price_display = Column(String)
    price_status = Column(String)  # available, contact_for_price
    
    # Specifications
    mileage = Column(Integer)
    engine = Column(String)
    slide_count = Column(Integer, default=0)
    
    # Features and details
    features = Column(JSON, default=list)
    bathroom_config = Column(String)
    stock_number = Column(String)
    
    # Media
    images = Column(JSON, default=list)
    virtual_tour_url = Column(String)
    
    # Dealer information
    dealer_name = Column(String)
    dealer_state = Column(String)
    dealer_phone = Column(String)
    dealer_email = Column(String)
    
    # Metadata
    listing_url = Column(String)
    source = Column(String, default="prevost-stuff.com")
    status = Column(String, default="available")  # available, sold, pending
    scraped_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    views = Column(Integer, default=0)
    inquiries = Column(Integer, default=0)

class Lead(Base):
    """Lead/inquiry model"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Contact information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    
    # Lead details
    budget_min = Column(Integer)
    budget_max = Column(Integer)
    timeframe = Column(String)  # immediate, 3_months, 6_months, planning
    financing_status = Column(String)  # cash, pre_approved, need_financing
    
    # Preferences
    preferred_models = Column(JSON, default=list)
    preferred_years = Column(JSON, default=list)
    must_have_features = Column(JSON, default=list)
    
    # Interest tracking
    coaches_viewed = Column(JSON, default=list)  # List of coach IDs
    coaches_inquired = Column(JSON, default=list)
    
    # Lead scoring
    score = Column(Integer, default=0)
    score_factors = Column(JSON, default=dict)
    status = Column(String, default="new")  # new, contacted, qualified, converted
    
    # Assignment
    assigned_dealer = Column(String)
    assigned_at = Column(DateTime)
    
    # Metadata
    source = Column(String)  # direct, search, referral, ad
    utm_campaign = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Communication
    notes = Column(Text)
    last_contacted = Column(DateTime)
    followup_date = Column(DateTime)

class SearchAlert(Base):
    """Search alerts for users"""
    __tablename__ = "search_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Alert criteria
    criteria = Column(JSON)  # Stored search parameters
    frequency = Column(String, default="immediate")  # immediate, daily, weekly
    
    # Status
    active = Column(Boolean, default=True)
    last_sent = Column(DateTime)
    matches_found = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Analytics(Base):
    """Analytics tracking"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String)  # view, inquiry, search, filter
    coach_id = Column(String, ForeignKey("coaches.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    
    # Event details
    event_data = Column(JSON)
    session_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    
    created_at = Column(DateTime, default=func.now())

# Database initialization
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connections"""
    await engine.dispose()

# Dependency to get database session
async def get_db():
    """Get database session for dependency injection"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
