#!/bin/bash

# PrevostGO Quick Start Script

echo "🚀 Starting PrevostGO Setup..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check Node version
node_version=$(node --version)
echo "✓ Node version: $node_version"

# Backend setup
echo -e "\n📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
fi

# Frontend setup
echo -e "\n📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

# Create placeholder image
if [ ! -f public/placeholder-coach.jpg ]; then
    echo "⚠️  Please add a placeholder-coach.jpg to frontend/public/"
fi

echo -e "\n✅ Setup complete!"
echo -e "\nTo start the application:"
echo "1. Backend: cd backend && python main.py"
echo "2. Frontend: cd frontend && npm run dev"
echo -e "\nVisit http://localhost:3000 to see the app"
