"""
Database configuration for PrevostGO
Supports both SQLite and PostgreSQL
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")

# Fix for SQLAlchemy - PostgreSQL URLs need postgresql:// not postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For async support, we need different URLs
if "postgresql" in DATABASE_URL:
    # PostgreSQL async - but check if asyncpg is available
    try:
        import asyncpg
        ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    except ImportError:
        print("Warning: asyncpg not installed, using sync engine only")
        ASYNC_DATABASE_URL = DATABASE_URL
elif "sqlite" in DATABASE_URL:
    # SQLite async
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create sync engine (for migrations and sync operations)
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create async engine only if we have async support
try:
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False
    )
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False
    )
except Exception as e:
    print(f"Warning: Could not create async engine: {e}")
    async_engine = None
    AsyncSessionLocal = None

# Session factory for sync operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Define models here to avoid circular imports
class Coach(Base):
    __tablename__ = "coaches"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    year = Column(Integer)
    model = Column(String)
    chassis_type = Column(String)
    converter = Column(String)
    condition = Column(String)
    price = Column(Integer)  # Price in cents
    price_display = Column(String)
    price_status = Column(String)
    mileage = Column(Integer)
    engine = Column(String)
    slide_count = Column(Integer, default=0)
    features = Column(JSON)
    bathroom_config = Column(String)
    stock_number = Column(String)
    images = Column(JSON)
    virtual_tour_url = Column(String)
    dealer_name = Column(String)
    dealer_state = Column(String)
    dealer_phone = Column(String)
    dealer_email = Column(String)
    listing_url = Column(String)
    source = Column(String, default='prevost-stuff.com')
    status = Column(String, default='available')
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = Column(Integer, default=0)
    inquiries = Column(Integer, default=0)

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    lead_type = Column(String)
    source = Column(String)
    message = Column(Text)
    coach_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default='new')
    notes = Column(Text)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    event_data = Column(JSON)
    coach_id = Column(String)
    lead_id = Column(Integer)
    session_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchAlert(Base):
    __tablename__ = "search_alerts"
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, nullable=False)
    criteria = Column(JSON, nullable=False)
    frequency = Column(String, default='daily')
    active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    print(f"Database tables created/verified")
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

# Dependency to get DB session
async def get_db():
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        # Fallback to sync session
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# For sync operations
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database (create tables)
async def init_db():
    """Initialize database - create tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Close database connections
async def close_db():
    """Close database connections"""
    if async_engine:
        await async_engine.dispose()
    print("Database connections closed")
