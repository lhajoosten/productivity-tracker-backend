import logging
import time
from collections.abc import Callable

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def _get_user_info(self, request: Request) -> str:
        """Extract user information from request."""
        client_host = request.client.host if request.client else "unknown"

        # Try to get authenticated user from request state
        user = getattr(request.state, "user", None)

        if user:
            # Authenticated user
            return (
                f"{client_host} | "
                f"User(id={user.id}, name={user.name}, email={user.email})"
            )
        else:
            # Unauthenticated user
            return f"{client_host} | Unknown"

    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()

        # Get user info
        user_info = self._get_user_info(request)

        # Log request start
        logger.info(f"→ {request.method} {request.url.path} | {user_info}")

        # Process request
        try:
            response: Response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = logging.ERROR
                status_symbol = "✗"
            elif response.status_code >= 400:
                log_level = logging.WARNING
                status_symbol = "⚠"
            else:
                log_level = logging.INFO
                status_symbol = "✓"

            # Log response with status code and duration
            logger.log(
                log_level,
                f"{status_symbol} {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration_ms}ms) | {user_info}",
            )

            return response

        except Exception as e:
            # Calculate duration even for errors
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Log exception
            logger.error(
                f"✗ {request.method} {request.url.path} "
                f"→ EXCEPTION: {type(e).__name__}: {str(e)} ({duration_ms}ms) | {user_info}",
                exc_info=True,
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error on {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
