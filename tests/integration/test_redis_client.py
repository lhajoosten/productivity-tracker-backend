import json
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from redis import Redis

from productivity_tracker.core.redis_client import RedisClient
from productivity_tracker.core.settings import settings

pytestmark = [pytest.mark.integration, pytest.mark.auth]


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return MagicMock(spec=Redis)


@pytest.fixture
def redis_client_with_mock(mock_redis):
    """Create RedisClient with mocked Redis connection."""
    with patch("redis.from_url", return_value=mock_redis):
        client = RedisClient()
    return client, mock_redis


class TestRedisClientConnection:
    """Tests for Redis connection management."""

    def test_connect_success(self, mock_redis):
        """Test successful Redis connection."""
        with patch("redis.from_url", return_value=mock_redis) as mock_from_url:
            client = RedisClient()
            assert client.is_connected is True
            mock_from_url.assert_called_once()
            mock_redis.ping.assert_called_once()

    def test_connect_failure(self, mock_redis):
        """Test failed Redis connection."""
        mock_redis.ping.side_effect = Exception("Connection failed")
        with patch("redis.from_url", return_value=mock_redis):
            client = RedisClient()
            assert client.is_connected is False

    def test_no_redis_url_configured(self):
        """Test behavior when Redis URL is not configured."""
        with patch.object(settings, "REDIS_URL", None):
            client = RedisClient()
            assert client.is_connected is False

    def test_close_connection(self, redis_client_with_mock):
        """Test closing Redis connection."""
        client, mock_redis = redis_client_with_mock
        client.close()
        mock_redis.close.assert_called_once()


class TestSessionCreation:
    """Tests for session creation."""

    def test_create_session_success(self, redis_client_with_mock):
        """Test successful session creation."""
        client, mock_redis = redis_client_with_mock
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe

        session_id = "test_session_123"
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        metadata = {"ip": "192.168.1.1"}

        result = client.create_session(session_id, user_id, metadata)

        assert result is True
        mock_redis.pipeline.assert_called_once()
        mock_pipe.setex.assert_called_once()
        mock_pipe.sadd.assert_called_once()
        mock_pipe.execute.assert_called_once()

    def test_create_session_not_connected(self, mock_redis):
        """Test session creation when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.create_session(
                "session_id", UUID("12345678-1234-5678-1234-567812345678")
            )
            assert result is False

    def test_create_session_with_custom_ttl(self, redis_client_with_mock):
        """Test session creation with custom TTL."""
        client, mock_redis = redis_client_with_mock
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe

        session_id = "test_session_456"
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        ttl_seconds = 7200

        client.create_session(session_id, user_id, ttl_seconds=ttl_seconds)

        call_args = mock_pipe.setex.call_args
        assert call_args[0][1] == ttl_seconds

    def test_create_session_exception_handling(self, redis_client_with_mock):
        """Test exception handling during session creation."""
        client, mock_redis = redis_client_with_mock
        mock_redis.pipeline.side_effect = Exception("Pipeline error")

        result = client.create_session("session_id", UUID("12345678-1234-5678-1234-567812345678"))
        assert result is False


class TestSessionRetrieval:
    """Tests for session retrieval."""

    def test_get_session_success(self, redis_client_with_mock):
        """Test successful session retrieval."""
        client, mock_redis = redis_client_with_mock
        session_id = "test_session_123"
        user_id = "12345678-1234-5678-1234-567812345678"
        session_data = {"user_id": user_id, "metadata": {}}

        mock_redis.get.return_value = json.dumps(session_data)

        result = client.get_session(session_id)

        assert result == session_data
        mock_redis.get.assert_called_once_with(f"session:{session_id}")

    def test_get_session_not_found(self, redis_client_with_mock):
        """Test session retrieval when session doesn't exist."""
        client, mock_redis = redis_client_with_mock
        mock_redis.get.return_value = None

        result = client.get_session("nonexistent_session")

        assert result is None

    def test_get_session_not_connected(self, mock_redis):
        """Test session retrieval when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.get_session("session_id")
            assert result is None

    def test_get_session_exception_handling(self, redis_client_with_mock):
        """Test exception handling during session retrieval."""
        client, mock_redis = redis_client_with_mock
        mock_redis.get.side_effect = Exception("Redis error")

        result = client.get_session("session_id")
        assert result is None


class TestSessionDeletion:
    """Tests for session deletion."""

    def test_delete_session_success(self, redis_client_with_mock):
        """Test successful session deletion."""
        client, mock_redis = redis_client_with_mock
        session_id = "test_session_123"
        user_id = "12345678-1234-5678-1234-567812345678"
        session_data = {"user_id": user_id, "metadata": {}}

        mock_redis.get.return_value = json.dumps(session_data)
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe

        result = client.delete_session(session_id)

        assert result is True
        mock_redis.get.assert_called_once()
        mock_pipe.delete.assert_called()
        mock_pipe.srem.assert_called_once()
        mock_pipe.execute.assert_called_once()

    def test_delete_session_not_found(self, redis_client_with_mock):
        """Test deletion of non-existent session."""
        client, mock_redis = redis_client_with_mock
        mock_redis.get.return_value = None
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe

        result = client.delete_session("nonexistent_session")

        assert result is True
        mock_pipe.delete.assert_called_once()

    def test_delete_session_not_connected(self, mock_redis):
        """Test session deletion when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.delete_session("session_id")
            assert result is False

    def test_delete_session_exception_handling(self, redis_client_with_mock):
        """Test exception handling during session deletion."""
        client, mock_redis = redis_client_with_mock
        mock_redis.get.side_effect = Exception("Redis error")

        result = client.delete_session("session_id")
        assert result is False


class TestUserSessionManagement:
    """Tests for user session management."""

    def test_delete_user_sessions_success(self, redis_client_with_mock):
        """Test successful deletion of all user sessions."""
        client, mock_redis = redis_client_with_mock
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        session_ids = {"session_1", "session_2", "session_3"}

        mock_redis.smembers.return_value = session_ids
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe
        mock_pipe.execute.return_value = [3]

        result = client.delete_user_sessions(user_id)

        assert result == 3
        mock_redis.smembers.assert_called_once()
        mock_pipe.delete.assert_called()
        mock_pipe.execute.assert_called_once()

    def test_delete_user_sessions_no_sessions(self, redis_client_with_mock):
        """Test deletion when user has no sessions."""
        client, mock_redis = redis_client_with_mock
        user_id = UUID("12345678-1234-5678-1234-567812345678")

        mock_redis.smembers.return_value = set()

        result = client.delete_user_sessions(user_id)

        assert result == 0

    def test_delete_user_sessions_not_connected(self, mock_redis):
        """Test user session deletion when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.delete_user_sessions(UUID("12345678-1234-5678-1234-567812345678"))
            assert result == 0

    def test_get_user_sessions_count(self, redis_client_with_mock):
        """Test getting user sessions count."""
        client, mock_redis = redis_client_with_mock
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        mock_redis.scard.return_value = 5

        result = client.get_user_sessions_count(user_id)

        assert result == 5
        mock_redis.scard.assert_called_once()

    def test_get_user_sessions_count_not_connected(self, mock_redis):
        """Test getting sessions count when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.get_user_sessions_count(UUID("12345678-1234-5678-1234-567812345678"))
            assert result == 0


class TestSessionExtension:
    """Tests for session TTL extension."""

    def test_extend_session_success(self, redis_client_with_mock):
        """Test successful session TTL extension."""
        client, mock_redis = redis_client_with_mock
        session_id = "test_session_123"
        ttl_seconds = 3600

        result = client.extend_session(session_id, ttl_seconds)

        assert result is True
        mock_redis.expire.assert_called_once_with(f"session:{session_id}", ttl_seconds)

    def test_extend_session_not_connected(self, mock_redis):
        """Test session extension when not connected."""
        with patch("redis.from_url", side_effect=Exception("Connection failed")):
            client = RedisClient()
            result = client.extend_session("session_id", 3600)
            assert result is False

    def test_extend_session_exception_handling(self, redis_client_with_mock):
        """Test exception handling during session extension."""
        client, mock_redis = redis_client_with_mock
        mock_redis.expire.side_effect = Exception("Redis error")

        result = client.extend_session("session_id", 3600)
        assert result is False
