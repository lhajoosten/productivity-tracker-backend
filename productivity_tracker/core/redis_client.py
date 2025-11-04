# python
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

    def _user_set_key(self, user_id: UUID) -> str:
        return f"user_sessions:{user_id}"

    def create_session(
        self,
        session_id: str,
        user_id: UUID,
        metadata: dict[str, Any] | None = None,
        ttl_seconds: int | None = None,
    ) -> bool:
        """
        Create a new session in Redis and add the session id to the user's session set.
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
            user_key = self._user_set_key(user_id)

            # Use pipeline to set session and record the index atomically
            pipe = self._client.pipeline()
            pipe.setex(key, ttl, json.dumps(session_data))
            pipe.sadd(user_key, session_id)
            pipe.execute()

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
        Delete a session from Redis and remove it from the user's session set.
        """
        if not self._client:
            return False

        try:
            key = f"session:{session_id}"
            data = self._client.get(key)
            user_key = None

            if data:
                session_data = json.loads(data)
                user_id = session_data.get("user_id")
                if user_id:
                    user_key = f"user_sessions:{user_id}"

            # Use pipeline to remove session and update index
            pipe = self._client.pipeline()
            pipe.delete(key)
            if user_key:
                pipe.srem(user_key, session_id)
            pipe.execute()

            logger.debug(f"Deleted session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def delete_user_sessions(self, user_id: UUID) -> int:
        """
        Delete all sessions for a user using the user-to-sessions index set.

        Returns:
            Number of sessions deleted
        """
        if not self._client:
            return 0

        try:
            user_key = self._user_set_key(user_id)
            session_ids = self._client.smembers(user_key)
            if not session_ids:
                logger.info(f"No sessions found for user {user_id}")
                return 0

            # Build session keys and delete them in a pipeline, then remove the user set
            session_keys = [f"session:{sid}" for sid in session_ids]
            pipe = self._client.pipeline()
            if session_keys:
                pipe.delete(*session_keys)
            pipe.delete(user_key)
            results = pipe.execute()

            deleted = results[0] if results else 0
            logger.info(f"Deleted {deleted} sessions for user {user_id}")
            return int(deleted)
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
        Get count of active sessions for a user using SCARD on the user set.

        Note: This may include stale entries if sessions expired without explicit removal.
        """
        if not self._client:
            return 0

        try:
            user_key = self._user_set_key(user_id)
            count = self._client.scard(user_key)
            return int(count)
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
