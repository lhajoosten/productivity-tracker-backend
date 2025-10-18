import logging
from typing import cast
from uuid import UUID

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    PermissionDeniedError,
)
from productivity_tracker.core.security import decode_token
from productivity_tracker.core.settings import settings
from productivity_tracker.database import get_db
from productivity_tracker.database.entities import User

logger = logging.getLogger(__name__)


async def get_current_user(
    access_token: str | None = Cookie(None, alias=settings.COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from the access token cookie."""
    if not access_token:
        raise InvalidTokenError(reason="No authentication token provided")

    payload = decode_token(access_token)

    if payload is None:
        raise InvalidTokenError(reason="Token validation failed")

    user_id_str = payload.get("sub")
    token_type = payload.get("type")

    if user_id_str is None or token_type != "access":  # nosec
        raise InvalidTokenError(reason="Invalid token payload")

    # Convert string UUID to UUID object
    try:
        user_id = UUID(str(user_id_str))
    except (ValueError, AttributeError) as e:
        raise InvalidTokenError(reason="Invalid user ID in token") from e

    # Ensure we flush any pending changes first to make them visible
    db.flush()
    user = cast(
        User | None,
        db.query(User).filter(User.id == user_id, User.is_deleted.is_(False)).first(),  # noqa: E712
    )

    if user is None:
        # Additional debug: check if user exists without is_deleted filter
        logger.warning(f"User not found for ID: {user_id}")
        raise InvalidTokenError(reason="User not found")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise InactiveUserError(user_id=str(current_user.id))
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current superuser."""
    if not current_user.is_superuser:
        raise PermissionDeniedError(permission="superuser", resource="admin endpoints")
    return current_user


def require_permission(permission_name: str):
    """Dependency factory to require a specific permission."""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_permission(permission_name):
            raise PermissionDeniedError(permission=permission_name, resource=None)
        return current_user

    return permission_checker


def require_any_permission(*permission_names: str):
    """Dependency factory to require any of the specified permissions."""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_any_permission(*permission_names):
            permissions_str = ", ".join(permission_names)
            raise PermissionDeniedError(permission=f"one of: {permissions_str}", resource=None)
        return current_user

    return permission_checker
