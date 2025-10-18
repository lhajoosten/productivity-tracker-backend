from typing import cast

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

from productivity_tracker.api import auth, health, permissions, roles
from productivity_tracker.core.database import Base, engine
from productivity_tracker.core.exceptions import AppError
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


# Type-safe exception handler wrappers
async def _app_exception_wrapper(request: Request, exc: Exception) -> Response:
    return cast(Response, await app_exception_handler(request, exc))  # type: ignore[arg-type]


async def _http_exception_wrapper(request: Request, exc: Exception) -> Response:
    return cast(Response, await http_exception_handler(request, exc))  # type: ignore[arg-type]


async def _validation_exception_wrapper(request: Request, exc: Exception) -> Response:
    return cast(Response, await validation_exception_handler(request, exc))  # type: ignore[arg-type]


async def _sqlalchemy_exception_wrapper(request: Request, exc: Exception) -> Response:
    return cast(Response, await sqlalchemy_exception_handler(request, exc))  # type: ignore[arg-type]


# Register handlers in this order (more specific first)
app.add_exception_handler(AppError, _app_exception_wrapper)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, _http_exception_wrapper)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, _validation_exception_wrapper)  # type: ignore[arg-type]
app.add_exception_handler(SQLAlchemyError, _sqlalchemy_exception_wrapper)  # type: ignore[arg-type]
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

# Include routers with `/api/v1` prefix for versioning
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")


@app.get("/health")
@app.head("/health")  # Support HEAD requests
async def root_health():
    """Root-level health check for infrastructure."""
    return {"status": "healthy"}


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
