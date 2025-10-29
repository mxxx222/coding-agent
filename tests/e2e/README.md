# E2E Tests for Automation Pipeline

## Overview

End-to-end tests for the complete Notion → Vercel automation pipeline.

## Test Structure

```
tests/e2e/
├── test_automation_pipeline.py    # Main test suite
├── conftest.py                    # Pytest configuration
├── test_runner.sh                 # Manual test runner
└── README.md                      # This file
```

## Running Tests

### Manual Execution

```bash
# Run all tests
./tests/e2e/test_runner.sh

# Run only unit tests
./tests/e2e/test_runner.sh unit

# Run only integration tests
./tests/e2e/test_runner.sh integration

# Run container tests
RUN_CONTAINER_TESTS=true ./tests/e2e/test_runner.sh container
```

### Using Pytest

```bash
# Install dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/e2e/ -v

# Run specific test class
pytest tests/e2e/test_automation_pipeline.py::TestAutomationPipeline -v

# Run with coverage
pytest tests/e2e/ --cov=server --cov-report=html
```

### Environment Setup

```bash
# For unit tests (mocked)
export SKIP_REAL_APIS=true

# For integration tests (real APIs)
export TEST_NOTION_API_KEY="secret_xxx"
export TEST_VERCEL_TOKEN="xxx"
export TEST_NOTION_PAGE_ID="xxx"
export SKIP_REAL_APIS=false
```

## Test Classes

### TestAutomationPipeline

Tests the complete automation workflow with real or mocked services.

**Tests:**
- Notion page fetching
- Structured data extraction
- Vercel project listing
- Complete pipeline flow
- Individual workflow steps

### TestMockAutomationPipeline

Tests automation workflow with mocked responses.

**Tests:**
- Complete pipeline with mocks
- Error handling
- Flow validation

### TestEphemeralContainer

Tests automation in ephemeral containers (requires `RUN_CONTAINER_TESTS=true`).

**Tests:**
- Full pipeline in container
- Environment isolation
- Resource cleanup

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Pushes to main/deploy
- Manual workflow dispatch

See `.github/workflows/e2e-tests.yml` for configuration.

## Coverage

Aim for >70% code coverage for E2E tests.

```bash
# Generate coverage report
pytest tests/e2e/ --cov=server --cov-report=html

# View report
open htmlcov/index.html
```

## Best Practices

### Test Independence

Each test should be independent and not rely on other tests.

### Mock External Services

Use mocks for external APIs unless specifically testing integration:
```python
@pytest.fixture
def mock_notion_api():
    # Mock Notion API responses
    pass
```

### Clear Assertions

Use descriptive assertions:
```python
assert result["status"] == "success", "Pipeline should complete successfully"
```

### Error Handling

Test both success and failure paths:
```python
# Test success
result = await workflow.run_pipeline()
assert result["status"] == "success"

# Test failure
result = await workflow.run_pipeline(invalid_input)
assert result["status"] == "failed"
```

## Debugging

### Verbose Output

```bash
pytest tests/e2e/ -v -s
```

### Specific Test

```bash
pytest tests/e2e/test_automation_pipeline.py::TestAutomationPipeline::test_notion_page_fetch -v
```

### Logs

```bash
pytest tests/e2e/ --log-cli-level=DEBUG
```

## Known Issues

- Container tests require Docker
- Integration tests need real API keys
- Some tests may fail if services are down

## Contributing

When adding new tests:
1. Add to appropriate test class
2. Use descriptive test names
3. Add docstrings
4. Update this README if needed
5. Run locally before submitting PR

## Troubleshooting

### Tests Fail with "Module not found"

```bash
# Ensure you're in the project root
cd /path/to/coding-agent

# Install dependencies
pip install -r server/requirements.txt
pip install pytest pytest-asyncio
```

### Tests Skip Unexpectedly

Check environment variables:
```bash
echo $SKIP_REAL_APIS
echo $TEST_NOTION_API_KEY
```

### Container Tests Don't Run

Ensure Docker is running and accessible:
```bash
docker ps
```

