"""Repository for Role entity operations."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.database.entities.role import Permission, Role
from productivity_tracker.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role-specific database operations."""

    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        return (
            self.db.query(Role)
            .filter(Role.name == name, Role.is_deleted is False)
            .first()
        )

    def assign_permissions(self, role: Role, permission_ids: list[UUID]) -> Role:
        """Assign permissions to a role."""
        permissions = (
            self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        )
        role.permissions = permissions
        self.db.commit()
        self.db.refresh(role)
        return role

    def add_permission(self, role: Role, permission_id: UUID) -> Role:
        """Add a single permission to a role."""
        permission = (
            self.db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if permission and permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
            self.db.refresh(role)
        return role

    def remove_permission(self, role: Role, permission_id: UUID) -> Role:
        """Remove a permission from a role."""
        permission = (
            self.db.query(Permission).filter(Permission.id == permission_id).first()
        )
        if permission and permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
            self.db.refresh(role)
        return role

    def get_roles_with_permission(self, permission_name: str) -> list[Role]:
        """Get all roles that have a specific permission."""
        return (
            self.db.query(Role)
            .join(Role.permissions)
            .filter(Permission.name == permission_name, Role.is_deleted is False)
            .all()
        )
