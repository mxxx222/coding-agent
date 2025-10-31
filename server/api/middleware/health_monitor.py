"""
Health Monitoring Middleware
Tracks request-level health metrics and integrates with the health check service.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from services.health import health_service

logger = logging.getLogger(__name__)

class HealthMonitoringMiddleware:
    """
    Middleware for monitoring request-level health metrics.

    Tracks:
    - Request response times
    - Error rates by endpoint
    - Request counts
    - Timeout events
    """

    def __init__(self, app: Callable):
        self.app = app
        self.request_counts = {}
        self.error_counts = {}
        self.response_times = []

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create ASGI app wrapper for monitoring
        start_time = time.time()

        async def monitored_send(message):
            if message["type"] == "http.response.start":
                # Track response
                status_code = message.get("status", 200)
                end_time = time.time()
                response_time = end_time - start_time

                # Store response time (keep last 1000)
                self.response_times.append(response_time)
                if len(self.response_times) > 1000:
                    self.response_times = self.response_times[-1000:]

                # Track request counts
                path = scope.get("path", "/")
                method = scope.get("method", "GET")

                key = f"{method} {path}"
                self.request_counts[key] = self.request_counts.get(key, 0) + 1

                # Track errors
                if status_code >= 400:
                    self.error_counts[key] = self.error_counts.get(key, 0) + 1

                # Log slow requests (>5 seconds)
                if response_time > 5.0:
                    logger.warning(f"Slow request: {key} took {response_time:.2f}s")

                # Log very slow requests (>30 seconds) as errors
                if response_time > 30.0:
                    logger.error(f"Very slow request: {key} took {response_time:.2f}s")

            await send(message)

        await self.app(scope, receive, monitored_send)

    def get_request_metrics(self) -> dict:
        """Get current request monitoring metrics."""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())

        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )

        error_rate = (total_errors / total_requests) if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "request_counts_by_endpoint": self.request_counts.copy(),
            "error_counts_by_endpoint": self.error_counts.copy(),
            "recent_response_times_count": len(self.response_times)
        }

async def health_monitoring_middleware(request: Request, call_next) -> Response:
    """
    FastAPI middleware for health monitoring.

    This is the FastAPI-compatible middleware function that can be added
    to the FastAPI app middleware stack.
    """
    start_time = time.time()

    try:
        # Process the request
        response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log metrics for health monitoring
        path = request.url.path
        method = request.method

        # Track in health service if it's a health endpoint
        if path.startswith("/api/health"):
            logger.debug(f"Health endpoint {method} {path} responded in {response_time:.3f}s with status {response.status_code}")

        # Log slow requests
        if response_time > 10.0:  # 10 seconds threshold for API requests
            logger.warning(f"Slow API request: {method} {path} took {response_time:.2f}s")

        # For timeout monitoring, we could integrate with the timeout managers
        # but for now, just log significant delays
        if response_time > 60.0:  # 1 minute threshold
            logger.error(f"Very slow API request: {method} {path} took {response_time:.2f}s")

            # Record as a timeout event in health service
            health_service.record_timeout_event(
                service_name="api",
                operation=f"{method} {path}",
                timeout_seconds=response_time,
                error=f"Request exceeded 60s threshold"
            )

        return response

    except Exception as e:
        # Calculate response time even for errors
        response_time = time.time() - start_time

        # Log the error with timing
        logger.error(f"Request failed: {request.method} {request.url.path} after {response_time:.2f}s - {str(e)}")

        # Record timeout event for failed requests that took too long
        if response_time > 30.0:
            health_service.record_timeout_event(
                service_name="api",
                operation=f"{request.method} {request.url.path}",
                timeout_seconds=response_time,
                error=f"Request failed after {response_time:.2f}s: {str(e)}"
            )

        # Re-raise the exception to maintain normal error handling
        raise