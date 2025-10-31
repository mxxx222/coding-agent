"""
Health Check API Routes
Provides endpoints for monitoring system health, services, and circuit breakers.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from services.health import health_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def get_overall_health() -> Dict[str, Any]:
    """
    Get overall system health status.

    Returns comprehensive health information including:
    - Overall system status (healthy/degraded/unhealthy)
    - Individual service statuses
    - System resource usage
    - Circuit breaker states
    - Recent timeout events
    """
    try:
        health = await health_service.check_overall_health()

        # Convert to dict for JSON response
        response = {
            "status": health.status,
            "timestamp": health.timestamp.isoformat(),
            "uptime": health.uptime,
            "services": [
                {
                    "name": service.name,
                    "status": service.status,
                    "response_time": service.response_time,
                    "last_check": service.last_check.isoformat() if service.last_check else None,
                    "error_message": service.error_message,
                    "details": service.details
                }
                for service in health.services
            ],
            "system_resources": health.system_resources,
            "circuit_breakers": health.circuit_breakers,
            "timeout_events": [
                {
                    "service": event["service"],
                    "operation": event["operation"],
                    "timeout_seconds": event["timeout_seconds"],
                    "error": event["error"],
                    "timestamp": event["timestamp"].isoformat()
                }
                for event in health.timeout_events
            ]
        }

        # Set HTTP status code based on health status
        status_code = 200
        if health.status == "degraded":
            status_code = 200  # Still OK, but with warnings
        elif health.status == "unhealthy":
            status_code = 503  # Service Unavailable

        return JSONResponse(content=response, status_code=status_code)

    except Exception as e:
        logger.error(f"Health check endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/timeout")
async def get_timeout_health() -> Dict[str, Any]:
    """
    Get timeout system health and configuration.

    Returns:
    - Timeout configurations for all services
    - Recent timeout events (last 24 hours)
    - Overall timeout system status
    """
    try:
        timeout_health = await health_service.check_timeout_health()

        # Set HTTP status code
        status_code = 200 if timeout_health["status"] == "healthy" else 503

        return JSONResponse(content=timeout_health, status_code=status_code)

    except Exception as e:
        logger.error(f"Timeout health check endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Timeout health check failed: {str(e)}")

@router.get("/health/services")
async def get_services_health() -> Dict[str, Any]:
    """
    Get individual service health statuses.

    Returns health status for each service including:
    - Service status (healthy/unhealthy/degraded)
    - Response times
    - Last check timestamps
    - Error messages and details
    """
    try:
        services_health = await health_service.check_services_health()

        # Check if any services are unhealthy
        unhealthy_services = [
            name for name, service in services_health["services"].items()
            if service["status"] == "unhealthy"
        ]

        status_code = 200 if not unhealthy_services else 503

        return JSONResponse(content=services_health, status_code=status_code)

    except Exception as e:
        logger.error(f"Services health check endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Services health check failed: {str(e)}")

@router.get("/health/circuit-breakers")
async def get_circuit_breakers_health() -> Dict[str, Any]:
    """
    Get circuit breaker states for all services.

    Returns:
    - Circuit breaker states (closed/open/half-open)
    - Failure counts and success counts
    - Recovery timeout information
    - Overall circuit breaker system status
    """
    try:
        circuit_breakers_health = await health_service.check_circuit_breakers_health()

        status_code = 200 if circuit_breakers_health["status"] == "healthy" else 503

        return JSONResponse(content=circuit_breakers_health, status_code=status_code)

    except Exception as e:
        logger.error(f"Circuit breakers health check endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Circuit breakers health check failed: {str(e)}")

@router.get("/health/ready")
async def readiness_probe() -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.

    Returns simple ready/not ready status for load balancer health checks.
    """
    try:
        health = await health_service.check_overall_health()

        # For readiness, we consider the system ready if not completely unhealthy
        is_ready = health.status != "unhealthy"

        response = {
            "status": "ready" if is_ready else "not ready",
            "timestamp": health.timestamp.isoformat()
        }

        status_code = 200 if is_ready else 503

        return JSONResponse(content=response, status_code=status_code)

    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return JSONResponse(
            content={"status": "not ready", "error": str(e)},
            status_code=503
        )

@router.get("/health/live")
async def liveness_probe() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.

    Returns simple alive/dead status for container health checks.
    Always returns alive unless the application is completely unresponsive.
    """
    try:
        response = {
            "status": "alive",
            "timestamp": health_service.last_health_check.isoformat() if health_service.last_health_check else None
        }

        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        # If we can't even respond, the service is dead
        logger.critical(f"Liveness probe failed: {str(e)}")
        return JSONResponse(
            content={"status": "dead", "error": str(e)},
            status_code=503
        )