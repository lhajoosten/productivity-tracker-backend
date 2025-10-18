"""Service for permission management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    BusinessLogicError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from productivity_tracker.database.entities.role import Permission
from productivity_tracker.models.auth import PermissionCreate, PermissionUpdate
from productivity_tracker.repositories.permission_repository import PermissionRepository


class PermissionService:
    """Service for permission-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PermissionRepository(db)

    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission already exists
        existing_permission = self.repository.get_by_name(permission_data.name)
        if existing_permission:
            raise ResourceAlreadyExistsError(
                resource_type="Permission",
                field="name",
                value=permission_data.name,
            )

        # Check if resource+action combination already exists
        existing_combination = self.repository.get_by_resource_and_action(
            permission_data.resource, permission_data.action
        )
        if existing_combination:
            raise BusinessLogicError(
                message=f"Permission for resource '{permission_data.resource}' "
                f"and action '{permission_data.action}' already exists",
                user_message="A permission for this resource and action combination already exists.",
                context={
                    "resource": permission_data.resource,
                    "action": permission_data.action,
                },
            )

        # Create new permission
        new_permission = Permission(
            name=permission_data.name,
            resource=permission_data.resource,
            action=permission_data.action,
            description=permission_data.description,
        )

        return self.repository.create(new_permission)

    def get_permission(self, permission_id: UUID) -> Permission:
        """Get permission by ID."""
        permission = self.repository.get_by_id(permission_id)
        if not permission:
            raise ResourceNotFoundError(
                resource_type="Permission", resource_id=str(permission_id)
            )
        return permission

    def get_permission_by_name(self, name: str) -> Permission:
        """Get permission by name."""
        permission = self.repository.get_by_name(name)
        if not permission:
            raise ResourceNotFoundError(resource_type="Permission", resource_id=name)
        return permission

    def get_all_permissions(self, skip: int = 0, limit: int = 100) -> list[Permission]:
        """Get all permissions with pagination."""
        return self.repository.get_all(skip, limit)

    def get_permissions_by_resource(self, resource: str) -> list[Permission]:
        """Get all permissions for a specific resource."""
        return self.repository.get_by_resource(resource)

    def update_permission(
        self, permission_id: UUID, permission_data: PermissionUpdate
    ) -> Permission:
        """Update permission information."""
        permission = self.get_permission(permission_id)

        # Check if new name already exists
        if permission_data.name and permission_data.name != permission.name:
            existing = self.repository.get_by_name(permission_data.name)
            if existing:
                raise ResourceAlreadyExistsError(
                    resource_type="Permission",
                    field="name",
                    value=permission_data.name,
                )
            permission.name = permission_data.name

        if permission_data.resource:
            permission.resource = permission_data.resource

        if permission_data.action:
            permission.action = permission_data.action

        if permission_data.description is not None:
            permission.description = permission_data.description

        return self.repository.update(permission)

    def delete_permission(self, permission_id: UUID, soft: bool = True) -> bool:
        """Delete a permission."""
        return self.repository.delete(permission_id, soft=soft)
