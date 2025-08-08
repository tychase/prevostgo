# PrevostGO - Working Setup Guide

## Option 1: Flask Version (Simplest - Recommended!)

### Step 1: Install Flask Requirements
```bash
cd backend
pip install flask flask-cors requests beautifulsoup4
```

Or use the requirements file:
```bash
pip install -r requirements_flask.txt
```

### Step 2: Run the Scraper
```bash
python scraper_fixed.py
```

This will:
- Try to scrape real data from prevost-stuff.com
- If that fails, it will create sample data so you can test

### Step 3: Run the Flask API
```bash
python app_flask.py
```

The API will run on http://localhost:8000

### Step 4: Test the API
Open your browser and visit:
- http://localhost:8000 - API info
- http://localhost:8000/api/inventory - See coaches
- http://localhost:8000/api/inventory/summary - See statistics

## Option 2: FastAPI with Compatible Versions

### Step 1: Install Working Requirements
```bash
pip install -r requirements_working.txt
```

### Step 2: Run scraper and API as above

## Frontend Setup

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

## What's Working Now

✅ Flask API (no dependency issues!)
✅ Scraper with fallback sample data
✅ SQLite database
✅ React frontend
✅ All features working

## Troubleshooting

### If the scraper doesn't find listings:
The scraper will automatically create sample data so you can test the app.

### If pip install fails:
Just install the packages one by one:
```bash
pip install flask
pip install flask-cors
pip install requests
pip install beautifulsoup4
```

### Frontend API calls failing?
Make sure the Flask API is running on port 8000.

## Quick Test

1. Run the scraper: `python scraper_fixed.py`
2. Run the API: `python app_flask.py`
3. Visit: http://localhost:8000/api/inventory
4. You should see coach data!

## Success!

The app is now working with Python 3.13 without any Rust compilation issues!
