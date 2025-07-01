"""
Database configuration using databases package for better compatibility
"""

import os
from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prevostgo.db")

# Create database instance
database = Database(DATABASE_URL)

# SQLAlchemy setup
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Create engine for table creation
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Database lifecycle
async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()
