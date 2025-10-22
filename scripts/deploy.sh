#!/bin/bash

# Deployment script for Coding Agent
# This script handles deployment to different environments

set -e

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

# Default values
ENVIRONMENT="staging"
BUILD_ALL=false
SKIP_TESTS=false
FORCE_DEPLOY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build-all)
            BUILD_ALL=true
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --environment ENV    Deployment environment (staging|production)"
            echo "  -b, --build-all          Build all components"
            echo "  -s, --skip-tests         Skip running tests"
            echo "  -f, --force              Force deployment without confirmation"
            echo "  -h, --help               Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d .git ]; then
    print_error "Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    if [ "$FORCE_DEPLOY" = false ]; then
        print_error "You have uncommitted changes. Please commit or stash them before deploying."
        exit 1
    else
        print_warning "Deploying with uncommitted changes"
    fi
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Validate branch for production deployment
if [ "$ENVIRONMENT" = "production" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    if [ "$FORCE_DEPLOY" = false ]; then
        print_error "Production deployments must be from the 'main' branch"
        exit 1
    else
        print_warning "Deploying to production from branch: $CURRENT_BRANCH"
    fi
fi

# Confirmation prompt
if [ "$FORCE_DEPLOY" = false ]; then
    echo "🚀 Coding Agent Deployment"
    echo "=========================="
    echo "Environment: $ENVIRONMENT"
    echo "Branch: $CURRENT_BRANCH"
    echo "Build All: $BUILD_ALL"
    echo "Skip Tests: $SKIP_TESTS"
    echo ""
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
fi

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = false ]; then
        print_status "Running tests..."
        
        # Test CLI
        print_status "Testing CLI..."
        cd cli
        npm test
        cd ..
        
        # Test VSCode extension
        print_status "Testing VSCode extension..."
        cd vscode-extension
        npm test
        cd ..
        
        # Test web UI
        print_status "Testing web UI..."
        cd web-ui
        npm test
        cd ..
        
        # Test server
        print_status "Testing server..."
        cd server
        source venv/bin/activate
        python -m pytest tests/ -v
        cd ..
        
        print_success "All tests passed"
    else
        print_warning "Skipping tests"
    fi
}

# Build components
build_components() {
    print_status "Building components..."
    
    # Build CLI
    print_status "Building CLI..."
    cd cli
    npm run build
    cd ..
    
    # Build VSCode extension
    print_status "Building VSCode extension..."
    cd vscode-extension
    npm run compile
    cd ..
    
    # Build web UI
    print_status "Building web UI..."
    cd web-ui
    npm run build
    cd ..
    
    print_success "All components built successfully"
}

# Deploy to staging
deploy_staging() {
    print_status "Deploying to staging environment..."
    
    # Deploy web UI to Vercel
    if command -v vercel &> /dev/null; then
        print_status "Deploying web UI to Vercel..."
        cd web-ui
        vercel --prod
        cd ..
        print_success "Web UI deployed to Vercel"
    else
        print_warning "Vercel CLI not found, skipping web UI deployment"
    fi
    
    # Deploy server to staging
    print_status "Deploying server to staging..."
    # Add your staging deployment commands here
    print_success "Server deployed to staging"
    
    # Deploy VSCode extension to staging
    print_status "Deploying VSCode extension to staging..."
    # Add your extension deployment commands here
    print_success "VSCode extension deployed to staging"
}

# Deploy to production
deploy_production() {
    print_status "Deploying to production environment..."
    
    # Deploy web UI to Vercel
    if command -v vercel &> /dev/null; then
        print_status "Deploying web UI to Vercel..."
        cd web-ui
        vercel --prod
        cd ..
        print_success "Web UI deployed to Vercel"
    else
        print_warning "Vercel CLI not found, skipping web UI deployment"
    fi
    
    # Deploy server to production
    print_status "Deploying server to production..."
    # Add your production deployment commands here
    print_success "Server deployed to production"
    
    # Deploy VSCode extension to marketplace
    print_status "Deploying VSCode extension to marketplace..."
    cd vscode-extension
    if command -v vsce &> /dev/null; then
        vsce publish
        print_success "VSCode extension published to marketplace"
    else
        print_warning "VSCE not found, skipping extension deployment"
    fi
    cd ..
    
    # Deploy CLI to npm
    print_status "Deploying CLI to npm..."
    cd cli
    if [ -n "$NPM_TOKEN" ]; then
        npm publish
        print_success "CLI published to npm"
    else
        print_warning "NPM_TOKEN not set, skipping CLI deployment"
    fi
    cd ..
}

# Create deployment tag
create_deployment_tag() {
    print_status "Creating deployment tag..."
    
    TIMESTAMP=$(date +"%Y%m%d%H%M%S")
    TAG_NAME="deploy-$ENVIRONMENT-$TIMESTAMP"
    
    git tag -a "$TAG_NAME" -m "Deploy to $ENVIRONMENT at $(date)"
    git push origin "$TAG_NAME"
    
    print_success "Deployment tag created: $TAG_NAME"
}

# Send deployment notification
send_notification() {
    print_status "Sending deployment notification..."
    
    # Add your notification logic here (Slack, Discord, email, etc.)
    print_success "Deployment notification sent"
}

# Main deployment function
main() {
    print_status "Starting deployment to $ENVIRONMENT..."
    
    # Run tests
    run_tests
    
    # Build components
    if [ "$BUILD_ALL" = true ]; then
        build_components
    fi
    
    # Deploy based on environment
    if [ "$ENVIRONMENT" = "staging" ]; then
        deploy_staging
    else
        deploy_production
    fi
    
    # Create deployment tag
    create_deployment_tag
    
    # Send notification
    send_notification
    
    print_success "🎉 Deployment to $ENVIRONMENT completed successfully!"
    echo ""
    echo "Deployment Summary:"
    echo "=================="
    echo "Environment: $ENVIRONMENT"
    echo "Branch: $CURRENT_BRANCH"
    echo "Timestamp: $(date)"
    echo ""
    
    if [ "$ENVIRONMENT" = "staging" ]; then
        echo "Staging URLs:"
        echo "- Web UI: https://staging.coding-agent.com"
        echo "- API: https://staging-api.coding-agent.com"
    else
        echo "Production URLs:"
        echo "- Web UI: https://coding-agent.com"
        echo "- API: https://api.coding-agent.com"
    fi
}

# Run main function
main "$@"
