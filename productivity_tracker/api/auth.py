from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
)
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

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    new_user = user_service.create_user(user_data)
    return new_user


@router.post("/login", response_model=LoginResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login user and set access token cookie."""
    user_service = UserService(db)

    # Authenticate user
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    # Set access token cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "message": "Login successful",
        "user": UserListResponse.model_validate(user),
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    response: Response,
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    payload = decode_token(token_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify user still exists and is active
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Set new access token cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing the access token cookie."""
    response.delete_cookie(key=settings.COOKIE_NAME)
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user information."""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_data)
    return updated_user


@router.put("/me/password", response_model=UserResponse)
def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change current user's password."""
    user_service = UserService(db)
    updated_user = user_service.update_password(current_user.id, password_data)
    return updated_user


# Admin endpoints (require superuser)
@router.get("/users", response_model=list[UserListResponse])
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


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)."""
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return None


@router.post("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Activate a user (admin only)."""
    user_service = UserService(db)
    user = user_service.activate_user(user_id)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Deactivate a user (admin only)."""
    user_service = UserService(db)
    user = user_service.deactivate_user(user_id)
    return user


@router.post("/users/{user_id}/roles", response_model=UserResponse)
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
