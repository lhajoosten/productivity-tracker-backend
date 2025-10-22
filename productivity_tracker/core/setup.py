"""
Application setup utilities for exception handling and middleware configuration.
"""

from typing import cast

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

from productivity_tracker.core.exceptions import AppError
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    VersionHeaderMiddleware,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from productivity_tracker.core.settings import settings

logger = get_logger(__name__)


def setup_exception_handling(app: FastAPI) -> None:
    """
    Configure all exception handlers for the application using the Global Exception Filter pattern.
    Handlers are registered in order of specificity (most specific first).
    """

    # Type-safe exception handler wrappers
    async def _app_exception_wrapper(request: Request, exc: Exception) -> Response:
        return cast(Response, await app_exception_handler(request, exc))  # type: ignore[arg-type]

    async def _validation_exception_wrapper(request: Request, exc: Exception) -> Response:
        return cast(Response, await validation_exception_handler(request, exc))  # type: ignore[arg-type]

    async def _sqlalchemy_exception_wrapper(request: Request, exc: Exception) -> Response:
        return cast(Response, await sqlalchemy_exception_handler(request, exc))  # type: ignore[arg-type]

    async def _general_exception_wrapper(request: Request, exc: Exception) -> Response:
        return cast(Response, await general_exception_handler(request, exc))

    # Register handlers in order of specificity
    # 1. Custom application exceptions (most specific)
    app.add_exception_handler(AppError, _app_exception_wrapper)  # type: ignore[arg-type]
    logger.info("✓ AppError handler registered")

    # 2. Validation errors (Pydantic)
    app.add_exception_handler(RequestValidationError, _validation_exception_wrapper)  # type: ignore[arg-type]
    logger.info("✓ RequestValidationError handler registered")

    # 3. Database errors (SQLAlchemy)
    app.add_exception_handler(SQLAlchemyError, _sqlalchemy_exception_wrapper)  # type: ignore[arg-type]
    logger.info("✓ SQLAlchemyError handler registered")

    # 4. FastAPI HTTPException - convert to Problem Details
    async def _http_exception_wrapper(request: Request, exc: Exception) -> Response:
        return cast(Response, await http_exception_handler(request, exc))  # type: ignore[arg-type]

    app.add_exception_handler(HTTPException, _http_exception_wrapper)  # type: ignore[arg-type]
    logger.info("✓ HTTPException handler registered")

    # 5. Catch-all for unexpected exceptions (least specific)
    app.add_exception_handler(Exception, _general_exception_wrapper)
    logger.info("✓ General Exception handler registered")

    logger.info("Global exception filter configured successfully")


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the application.
    Middleware is applied in reverse order (last added = first executed).

    Execution order:
    1. RequestLoggingMiddleware (first to receive request, last to process response)
    2. SecurityHeadersMiddleware
    3. GZipMiddleware
    4. VersionHeaderMiddleware
    5. CORSMiddleware (last to receive request, first to process response)
    """
    # CORS middleware - must be first to handle preflight requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    logger.info(f"✓ CORS configured for origins: {settings.CORS_ORIGINS}")

    # Versioning middleware - adds API version headers
    app.add_middleware(VersionHeaderMiddleware)
    logger.info("✓ Version header middleware configured")

    # GZip compression for responses (minimum 1KB)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✓ GZip compression middleware configured (min 1KB)")

    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("✓ Security headers middleware configured")

    # Request logging middleware (last = logs entire request/response cycle)
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("✓ Request logging middleware configured")

    logger.info("All middleware configured successfully")
