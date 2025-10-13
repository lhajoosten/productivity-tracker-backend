from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from productivity_tracker.database.entities.base import BaseEntity

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    "user_roles",
    BaseEntity.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    "role_permissions",
    BaseEntity.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(BaseEntity):
    """Role model for RBAC."""

    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))

    # Relationships
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )
    users = relationship(
        "User", secondary="user_roles", back_populates="roles", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission."""
        return any(p.name == permission_name for p in self.permissions)


class Permission(BaseEntity):
    """Permission model for RBAC."""

    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(
        String(50), nullable=False, index=True
    )  # e.g., "user", "task", "project"
    action = Column(
        String(50), nullable=False
    )  # e.g., "create", "read", "update", "delete"
    description = Column(String(255))

    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"
