"""
PrevostGO Backend API
FastAPI application for the PrevostGO digital showroom
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime

from app.routers import inventory, leads, search
from app.services.scraper import PrevostInventoryScraper
from app.models.database import init_db, close_db

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting PrevostGO API...")
    await init_db()
    
    # Check if we need to run initial scrape
    if os.getenv("RUN_INITIAL_SCRAPE", "false").lower() == "true":
        print("Running initial inventory scrape...")
        scraper = PrevostInventoryScraper()
        await scraper.run_initial_scrape()
    
    yield
    
    # Shutdown
    print("Shutting down PrevostGO API...")
    await close_db()

# Create FastAPI app
app = FastAPI(
    title="PrevostGO API",
    description="B2B/B2C digital showroom and lead management for Prevost luxury coaches",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Get allowed origins from environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "https://prevostgo.com,https://www.prevostgo.com,http://prevostgo.com,http://www.prevostgo.com,http://localhost:3000,http://localhost:5173").split(",")
if "*" in allowed_origins:
    print("WARNING: CORS is configured to allow all origins. Update CORS_ORIGINS in production.")
print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PrevostGO API"
    }



# Debug endpoint for coach details (temporary)
@app.get("/api/debug/coach/{coach_id}")
async def debug_get_coach(coach_id: str):
    """Debug endpoint to get raw coach data without Pydantic validation"""
    import sqlite3
    import json
    
    conn = sqlite3.connect('prevostgo.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Coach not found")
    
    columns = [desc[0] for desc in cursor.description]
    coach = dict(zip(columns, row))
    
    # Parse JSON fields
    for field in ['images', 'features']:
        if coach.get(field):
            try:
                coach[field] = json.loads(coach[field])
            except:
                coach[field] = []
    
    # Convert price from cents to dollars
    if coach.get('price'):
        coach['price'] = coach['price'] // 100
    
    conn.close()
    
    return coach

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to PrevostGO API",
        "docs": "/docs",
        "health": "/api/health"
    }

# Test endpoint for debugging CORS
@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "cors": "enabled"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
