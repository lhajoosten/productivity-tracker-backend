"""Service for role management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from productivity_tracker.database.entities.role import Role
from productivity_tracker.models.auth import RoleCreate, RoleUpdate
from productivity_tracker.repositories.role_repository import RoleRepository


class RoleService:
    """Service for role-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = RoleRepository(db)

    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role already exists
        existing_role = self.repository.get_by_name(role_data.name)
        if existing_role:
            raise ResourceAlreadyExistsError(
                resource_type="Role",
                field="name",
                value=role_data.name,
            )

        # Create new role
        new_role = Role(
            name=role_data.name,
            description=role_data.description,
        )
        created_role = self.repository.create(new_role)

        # Assign permissions if provided
        if role_data.permission_ids:
            created_role = self.repository.assign_permissions(
                created_role, role_data.permission_ids
            )

        return created_role

    def get_role(self, role_id: UUID) -> Role:
        """Get role by ID."""
        role = self.repository.get_by_id(role_id)
        if not role:
            raise ResourceNotFoundError(resource_type="Role", resource_id=str(role_id))
        return role

    def get_role_by_name(self, name: str) -> Role:
        """Get role by name."""
        role = self.repository.get_by_name(name)
        if not role:
            raise ResourceNotFoundError(resource_type="Role", resource_id=name)
        return role

    def get_all_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        """Get all roles with pagination."""
        return self.repository.get_all(skip, limit)

    def update_role(self, role_id: UUID, role_data: RoleUpdate) -> Role:
        """Update role information."""
        role = self.get_role(role_id)

        # Check if new name already exists
        if role_data.name and role_data.name != role.name:
            existing = self.repository.get_by_name(role_data.name)
            if existing:
                raise ResourceAlreadyExistsError(
                    resource_type="Role",
                    field="name",
                    value=role_data.name,
                )
            role.name = role_data.name

        if role_data.description is not None:
            role.description = role_data.description

        updated_role = self.repository.update(role)

        # Update permissions if provided
        if role_data.permission_ids is not None:
            updated_role = self.repository.assign_permissions(
                updated_role, role_data.permission_ids
            )

        return updated_role

    def delete_role(self, role_id: UUID, soft: bool = True) -> bool:
        """Delete a role."""
        return self.repository.delete(role_id, soft=soft)

    def assign_permissions(self, role_id: UUID, permission_ids: list[UUID]) -> Role:
        """Assign permissions to a role."""
        role = self.get_role(role_id)
        return self.repository.assign_permissions(role, permission_ids)

    def add_permission(self, role_id: UUID, permission_id: UUID) -> Role:
        """Add a permission to a role."""
        role = self.get_role(role_id)
        return self.repository.add_permission(role, permission_id)

    def remove_permission(self, role_id: UUID, permission_id: UUID) -> Role:
        """Remove a permission from a role."""
        role = self.get_role(role_id)
        return self.repository.remove_permission(role, permission_id)
