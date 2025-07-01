# PrevostGo MCP Search Agent Setup Script
# This script sets up the search agent MCP server for Claude Desktop

Write-Host "🚀 PrevostGo MCP Search Agent Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Navigate to search-agent directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`n📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file (using defaults)" -ForegroundColor Green
}
else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host "`n🔨 Building TypeScript..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build TypeScript" -ForegroundColor Red
    exit 1
}

Write-Host "`n🧪 Running integration tests..." -ForegroundColor Yellow
$env:API_BASE_URL = "http://localhost:8000"

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/inventory/summary" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Backend is running" -ForegroundColor Green
    
    # Run integration tests
    npm run test:integration
} catch {
    Write-Host "⚠️  Backend not accessible. Make sure PrevostGo backend is running on http://localhost:8000" -ForegroundColor Yellow
    Write-Host "   Skipping integration tests..." -ForegroundColor Yellow
}

Write-Host "`n🔧 Setting up Claude Desktop configuration..." -ForegroundColor Yellow
npm run setup-claude

Write-Host "`n✨ Setup Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Make sure PrevostGo backend is running on http://localhost:8000" -ForegroundColor White
Write-Host "2. Restart Claude Desktop" -ForegroundColor White
Write-Host "3. Try asking Claude: 'Search for Marathon coaches under 500k'" -ForegroundColor White

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
