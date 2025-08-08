"""
PostgreSQL Database Models for PrevostGO
Clean, robust, and easy to understand
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")

# Fix for SQLAlchemy - PostgreSQL URLs need postgresql:// not postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Coach(Base):
    """Main coach listing table"""
    __tablename__ = "coaches"
    
    # Primary identifier
    id = Column(String, primary_key=True, index=True)
    
    # Basic info
    title = Column(String, nullable=False)
    year = Column(Integer, index=True)
    model = Column(String, index=True)
    chassis_type = Column(String)
    converter = Column(String, index=True)
    condition = Column(String, index=True)  # 'new' or 'pre-owned'
    
    # Pricing
    price_cents = Column(Integer, index=True)  # Store in cents for accuracy
    price_display = Column(String)  # Human readable: "$450,000"
    price_status = Column(String)  # 'available', 'contact_for_price', 'sold'
    
    # Details
    mileage = Column(Integer)
    engine = Column(String)
    slide_count = Column(Integer, default=0)
    features = Column(JSON, default=list)  # PostgreSQL JSON field
    bathroom_config = Column(String)
    stock_number = Column(String)
    
    # Media
    images = Column(JSON, default=list)  # List of image URLs
    virtual_tour_url = Column(String)
    
    # Dealer info
    dealer_name = Column(String, index=True)
    dealer_state = Column(String, index=True)
    dealer_phone = Column(String)
    dealer_email = Column(String)
    
    # Source
    listing_url = Column(String)
    source = Column(String, default='prevost-stuff.com')
    
    # Status tracking
    status = Column(String, default='available', index=True)  # 'available', 'pending', 'sold'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = Column(DateTime)
    
    # Analytics
    view_count = Column(Integer, default=0)
    inquiry_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_price_status', 'price_cents', 'status'),
        Index('idx_year_model', 'year', 'model'),
        Index('idx_converter_state', 'converter', 'dealer_state'),
    )

class Lead(Base):
    """Customer leads and inquiries"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact info
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String)
    company = Column(String)
    
    # Lead details
    lead_type = Column(String)  # 'inquiry', 'newsletter', 'contact'
    source = Column(String)  # 'website', 'api', 'import'
    message = Column(Text)
    
    # Related coach (if applicable)
    coach_id = Column(String, index=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    status = Column(String, default='new')  # 'new', 'contacted', 'qualified', 'closed'
    notes = Column(Text)

class Analytics(Base):
    """Track all user interactions"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event info
    event_type = Column(String, index=True)  # 'view', 'inquiry', 'search', 'filter'
    event_data = Column(JSON)
    
    # Relations
    coach_id = Column(String, index=True)
    lead_id = Column(Integer, index=True)
    
    # Session tracking
    session_id = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
