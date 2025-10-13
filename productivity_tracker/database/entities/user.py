from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from productivity_tracker.database.entities.base import BaseEntity


class User(BaseEntity):
    """User model for authentication and user management with RBAC."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

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
