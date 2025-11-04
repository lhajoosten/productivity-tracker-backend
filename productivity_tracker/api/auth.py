from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
)
from productivity_tracker.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.core.redis_client import get_redis_client
from productivity_tracker.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from productivity_tracker.core.settings import settings
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import (
    AssignRolesToUser,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserListResponse,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)
from productivity_tracker.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


def set_auth_cookie(response: Response, token: str) -> None:
    """Set authentication cookie in response."""
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        domain=settings.COOKIE_DOMAIN or None,
        path=settings.COOKIE_PATH,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.COOKIE_MAX_AGE,
    )


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="register",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    new_user = user_service.create_user(user_data)
    return new_user


@router.post("/auth/login", response_model=LoginResponse, operation_id="login")
def login(
    response: Response,
    form_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """Login user and set access token cookie."""
    user_service = UserService(db)

    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise InvalidCredentialsError(username=form_data.username)

    if not user.is_active:
        raise InactiveUserError(user_id=str(user.id))

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, jti = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    # Create session in Redis
    redis_client = get_redis_client()
    if redis_client.is_connected:
        redis_client.create_session(
            session_id=jti,
            user_id=user.id,
            metadata={
                "username": user.username,
                "login_time": datetime.utcnow().isoformat(),
            },
            ttl_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        logger.info(f"Created Redis session {jti} for user {user.id}")

    # Set authentication cookie
    set_auth_cookie(response, access_token)

    return LoginResponse(
        message="Login successful",
        user=UserListResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # nosec
    )


@router.post("/auth/logout", operation_id="logout")
def logout(
    response: Response,
    access_token: str | None = None,
):
    """Logout user by clearing the access token cookie and deleting Redis session."""
    # Try to get token from cookie
    if access_token:
        payload = decode_token(access_token)
        if payload:
            jti = payload.get("jti")
            if jti:
                # Delete session from Redis
                redis_client = get_redis_client()
                if redis_client.is_connected:
                    redis_client.delete_session(jti)
                    logger.info(f"Deleted Redis session {jti}")

    response.delete_cookie(key=settings.COOKIE_NAME)
    return {"message": "Logout successful"}


@router.post("/auth/refresh", response_model=Token, operation_id="refreshToken")
def refresh_token(
    response: Response,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_data.refresh_token)
        if payload is None:
            raise InvalidTokenError(reason="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise InvalidTokenError(reason="Not a refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError(reason="Missing user ID in token")

        # Create new access token with new session ID
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, jti = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )

        # Create new session in Redis
        redis_client = get_redis_client()
        if redis_client.is_connected:
            redis_client.create_session(
                session_id=jti,
                user_id=UUID(user_id),
                metadata={"refreshed": True},
                ttl_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
            logger.info(f"Created new Redis session {jti} after token refresh")

        # Set authentication cookie
        set_auth_cookie(response, access_token)

        return Token(access_token=access_token, token_type="bearer")  # nosec

    except InvalidTokenError:
        raise
    except Exception as e:
        raise InvalidTokenError(reason="Token verification failed") from e


@router.get("/auth/me", response_model=UserResponse, operation_id="getCurrentUser")
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user."""
    return current_user


@router.put("/auth/me", response_model=UserResponse, operation_id="updateCurrentUser")
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user information."""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_data)  # type: ignore[arg-type]
    return updated_user


@router.put("/auth/me/password", response_model=UserResponse, operation_id="changePassword")
def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change current user's password."""
    user_service = UserService(db)
    updated_user = user_service.update_password(current_user.id, password_data)  # type: ignore[arg-type]
    return updated_user


# Admin endpoints (require superuser)
@router.get("/auth/users", response_model=list[UserListResponse], operation_id="getAllUsers")
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)."""
    user_service = UserService(db)
    users = user_service.get_all_users(skip, limit, active_only=False)
    return users


@router.get("/auth/users/{user_id}", response_model=UserResponse, operation_id="getUser")
def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    return user


@router.put("/auth/users/{user_id}", response_model=UserResponse, operation_id="updateUser")
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Update user (admin only)."""
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, user_data)
    return updated_user


@router.delete(
    "/auth/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteUser"
)
def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)."""
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return None


@router.post(
    "/auth/users/{user_id}/activate", response_model=UserResponse, operation_id="activateUser"
)
def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Activate a user (admin only)."""
    user_service = UserService(db)
    user = user_service.activate_user(user_id)
    return user


@router.post(
    "/auth/users/{user_id}/deactivate", response_model=UserResponse, operation_id="deactivateUser"
)
def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Deactivate a user (admin only)."""
    user_service = UserService(db)
    user = user_service.deactivate_user(user_id)
    return user


@router.post(
    "/auth/users/{user_id}/roles", response_model=UserResponse, operation_id="assignRolesToUser"
)
def assign_roles_to_user(
    user_id: UUID,
    role_data: AssignRolesToUser,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Assign roles to a user (admin only)."""
    user_service = UserService(db)
    user = user_service.assign_roles(user_id, role_data.role_ids)
    return user


@router.patch("/auth/users/{user_id}/toggle-superuser", operation_id="toggleSuperuser")
def toggle_superuser(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Toggle superuser status of a user (admin only)."""
    user_service = UserService(db)
    user = user_service.toggle_superuser_status(user_id)
    return user
