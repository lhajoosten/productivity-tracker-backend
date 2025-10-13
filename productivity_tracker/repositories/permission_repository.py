"""Repository for Permission entity operations."""

from sqlalchemy.orm import Session

from productivity_tracker.database.entities.role import Permission
from productivity_tracker.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission-specific database operations."""

    def __init__(self, db: Session):
        super().__init__(Permission, db)

    def get_by_name(self, name: str) -> Permission | None:
        """Get permission by name."""
        return (
            self.db.query(Permission)
            .filter(Permission.name == name, Permission.is_deleted is False)
            .first()
        )

    def get_by_resource_and_action(
        self, resource: str, action: str
    ) -> Permission | None:
        """Get permission by resource and action."""
        return (
            self.db.query(Permission)
            .filter(
                Permission.resource == resource,
                Permission.action == action,
                Permission.is_deleted is False,
            )
            .first()
        )

    def get_by_resource(self, resource: str) -> list[Permission]:
        """Get all permissions for a specific resource."""
        return (
            self.db.query(Permission)
            .filter(Permission.resource == resource, Permission.is_deleted is False)
            .all()
        )

    def get_by_action(self, action: str) -> list[Permission]:
        """Get all permissions with a specific action."""
        return (
            self.db.query(Permission)
            .filter(Permission.action == action, Permission.is_deleted is False)
            .all()
        )
