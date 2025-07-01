"""
PrevostGO Backend API - Simplified version
FastAPI application for the PrevostGO digital showroom
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

# Import database
from app.database import database, engine, metadata
from app.models import models

# Create tables
metadata.create_all(bind=engine)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting PrevostGO API...")
    await database.connect()
    yield
    # Shutdown
    print("Shutting down PrevostGO API...")
    await database.disconnect()

# Create FastAPI app
app = FastAPI(
    title="PrevostGO API",
    description="B2B/B2C digital showroom for Prevost luxury coaches",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to PrevostGO API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if database.is_connected else "disconnected"
    }

@app.get("/api/inventory")
async def get_inventory():
    """Get all coaches - simplified version"""
    query = "SELECT * FROM coaches WHERE status = 'available' LIMIT 20"
    try:
        rows = await database.fetch_all(query)
        return {
            "total": len(rows),
            "coaches": [dict(row) for row in rows]
        }
    except Exception as e:
        # Table might not exist yet
        return {
            "total": 0,
            "coaches": [],
            "message": "No inventory available yet. Run the scraper to populate data."
        }

@app.post("/api/scrape")
async def trigger_scrape():
    """Trigger inventory scrape - simplified version"""
    # For now, just return a message
    return {
        "message": "Scraping functionality will be implemented soon",
        "status": "pending"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
