"""Session management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from productivity_tracker.core.dependencies import get_current_active_user
from productivity_tracker.core.redis_client import get_redis_client
from productivity_tracker.database.entities.user import User

router = APIRouter()


class SessionInfo(BaseModel):
    """Session information response model."""

    active_sessions: int
    redis_available: bool


class LogoutAllResponse(BaseModel):
    """Response for logout all sessions."""

    message: str
    sessions_deleted: int


@router.get("/auth/sessions", response_model=SessionInfo, operation_id="getSessionInfo")
def get_session_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get information about active sessions for the current user."""
    redis_client = get_redis_client()

    if not redis_client.is_connected:
        return SessionInfo(active_sessions=0, redis_available=False)

    session_count = redis_client.get_user_sessions_count(current_user.id)

    return SessionInfo(active_sessions=session_count, redis_available=True)


@router.post("/auth/logout-all", response_model=LogoutAllResponse, operation_id="logoutAllSessions")
def logout_all_sessions(
    current_user: User = Depends(get_current_active_user),
):
    """Logout from all active sessions (invalidate all access tokens)."""
    redis_client = get_redis_client()

    if not redis_client.is_connected:
        return LogoutAllResponse(
            message="Redis not available, cannot logout all sessions", sessions_deleted=0
        )

    deleted_count = redis_client.delete_user_sessions(current_user.id)

    return LogoutAllResponse(
        message="Successfully logged out from all sessions", sessions_deleted=deleted_count
    )
