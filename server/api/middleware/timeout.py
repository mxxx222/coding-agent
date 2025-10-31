"""
Timeout middleware for FastAPI application.
Provides request-level timeout protection with configurable timeouts per route.
"""

import asyncio
import time
import logging
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .exceptions import TimeoutException

logger = logging.getLogger(__name__)


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts."""

    def __init__(
        self,
        app,
        default_timeout: float = 30.0,
        route_timeouts: Optional[Dict[str, float]] = None
    ):
        super().__init__(app)
        self.default_timeout = default_timeout
        self.route_timeouts = route_timeouts or {}

    def _get_timeout_for_route(self, path: str, method: str) -> float:
        """Get timeout for specific route."""
        route_key = f"{method}:{path}"
        return self.route_timeouts.get(route_key, self.default_timeout)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with timeout handling."""
        timeout_seconds = self._get_timeout_for_route(
            request.url.path,
            request.method
        )

        try:
            # Create timeout task
            start_time = time.time()

            # Use asyncio.wait_for with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout_seconds
            )

            # Log successful request timing
            duration = time.time() - start_time
            logger.info(
                f"Request completed successfully",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "duration": f"{duration:.2f}s",
                    "timeout_limit": f"{timeout_seconds:.1f}s"
                }
            )

            return response

        except asyncio.TimeoutError:
            # Request timed out
            duration = time.time() - start_time
            logger.warning(
                f"Request timeout after {duration:.2f}s (limit: {timeout_seconds:.1f}s)",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "timeout_limit": timeout_seconds,
                    "actual_duration": duration
                }
            )

            raise TimeoutException(
                message=f"Request timed out after {timeout_seconds:.1f} seconds",
                details={
                    "timeout_limit": timeout_seconds,
                    "actual_duration": duration,
                    "path": request.url.path,
                    "method": request.method
                }
            )

        except Exception as e:
            # Re-raise other exceptions to be handled by error handlers
            logger.error(
                f"Request failed with exception: {type(e).__name__}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "exception": str(e)
                }
            )
            raise


def create_timeout_middleware(
    default_timeout: float = 30.0,
    route_timeouts: Optional[Dict[str, float]] = None
) -> TimeoutMiddleware:
    """Factory function to create timeout middleware with configuration."""
    return TimeoutMiddleware(
        app=None,  # Will be set by FastAPI
        default_timeout=default_timeout,
        route_timeouts=route_timeouts
    )