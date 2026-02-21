"""
Main FastAPI application entry point.
Configures middleware, routes, and startup/shutdown events.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.minio_client import init_minio
from app.middleware.audit import AuditMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up surveillance system API...")
    await init_db()
    await init_redis()
    await init_minio()
    logger.info("Surveillance system API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down surveillance system API...")
    await close_db()
    await close_redis()
    logger.info("Surveillance system API shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="IPTV Facial Recognition Surveillance System",
    description="""
    Microservices-based facial recognition platform for IPTV surveillance cameras.
    
    ## Features
    
    * **Camera Management**: Add, configure, and monitor RTSP/HTTP camera streams
    * **Subject Tracking**: Face recognition with vector-based identity management
    * **Real-time Alerts**: Rule-based notifications for security events
    * **Analytics**: Heatmaps, movement patterns, and demographic insights
    * **GDPR Compliance**: Audit trails, data retention, and consent management
    
    ## Authentication
    
    Most endpoints require JWT authentication. Obtain a token from `/api/v1/auth/login`.
    """,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "surveillance-api"
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "IPTV Facial Recognition Surveillance System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
