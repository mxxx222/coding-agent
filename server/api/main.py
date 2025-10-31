from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from api.routes import code, refactor, test, integrate, workflow, health, work_items, flow_board
from api.middleware.auth import AuthMiddleware
from api.middleware.policy import PolicyMiddleware
from api.middleware.cost_tracker import CostTrackerMiddleware
from api.middleware.health_monitor import health_monitoring_middleware
from api.middleware.timeout import TimeoutMiddleware
from api.middleware.error_handlers import (
    api_exception_handler,
    timeout_exception_handler,
    circuit_breaker_exception_handler,
    service_unavailable_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler,
    generic_exception_handler
)
from api.middleware.exceptions import (
    APIException,
    TimeoutException,
    CircuitBreakerException,
    ServiceUnavailableException
)
from services.llm.openai_client import OpenAIClient
from services.indexer.vector_store import VectorStore
from database.schema import init_db
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

# Load environment variables
load_dotenv()

# Initialize Sentry if DSN is provided
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn and SENTRY_AVAILABLE:
    try:
        # Note: User Reporting DSNs (sntryu_*) are not directly supported by sentry-sdk
        # They require a standard DSN format (https://key@host/project)
        # For now, we'll store the User Reporting DSN but notify that standard DSN is needed
        if sentry_dsn.startswith("sntryu_"):
            print("⚠️  User Reporting DSN detected - this format is not directly supported")
            print("   User Reporting DSNs are for frontend user feedback, not backend error tracking")
            print("   Please use a standard Sentry DSN (https://...) for backend error tracking")
            print("   Current DSN will be stored but Sentry will not be initialized")
            print("   To enable Sentry, add a standard DSN from: Settings → Projects → Client Keys (DSN)")
        elif sentry_dsn.startswith("https://"):
            # Standard DSN format - initialize Sentry
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=1.0,
                environment=os.getenv("ENVIRONMENT", "development"),
                # Enable performance monitoring
                enable_tracing=True,
                # Attach stack traces
                attach_stacktrace=True,
                # Release tracking
                release=os.getenv("SENTRY_RELEASE", None),
            )
            print("✅ Sentry initialized for error tracking")
            print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
        else:
            print(f"⚠️  Invalid Sentry DSN format: {sentry_dsn}")
            print("   Expected format: https://key@host/project or sntryu_* (for frontend)")
    except Exception as e:
        print(f"⚠️  Sentry initialization failed: {e}")
        print("   Error tracking will continue without Sentry")
elif sentry_dsn and not SENTRY_AVAILABLE:
    print("⚠️  Sentry DSN provided but sentry-sdk not installed - skipping Sentry initialization")
    print("   Install with: pip install sentry-sdk[fastapi]")
else:
    print("ℹ️  No Sentry DSN provided - error tracking disabled")

# Initialize FastAPI app
app = FastAPI(
    title="Coding Agent API",
    description="AI-powered coding assistant API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Policy middleware with route-specific configurations
route_policy_configs = {
    "POST:/api/analyze/code": {
        "security": {
            "rate_limit": {"requests_per_minute": 30},
            "access_control": {"require_auth": True}
        },
        "content": {
            "max_code_length": 50000,
            "validation_rules": {"require_syntax_check": True}
        }
    },
    "POST:/api/analyze/refactor": {
        "security": {
            "rate_limit": {"requests_per_minute": 20},
            "access_control": {"require_auth": True}
        },
        "content": {
            "max_code_length": 100000,
            "validation_rules": {"require_syntax_check": True}
        }
    },
    "POST:/api/generate/test": {
        "security": {
            "rate_limit": {"requests_per_minute": 15},
            "access_control": {"require_auth": True}
        },
        "business_rules": {
            "max_concurrent_requests": 3
        }
    },
    "POST:/api/workflow/actions": {
        "security": {
            "rate_limit": {"requests_per_minute": 10},
            "access_control": {"require_auth": True}
        },
        "business_rules": {
            "time_window_restrictions": {
                "maintenance_hours": [2, 3, 4]  # 2-5 AM maintenance
            }
        }
    }
}

app.add_middleware(
    PolicyMiddleware,
    policy_file="server/api/middleware/policies.json",
    route_configs=route_policy_configs
)

# Timeout middleware (must be first for proper timeout handling)
app.add_middleware(
    TimeoutMiddleware,
    default_timeout=30.0,
    route_timeouts={
        "POST:/api/analyze/code": 45.0,  # Code analysis
        "POST:/api/analyze/explain": 35.0,  # Code explanation
        "POST:/api/analyze/refactor": 60.0,  # Refactoring
        "POST:/api/analyze/apply": 45.0,  # Apply refactoring
        "POST:/api/generate/test": 60.0,  # Test generation
        "POST:/api/generate/coverage": 30.0,  # Coverage analysis
        "GET:/api/workflow/flow/{owner}/{repo}": 30.0,  # Flow status
        "POST:/api/workflow/actions": 60.0,  # Action execution
        "POST:/api/workflow/events": 30.0,  # Event emission
        "POST:/api/workflow/specs": 30.0,  # Spec creation
    }
)

# Health monitoring middleware
app.middleware("http")(health_monitoring_middleware)

# Include routers
app.include_router(code.router, prefix="/api/analyze", tags=["code-analysis"])
app.include_router(refactor.router, prefix="/api/analyze", tags=["refactoring"])
app.include_router(test.router, prefix="/api/generate", tags=["test-generation"])
app.include_router(integrate.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(work_items.router, prefix="/api/workitems", tags=["work-items"])
app.include_router(flow_board.router, prefix="/api", tags=["flow-board"])
app.include_router(health.router, prefix="/api", tags=["health"])

# Custom exception handlers (must be added before generic handlers)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(TimeoutException, timeout_exception_handler)
app.add_exception_handler(CircuitBreakerException, circuit_breaker_exception_handler)
app.add_exception_handler(ServiceUnavailableException, service_unavailable_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)

# Global exception handler (fallback for unhandled exceptions)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await generic_exception_handler(request, exc)

# Legacy health check endpoint (now handled by health router)
# This can be removed once clients migrate to the new health endpoints

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Coding Agent API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize database (optional - won't fail if not available)
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        print("   Server will run without database in mock mode")
    
    try:
        # Initialize vector store
        vector_store = VectorStore()
        await vector_store.initialize()
        print("✅ Vector store initialized")
    except Exception as e:
        print(f"⚠️  Vector store not available: {e}")
    
    try:
        # Initialize OpenAI client
        openai_client = OpenAIClient()
        await openai_client.initialize()
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"⚠️  OpenAI client not available: {e}")
    
    print("🚀 Coding Agent API started successfully!")

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Coding Agent API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
