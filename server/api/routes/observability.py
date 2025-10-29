"""
Observability test endpoints.
"""

from fastapi import APIRouter
import random

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("/sentry-test", summary="Trigger a test error to ensure Sentry integration works")
async def sentry_test():
    """
    This endpoint intentionally raises an error so you can verify Sentry captures it.
    
    Usage:
        curl http://localhost:8000/api/observability/sentry-test
    
    Expected:
        - HTTP 500 response
        - Error appears in Sentry project
    """
    raise RuntimeError("Sentry test error - verify this appears in Sentry")


@router.get("/metrics-test", summary="Generate test traffic for metrics")
async def metrics_test():
    """
    Generate test traffic to verify metrics collection.
    
    Usage:
        curl http://localhost:8000/api/observability/metrics-test
    
    Expected:
        - HTTP 200 response
        - Metrics visible in /api/metrics endpoint
    """
    # Simulate some work
    import time
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay)
    
    return {
        "status": "success",
        "message": "Test request completed",
        "delay": delay
    }


@router.get("/health")
async def observability_health():
    """Health check for observability features."""
    return {
        "status": "healthy",
        "features": {
            "prometheus": "enabled",
            "sentry": "enabled" if hasattr(router.app, "sentry") else "disabled"
        }
    }

