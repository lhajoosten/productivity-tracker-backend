"""Custom exceptions for the application with user-friendly messages."""

from typing import Any


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        user_message: str | None = None,
        status_code: int = 500,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Initialize application exception.

        Args:
            message: Technical message for logging
            user_message: User-friendly message to display to end users
            status_code: HTTP status code
            error_code: Application-specific error code
            context: Additional context for debugging
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


# Authentication & Authorization Exceptions
class AuthenticationError(AppError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        user_message: str = "Invalid login credentials. Please try again.",
        context: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            user_message=user_message,
            status_code=401,
            error_code="AUTH_FAILED",
            context=context,
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when username or password is incorrect."""

    def __init__(self, username: str | None = None):
        context = {"username": username} if username else {}
        super().__init__(
            message=f"Invalid credentials for user: {username or 'unknown'}",
            user_message="Invalid email or password. Please check your credentials and try again.",
            context=context,
        )
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""

    def __init__(self):
        super().__init__(
            message="Token has expired",
            user_message="Your session has expired. Please log in again.",
        )
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid."""

    def __init__(self, reason: str = "Invalid token"):
        super().__init__(
            message=f"Invalid token: {reason}",
            user_message="Your session is invalid. Please log in again.",
        )
        self.error_code = "INVALID_TOKEN"


class InactiveUserError(AppError):
    """Raised when trying to authenticate an inactive user."""

    def __init__(self, user_id: str | None = None):
        context = {"user_id": user_id} if user_id else {}
        super().__init__(
            message=f"User account is inactive: {user_id or 'unknown'}",
            user_message="Your account is inactive. Please contact support.",
            status_code=403,
            error_code="INACTIVE_USER",
            context=context,
        )


class PermissionDeniedError(AppError):
    """Raised when user doesn't have required permissions."""

    def __init__(self, permission: str | None = None, resource: str | None = None):
        context = {}
        if permission:
            context["permission"] = permission
        if resource:
            context["resource"] = resource

        message = f"Permission denied: {permission or 'unknown permission'}"
        if resource:
            message += f" on {resource}"

        super().__init__(
            message=message,
            user_message="You don't have permission to perform this action.",
            status_code=403,
            error_code="PERMISSION_DENIED",
            context=context,
        )


# Resource Exceptions
class ResourceNotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str | None = None):
        context = {"resource_type": resource_type}
        if resource_id:
            context["resource_id"] = resource_id

        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"

        super().__init__(
            message=message,
            user_message=f"The {resource_type.lower()} you're looking for doesn't exist.",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            context=context,
        )


class ResourceAlreadyExistsError(AppError):
    """Raised when trying to create a resource that already exists."""

    def __init__(
        self,
        resource_type: str,
        field: str | None = None,
        value: str | None = None,
    ):
        context = {"resource_type": resource_type}
        if field:
            context["field"] = field
        if value:
            context["value"] = value

        message = f"{resource_type} already exists"
        if field and value:
            message += f": {field}='{value}'"

        user_message = (
            f"A {resource_type.lower()} with this {field or 'information'} already exists."
        )

        super().__init__(
            message=message,
            user_message=user_message,
            status_code=409,
            error_code="RESOURCE_ALREADY_EXISTS",
            context=context,
        )


# Validation Exceptions
class ValidationError(AppError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        user_message: str | None = None,
        field: str | None = None,
        value: Any = None,
    ):
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)

        super().__init__(
            message=message,
            user_message=user_message or "The information provided is invalid.",
            status_code=422,
            error_code="VALIDATION_ERROR",
            context=context,
        )


class InvalidPasswordError(ValidationError):
    """Raised when password doesn't meet requirements."""

    def __init__(self, reason: str | None = None):
        message = f"Invalid password: {reason}" if reason else "Invalid password"
        super().__init__(
            message=message,
            user_message="Password doesn't meet security requirements. Please choose a stronger password.",
        )
        self.error_code = "INVALID_PASSWORD"


class PasswordMismatchError(ValidationError):
    """Raised when current password is incorrect."""

    def __init__(self):
        super().__init__(
            message="Current password is incorrect",
            user_message="The current password you entered is incorrect.",
        )
        self.error_code = "PASSWORD_MISMATCH"


# Business Logic Exceptions
class BusinessLogicError(AppError):
    """Raised when business logic validation fails."""

    def __init__(self, message: str, user_message: str, context: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            user_message=user_message,
            status_code=400,
            error_code="BUSINESS_LOGIC_ERROR",
            context=context,
        )


class EmailAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when trying to register with an email that already exists."""

    def __init__(self, email: str):
        super().__init__(
            resource_type="User",
            field="email",
            value=email,
        )
        self.user_message = "An account with this email address already exists. Please use a different email or try logging in."
        self.error_code = "EMAIL_ALREADY_EXISTS"


class UsernameAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when trying to register with a username that already exists."""

    def __init__(self, username: str):
        super().__init__(
            resource_type="User",
            field="username",
            value=username,
        )
        self.user_message = "This username is already taken. Please choose a different username."
        self.error_code = "USERNAME_ALREADY_EXISTS"


# Database Exceptions
class DatabaseError(AppError):
    """Raised when a database operation fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        context = {}
        if original_error:
            context["original_error"] = str(original_error)
            context["error_type"] = type(original_error).__name__

        super().__init__(
            message=f"Database error: {message}",
            user_message="We're experiencing technical difficulties. Please try again later.",
            status_code=500,
            error_code="DATABASE_ERROR",
            context=context,
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, original_error: Exception | None = None):
        super().__init__(
            message="Failed to connect to database",
            original_error=original_error,
        )
        self.error_code = "DATABASE_CONNECTION_ERROR"
        self.user_message = "Unable to connect to the database. Please try again later."


# Rate Limiting
class RateLimitError(AppError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        context = {}
        if retry_after:
            context["retry_after"] = retry_after

        super().__init__(
            message="Rate limit exceeded",
            user_message="Too many requests. Please wait a moment and try again.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            context=context,
        )


# External Service Exceptions
class ExternalServiceError(AppError):
    """Raised when an external service fails."""

    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"External service error ({service_name}): {message}",
            user_message="We're having trouble connecting to an external service. Please try again later.",
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            context={"service": service_name},
        )
