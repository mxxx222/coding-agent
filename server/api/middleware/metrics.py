"""
Metrics collection middleware.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from services.metrics.prometheus import MetricsCollector

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect metrics for all requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Record metrics for each request."""
        start_time = datetime.now()
        method = request.method
        endpoint = request.url.path
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Record metrics
            MetricsCollector.record_http_request(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Record failed request
            MetricsCollector.record_http_request(
                method=method,
                endpoint=endpoint,
                status=500,
                duration=duration
            )
            
            raise

