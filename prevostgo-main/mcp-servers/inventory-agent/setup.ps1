# PrevostGo MCP Inventory Agent Setup Script
# This script sets up the inventory agent MCP server for Claude Desktop

Write-Host "🚀 PrevostGo MCP Inventory Agent Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if Python is installed (needed for scraper)
try {
    $pythonVersion = python --version
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Python not found. The scraper functionality will not work." -ForegroundColor Yellow
    Write-Host "   Install Python from: https://python.org/" -ForegroundColor Yellow
}

# Navigate to inventory-agent directory
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
    
    # Update scraper path in .env
    $envContent = Get-Content ".env"
    $scraperPath = "C:\Users\tmcha\Dev\prevostgo\backend\scraper_final_v2.py"
    if (Test-Path $scraperPath) {
        Write-Host "✅ Scraper found at default location" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Scraper not found at default location. Update SCRAPER_PATH in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host "`n🔨 Building TypeScript..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build TypeScript" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 Setting up Claude Desktop configuration..." -ForegroundColor Yellow
npm run setup-claude

Write-Host "`n✨ Setup Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Make sure PrevostGo backend is running on http://localhost:8000" -ForegroundColor White
Write-Host "2. Restart Claude Desktop" -ForegroundColor White
Write-Host "3. Try asking Claude: 'Run the inventory scraper'" -ForegroundColor White
Write-Host "4. Then: 'Show me the database statistics'" -ForegroundColor White

Write-Host "`n💡 Pro tip: The inventory agent will populate your database with coaches!" -ForegroundColor Yellow
Write-Host "   After running the scraper, use the search agent to browse them." -ForegroundColor Yellow

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
