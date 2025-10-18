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
