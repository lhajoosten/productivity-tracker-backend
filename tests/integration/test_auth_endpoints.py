"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient

from productivity_tracker.database.entities import User
from productivity_tracker.versioning.versioning import CURRENT_VERSION
from tests.utilities import (
    assert_problem_detail_response,
    assert_validation_error_response,
)

pytestmark = pytest.mark.integration

# Get the version prefix for all endpoints
API_PREFIX = CURRENT_VERSION.api_prefix


class TestAuthenticationEndpoints:
    """Integration tests for /api/v1.1/auth endpoints."""

    pytestmark = pytest.mark.auth

    # ============================================================================
    # Registration Tests
    # ============================================================================

    def test_register_user_success(self, client_integration: TestClient):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_user_duplicate_email(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test registration fails with duplicate email."""
        # Arrange
        user_data = {
            "username": "differentuser",
            "email": sample_user_integration.email,
            "password": "SecurePass123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/register", json=user_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="email-already-exists",
            expected_status=409,
            expected_detail_contains="email",
        )

    def test_register_user_duplicate_username(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test registration fails with duplicate username."""
        # Arrange
        from uuid import uuid4

        unique_suffix = uuid4().hex
        user_data = {
            "username": sample_user_integration.username,
            "email": f"unique_{unique_suffix}@example.com",
            "password": "SecurePass123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/register", json=user_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="username-already-exists",
            expected_status=409,
            expected_detail_contains="username",
        )

    def test_register_user_invalid_email(self, client_integration: TestClient):
        """Test registration fails with invalid email format."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "SecurePass123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert_validation_error_response(data, expected_field="email")

    def test_register_user_missing_required_fields(self, client_integration: TestClient):
        """Test registration fails with missing required fields."""
        # Arrange
        user_data = {
            "username": "newuser",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert_validation_error_response(data)

    # ============================================================================
    # Login Tests
    # ============================================================================

    def test_login_success(self, client_integration: TestClient, sample_user_integration: User):
        """Test successful login."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == sample_user_integration.username
        assert "access_token" in response.cookies or "Set-Cookie" in response.headers

    def test_login_invalid_username(self, client_integration: TestClient):
        """Test login fails with non-existent username."""
        # Arrange
        login_data = {
            "username": "nonexistent",
            "password": "AnyPassword123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="invalid-credentials",
            expected_status=401,
            expected_detail_contains="invalid",
        )

    def test_login_wrong_password(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test login fails with wrong password."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "WrongPassword123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="invalid-credentials",
            expected_status=401,
            expected_detail_contains="invalid",
        )

    def test_login_inactive_user(
        self, client_integration: TestClient, sample_inactive_user_integration: User
    ):
        """Test login fails for inactive user."""
        # Arrange
        login_data = {
            "username": sample_inactive_user_integration.username,
            "password": "InactivePassword123!",
        }

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="inactive-user",
            expected_status=403,
            expected_detail_contains="inactive",
        )

    # ============================================================================
    # Get Current User Tests
    # ============================================================================

    def test_get_current_user_success(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test getting current authenticated user."""
        # Arrange - Login first
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200

        # Act
        response = client_integration.get(f"{API_PREFIX}/auth/me")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user_integration.username
        assert data["email"] == sample_user_integration.email

    def test_get_current_user_unauthorized(self, client_integration: TestClient):
        """Test getting current user fails without authentication."""
        # Act
        response = client_integration.get(f"{API_PREFIX}/auth/me")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="invalid-token",
            expected_status=401,
            expected_detail_contains="session is invalid",
        )

    # ============================================================================
    # Logout Tests
    # ============================================================================

    def test_logout_success(self, client_integration: TestClient, sample_user_integration: User):
        """Test successful logout."""
        # Arrange - Login first
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        # Act
        response = client_integration.post(f"{API_PREFIX}/auth/logout")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    # ============================================================================
    # Refresh Token Tests
    # ============================================================================

    def test_refresh_token_success(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test successful token refresh."""
        # Arrange - Login to get refresh token
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Act
        response = client_integration.post(
            f"{API_PREFIX}/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client_integration: TestClient):
        """Test token refresh fails with invalid token."""
        # Act
        response = client_integration.post(
            f"{API_PREFIX}/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="invalid-token",
            expected_status=401,
            expected_detail_contains="session is invalid",
        )

    # ============================================================================
    # Update Current User Tests
    # ============================================================================

    def test_update_current_user_success(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test updating current user information."""
        # Arrange - Login first
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        # Act
        response = client_integration.put(
            f"{API_PREFIX}/auth/me",
            json={"username": "updatedusername"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updatedusername"

    def test_update_current_user_unauthorized(self, client_integration: TestClient):
        """Test updating user fails without authentication."""
        # Act
        response = client_integration.put(
            f"{API_PREFIX}/auth/me",
            json={"username": "newname"},
        )

        # Assert
        assert response.status_code == 401

    # ============================================================================
    # Change Password Tests
    # ============================================================================

    def test_change_password_success(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test successful password change."""
        # Arrange - Login first
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        # Act
        response = client_integration.put(
            f"{API_PREFIX}/auth/me/password",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewSecurePass123!",
            },
        )

        # Assert
        assert response.status_code == 200

        # Verify can login with new password
        logout_response = client_integration.post(f"{API_PREFIX}/auth/logout")
        assert logout_response.status_code == 200

        new_login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "NewSecurePass123!",
            },
        )
        assert new_login_response.status_code == 200

    def test_change_password_wrong_current(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test password change fails with wrong current password."""
        # Arrange - Login first
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        # Act
        response = client_integration.put(
            f"{API_PREFIX}/auth/me/password",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewSecurePass123!",
            },
        )

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="password-mismatch",
            expected_status=422,
            expected_detail_contains="password",
        )


class TestAdminUserEndpoints:
    """Integration tests for admin user management endpoints."""

    def test_get_all_users_as_superuser(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        sample_user_integration: User,
    ):
        """Test superuser can get all users."""
        # Arrange - Login as superuser
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get(f"{API_PREFIX}/auth/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_all_users_as_regular_user(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test regular user cannot get all users."""
        # Arrange - Login as regular user
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        # Act
        response = client_integration.get(f"{API_PREFIX}/auth/users")

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert_problem_detail_response(
            data,
            expected_type="permission-denied",
            expected_status=403,
            expected_detail_contains="permission",
        )

    def test_activate_user_as_superuser(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        sample_inactive_user_integration: User,
    ):
        """Test superuser can activate a user."""
        # Arrange - Login as superuser
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            f"{API_PREFIX}/auth/users/{sample_inactive_user_integration.id}/activate"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    def test_deactivate_user_as_superuser(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        sample_user_integration: User,
    ):
        """Test superuser can deactivate a user."""
        # Arrange - Login as superuser
        client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            f"{API_PREFIX}/auth/users/{sample_user_integration.id}/deactivate"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
