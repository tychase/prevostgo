# Railway PostgreSQL Connection Fix

## The Problem
Your backend is not connecting to the Railway PostgreSQL database. It's likely using a local SQLite database instead.

## Solution Steps

### 1. Set the DATABASE_URL in Railway

Go to your Railway backend service and add this environment variable:

```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:[YOUR-PORT]/railway
```

To get your DATABASE_URL:
1. Click "Connect" button in your PostgreSQL service
2. Copy the connection string
3. Add it as DATABASE_URL in your backend service variables

### 2. Add these environment variables to your backend service:

```
DATABASE_URL=<your-postgres-connection-string>
CORS_ORIGINS=https://prevostgo.com,https://www.prevostgo.com,http://prevostgo.com,http://www.prevostgo.com
ALLOW_ALL_ORIGINS=false
RUN_INITIAL_SCRAPE=false
PORT=8000
```

### 3. Update your backend dependencies

Make sure your `requirements.txt` includes PostgreSQL support:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
httpx==0.25.2
beautifulsoup4==4.12.2
pydantic==2.5.2
```

### 4. Redeploy your backend

After setting the environment variables:
1. Go to your backend service in Railway
2. Click "Redeploy" or push a small change to trigger a new deployment

### 5. Verify the connection

Once redeployed, the logs should show it's connecting to PostgreSQL, not SQLite.

### 6. Run the scraper again

After the backend is properly connected to PostgreSQL, run the scraper again to populate the database.
