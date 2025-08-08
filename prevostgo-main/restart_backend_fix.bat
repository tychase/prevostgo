@echo off
echo Stopping any running Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2

echo Starting backend server...
cd backend
start cmd /k "python main.py"

echo Waiting for server to start...
timeout /t 5

echo Testing the API...
curl -s http://localhost:8000/api/health

echo.
echo Backend server is running!
echo You can now test the coach details page at http://localhost:3000/inventory
