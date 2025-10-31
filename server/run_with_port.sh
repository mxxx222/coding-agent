#!/bin/bash
# Kill existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Wait a moment
sleep 1

# Activate venv and run server
source venv/bin/activate
python run.py
