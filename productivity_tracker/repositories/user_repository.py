"""Repository for User entity operations."""

from typing import cast
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.orm import Session

from productivity_tracker.database.entities.role import Role
from productivity_tracker.database.entities.user import User
from productivity_tracker.repositories.base import BaseRepository

logger = __import__("logging").getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User database operations."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        logger.debug(f"Querying user by username: {username}")
        # Ensure any pending changes are flushed before querying
        self.db.flush()
        user = cast(
            User | None,
            self.db.query(User)
            .filter(User.username == username, User.is_deleted == False)  # noqa: E712
            .first(),
        )
        logger.debug(f"Query result for {username}: {user}")
        return user

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        # Ensure any pending changes are flushed before querying
        self.db.flush()
        return cast(
            User | None,
            self.db.query(User)
            .filter(User.email == email, User.is_deleted == False)  # noqa: E712
            .first(),
        )

    def get_by_email_or_username(self, email: EmailStr, username: str) -> User | None:
        """Get user by email or username."""
        # Ensure any pending changes are flushed before querying
        self.db.flush()
        return cast(
            User | None,
            self.db.query(User)
            .filter(
                (User.email == email) | (User.username == username),
                User.is_deleted == False,  # noqa: E712
            )
            .first(),
        )

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users."""
        # Ensure any pending changes are flushed before querying
        self.db.flush()
        return cast(
            list[User],
            self.db.query(User)
            .filter(User.is_active == True, User.is_deleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all(),
        )

    def get_superusers(self) -> list[User]:
        """Get all superusers."""
        return cast(
            list[User],
            self.db.query(User).filter(User.is_superuser, User.is_deleted.is_(False)).all(),
        )

    def assign_roles(self, user: User, role_ids: list[UUID]) -> User:
        """Assign roles to a user."""
        roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()
        user.roles = roles
        self.db.commit()
        self.db.refresh(user)
        return user

    def add_role(self, user: User, role_id: UUID) -> User:
        """Add a single role to a user."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role not in user.roles:
            user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        return user

    def remove_role(self, user: User, role_id: UUID) -> User:
        """Remove a role from a user."""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_users_by_role(self, role_name: str) -> list[User]:
        """Get all users with a specific role."""
        return cast(
            list[User],
            self.db.query(User)
            .join(User.roles)
            .filter(Role.name == role_name, User.is_deleted == False)  # noqa: E712
            .all(),
        )

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> list[User]:
        """Search users by username or email."""
        search_pattern = f"%{query}%"
        return cast(
            list[User],
            self.db.query(User)
            .filter(
                (User.username.ilike(search_pattern) | User.email.ilike(search_pattern)),
                User.is_deleted == False,  # noqa: E712
            )
            .offset(skip)
            .limit(limit)
            .all(),
        )
