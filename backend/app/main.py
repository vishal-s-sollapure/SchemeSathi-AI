import anyio
from contextlib import asynccontextmanager
import logging
import os
import shutil
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    EntityConflictException,
    EntityNotFoundException,
    SchemeSathiException,
    ValidationException,
)
from app.core.rate_limiter import RateLimitMiddleware
from app.database import init_db

# Configure basic logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("schemesathi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schema safely in threadpool
    logger.info("Initializing SchemeSathi AI database tables...")
    await anyio.to_thread.run_sync(init_db)
    
    # Automatically seed verified official knowledge base on fresh deployment
    from app.data.seed_db import seed_database
    await anyio.to_thread.run_sync(seed_database)
    logger.info("Database initialized and verified knowledge base seeded successfully.")
    yield
    # Graceful shutdown: cleanly dispose database engine and connection pool
    logger.info("SchemeSathi AI shutdown initiated: disposing database connection pool...")
    from app.database import engine
    await anyio.to_thread.run_sync(engine.dispose)
    logger.info("SchemeSathi AI shutdown complete: database connections successfully drained.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for SchemeSathi AI — Government Benefits and Scholarship Readiness Assistant",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# CORS Middleware — strictly scoped to explicit allowed origins and optional project preview regex
cors_options = {
    "allow_origins": settings.BACKEND_CORS_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With", "X-Admin-Key"],
}
if settings.CORS_ORIGIN_REGEX:
    cors_options["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX

app.add_middleware(
    CORSMiddleware,
    **cors_options,
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.ENVIRONMENT == "production" or not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# Exception Handlers
@app.exception_handler(EntityNotFoundException)
async def not_found_exception_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "NotFoundError",
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(EntityConflictException)
async def conflict_exception_handler(request: Request, exc: EntityConflictException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "ConflictError",
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": exc.message,
            "detail": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "path": request.url.path,
        },
    )


# Root health endpoint (Liveness probe: returns 200 without blocking on downstream dependencies)
@app.get("/api/health", tags=["Health"])
def get_root_health():
    """Exact requirement: GET /api/health -> {'status': 'healthy', 'application': 'SchemeSathi AI'}"""
    return {
        "status": "healthy",
        "application": settings.PROJECT_NAME,
    }


# Root readiness probe (Validates database connectivity and disk storage availability)
@app.get("/api/ready", tags=["Health"])
def get_readiness_probe():
    """Readiness probe that validates application readiness, database connectivity, and storage availability."""
    from sqlalchemy import text
    from app.database import SessionLocal

    # 1. Probe storage availability
    try:
        total, used, free = shutil.disk_usage(os.path.abspath("."))
        free_mb = round(free / (1024 * 1024), 2)
        if free_mb < 10.0:  # Critically low storage (<10MB)
            logger.error(f"Readiness probe failed: critically low disk space ({free_mb} MB available).")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "database": "connected",
                    "disk": "exhausted",
                    "disk_free_mb": free_mb,
                    "application": settings.PROJECT_NAME,
                    "error": "Critically low disk storage (<10 MB remaining).",
                },
            )
        disk_status = "warning" if free_mb < 50.0 else "healthy"
    except Exception as d_exc:
        logger.warning(f"Disk space inspection warning: {d_exc}")
        disk_status = "unknown"
        free_mb = -1.0

    # 2. Probe database connectivity
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "disk": disk_status,
            "disk_free_mb": free_mb,
            "application": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }
    except Exception as exc:
        logger.error(f"Readiness probe failed: {type(exc).__name__}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "unavailable",
                "disk": disk_status,
                "disk_free_mb": free_mb,
                "application": settings.PROJECT_NAME,
                "error": "Database connectivity check failed.",
            },
        )


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "ready": "/api/ready",
    }
