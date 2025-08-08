#!/bin/bash

echo "🚀 Starting PrevostGO (Simple Mode)..."

# Start backend
cd backend
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt
echo "🔧 Starting backend..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait a bit
sleep 5

# Start frontend
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install
echo "🎨 Starting frontend..."

# Update the API URL for Replit
export VITE_API_URL=""  # Empty means use proxy
npm run dev -- --host 0.0.0.0 --port 3000

# Keep running
wait
