"""
Sentry initialization for FastAPI/ASGI apps.
"""

import os
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


def init_sentry(app):
    """
    Initialize Sentry for a FastAPI/ASGI app.
    
    Usage:
        from server.monitoring.sentry_init import init_sentry
        app = FastAPI(...)
        app = init_sentry(app)
    
    Args:
        app: FastAPI/ASGI application instance
        
    Returns:
        ASGI application wrapped with Sentry middleware
    """
    dsn = os.getenv("SENTRY_DSN")
    
    if not dsn:
        # No DSN configured — skip initialization (safe for local dev)
        print("Sentry DSN not configured, skipping Sentry initialization")
        return app
    
    traces_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=traces_rate,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("RELEASE", None),
        
        # Integrations
        integrations=[
            sentry_sdk.integrations.fastapi.FastApiIntegration(),
        ],
    )
    
    print(f"Sentry initialized: {os.getenv('SENTRY_ENVIRONMENT', 'development')}")
    
    # Wrap the ASGI app so Sentry captures exceptions & performance
    return SentryAsgiMiddleware(app)

