#!/bin/bash

# Development script for Coding Agent
# This script starts the development environment

set -e

echo "🚀 Starting Coding Agent development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Start database services
start_database() {
    print_status "Starting database services..."
    
    if command -v docker &> /dev/null; then
        if [ -f docker-compose.yml ]; then
            docker-compose up -d postgres redis
            print_success "Database services started with Docker"
        else
            print_warning "docker-compose.yml not found, please start PostgreSQL and Redis manually"
        fi
    else
        print_warning "Docker not available, please start PostgreSQL and Redis manually"
        print_status "On macOS with Homebrew: brew services start postgresql redis"
        print_status "On Ubuntu: sudo systemctl start postgresql redis"
    fi
}

# Start Python server
start_server() {
    print_status "Starting Python server..."
    
    cd server
    
    # Check if virtual environment exists
    if [ ! -d venv ]; then
        print_error "Virtual environment not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start server
    python api/main.py &
    SERVER_PID=$!
    
    cd ..
    print_success "Python server started (PID: $SERVER_PID)"
}

# Start web UI
start_web_ui() {
    print_status "Starting web UI..."
    
    cd web-ui
    
    # Check if node_modules exists
    if [ ! -d node_modules ]; then
        print_error "Web UI dependencies not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
    
    # Start web UI
    npm run dev &
    WEB_PID=$!
    
    cd ..
    print_success "Web UI started (PID: $WEB_PID)"
}

# Start VSCode extension in watch mode
start_vscode_extension() {
    print_status "Starting VSCode extension in watch mode..."
    
    cd vscode-extension
    
    # Check if node_modules exists
    if [ ! -d node_modules ]; then
        print_error "VSCode extension dependencies not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
    
    # Start extension in watch mode
    npm run watch &
    EXTENSION_PID=$!
    
    cd ..
    print_success "VSCode extension started in watch mode (PID: $EXTENSION_PID)"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for server
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            print_success "Server is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Server may not be ready yet"
        fi
        sleep 1
    done
    
    # Wait for web UI
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Web UI is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Web UI may not be ready yet"
        fi
        sleep 1
    done
}

# Cleanup function
cleanup() {
    echo ""
    print_status "Stopping services..."
    
    # Kill all background processes
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        print_status "Stopped Python server"
    fi
    
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
        print_status "Stopped web UI"
    fi
    
    if [ ! -z "$EXTENSION_PID" ]; then
        kill $EXTENSION_PID 2>/dev/null || true
        print_status "Stopped VSCode extension"
    fi
    
    # Stop Docker services
    if command -v docker &> /dev/null && [ -f docker-compose.yml ]; then
        docker-compose down
        print_status "Stopped Docker services"
    fi
    
    print_success "All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "🎯 Coding Agent Development Environment"
    echo "======================================"
    echo ""
    
    start_database
    start_server
    start_web_ui
    start_vscode_extension
    wait_for_services
    
    echo ""
    print_success "✅ Development environment started successfully!"
    echo ""
    echo "🌐 Web UI: http://localhost:3000"
    echo "🔧 API Server: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/api/docs"
    echo "🔍 Health Check: http://localhost:8000/api/health"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Wait for user to stop
    wait
}

# Run main function
main "$@"