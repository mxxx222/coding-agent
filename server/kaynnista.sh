#!/bin/bash
# Coding Agent Server - Start Script

# Kill any existing processes on port 8000
echo "🔍 Checking for existing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Run server
echo "🚀 Starting Coding Agent Server..."
echo ""
python run.py

