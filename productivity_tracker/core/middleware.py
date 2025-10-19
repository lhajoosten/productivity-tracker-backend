import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

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

        # Try to get authenticated user from request state
        user = getattr(request.state, "user", None)

        if user:
            # Authenticated user
            return f"{client_host} | User(id={user.id}, name={user.name}, email={user.email})"
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
        response: Response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class VersionHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add version headers to all API responses."""

    async def dispatch(self, request: Request, call_next):
        """Add version headers to response."""
        # Get version from request path
        version = get_api_version_from_request(request)

        # Process request
        response: Response = await call_next(request)

        # Add version headers
        response = add_version_headers(response, version)

        return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = []
    for error in exc.errors():
        field_name = " -> ".join(str(x) for x in error["loc"])
        error_msg = error["msg"]
        error_type = error["type"]

        # Convert technical validation messages to user-friendly ones
        user_friendly_msg = _get_user_friendly_validation_message(field_name, error_msg, error_type)

        errors.append(
            {
                "field": field_name,
                "message": user_friendly_msg,
                "type": error_type,
            }
        )

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "The information provided is invalid. Please check the fields and try again.",
            "details": errors,
        },
    )


def _get_user_friendly_validation_message(field_name: str, error_msg: str, error_type: str) -> str:
    """Convert technical validation messages to user-friendly ones."""
    # Remove technical prefixes like "body -> " or "query -> "
    display_field = field_name.split(" -> ")[-1].replace("_", " ").title()

    # Common validation error mappings
    if error_type == "missing":
        return f"{display_field} is required."
    elif error_type == "value_error.missing":
        return f"{display_field} is required."
    elif error_type == "type_error.integer":
        return f"{display_field} must be a number."
    elif error_type == "type_error.float":
        return f"{display_field} must be a number."
    elif error_type == "type_error.boolean":
        return f"{display_field} must be true or false."
    elif error_type == "value_error.email":
        return "Please enter a valid email address."
    elif error_type == "value_error.url":
        return f"{display_field} must be a valid URL."
    elif "too_short" in error_type or "min_length" in error_msg.lower():
        return f"{display_field} is too short."
    elif "too_long" in error_type or "max_length" in error_msg.lower():
        return f"{display_field} is too long."
    elif "greater_than" in error_type:
        return f"{display_field} must be greater than the minimum allowed value."
    elif "less_than" in error_type:
        return f"{display_field} must be less than the maximum allowed value."
    else:
        # Fallback to a more generic but still friendly message
        return f"{display_field}: {error_msg}"


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors with user-friendly messages."""
    error_str = str(exc)

    # Log the full technical error
    logger.error(
        f"Database error on {request.url.path}: {type(exc).__name__} - {error_str}",
        exc_info=True,
    )

    # Determine user-friendly message based on error type
    user_message = "We're experiencing technical difficulties. Please try again later."
    error_code = "DATABASE_ERROR"

    # Check for specific database errors
    if "duplicate key" in error_str.lower() or "unique constraint" in error_str.lower():
        user_message = (
            "This information already exists in our system. Please use different details."
        )
        error_code = "DUPLICATE_ENTRY"
    elif "foreign key" in error_str.lower():
        user_message = (
            "This operation cannot be completed due to related data. Please contact support."
        )
        error_code = "FOREIGN_KEY_VIOLATION"
    elif "connection" in error_str.lower() or "timeout" in error_str.lower():
        user_message = "Unable to connect to the database. Please try again in a moment."
        error_code = "DATABASE_CONNECTION_ERROR"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": error_code,
            "message": user_message,
        },
    )


async def app_exception_handler(request: Request, exc: AppError):
    """Handle custom application exceptions with context and user-friendly messages."""
    # Log with full context
    log_message = f"Application error on {request.url.path}: [{exc.error_code}] {exc.message}"

    if exc.context:
        log_message += f" | Context: {exc.context}"

    # Log at appropriate level based on status code
    if exc.status_code >= 500:
        logger.error(log_message, exc_info=True)
    elif exc.status_code >= 400:
        logger.warning(log_message)
    else:
        logger.info(log_message)

    # Return user-friendly response
    response_content: dict[str, Any] = {
        "error": exc.error_code,
        "message": exc.user_message,
    }

    # Include context in development/debug mode only
    from productivity_tracker.core.settings import settings

    if settings.DEBUG and exc.context:
        response_content["debug_context"] = exc.context

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with proper logging and user-friendly messages."""
    # Log full details for debugging
    logger.error(
        f"Unhandled exception on {request.url.path}: {type(exc).__name__} - {str(exc)}",
        exc_info=True,
    )

    # Return generic user-friendly message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Our team has been notified and will look into it.",
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions with improved user-friendly messages."""
    # Log the exception
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    else:
        logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    # Convert technical messages to user-friendly ones
    user_message = _get_user_friendly_http_message(exc.status_code, exc.detail)
    error_code = _get_error_code_from_status(exc.status_code)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_code,
            "message": user_message,
        },
    )


def _get_user_friendly_http_message(status_code: int, detail: str) -> str:
    """Convert HTTP exception details to user-friendly messages."""
    # Check if detail is already user-friendly (doesn't contain technical terms)
    technical_terms = ["database", "sql", "query", "exception", "traceback", "error"]
    is_technical = any(term in detail.lower() for term in technical_terms)

    if not is_technical and len(detail) < 150:
        return detail

    # Default user-friendly messages based on status code
    friendly_messages = {
        400: "The request was invalid. Please check your input and try again.",
        401: "You need to be logged in to access this resource.",
        403: "You don't have permission to access this resource.",
        404: "The resource you're looking for doesn't exist.",
        405: "This action is not allowed.",
        409: "This action conflicts with existing data.",
        422: "The information provided is invalid.",
        429: "Too many requests. Please wait a moment and try again.",
        500: "We're experiencing technical difficulties. Please try again later.",
        502: "The service is temporarily unavailable. Please try again later.",
        503: "The service is currently unavailable. Please try again later.",
    }

    return friendly_messages.get(status_code, detail)


def _get_error_code_from_status(status_code: int) -> str:
    """Get error code from HTTP status code."""
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    return error_codes.get(status_code, f"HTTP_{status_code}")
