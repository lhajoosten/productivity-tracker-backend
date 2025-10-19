"""Unit tests for custom exceptions."""

import pytest

from productivity_tracker.core.exceptions import (
    AppError,
    BusinessLogicError,
    DatabaseError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidTokenError,
    PasswordMismatchError,
    PermissionDeniedError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    TokenExpiredError,
    UsernameAlreadyExistsError,
    ValidationError,
)

pytestmark = [pytest.mark.unit]


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_app_exception_base(self):
        """Test base AppError."""
        exc = AppError(
            message="Technical error",
            user_message="User-friendly error",
            status_code=400,
            error_code="TEST_ERROR",
            context={"key": "value"},
        )

        assert exc.message == "Technical error"
        assert exc.user_message == "User-friendly error"
        assert exc.status_code == 400
        assert exc.error_code == "TEST_ERROR"
        assert exc.context == {"key": "value"}
        assert str(exc) == "[TEST_ERROR] Technical error"

    def test_app_exception_defaults(self):
        """Test AppError with default values."""
        exc = AppError(message="Error message")

        assert exc.user_message == "Error message"  # Defaults to message
        assert exc.status_code == 500  # Default status
        assert exc.error_code == "AppError"  # Defaults to class name
        assert exc.context == {}

    def test_invalid_credentials_error(self):
        """Test InvalidCredentialsError."""
        exc = InvalidCredentialsError(username="testuser")

        assert exc.status_code == 401
        assert exc.error_code == "INVALID_CREDENTIALS"
        assert "invalid" in exc.user_message.lower()
        assert exc.context["username"] == "testuser"

    def test_inactive_user_error(self):
        """Test InactiveUserError."""
        exc = InactiveUserError(user_id="123")

        assert exc.status_code == 403
        assert exc.error_code == "INACTIVE_USER"
        assert "inactive" in exc.user_message.lower()
        assert exc.context["user_id"] == "123"

    def test_invalid_token_error(self):
        """Test InvalidTokenError."""
        exc = InvalidTokenError(reason="Token expired")

        assert exc.status_code == 401
        assert exc.error_code == "INVALID_TOKEN"
        assert "session" in exc.user_message.lower()

    def test_token_expired_error(self):
        """Test TokenExpiredError."""
        exc = TokenExpiredError()

        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"
        assert "expired" in exc.user_message.lower()

    def test_permission_denied_error(self):
        """Test PermissionDeniedError."""
        exc = PermissionDeniedError(permission="admin", resource="users")

        assert exc.status_code == 403
        assert exc.error_code == "PERMISSION_DENIED"
        assert "permission" in exc.user_message.lower()
        assert exc.context["permission"] == "admin"
        assert exc.context["resource"] == "users"

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        exc = ResourceNotFoundError(resource_type="User", resource_id="123")

        assert exc.status_code == 404
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert "user" in exc.user_message.lower()
        assert exc.context["resource_type"] == "User"
        assert exc.context["resource_id"] == "123"

    def test_email_already_exists_error(self):
        """Test EmailAlreadyExistsError."""
        exc = EmailAlreadyExistsError(email="test@example.com")

        assert exc.status_code == 409
        assert exc.error_code == "EMAIL_ALREADY_EXISTS"
        assert "email" in exc.user_message.lower()
        assert exc.context["value"] == "test@example.com"

    def test_username_already_exists_error(self):
        """Test UsernameAlreadyExistsError."""
        exc = UsernameAlreadyExistsError(username="testuser")

        assert exc.status_code == 409
        assert exc.error_code == "USERNAME_ALREADY_EXISTS"
        assert "username" in exc.user_message.lower()
        assert exc.context["value"] == "testuser"

    def test_resource_already_exists_error(self):
        """Test ResourceAlreadyExistsError."""
        exc = ResourceAlreadyExistsError(
            resource_type="Role",
            field="name",
            value="admin",
        )

        assert exc.status_code == 409
        assert exc.error_code == "RESOURCE_ALREADY_EXISTS"
        assert "role" in exc.user_message.lower()
        assert exc.context["resource_type"] == "Role"
        assert exc.context["field"] == "name"
        assert exc.context["value"] == "admin"

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError(
            message="Password too short",
            user_message="Password must be longer",
            field="password",
            value="abc",
        )

        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.context["field"] == "password"
        assert exc.context["value"] == "abc"

    def test_password_mismatch_error(self):
        """Test PasswordMismatchError."""
        exc = PasswordMismatchError()

        assert exc.status_code == 422
        assert exc.error_code == "PASSWORD_MISMATCH"
        assert "current password" in exc.user_message.lower()

    def test_invalid_password_error(self):
        """Test InvalidPasswordError."""
        exc = InvalidPasswordError(reason="Too short")

        assert exc.status_code == 422
        assert exc.error_code == "INVALID_PASSWORD"
        assert "password" in exc.user_message.lower()

    def test_business_logic_error(self):
        """Test BusinessLogicError."""
        exc = BusinessLogicError(
            message="Cannot delete active user",
            user_message="This user is active and cannot be deleted",
            context={"user_id": "123"},
        )

        assert exc.status_code == 400
        assert exc.error_code == "BUSINESS_LOGIC_ERROR"
        assert exc.context["user_id"] == "123"

    def test_database_error(self):
        """Test DatabaseError."""
        original_error = Exception("Connection timeout")
        exc = DatabaseError(message="Connection failed", original_error=original_error)

        assert exc.status_code == 500
        assert exc.error_code == "DATABASE_ERROR"
        assert "technical difficulties" in exc.user_message.lower()
        assert exc.context["original_error"] == "Connection timeout"
        assert exc.context["error_type"] == "Exception"
