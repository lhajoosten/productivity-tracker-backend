import logging
import time
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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
