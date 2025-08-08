# PrevostGO Quick Start Guide

## Backend Setup (Python 3.13 Compatible)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements_simple.txt
```

### Step 2: Run the API Server
```bash
python main_simple.py
```

The API will be available at http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 3: Run the Scraper (Optional)
In a new terminal:
```bash
cd backend
python scraper_simple.py
```

This will populate the database with coaches from prevost-stuff.com

### Step 4: Test the API
Visit http://localhost:8000/api/inventory to see the scraped coaches

## Frontend Setup

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Add Placeholder Image
Create a placeholder image at `frontend/public/placeholder-coach.jpg`

### Step 3: Run the Development Server
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Features Working

✅ Backend API with FastAPI
✅ SQLite database (no compilation issues)
✅ Web scraper for prevost-stuff.com
✅ React frontend with Tailwind CSS
✅ Inventory browsing with filters
✅ Coach detail pages
✅ Lead capture forms

## Next Steps

1. **Test the Scraper**: Run `python scraper_simple.py` to populate data
2. **Explore the API**: Visit http://localhost:8000/docs
3. **Browse the Frontend**: Visit http://localhost:3000
4. **Customize**: Modify the code to fit your needs

## Troubleshooting

### If you get import errors:
```bash
pip install databases[sqlite] sqlalchemy
```

### If the frontend won't start:
```bash
npm install
npm run dev
```

### If you want to use PostgreSQL instead:
1. Install PostgreSQL
2. Update DATABASE_URL in .env
3. Install: `pip install databases[postgresql] asyncpg`

## Production Deployment

For production:
1. Use PostgreSQL instead of SQLite
2. Add authentication to the API
3. Build the frontend: `npm run build`
4. Deploy to your hosting provider
