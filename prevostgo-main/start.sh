#!/bin/bash

echo "🚀 Starting PrevostGO Setup..."

# Kill any existing processes
pkill -f "uvicorn" || true
pkill -f "vite" || true

# Setup Python environment
echo "📦 Setting up Python environment..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start backend
echo "🔧 Starting backend server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

# Start frontend dev server
echo "🎨 Starting frontend server..."
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

echo "✅ Setup complete!"
echo "🌐 Frontend: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "🔌 Backend API: https://$REPL_SLUG.$REPL_OWNER.repl.co:8000/api"
echo ""
echo "📝 Notes:"
echo "- Frontend runs on port 3000 (main URL)"
echo "- Backend API runs on port 8000"
echo "- It may take a minute for everything to load"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
