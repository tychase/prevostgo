@echo off
echo Starting PrevostGO Development Environment...

:: Start backend
echo.
echo Starting Backend API...
cd backend
start cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python main.py"

:: Wait a bit for backend to start
timeout /t 5 /nobreak

:: Start frontend
echo.
echo Starting Frontend...
cd ..\frontend
start cmd /k "npm install && npm run dev"

echo.
echo =======================================
echo PrevostGO is starting up!
echo =======================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo =======================================
echo.
pause
