"""
Railway Environment Setup Helper
This script helps you configure your Railway backend with the correct environment variables
"""

print("🚀 Railway Environment Setup Helper\n")
print("This will help you configure your Railway backend service.\n")

# Get PostgreSQL URL
print("Step 1: Get your PostgreSQL connection string")
print("1. Go to your Railway PostgreSQL service")
print("2. Click the 'Connect' button")
print("3. Copy the connection string\n")

database_url = input("Paste your PostgreSQL connection string here: ").strip()

if not database_url or not database_url.startswith("postgresql://"):
    print("❌ Invalid PostgreSQL URL. It should start with 'postgresql://'")
    exit(1)

# Generate the environment variables
env_vars = f"""
# Copy these environment variables to your Railway backend service:

DATABASE_URL={database_url}
CORS_ORIGINS=https://prevostgo.com,https://www.prevostgo.com,http://prevostgo.com,http://www.prevostgo.com
ALLOW_ALL_ORIGINS=false
RUN_INITIAL_SCRAPE=false
PORT=${{PORT}}
"""

print("\n" + "="*60)
print(env_vars)
print("="*60)

print("\nStep 2: Add these variables to Railway")
print("1. Go to your Railway backend service (prevostgo)")
print("2. Click on 'Variables' tab")
print("3. Add each variable above")
print("4. Click 'Deploy' or 'Redeploy' to apply changes")

print("\nStep 3: After deployment completes")
print("1. Check the deployment logs for 'Database tables created/verified'")
print("2. Run: python scripts/trigger_production_scraper.py")
print("3. Check https://prevostgo.com - coaches should appear!")

# Save to file for reference
with open("railway_env_vars.txt", "w") as f:
    f.write(env_vars)
print("\n✅ Environment variables saved to 'railway_env_vars.txt'")
