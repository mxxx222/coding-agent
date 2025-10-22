#!/bin/bash

# Coding Agent Setup Script
# This script sets up the development environment for Coding Agent

set -e

echo "🚀 Setting up Coding Agent development environment..."

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

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    print_success "Node.js $(node --version) is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ from https://python.org"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION < 3.11" | bc -l)" -eq 1 ]; then
        print_warning "Python 3.11+ is recommended. Current version: $(python3 --version)"
    fi
    print_success "Python $(python3 --version) is installed"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Some features may not work without Docker."
    else
        print_success "Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1) is installed"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git from https://git-scm.com"
        exit 1
    fi
    print_success "Git $(git --version | cut -d' ' -f3) is installed"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_success "Created .env file"
        print_warning "Please update .env file with your actual values"
    else
        print_success ".env file already exists"
    fi
}

# Install CLI dependencies
setup_cli() {
    print_status "Setting up CLI tool..."
    
    cd cli
    if [ ! -d node_modules ]; then
        print_status "Installing CLI dependencies..."
        npm install
        print_success "CLI dependencies installed"
    else
        print_success "CLI dependencies already installed"
    fi
    
    print_status "Building CLI..."
    npm run build
    print_success "CLI built successfully"
    
    cd ..
}

# Install VSCode extension dependencies
setup_vscode() {
    print_status "Setting up VSCode extension..."
    
    cd vscode-extension
    if [ ! -d node_modules ]; then
        print_status "Installing VSCode extension dependencies..."
        npm install
        print_success "VSCode extension dependencies installed"
    else
        print_success "VSCode extension dependencies already installed"
    fi
    
    print_status "Building VSCode extension..."
    npm run compile
    print_success "VSCode extension built successfully"
    
    cd ..
}

# Install web UI dependencies
setup_web_ui() {
    print_status "Setting up web UI..."
    
    cd web-ui
    if [ ! -d node_modules ]; then
        print_status "Installing web UI dependencies..."
        npm install
        print_success "Web UI dependencies installed"
    else
        print_success "Web UI dependencies already installed"
    fi
    
    print_status "Building web UI..."
    npm run build
    print_success "Web UI built successfully"
    
    cd ..
}

# Install server dependencies
setup_server() {
    print_status "Setting up server..."
    
    cd server
    if [ ! -d venv ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Server dependencies installed"
    
    cd ..
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL is running
    if ! pg_isready -q; then
        print_warning "PostgreSQL is not running. Please start PostgreSQL service."
        print_status "On macOS with Homebrew: brew services start postgresql"
        print_status "On Ubuntu: sudo systemctl start postgresql"
        print_status "On Windows: Start PostgreSQL service from Services"
    else
        print_success "PostgreSQL is running"
    fi
    
    # Check if Redis is running
    if ! redis-cli ping &> /dev/null; then
        print_warning "Redis is not running. Please start Redis service."
        print_status "On macOS with Homebrew: brew services start redis"
        print_status "On Ubuntu: sudo systemctl start redis"
        print_status "On Windows: Start Redis service from Services"
    else
        print_success "Redis is running"
    fi
}

# Setup Git hooks
setup_git_hooks() {
    print_status "Setting up Git hooks..."
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Coding Agent

echo "Running pre-commit checks..."

# Run linting
echo "Running ESLint..."
cd cli && npm run lint
cd ../vscode-extension && npm run lint
cd ../web-ui && npm run lint

# Run type checking
echo "Running TypeScript type checking..."
cd cli && npm run type-check
cd ../vscode-extension && npm run type-check
cd ../web-ui && npm run type-check

# Run tests
echo "Running tests..."
cd cli && npm test
cd ../vscode-extension && npm test
cd ../web-ui && npm test

echo "Pre-commit checks completed successfully!"
EOF

    chmod +x .git/hooks/pre-commit
    print_success "Git hooks configured"
}

# Create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Create dev.sh script
    cat > dev.sh << 'EOF'
#!/bin/bash
# Development script for Coding Agent

echo "🚀 Starting Coding Agent development environment..."

# Start database services
echo "Starting database services..."
if command -v docker &> /dev/null; then
    docker-compose up -d postgres redis
else
    echo "Docker not available, please start PostgreSQL and Redis manually"
fi

# Start server
echo "Starting Python server..."
cd server
source venv/bin/activate
python api/main.py &
SERVER_PID=$!

# Start web UI
echo "Starting web UI..."
cd ../web-ui
npm run dev &
WEB_PID=$!

# Wait for services to start
sleep 5

echo "✅ Development environment started!"
echo "🌐 Web UI: http://localhost:3000"
echo "🔧 API Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo "Stopping services..."
    kill $SERVER_PID $WEB_PID 2>/dev/null
    if command -v docker &> /dev/null; then
        docker-compose down
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
EOF

    chmod +x dev.sh
    print_success "Development script created"
}

# Create Docker Compose file
create_docker_compose() {
    print_status "Creating Docker Compose configuration..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: coding_agent
      POSTGRES_USER: coding_agent
      POSTGRES_PASSWORD: coding_agent
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U coding_agent"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  server:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://coding_agent:coding_agent@postgres:5432/coding_agent
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./server:/app
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  redis_data:
EOF

    print_success "Docker Compose configuration created"
}

# Main setup function
main() {
    echo "🎯 Coding Agent Setup"
    echo "===================="
    echo ""
    
    check_requirements
    setup_env
    setup_cli
    setup_vscode
    setup_web_ui
    setup_server
    setup_database
    setup_git_hooks
    create_dev_scripts
    create_docker_compose
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update .env file with your actual values"
    echo "2. Run './dev.sh' to start the development environment"
    echo "3. Visit http://localhost:3000 for the web UI"
    echo "4. Visit http://localhost:8000/api/docs for API documentation"
    echo ""
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"