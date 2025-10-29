from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .routes import code, refactor, test, integrate, indexer, notion, deployment, automation
from .middleware.auth import AuthMiddleware
from .middleware.policy import PolicyMiddleware
from .middleware.cost_tracker import CostTrackerMiddleware
from .middleware.audit_logger import AuditLoggerMiddleware
from .middleware.rate_limiter import RateLimiterMiddleware
from services.llm.openai_client import OpenAIClient
from services.indexer.vector_store import VectorStore
from database.schema import init_db

# Load environment variables
load_dotenv()

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

# Custom middleware (order matters!)
app.add_middleware(AuditLoggerMiddleware)  # Log all requests first
app.add_middleware(RateLimiterMiddleware)  # Rate limit before auth
app.add_middleware(AuthMiddleware)         # Authenticate requests
app.add_middleware(PolicyMiddleware)       # Apply policies
app.add_middleware(CostTrackerMiddleware)  # Track costs

# Include routers
app.include_router(code.router, prefix="/api/analyze", tags=["code-analysis"])
app.include_router(refactor.router, prefix="/api/analyze", tags=["refactoring"])
app.include_router(test.router, prefix="/api/generate", tags=["test-generation"])
app.include_router(integrate.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(indexer.router, prefix="/api/indexer", tags=["indexing"])
app.include_router(notion.router, prefix="/api/notion", tags=["notion"])
app.include_router(deployment.router, prefix="/api/deploy", tags=["deployment"])
app.include_router(automation.router, prefix="/api/automation", tags=["automation"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    # Import integrations to check their status
    try:
        from .routes import notion, deployment
        notion_status = notion.NOTION_ENABLED if notion.NOTION_ENABLED else False
        vercel_status = deployment.VERCEL_ENABLED if deployment.VERCEL_ENABLED else False
    except:
        notion_status = False
        vercel_status = False
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "vector_store": "connected",
            "llm": "connected",
            "notion": "enabled" if notion_status else "disabled",
            "vercel": "enabled" if vercel_status else "disabled"
        }
    }

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
    # Initialize database
    await init_db()
    
    # Initialize vector store
    vector_store = VectorStore()
    await vector_store.initialize()
    
    # Initialize OpenAI client
    openai_client = OpenAIClient()
    await openai_client.initialize()
    
    print("Coding Agent API started successfully!")

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
