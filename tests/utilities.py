"""Test utilities and helper functions."""

from typing import Any
from uuid import uuid4

from productivity_tracker.core.security import hash_password
from productivity_tracker.database.entities import Permission, Role, User


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "TestPassword123!",
        is_active: bool = True,
        is_superuser: bool = False,
        **kwargs: Any,
    ) -> User:
        """Create a user instance for testing."""
        return User(
            id=kwargs.get("id", uuid4()),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=is_active,
            is_superuser=is_superuser,
            **{k: v for k, v in kwargs.items() if k != "id"},
        )

    @staticmethod
    def create_superuser(
        username: str = "admin",
        email: str = "admin@example.com",
        password: str = "AdminPassword123!",
        **kwargs: Any,
    ) -> User:
        """Create a superuser instance for testing."""
        return UserFactory.create(
            username=username,
            email=email,
            password=password,
            is_superuser=True,
            **kwargs,
        )


class RoleFactory:
    """Factory for creating test roles."""

    @staticmethod
    def create(
        name: str = "user",
        description: str = "Regular user role",
        permissions: list[Permission] | None = None,
        **kwargs: Any,
    ) -> Role:
        """Create a role instance for testing."""
        role = Role(
            id=kwargs.get("id", uuid4()),
            name=name,
            description=description,
        )
        if permissions:
            role.permissions = permissions
        return role


class PermissionFactory:
    """Factory for creating test permissions."""

    @staticmethod
    def create(
        name: str = "tasks:read",
        resource: str = "task",
        action: str = "read",
        description: str = "Read tasks",
        **kwargs: Any,
    ) -> Permission:
        """Create a permission instance for testing."""
        return Permission(
            id=kwargs.get("id", uuid4()),
            name=name,
            resource=resource,
            action=action,
            description=description,
        )

    @staticmethod
    def create_crud_permissions(resource: str) -> list[Permission]:
        """Create a full set of CRUD permissions for a resource."""
        actions = ["create", "read", "update", "delete"]
        return [
            PermissionFactory.create(
                name=f"{resource}:{action}",
                resource=resource,
                action=action,
                description=f"{action.capitalize()} {resource}",
            )
            for action in actions
        ]


def assert_error_response(
    response_data: dict,
    expected_error_code: str,
    expected_status: int,
) -> None:
    """Assert that an error response has the expected format and values."""
    assert "error" in response_data
    assert "message" in response_data
    assert response_data["error"] == expected_error_code
    # The status is checked separately in the test


def assert_user_response(response_data: dict, expected_username: str | None = None) -> None:
    """Assert that a user response has the expected format."""
    assert "id" in response_data
    assert "username" in response_data
    assert "email" in response_data
    assert "is_active" in response_data
    assert "created_at" in response_data

    # Should NOT include sensitive data
    assert "hashed_password" not in response_data
    assert "password" not in response_data

    if expected_username:
        assert response_data["username"] == expected_username


def assert_role_response(response_data: dict, expected_name: str | None = None) -> None:
    """Assert that a role response has the expected format."""
    assert "id" in response_data
    assert "name" in response_data
    assert "description" in response_data

    if expected_name:
        assert response_data["name"] == expected_name


def assert_permission_response(response_data: dict, expected_name: str | None = None) -> None:
    """Assert that a permission response has the expected format."""
    assert "id" in response_data
    assert "name" in response_data
    assert "resource" in response_data
    assert "action" in response_data

    if expected_name:
        assert response_data["name"] == expected_name


def get_auth_headers(access_token: str) -> dict[str, str]:
    """Get authorization headers for API requests."""
    return {"Authorization": f"Bearer {access_token}"}


def assert_problem_detail_response(
    response_data: dict[str, Any],
    expected_type: str,
    expected_status: int,
    expected_detail_contains: str | None = None,
    expected_detail_exact: str | None = None,
) -> None:
    """
    Assert that a response follows RFC 7807 Problem Details format.

    Args:
        response_data: The JSON response data
        expected_type: Expected error type (e.g., "email-already-exists")
        expected_status: Expected HTTP status code
        expected_detail_contains: String that should be contained in the detail field
        expected_detail_exact: Exact string that detail field should match
    """
    # Check required Problem Details fields
    assert "type" in response_data, "Response should have 'type' field"
    assert "title" in response_data, "Response should have 'title' field"
    assert "status" in response_data, "Response should have 'status' field"
    assert "detail" in response_data, "Response should have 'detail' field"

    # Check expected values
    assert response_data["type"] == expected_type, (
        f"Expected type '{expected_type}', got '{response_data['type']}'"
    )
    assert response_data["status"] == expected_status, (
        f"Expected status {expected_status}, got {response_data['status']}"
    )

    # Check detail field
    if expected_detail_exact is not None:
        assert response_data["detail"] == expected_detail_exact, (
            f"Expected detail '{expected_detail_exact}', got '{response_data['detail']}'"
        )
    elif expected_detail_contains is not None:
        detail = response_data["detail"]
        if isinstance(detail, str):
            assert expected_detail_contains.lower() in detail.lower(), (
                f"Expected '{expected_detail_contains}' in detail '{detail}'"
            )
        elif isinstance(detail, list):
            # For validation errors with array of errors
            detail_str = str(detail).lower()
            assert expected_detail_contains.lower() in detail_str, (
                f"Expected '{expected_detail_contains}' in validation errors '{detail}'"
            )


def assert_validation_error_response(
    response_data: dict[str, Any],
    expected_field: str | None = None,
) -> None:
    """
    Assert that a response is a validation error with array of field errors.

    Args:
        response_data: The JSON response data
        expected_field: Optional field name that should be in the validation errors
    """
    assert_problem_detail_response(response_data, "validation-error", 422)

    # Detail should be an array for validation errors
    assert isinstance(response_data["detail"], list), "Validation error detail should be an array"
    assert len(response_data["detail"]) > 0, "Validation error should have at least one error"

    if expected_field:
        fields = [error.get("field", "") for error in response_data["detail"]]
        field_found = any(expected_field in field for field in fields)
        assert field_found, (
            f"Expected field '{expected_field}' not found in validation errors: {fields}"
        )
