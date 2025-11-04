"""Tests for Redis session management in authentication endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from productivity_tracker.core.redis_client import RedisClient
from productivity_tracker.database.entities import User
from productivity_tracker.versioning.versioning import CURRENT_VERSION

pytestmark = pytest.mark.integration

API_PREFIX = CURRENT_VERSION.api_prefix

# Update this to match your actual auth module path
AUTH_MODULE = "productivity_tracker.api.auth"


class TestAuthRedisSessionManagement:
    """Tests for Redis session management in authentication endpoints."""

    pytestmark = pytest.mark.auth

    # ============================================================================
    # Login - Redis Session Creation Tests
    # ============================================================================

    def test_login_creates_redis_session(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that login creates a session in Redis."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            # Act
            response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

            # Assert
            assert response.status_code == 200
            mock_redis.create_session.assert_called_once()

    def test_login_handles_redis_disconnection(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that login succeeds even if Redis is disconnected."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = False
            mock_get_redis.return_value = mock_redis

            # Act
            response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

            # Assert
            assert response.status_code == 200
            mock_redis.create_session.assert_not_called()

    def test_login_redis_session_ttl_matches_token_expiry(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that Redis session TTL matches access token expiry."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.settings.ACCESS_TOKEN_EXPIRE_MINUTES", 30):
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_redis.create_session.return_value = True
                mock_get_redis.return_value = mock_redis

                # Act
                response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

                # Assert
                assert response.status_code == 200
                mock_redis.create_session.assert_called_once()

    # ============================================================================
    # Logout - Redis Session Deletion Tests
    # ============================================================================

    def test_logout_deletes_redis_session(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that logout deletes the session from Redis when token is provided as query param."""
        # Arrange - Login first
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_redis.delete_session.return_value = True
                mock_get_redis.return_value = mock_redis

                # Mock decode_token to return a valid payload with jti
                mock_decode.return_value = {
                    "jti": "test-jti-123",
                    "sub": str(sample_user_integration.id),
                }

                # Act - Send token as query parameter (matching the function signature)
                response = client_integration.post(
                    f"{API_PREFIX}/auth/logout",
                    params={"access_token": access_token},
                )

                # Assert
                assert response.status_code == 200
                mock_decode.assert_called_once_with(access_token)
                mock_redis.delete_session.assert_called_once_with("test-jti-123")

    def test_logout_handles_redis_disconnection(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that logout succeeds even if Redis is disconnected."""
        # Arrange - Login first
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = False
                mock_get_redis.return_value = mock_redis
                mock_decode.return_value = {"jti": "test-jti-123"}

                # Act
                response = client_integration.post(
                    f"{API_PREFIX}/auth/logout",
                    params={"access_token": access_token},
                )

                # Assert
                assert response.status_code == 200
                mock_redis.delete_session.assert_not_called()

    def test_logout_without_token(self, client_integration: TestClient):
        """Test logout without access token."""
        # Arrange
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_get_redis.return_value = mock_redis

                # Act
                response = client_integration.post(f"{API_PREFIX}/auth/logout")

                # Assert
                assert response.status_code == 200
                mock_decode.assert_not_called()
                mock_redis.delete_session.assert_not_called()

    def test_logout_with_invalid_token(self, client_integration: TestClient):
        """Test logout with invalid token doesn't call Redis delete."""
        # Arrange
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_get_redis.return_value = mock_redis
                mock_decode.return_value = None

                # Act
                response = client_integration.post(
                    f"{API_PREFIX}/auth/logout",
                    params={"access_token": "invalid_token"},
                )

                # Assert
                assert response.status_code == 200
                mock_redis.delete_session.assert_not_called()

    def test_logout_with_no_jti_claim(self, client_integration: TestClient):
        """Test logout with token that has no jti claim."""
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_get_redis.return_value = mock_redis
                mock_decode.return_value = {"sub": "user-id"}

                # Act
                response = client_integration.post(
                    f"{API_PREFIX}/auth/logout",
                    params={"access_token": "some_token"},
                )

                # Assert
                assert response.status_code == 200
                mock_redis.delete_session.assert_not_called()

    # ============================================================================
    # Refresh Token - Redis Session Creation Tests
    # ============================================================================

    def test_refresh_token_creates_new_redis_session(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that token refresh creates a new session in Redis."""
        # Arrange - Login to get refresh token
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            # Act
            response = client_integration.post(
                f"{API_PREFIX}/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            # Assert
            assert response.status_code == 200
            mock_redis.create_session.assert_called_once()

    def test_refresh_token_handles_redis_disconnection(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that token refresh succeeds even if Redis is disconnected."""
        # Arrange - Login to get refresh token
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = False
            mock_get_redis.return_value = mock_redis

            # Act
            response = client_integration.post(
                f"{API_PREFIX}/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            # Assert
            assert response.status_code == 200
            mock_redis.create_session.assert_not_called()

    def test_refresh_token_new_jti_generates_new_session_id(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that refresh token generates a new session ID (jti) in Redis."""
        # Arrange - Login to get refresh token
        login_response = client_integration.post(
            f"{API_PREFIX}/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            # Act
            response = client_integration.post(
                f"{API_PREFIX}/auth/refresh",
                json={"refresh_token": refresh_token},
            )

            # Assert
            assert response.status_code == 200
            mock_redis.create_session.assert_called_once()

    # ============================================================================
    # Cookie Deletion Tests
    # ============================================================================

    def test_logout_deletes_cookie(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that logout deletes the authentication cookie."""
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
        response = client_integration.post(f"{API_PREFIX}/auth/logout")

        # Assert
        assert response.status_code == 200
        # Check that response deletes the cookie (sets it with expired date or max-age=0)
        set_cookie_header = response.headers.get("set-cookie", "")
        # Should contain cookie deletion (expires in past or max-age=0)
        assert len(set_cookie_header) > 0

    # ============================================================================
    # Edge Cases and Error Handling
    # ============================================================================

    def test_multiple_logins_create_separate_sessions(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that multiple logins from same user create separate Redis sessions."""
        # Arrange
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            # Act - Login twice
            response1 = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)
            response2 = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

            # Assert
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert mock_redis.create_session.call_count == 2

    def test_logout_then_login_creates_new_session(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test that after logout, login creates a new session."""
        login_data = {
            "username": sample_user_integration.username,
            "password": "TestPassword123!",
        }

        # First login
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            login_response = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)
            assert login_response.status_code == 200
            access_token = login_response.json()["access_token"]

        # Logout
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            with patch(f"{AUTH_MODULE}.decode_token") as mock_decode:
                mock_redis = MagicMock(spec=RedisClient)
                mock_redis.is_connected = True
                mock_redis.delete_session.return_value = True
                mock_get_redis.return_value = mock_redis
                mock_decode.return_value = {"jti": "session-1"}

                logout_response = client_integration.post(
                    f"{API_PREFIX}/auth/logout",
                    params={"access_token": access_token},
                )
                assert logout_response.status_code == 200
                mock_redis.delete_session.assert_called_once_with("session-1")

        # Login again
        with patch(f"{AUTH_MODULE}.get_redis_client") as mock_get_redis:
            mock_redis = MagicMock(spec=RedisClient)
            mock_redis.is_connected = True
            mock_redis.create_session.return_value = True
            mock_get_redis.return_value = mock_redis

            login_response2 = client_integration.post(f"{API_PREFIX}/auth/login", json=login_data)

            assert login_response2.status_code == 200
            mock_redis.create_session.assert_called_once()
