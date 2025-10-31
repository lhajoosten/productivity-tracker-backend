from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from productivity_tracker.database.entities.base import BaseEntity


class User(BaseEntity):
    """User model for authentication and user management with RBAC."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # RBAC relationship - many-to-many with roles
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through their roles."""
        if self.is_superuser:
            return True
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False

    def has_any_permission(self, *permission_names: str) -> bool:
        """Check if user has any of the specified permissions."""
        if self.is_superuser:
            return True
        return any(self.has_permission(perm) for perm in permission_names)

    def has_all_permissions(self, *permission_names: str) -> bool:
        """Check if user has all of the specified permissions."""
        if self.is_superuser:
            return True
        return all(self.has_permission(perm) for perm in permission_names)

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        if self.is_superuser:
            return True
        return any(role.name == role_name for role in self.roles)
