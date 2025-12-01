"""
PlexSync AI - FastAPI Application
Main entry point for the API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from db.session import create_db_and_tables
from loguru import logger

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url if settings.docs_enabled else None,
    redoc_url=settings.redoc_url if settings.docs_enabled else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting PlexSync AI...")
    create_db_and_tables()
    logger.success("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down PlexSync AI...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }

# Include routers
from api import auth, invoices, sync, analytics, webhooks

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(sync.router, prefix="/api/sync", tags=["Sync"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

