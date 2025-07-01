# PrevostGO Installation Guide for Python 3.13

## Issue with Python 3.13
The latest Python version (3.13) has compatibility issues with some packages that require Rust compilation. Here are several solutions:

## Solution 1: Use the Simplified Requirements (Recommended)
```bash
cd backend
pip install -r requirements_simple.txt
python main_simple.py
```

## Solution 2: Use Python 3.11 or 3.12
If you have pyenv or can install an older Python version:
```bash
# Install Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# Then use the original requirements
pip install -r requirements.txt
```

## Solution 3: Use PostgreSQL Instead
PostgreSQL drivers don't have the same compilation issues:

1. Install PostgreSQL
2. Update .env:
```
DATABASE_URL=postgresql://user:password@localhost/prevostgo
```
3. Install PostgreSQL requirements:
```bash
pip install asyncpg psycopg2-binary
```

## Solution 4: Manual Package Installation
Install packages one by one, skipping problematic ones:
```bash
pip install fastapi uvicorn python-multipart
pip install sqlalchemy databases[sqlite]
pip install pydantic email-validator python-dotenv
pip install requests beautifulsoup4 aiohttp lxml
pip install python-dateutil
```

## Running the Simplified Version
The simplified version (main_simple.py) works with the databases package:
```bash
python main_simple.py
```

Visit http://localhost:8000/docs to see the API documentation.

## Frontend Setup (No Issues)
The frontend works normally:
```bash
cd ../frontend
npm install
npm run dev
```

## Next Steps
Once the backend is running, you can:
1. Implement the scraper functionality
2. Add more endpoints
3. Connect the frontend to the backend
4. Add authentication
