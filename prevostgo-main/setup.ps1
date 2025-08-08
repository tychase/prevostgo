# PrevostGO Quick Start Script for Windows

Write-Host "🚀 Starting PrevostGO Setup..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version
Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Cyan

# Check Node version
$nodeVersion = node --version
Write-Host "✓ Node version: $nodeVersion" -ForegroundColor Cyan

# Backend setup
Write-Host "`n📦 Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file" -ForegroundColor Green
}

# Frontend setup
Write-Host "`n📦 Setting up frontend..." -ForegroundColor Yellow
Set-Location ..\frontend

# Install dependencies
npm install

# Check for placeholder image
if (!(Test-Path public\placeholder-coach.jpg)) {
    Write-Host "⚠️  Please add a placeholder-coach.jpg to frontend\public\" -ForegroundColor Red
}

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nTo start the application:"
Write-Host "1. Backend: cd backend && python main.py"
Write-Host "2. Frontend: cd frontend && npm run dev"
Write-Host "`nVisit http://localhost:3000 to see the app" -ForegroundColor Cyan
