#!/bin/bash

# Setup script for devcontainer

echo "🚀 Setting up Coding Agent Development Environment..."

# Install CLI dependencies
if [ -f "cli/package.json" ]; then
    echo "📦 Installing CLI dependencies..."
    cd cli && npm install && cd ..
fi

# Install VSCode Extension dependencies
if [ -f "vscode-extension/package.json" ]; then
    echo "📦 Installing VSCode Extension dependencies..."
    cd vscode-extension && npm install && cd ..
fi

# Install Web UI dependencies
if [ -f "web-ui/package.json" ]; then
    echo "📦 Installing Web UI dependencies..."
    cd web-ui && npm install && cd ..
fi

# Install Server dependencies
if [ -f "server/requirements.txt" ]; then
    echo "📦 Installing Server dependencies..."
    cd server && pip install -r requirements.txt && cd ..
fi

# Setup git hooks
echo "🔧 Setting up git hooks..."
git config core.hooksPath .githooks

# Create necessary directories
mkdir -p data logs

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  - Start the API server: cd server && python -m uvicorn api.main:app --reload"
echo "  - Start the Web UI: cd web-ui && npm run dev"
echo "  - Access the API docs: http://localhost:8000/api/docs"

