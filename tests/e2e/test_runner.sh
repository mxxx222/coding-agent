#!/bin/bash

# E2E Test Runner for Automation Pipeline
#
# Usage:
#   ./test_runner.sh              # Run all tests
#   ./test_runner.sh unit         # Run only unit tests
#   ./test_runner.sh integration  # Run only integration tests
#   ./test_runner.sh container    # Run container tests

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TEST_TYPE=${1:-all}
PYTEST_ARGS="-v --tb=short"
SKIP_REAL_APIS=true

echo -e "${GREEN}🚀 Starting E2E Test Runner${NC}"
echo "Test Type: $TEST_TYPE"

# Change to project root
cd "$(dirname "$0")/../.."

# Setup environment
echo -e "${YELLOW}📦 Setting up environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q pytest pytest-asyncio pytest-cov
cd server && pip install -q -r requirements.txt && cd ..

# Run different test types
case "$TEST_TYPE" in
    unit)
        echo -e "${GREEN}Running unit tests...${NC}"
        SKIP_REAL_APIS=true pytest tests/e2e/test_automation_pipeline.py -k "not integration and not container" $PYTEST_ARGS
        ;;
    integration)
        echo -e "${GREEN}Running integration tests...${NC}"
        SKIP_REAL_APIS=false pytest tests/e2e/test_automation_pipeline.py -k "integration" $PYTEST_ARGS
        ;;
    container)
        echo -e "${GREEN}Running container tests...${NC}"
        if [ "$RUN_CONTAINER_TESTS" != "true" ]; then
            echo -e "${RED}Container tests require RUN_CONTAINER_TESTS=true${NC}"
            exit 1
        fi
        pytest tests/e2e/test_automation_pipeline.py::TestEphemeralContainer $PYTEST_ARGS
        ;;
    all)
        echo -e "${GREEN}Running all tests...${NC}"
        
        # Unit tests
        echo -e "${YELLOW}📋 Running unit tests...${NC}"
        SKIP_REAL_APIS=true pytest tests/e2e/test_automation_pipeline.py::TestMockAutomationPipeline $PYTEST_ARGS
        
        # Integration tests (skip if no config)
        if [ -n "$TEST_NOTION_API_KEY" ] && [ -n "$TEST_VERCEL_TOKEN" ]; then
            echo -e "${YELLOW}📋 Running integration tests...${NC}"
            SKIP_REAL_APIS=false pytest tests/e2e/test_automation_pipeline.py::TestAutomationPipeline $PYTEST_ARGS
        else
            echo -e "${YELLOW}⏭️ Skipping integration tests (no API keys configured)${NC}"
        fi
        
        # Summary
        echo -e "${GREEN}✅ Tests completed${NC}"
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Usage: $0 [unit|integration|container|all]"
        exit 1
        ;;
esac

# Cleanup
deactivate

echo -e "${GREEN}🎉 Test run complete${NC}"

