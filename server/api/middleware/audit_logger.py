"""
Audit logging middleware for security and compliance.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests for audit purposes."""
    
    def __init__(self, app, audit_file: str = "logs/api-audit.log"):
        super().__init__(app)
        self.audit_file = audit_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup audit logging."""
        import os
        os.makedirs(os.path.dirname(self.audit_file), exist_ok=True)
        
        # Create file handler
        handler = logging.FileHandler(self.audit_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response for auditing."""
        start_time = datetime.now()
        
        # Log request details
        audit_entry = {
            "timestamp": start_time.isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "referer": request.headers.get("referer"),
        }
        
        # Add authentication info if available
        auth_header = request.headers.get("authorization")
        if auth_header:
            audit_entry["authenticated"] = True
            audit_entry["auth_type"] = auth_header.split()[0] if auth_header else None
        else:
            audit_entry["authenticated"] = False
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Add response details
            audit_entry["status_code"] = response.status_code
            audit_entry["duration_seconds"] = duration
            audit_entry["success"] = 200 <= response.status_code < 300
            
            # Log audit entry
            logger.info(json.dumps(audit_entry))
            
            return response
            
        except Exception as e:
            # Log error
            audit_entry["status_code"] = 500
            audit_entry["error"] = str(e)
            audit_entry["success"] = False
            audit_entry["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            
            logger.error(json.dumps(audit_entry))
            
            raise
    
    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "info"
    ):
        """Log a security-related event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if severity == "error" or severity == "critical":
            logger.error(json.dumps(event))
        else:
            logger.warning(json.dumps(event))

