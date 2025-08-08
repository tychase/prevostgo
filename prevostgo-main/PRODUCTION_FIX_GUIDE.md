# PrevostGO Production Fix Guide

## 🚨 Production Issues & Solutions

### 1. Check Production Status
Run this Python script to check if everything is working:
```bash
cd C:\Users\tmcha\Dev\prevostgo\scripts
python check_production.py
```

### 2. Railway Environment Variables
Make sure these are set in your Railway backend service:

```
DATABASE_URL=<your-railway-postgres-url>
CORS_ORIGINS=https://prevostgo.com,https://www.prevostgo.com,http://prevostgo.com,http://www.prevostgo.com
ALLOW_ALL_ORIGINS=false
RUN_INITIAL_SCRAPE=false
```

### 3. If Database is Empty
Run the scraper to populate with real data:
```bash
cd C:\Users\tmcha\Dev\prevostgo\scripts
python trigger_production_scraper.py
```

### 4. Common Issues & Fixes

#### ❌ Coaches not showing on frontend
1. Check browser console for errors (F12)
2. Look for CORS errors or 404s
3. Verify API URL in production

#### ❌ "No coaches found" message
1. Database is empty - run the scraper
2. API is not returning data - check Railway logs

#### ❌ CORS errors
1. Update CORS_ORIGINS in Railway to include your domain
2. Redeploy the backend service

### 5. Railway Deployment Commands
```bash
# Check Railway CLI is installed
railway --version

# Login to Railway
railway login

# Link to your project
cd C:\Users\tmcha\Dev\prevostgo
railway link

# View logs
railway logs

# Deploy backend
railway up

# Check environment variables
railway variables
```

### 6. Quick Diagnostics
1. **Backend Health**: https://prevostgo-production.up.railway.app/api/health
2. **API Docs**: https://prevostgo-production.up.railway.app/docs
3. **Inventory Check**: https://prevostgo-production.up.railway.app/api/inventory
4. **Frontend**: https://prevostgo.com

### 7. If Nothing Works
1. Check Railway dashboard for deployment status
2. Look at Railway logs for errors
3. Verify PostgreSQL database is running
4. Check that all environment variables are set correctly

## Next Steps
1. Run `python scripts/check_production.py` to see current status
2. If no coaches, run `python scripts/trigger_production_scraper.py`
3. Check https://prevostgo.com to see if coaches appear
4. If still issues, check Railway logs for errors
