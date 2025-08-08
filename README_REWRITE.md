# PrevostGo (Rewrite Drop)

This drop sets **Postgres as the default**, adds a **detail-page scraper** (full gallery, ad filtering), a new
`/api/coaches/search` endpoint with relevance sorting and facets, and a **DupontRegistry-style** search UI.

## Backend (FastAPI)

**Env (.env example at `backend/.env.example`):**
```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
CORS_ORIGINS=https://prevostgo.com,https://www.prevostgo.com,http://localhost:3000
BASE_LIST_URL=https://www.prevost-stuff.com/forsale/public_list_ads.php
ENABLE_SCRAPER_STARTUP=false
```

**Install & run locally:**
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # edit DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

**Scrape (one-off):**
```python
# run inside a script or ipython shell
# from app.scraper.prevost_scraper import scrape_all
# from app.config import settings
# from app.database import SessionLocal
# from app.crud import upsert_coach
# import asyncio
# data = asyncio.run(scrape_all(settings.BASE_LIST_URL))
# db = SessionLocal()
# for row in data:
#     upsert_coach(db, row)
```

**Endpoints:**
- `GET /api/health`
- `GET /api/coaches/search?q=&min_year=&max_year=&min_price=&max_price=&chassis=&converter=&sort=&page=&page_size=`

## Frontend (Vite React)

**Env (`frontend/.env.example`):**
```
VITE_API_URL=http://localhost:8000/api
```

**Run locally:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173 and try searching.

## Deploy

- **Backend (Railway):** uses `Procfile` → `uvicorn app.main:app`. Set `DATABASE_URL` and `CORS_ORIGINS` in Railway.
- **Frontend (Vercel/Netlify):** set `VITE_API_URL` to your Railway public URL + `/api`.

## Notes
- This is a first pass: tune the scraper selectors after the first production scrape.
- Add indexes on hot filters (year, price) in Postgres as volume grows.
