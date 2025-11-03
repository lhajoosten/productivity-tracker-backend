"""Redis client for session management."""

import json
import logging
from typing import Any
from uuid import UUID

import redis
from redis import Redis

from productivity_tracker.core.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for managing user sessions."""

    def __init__(self):
        """Initialize Redis connection."""
        self._client: Redis | None = None
        self._connect()

    def _connect(self):
        """Connect to Redis server."""
        if not settings.REDIS_URL:
            logger.warning("Redis URL not configured, session management disabled")
            return

        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self._client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._client is not None

    def create_session(
        self,
        session_id: str,
        user_id: UUID,
        metadata: dict[str, Any] | None = None,
        ttl_seconds: int | None = None,
    ) -> bool:
        """
        Create a new session in Redis.

        Args:
            session_id: Unique session identifier (typically JTI from JWT)
            user_id: User ID associated with the session
            metadata: Additional session metadata
            ttl_seconds: Session TTL in seconds (defaults to ACCESS_TOKEN_EXPIRE_MINUTES)

        Returns:
            True if session created successfully, False otherwise
        """
        if not self._client:
            return False

        try:
            session_data = {
                "user_id": str(user_id),
                "metadata": metadata or {},
            }

            # Use ACCESS_TOKEN_EXPIRE_MINUTES converted to seconds as default TTL
            ttl = ttl_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

            key = f"session:{session_id}"
            self._client.setex(key, ttl, json.dumps(session_data))
            logger.debug(f"Created session {session_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session data from Redis.

        Args:
            session_id: Session identifier

        Returns:
            Session data if found, None otherwise
        """
        if not self._client:
            return None

        try:
            key = f"session:{session_id}"
            data = self._client.get(key)
            if data:
                session_data: dict[str, Any] = json.loads(data)
                return session_data
            return None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from Redis.

        Args:
            session_id: Session identifier

        Returns:
            True if session deleted, False otherwise
        """
        if not self._client:
            return False

        try:
            key = f"session:{session_id}"
            self._client.delete(key)
            logger.debug(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def delete_user_sessions(self, user_id: UUID) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        if not self._client:
            return 0

        try:
            # Find all session keys for this user
            pattern = "session:*"
            deleted = 0

            for key in self._client.scan_iter(pattern):
                data = self._client.get(key)
                if data:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == str(user_id):
                        self._client.delete(key)
                        deleted += 1

            logger.info(f"Deleted {deleted} sessions for user {user_id}")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete user sessions: {e}")
            return 0

    def extend_session(self, session_id: str, ttl_seconds: int) -> bool:
        """
        Extend session TTL.

        Args:
            session_id: Session identifier
            ttl_seconds: New TTL in seconds

        Returns:
            True if TTL extended, False otherwise
        """
        if not self._client:
            return False

        try:
            key = f"session:{session_id}"
            self._client.expire(key, ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"Failed to extend session: {e}")
            return False

    def get_user_sessions_count(self, user_id: UUID) -> int:
        """
        Get count of active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active sessions
        """
        if not self._client:
            return 0

        try:
            pattern = "session:*"
            count = 0

            for key in self._client.scan_iter(pattern):
                data = self._client.get(key)
                if data:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == str(user_id):
                        count += 1

            return count
        except Exception as e:
            logger.error(f"Failed to get user sessions count: {e}")
            return 0

    def close(self):
        """Close Redis connection."""
        if self._client:
            self._client.close()
            logger.info("Redis connection closed")


# Global Redis client instance
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """Get Redis client instance."""
    return redis_client
