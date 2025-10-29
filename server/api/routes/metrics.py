"""
Metrics API endpoints for Prometheus.
"""

from fastapi import APIRouter
from fastapi.responses import Response
from services.metrics.prometheus import MetricsCollector

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics endpoint."""
    metrics = MetricsCollector.get_metrics()
    return Response(
        content=metrics,
        media_type="text/plain; version=0.0.4"
    )

@router.get("/metrics/json")
async def get_metrics_json():
    """Get metrics as JSON."""
    metrics = MetricsCollector.get_metrics_dict()
    return metrics

@router.get("/metrics/health")
async def metrics_health():
    """Health check for metrics endpoint."""
    return {
        "status": "healthy",
        "metrics_enabled": True
    }

