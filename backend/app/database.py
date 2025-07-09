"""
Updated database configuration to support both SQLite and PostgreSQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prevostgo.db")

# Fix for SQLAlchemy - PostgreSQL URLs need postgresql:// not postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For async support, we need different URLs
if "postgresql" in DATABASE_URL:
    # PostgreSQL async
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
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

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

# Base class for models
from app.models.base import Base

# Import all models to ensure they're registered
from app.models.coach import Coach
from app.models.lead import Lead  
from app.models.analytics import Analytics
from app.models.search_alert import SearchAlert

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

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
    # For PostgreSQL, we might want to create tables async
    # For now, using sync creation which works for both
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# Close database connections
async def close_db():
    """Close database connections"""
    await async_engine.dispose()
    print("Database connections closed")
