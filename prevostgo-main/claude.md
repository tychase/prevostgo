# Claude Code Overview for PrevostGo 🚐

Welcome Claude! Here's everything you need to know to help Tyler get PrevostGo fully production-ready with clean, professional search + coach detail UX.

---

## ✅ Current Deployment Setup

- **Frontend**: Vercel (deployed from `frontend/`)
- **Backend**: Railway (FastAPI with PostgreSQL, from `backend/`)
- **Local Dev**: Functional using `.env` pointing to `localhost:8000`
- **Goal**: Fully connected, search-optimized, professional UI for production at https://prevostgo.com

---

## 🗺️ Production Architecture

```
prevostgo.com ─▶ Vercel ─▶ frontend (React + Vite)
                         └──▶ FastAPI (Railway) ─▶ PostgreSQL (Railway DB)
```

---

## 🔧 Production Fix Instructions

### 1. Configure Frontend (Vercel)
- Set `VITE_API_URL` to your Railway backend URL + `/api`, e.g.:
  ```
  https://your-backend-name.up.railway.app/api
  ```
- Remove any localhost-only settings from `.env`

### 2. Fix CORS in FastAPI (Backend)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://prevostgo.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
`.env` for backend:
```
CORS_ORIGINS=https://prevostgo.com
```

### 3. Populate PostgreSQL via Scraper

#### Option A: Run via Railway Console
```python
from app.services.scraper_enhanced import EnhancedPrevostInventoryScraper
import asyncio

async def populate_database():
    scraper = EnhancedPrevostInventoryScraper()
    listings = await scraper.scrape_inventory(detail=True)
    print(f"Success! {len(listings)} coaches scraped.")
asyncio.run(populate_database())
```

#### Option B: Create Admin API Endpoint (in `inventory.py`)
```python
@router.post("/admin/populate", include_in_schema=False)
async def populate_database(secret: str, db: AsyncSession = Depends(get_db)):
    if secret != "your-admin-secret-key":
        raise HTTPException(status_code=401, detail="Unauthorized")
    ...
```
Then call:
```
POST https://your-backend.railway.app/api/inventory/admin/populate?secret=your-secret
```

---

## 🔍 Search Functionality Fixes

### Issues:
- Incomplete results or blank fields

### Fix:
- Add fuzzy matching and keyword ranking
- Skip/handle blank fields in filters

**Claude prompt**:
```
Improve `build_search_query()` in `search.py` to:
- Support fuzzy matching
- Add keyword relevance ranking
- Skip/handle blank fields without errors
```

---

## ⚙️ Search Optimizations (Performance)

### Add DB Indexes (migration):
```sql
CREATE INDEX idx_coaches_price ON coaches(price);
CREATE INDEX idx_coaches_year ON coaches(year);
CREATE INDEX idx_coaches_converter ON coaches(converter);
CREATE INDEX idx_coaches_status ON coaches(status);
```

### Add FastAPI Caching:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@router.get("/", response_model=CoachListResponse)
@cache(expire=300)
async def get_coaches(...):
```

### Track Analytics:
```python
@router.post("/track-search")
async def track_search(term: str):
    analytics = Analytics(...)
    db.add(analytics)
    await db.commit()
```

---

## 🎨 Coach Detail UI Cleanup

### Fix broken display on missing data:
```jsx
<img src={coach.imageUrl || '/default.jpg'} alt="Coach Image" />
<p>{coach.year || "Unknown Year"}</p>
```

**Claude prompt**:
```
Update CoachDetail page to show placeholders for missing data (e.g., image, price, converter). Layout should stay clean and mobile responsive.
```

---

## 💡 Bonus UI Enhancements (Inspired by DuPont Registry)

- Hero section: background image/video
- 3 CTA buttons: [ Buy a Coach ] [ Sell Your Coach ] [ Browse Inventory ]
- Add tags like "New Arrival", "Pending", "Price Drop"
- Loading skeletons while data loads

---

## 🧼 Production Cleanup Tasks

### Remove Local-Only Files:
- `.replit`, `.replit-backend`, `start-dev.bat`, `start-simple.sh`, `setup.ps1`
- `restart_backend.bat`, `railway.json.backup`
- `.env` files with `localhost` values

### Remove Debug/Test Files:
- `test-api.html`, `trigger-scraper.html`, `quick-scraper.html`, `errors.txt`, etc.
- `New Text Document (4).txt`, `New.txt`, `updatednotes.txt`
- `COACH_DETAILS_500_FIX.md`, `COACH_DETAILS_FIX.md`, etc.

### Remove Old Router Versions:
- `inventory_fixed.py`, `inventory_sync.py`

### Keep Only:
- `/frontend/src`, `/frontend/public`, `/backend/app`, `/backend/main.py`
- `QUICKSTART.md`, `SCRAPER_GUIDE.md`, `README.md`
- `.gitignore`, `requirements.txt`, `railway.toml`

---

## ✅ Deployment Checklist

- [ ] Clean up local-only files
- [ ] Set Railway `.env` and secrets
- [ ] Set `VITE_API_URL` in Vercel/Netlify
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Populate database
- [ ] Test API, inventory, and search
- [ ] Confirm coach pages display fully
- [ ] Monitor logs and uptime

---

## 🧪 Testing & Diagnostics

```bash
# Health check
curl https://your-backend.railway.app/api/health

# Inventory test
curl https://your-backend.railway.app/api/inventory?per_page=5

# Search test
curl https://your-backend.railway.app/api/inventory?search=Marathon
```

---

## 🔍 Frontend Debug Mode

```js
if (import.meta.env.DEV) {
  console.log("API Configuration", {
    url: API_URL,
    env: import.meta.env.MODE
  });
}
```

---

## 🔭 Future Enhancements

### Performance
- Redis caching
- CDN for images
- Query optimization

### Features
- Saved searches
- Email alerts
- Analytics dashboard

### SEO
- Server-side rendering
- Sitemap
- Meta tags

---

## 🧠 Summary

Claude, your mission:
- Perfect the search UX
- Fix and polish coach detail pages
- Ensure full scraper-to-UI pipeline works
- Prep for launch-level visual & functional quality

Let's finish strong. 🚀