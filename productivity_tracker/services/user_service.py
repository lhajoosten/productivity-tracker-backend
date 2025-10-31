"""Service for user authentication and management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    DatabaseError,
    EmailAlreadyExistsError,
    PasswordMismatchError,
    ResourceNotFoundError,
    UsernameAlreadyExistsError,
)
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.core.security import hash_password, verify_password
from productivity_tracker.database import User
from productivity_tracker.models.auth import UserCreate, UserPasswordUpdate, UserUpdate
from productivity_tracker.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class UserService:
    """Service for user-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def create_user(self, user_data: UserCreate, is_superuser: bool = False) -> User:
        """Create a new user."""
        logger.info(f"Creating new user: {user_data.username}")

        # Check if email already exists
        existing_user_by_email = self.repository.get_by_email(str(user_data.email))
        if existing_user_by_email:
            logger.warning(f"User creation failed: Email {user_data.email} already exists")
            raise EmailAlreadyExistsError(str(user_data.email))

        # Check if username already exists
        existing_user_by_username = self.repository.get_by_username(user_data.username)
        if existing_user_by_username:
            logger.warning(f"User creation failed: Username {user_data.username} already exists")
            raise UsernameAlreadyExistsError(user_data.username)

        # Create new user
        new_user = User(
            username=user_data.username,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
            is_active=True,
            is_superuser=is_superuser,
        )

        try:
            created_user = self.repository.create(new_user)
            logger.info(
                f"User created successfully: {created_user.username} (ID: {created_user.id})"
            )
            return created_user
        except DatabaseError as e:
            # Handle database integrity errors that weren't caught by the pre-check
            error_msg = str(e.context.get("original_error", ""))
            if "email" in error_msg.lower():
                raise EmailAlreadyExistsError(str(user_data.email)) from e
            elif "username" in error_msg.lower():
                raise UsernameAlreadyExistsError(user_data.username) from e
            else:
                # Re-raise if it's not a duplicate error
                raise

    def get_user(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))
        return user

    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.repository.get_by_email(email)

    def get_all_users(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> list[User]:
        """Get all users with pagination."""
        if active_only:
            return self.repository.get_active_users(skip, limit)
        return self.repository.get_all(skip, limit)

    def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user information."""
        user = self.get_user(user_id)

        # Check if new email/username already exists
        if user_data.email and user_data.email != user.email:
            existing = self.repository.get_by_email(str(user_data.email))
            if existing:
                raise EmailAlreadyExistsError(str(user_data.email))
            user.email = str(user_data.email)  # type: ignore[assignment]

        if user_data.username and user_data.username != user.username:
            existing = self.repository.get_by_username(user_data.username)
            if existing:
                raise UsernameAlreadyExistsError(user_data.username)
            user.username = user_data.username  # type: ignore[assignment]

        if user_data.is_active is not None:
            user.is_active = user_data.is_active  # type: ignore[assignment]

        updated_user = self.repository.update(user)
        return updated_user

    def update_password(self, user_id: UUID, password_data: UserPasswordUpdate) -> User:
        """Update user password."""
        user = self.get_user(user_id)

        # Verify current password
        if not verify_password(password_data.current_password, str(user.hashed_password)):
            raise PasswordMismatchError()

        # Update password
        user.hashed_password = hash_password(password_data.new_password)  # type: ignore[assignment]
        updated_user = self.repository.update(user)
        return updated_user

    def delete_user(self, user_id: UUID, soft: bool = True) -> bool:
        """Delete a user."""
        result = self.repository.delete(user_id, soft=soft)
        return result

    def activate_user(self, user_id: UUID) -> User:
        """Activate a user."""
        user = self.get_user(user_id)
        user.is_active = True  # type: ignore[assignment]
        return self.repository.update(user)

    def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user."""
        user = self.get_user(user_id)
        user.is_active = False  # type: ignore[assignment]
        return self.repository.update(user)

    def assign_roles(self, user_id: UUID, role_ids: list[UUID]) -> User:
        """Assign roles to a user."""
        user = self.get_user(user_id)
        return self.repository.assign_roles(user, role_ids)

    def add_role(self, user_id: UUID, role_id: UUID) -> User:
        """Add a role to a user."""
        user = self.get_user(user_id)
        return self.repository.add_role(user, role_id)

    def remove_role(self, user_id: UUID, role_id: UUID) -> User:
        """Remove a role from a user."""
        user = self.get_user(user_id)
        return self.repository.remove_role(user, role_id)

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> list[User]:
        """Search users by username or email."""
        return self.repository.search_users(query, skip, limit)

    def authenticate_user(self, username: str, password: str) -> User | None:
        """Authenticate a user by username and password."""
        user = self.repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user

    def toggle_superuser_status(self, user_id: UUID) -> User | None:
        "Toggle superuser status for a user."
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        user.is_superuser = not user.is_superuser
        return self.repository.update(user)
