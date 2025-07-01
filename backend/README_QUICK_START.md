# PrevostGO - Python 3.13 Compatible Setup

## Quick Start (Tested on Python 3.13)

### Step 1: Install Minimal Requirements

```bash
cd backend
pip install -r requirements_minimal.txt
```

If you get any errors, install packages one by one:
```bash
pip install fastapi==0.109.0
pip install uvicorn==0.27.0
pip install python-multipart==0.0.6
pip install sqlalchemy==2.0.25
pip install pydantic==1.10.13
pip install email-validator==1.3.1
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install beautifulsoup4==4.12.3
pip install python-dateutil==2.8.2
```

### Step 2: Run the Scraper (Populate Database)

```bash
python scraper_minimal.py
```

This will:
- Create the SQLite database
- Scrape coaches from prevost-stuff.com
- Save them to the database

### Step 3: Run the API Server

```bash
python main_minimal.py
```

The API will be available at:
- http://localhost:8000 - Root
- http://localhost:8000/docs - API Documentation
- http://localhost:8000/api/inventory - View coaches

### Step 4: Test the API

Open your browser and visit:
- http://localhost:8000/api/inventory - Should show scraped coaches
- http://localhost:8000/api/inventory/summary - Shows statistics

## Frontend Setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 to see the app!

## What's Working

✅ Scraper that populates real coach data
✅ API server with no async/Rust dependencies  
✅ SQLite database (no compilation needed)
✅ Frontend React app with filters
✅ Coach detail pages
✅ Lead capture

## Troubleshooting

### If pip install fails:
Use the minimal requirements:
```bash
pip install -r requirements_minimal.txt
```

### If you see "module not found":
Make sure you're in the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### If the scraper doesn't work:
Check your internet connection and try again.

## Next Steps

1. The scraper has populated your database with real coaches
2. The API is serving the data
3. The frontend can display and filter the coaches
4. You can now customize the design and add features!
