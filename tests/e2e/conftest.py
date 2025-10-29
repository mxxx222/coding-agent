"""
Pytest configuration for E2E tests.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_config() -> dict:
    """Provide test configuration."""
    return {
        "notion_api_key": os.getenv("TEST_NOTION_API_KEY"),
        "vercel_token": os.getenv("TEST_VERCEL_TOKEN"),
        "notion_page_id": os.getenv("TEST_NOTION_PAGE_ID"),
        "skip_real_apis": os.getenv("SKIP_REAL_APIS", "true").lower() == "true"
    }


@pytest.fixture
def mark_skipped_if_no_config(test_config):
    """Helper to skip tests if config is missing."""
    def _skip_if_missing(key):
        if not test_config.get(key):
            pytest.skip(f"Missing test configuration: {key}")
    return _skip_if_missing


# Pytest markers
pytest_plugins = ["pytest_asyncio"]

