"""
Rate limiting middleware to prevent abuse.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict
from collections import defaultdict
import os

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting."""
    
    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        
        # In-memory store (use Redis in production)
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Cleanup old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old request timestamps."""
        current_time = time.time()
        
        # Cleanup every 5 minutes
        if current_time - self.last_cleanup > 300:
            cutoff_time = current_time - 60  # Keep last minute
            
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    ts for ts in self.requests[key]
                    if ts > cutoff_time
                ]
                
                # Remove empty entries
                if not self.requests[key]:
                    del self.requests[key]
            
            self.last_cleanup = current_time
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique key for rate limiting."""
        # Use IP address for anonymous requests
        client_ip = request.client.host if request.client else "unknown"
        
        # Use user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request."""
        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Cleanup old entries
        self._cleanup_old_entries()
        
        # Get client key
        client_key = self._get_client_key(request)
        current_time = time.time()
        
        # Get request history
        request_times = self.requests[client_key]
        
        # Remove requests older than 1 minute
        request_times = [
            ts for ts in request_times
            if current_time - ts < 60
        ]
        self.requests[client_key] = request_times
        
        # Check burst limit
        recent_requests = [
            ts for ts in request_times
            if current_time - ts < 1  # Last second
        ]
        
        if len(recent_requests) >= self.burst_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down."
            )
        
        # Check requests per minute
        if len(request_times) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Record request
        request_times.append(current_time)
        self.requests[client_key] = request_times
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(request_times)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(request_times[0] + 60) if request_times else int(current_time + 60)
        )
        
        return response

