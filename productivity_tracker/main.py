from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.exc import SQLAlchemyError

from productivity_tracker.api import auth, health, permissions, roles
from productivity_tracker.core.database import Base, engine
from productivity_tracker.core.exceptions import AppException
from productivity_tracker.core.logging_config import get_logger, setup_logging
from productivity_tracker.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from productivity_tracker.core.settings import settings

# Setup logging first
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="A FastAPI-based backend for tracking productivity metrics",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register handlers in this order (more specific first)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add trusted host middleware (only in production)
if not settings.DEBUG:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[".com", "*.localhost.com"])

# Include routers with `/api/v1` prefix for versioning
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")
