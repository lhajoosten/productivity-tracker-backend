"""Service for user authentication and management."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.core.security import hash_password, verify_password
from productivity_tracker.database.entities.user import User
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

        # Check if user already exists
        existing_user = self.repository.get_by_email_or_username(
            user_data.email, user_data.username
        )
        if existing_user:
            logger.warning(
                f"User creation failed: User {user_data.username} already exists"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists",
            )

        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            is_active=True,
            is_superuser=is_superuser,
        )

        created_user = self.repository.create(new_user)
        logger.info(
            f"User created successfully: {created_user.username} (ID: {created_user.id})"
        )
        return created_user

    def get_user(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
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
        logger.info(f"Updating user: {user_id}")
        user = self.get_user(user_id)

        # Check if new email/username already exists
        if user_data.email and user_data.email != user.email:
            existing = self.repository.get_by_email(user_data.email)
            if existing:
                logger.warning(f"Email already in use: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )
            user.email = user_data.email

        if user_data.username and user_data.username != user.username:
            existing = self.repository.get_by_username(user_data.username)
            if existing:
                logger.warning(f"Username already in use: {user_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already in use",
                )
            user.username = user_data.username

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        updated_user = self.repository.update(user)
        logger.info(f"User updated successfully: {updated_user.username}")
        return updated_user

    def update_password(self, user_id: UUID, password_data: UserPasswordUpdate) -> User:
        """Update user password."""
        logger.info(f"Updating password for user: {user_id}")
        user = self.get_user(user_id)

        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            logger.warning(
                f"Password update failed: Incorrect current password for user {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )

        # Update password
        user.hashed_password = hash_password(password_data.new_password)
        updated_user = self.repository.update(user)
        logger.info(f"Password updated successfully for user: {user.username}")
        return updated_user

    def delete_user(self, user_id: UUID, soft: bool = True) -> bool:
        """Delete a user."""
        logger.info(f"Deleting user: {user_id} (soft={soft})")
        result = self.repository.delete(user_id, soft=soft)
        if result:
            logger.info(f"User deleted successfully: {user_id}")
        else:
            logger.warning(f"User deletion failed: {user_id}")
        return result

    def activate_user(self, user_id: UUID) -> User:
        """Activate a user."""
        user = self.get_user(user_id)
        user.is_active = True
        return self.repository.update(user)

    def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user."""
        user = self.get_user(user_id)
        user.is_active = False
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
        logger.debug(f"Authenticating user: {username}")
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            return None
        logger.info(f"User authenticated successfully: {username}")
        return user
