from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key")
        self.algorithm = "HS256"
        self.token_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    async def dispatch(self, request, call_next):
        """Process JWT authentication if token is provided."""
        # Skip auth for public endpoints
        if request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/redoc") or request.url.path.startswith("/api/health"):
            response = await call_next(request)
            return response
        
        # For protected endpoints, check token
        # We'll just pass through for now (full auth can be added later)
        response = await call_next(request)
        return response

    def create_access_token(self, data: dict) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.token_expire_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    secret_key = os.getenv("JWT_SECRET", "your-secret-key")
    algorithm = "HS256"
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = verify_token(credentials.credentials)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "permissions": payload.get("permissions", [])
    }

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Get the current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "permissions": payload.get("permissions", [])
        }
    except HTTPException:
        return None

def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user or permission not in user.get("permissions", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator