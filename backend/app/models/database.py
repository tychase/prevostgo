"""
Re-export database models from the main database module
This avoids duplication and confusion
"""

# Import everything from the main database module
from app.database import (
    Base,
    Coach,
    Lead,
    Analytics,
    SearchAlert,
    get_db,
    get_sync_db,
    init_db,
    close_db,
    engine,
    SessionLocal,
    DATABASE_URL
)

# Re-export for backward compatibility
__all__ = [
    'Base',
    'Coach',
    'Lead',
    'Analytics',
    'SearchAlert',
    'get_db',
    'get_sync_db',
    'init_db',
    'close_db',
    'engine',
    'SessionLocal',
    'DATABASE_URL'
]
