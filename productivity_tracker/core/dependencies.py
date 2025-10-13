from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from productivity_tracker.core.security import decode_token
from productivity_tracker.core.settings import settings
from productivity_tracker.database import get_db
from productivity_tracker.database.entities import User


async def get_current_user(
    access_token: str | None = Cookie(None, alias=settings.COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from the access token cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise credentials_exception

    payload = decode_token(access_token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    # nosec B105 - This is a token type check, not a hardcoded password
    if user_id is None or token_type != "access":  # nosec
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_deleted is False).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def require_permission(permission_name: str):
    """Dependency factory to require a specific permission."""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_name} required",
            )
        return current_user

    return permission_checker


def require_any_permission(*permission_names: str):
    """Dependency factory to require any of the specified permissions."""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_any_permission(*permission_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: one of {permission_names} required",
            )
        return current_user

    return permission_checker


def require_all_permissions(*permission_names: str):
    """Dependency factory to require all of the specified permissions."""

    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_all_permissions(*permission_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: all of {permission_names} required",
            )
        return current_user

    return permission_checker
