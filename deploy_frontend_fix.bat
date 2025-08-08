@echo off
echo === Fixing and deploying PrevostGo Frontend ===
echo.

cd /d "C:\Users\tmcha\Dev\prevostgo\frontend"

echo === Step 1: Cleaning up ===
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo === Step 2: Installing dependencies ===
npm install

echo === Step 3: Building for production ===
npm run build

echo === Step 4: Committing changes ===
cd /d "C:\Users\tmcha\Dev\prevostgo"
git add -A
git commit -m "Fix frontend: Ensure Tailwind CSS and API client work properly"
git push origin main

echo === Deployment complete! ===
echo.
echo Vercel should automatically redeploy from GitHub.
echo Check https://prevostgo.com in a few minutes.
pause
