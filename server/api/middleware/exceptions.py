"""
Custom exception hierarchy for the API.
Provides structured error handling with proper error codes and messages.
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base exception class for API errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class TimeoutException(APIException):
    """Exception raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            status_code=408,
            details=details
        )


class CircuitBreakerException(APIException):
    """Exception raised when circuit breaker is open."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable due to high error rate",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            details=details
        )


class ServiceUnavailableException(APIException):
    """Exception raised when a service is unavailable."""

    def __init__(
        self,
        message: str = "Service is currently unavailable",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details
        )


class ValidationException(APIException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class AuthenticationException(APIException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationException(APIException):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )