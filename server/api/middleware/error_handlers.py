"""
Global exception handlers for the FastAPI application.
Provides structured error responses and proper logging.
"""

import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from .exceptions import (
    APIException,
    TimeoutException,
    CircuitBreakerException,
    ServiceUnavailableException,
    ValidationException,
    AuthenticationException,
    AuthorizationException
)

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> Dict[str, Any]:
    """Create a structured error response."""
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status_code": status_code
        }
    }

    if details:
        response["error"]["details"] = details

    if request_id:
        response["request_id"] = request_id

    # Add debug information in development
    import os
    if os.getenv("ENVIRONMENT", "production").lower() == "development":
        response["debug"] = {
            "timestamp": "2025-10-31T01:45:46.582Z",  # This would be dynamic in real implementation
            "path": "would be request.url.path",
            "method": "would be request.method"
        }

    return response


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": str(request.url),
            "method": request.method
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def timeout_exception_handler(request: Request, exc: TimeoutException) -> JSONResponse:
    """Handle timeout exceptions with specific logging."""
    logger.warning(
        f"Request timeout: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": str(request.url),
            "method": request.method,
            "timeout_details": exc.details
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def circuit_breaker_exception_handler(request: Request, exc: CircuitBreakerException) -> JSONResponse:
    """Handle circuit breaker exceptions."""
    logger.warning(
        f"Circuit breaker open: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": str(request.url),
            "method": request.method
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailableException) -> JSONResponse:
    """Handle service unavailable exceptions."""
    logger.error(
        f"Service unavailable: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": str(request.url),
            "method": request.method
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    logger.error(
        f"Starlette HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=exc.status_code,
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.critical(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={
            "path": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )

    # Capture exception in Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_exception(exc)

    response_data = create_error_response(
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        request_id=getattr(request.state, 'request_id', None)
    )

    return JSONResponse(
        status_code=500,
        content=response_data
    )