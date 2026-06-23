#!/bin/bash
# Start ReadmeAI - Backend + Frontend

echo "🚀 Starting ReadmeAI..."

# Backend
echo "📦 Starting Flask backend on port 8000..."
cd backend
pip install -r requirements.txt -q
python app.py &
BACKEND_PID=$!

# Frontend
echo "⚛️  Starting React frontend on port 3000..."
cd ../frontend
npm install -q
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ ReadmeAI is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both services."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
