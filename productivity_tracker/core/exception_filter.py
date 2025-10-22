"""Global exception filter for centralized error handling - inspired by .NET exception filters."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.responses import JSONResponse

from productivity_tracker.core.exceptions import AppError

logger = logging.getLogger(__name__)


class GlobalExceptionFilter:
    """
    Centralized exception filter for converting exceptions to Problem Details format.
    Inspired by .NET's IExceptionFilter pattern.
    """

    @staticmethod
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            field_name = " -> ".join(str(x) for x in error["loc"])
            error_msg = error["msg"]
            error_type = error["type"]

            user_friendly_msg = GlobalExceptionFilter._get_user_friendly_validation_message(
                field_name, error_msg, error_type
            )

            errors.append(
                {
                    "field": field_name,
                    "msg": user_friendly_msg,
                    "type": error_type,
                }
            )

        logger.warning(f"Validation error on {request.url.path}: {errors}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": errors,
                "instance": str(request.url),
            },
        )

    @staticmethod
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        """Handle custom application exceptions."""
        log_message = f"Application error on {request.url.path}: [{exc.error_code}] {exc.message}"

        if exc.context:
            log_message += f" | Context: {exc.context}"

        # Log at appropriate level
        if exc.status_code >= 500:
            logger.error(log_message, exc_info=True)
        elif exc.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_problem_detail(str(request.url)),
        )

    @staticmethod
    async def handle_sqlalchemy_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle SQLAlchemy database errors."""
        error_str = str(exc)

        logger.error(
            f"Database error on {request.url.path}: {type(exc).__name__} - {error_str}",
            exc_info=True,
        )

        user_message = "We're experiencing technical difficulties. Please try again later."
        error_code = "database-error"
        error_title = "Database Error"

        # Detect specific database errors
        if "duplicate key" in error_str.lower() or "unique constraint" in error_str.lower():
            user_message = "This information already exists. Please use different details."
            error_code = "duplicate-entry"
            error_title = "Duplicate Entry"
        elif "foreign key" in error_str.lower():
            user_message = "This operation cannot be completed due to related data."
            error_code = "foreign-key-violation"
            error_title = "Foreign Key Violation"
        elif "connection" in error_str.lower() or "timeout" in error_str.lower():
            user_message = "Unable to connect to the database. Please try again."
            error_code = "database-connection-error"
            error_title = "Database Connection Error"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": error_code,
                "title": error_title,
                "status": 500,
                "detail": user_message,
                "instance": str(request.url),
            },
        )

    @staticmethod
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected/unhandled exceptions."""
        logger.error(
            f"Unhandled exception on {request.url.path}: {type(exc).__name__} - {str(exc)}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "internal-server-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred. Our team has been notified.",
                "instance": str(request.url),
            },
        )

    @staticmethod
    def _get_user_friendly_validation_message(
        field_name: str, error_msg: str, error_type: str
    ) -> str:
        """Convert technical validation messages to user-friendly ones."""
        display_field = field_name.split(" -> ")[-1].replace("_", " ").title()

        validation_message_map = {
            "missing": f"{display_field} is required.",
            "value_error.missing": f"{display_field} is required.",
            "type_error.integer": f"{display_field} must be a number.",
            "type_error.float": f"{display_field} must be a number.",
            "type_error.boolean": f"{display_field} must be true or false.",
            "value_error.email": "Please enter a valid email address.",
            "value_error.url": f"{display_field} must be a valid URL.",
        }

        if error_type in validation_message_map:
            return validation_message_map[error_type]

        # Pattern matching for common validation errors
        if "too_short" in error_type or "min_length" in error_msg.lower():
            return f"{display_field} is too short."
        elif "too_long" in error_type or "max_length" in error_msg.lower():
            return f"{display_field} is too long."
        elif "greater_than" in error_type:
            return f"{display_field} must be greater than the minimum allowed value."
        elif "less_than" in error_type:
            return f"{display_field} must be less than the maximum allowed value."

        # Fallback
        return f"{display_field}: {error_msg}"
