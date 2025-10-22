import logging
import time
from collections.abc import Callable

from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from productivity_tracker.core.exception_filter import GlobalExceptionFilter
from productivity_tracker.core.exceptions import AppError
from productivity_tracker.versioning.utils import (
    add_version_headers,
    get_api_version_from_request,
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def _get_user_info(self, request: Request) -> str:
        """Extract user information from request."""
        client_host = request.client.host if request.client else "unknown"
        user = getattr(request.state, "user", None)

        if user:
            return f"{client_host} | User(id={user.id}, name={user.name}, email={user.email})"
        else:
            return f"{client_host} | Unknown"

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        user_info = self._get_user_info(request)

        logger.info(f"→ {request.method} {request.url.path} | {user_info}")

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            if response.status_code >= 500:
                log_level = logging.ERROR
                status_symbol = "✗"
            elif response.status_code >= 400:
                log_level = logging.WARNING
                status_symbol = "⚠"
            else:
                log_level = logging.INFO
                status_symbol = "✓"

            logger.log(
                log_level,
                f"{status_symbol} {request.method} {request.url.path} "
                f"→ {response.status_code} ({duration_ms}ms) | {user_info}",
            )

            return response

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"✗ {request.method} {request.url.path} "
                f"→ EXCEPTION: {type(e).__name__}: {str(e)} ({duration_ms}ms) | {user_info}",
                exc_info=True,
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class VersionHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add version headers to all API responses."""

    async def dispatch(self, request: Request, call_next):
        version = get_api_version_from_request(request)
        response: Response = await call_next(request)
        response = add_version_headers(response, version)
        return response


# Exception Handlers using GlobalExceptionFilter
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return await GlobalExceptionFilter.handle_validation_error(request, exc)


async def app_exception_handler(request: Request, exc: AppError):
    """Handle custom application exceptions."""
    return await GlobalExceptionFilter.handle_app_error(request, exc)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    return await GlobalExceptionFilter.handle_sqlalchemy_error(request, exc)


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return await GlobalExceptionFilter.handle_unexpected_error(request, exc)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTPException."""
    logger.warning(f"HTTP exception on {request.url.path}: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "http-error",
            "title": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url),
        },
    )
