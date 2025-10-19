"""API routes for role management."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import get_current_superuser
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import (
    AssignPermissionsToRole,
    RoleCreate,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
)
from productivity_tracker.services.role_service import RoleService

router = APIRouter()


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createRole",
)
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Create a new role (admin only)."""
    role_service = RoleService(db)
    new_role = role_service.create_role(role_data)
    return new_role


@router.get("/roles", response_model=list[RoleListResponse], operation_id="getAllRoles")
def get_all_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get all roles (admin only)."""
    role_service = RoleService(db)
    roles = role_service.get_all_roles(skip, limit)
    return roles


@router.get("/roles/{role_id}", response_model=RoleResponse, operation_id="getRole")
def get_role(
    role_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get role by ID (admin only)."""
    role_service = RoleService(db)
    role = role_service.get_role(role_id)
    return role


@router.get("/roles/name/{role_name}", response_model=RoleResponse, operation_id="getRoleByName")
def get_role_by_name(
    role_name: str,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get role by name (admin only)."""
    role_service = RoleService(db)
    role = role_service.get_role_by_name(role_name)
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse, operation_id="updateRole")
def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Update role (admin only)."""
    role_service = RoleService(db)
    updated_role = role_service.update_role(role_id, role_data)
    return updated_role


@router.delete(
    "/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteRole"
)
def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Delete role (admin only)."""
    role_service = RoleService(db)
    role_service.delete_role(role_id)
    return None


@router.post(
    "/roles/{role_id}/permissions",
    response_model=RoleResponse,
    operation_id="assignPermissionsToRole",
)
def assign_permissions_to_role(
    role_id: UUID,
    permission_data: AssignPermissionsToRole,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Assign permissions to a role (admin only)."""
    role_service = RoleService(db)
    role = role_service.assign_permissions(role_id, permission_data.permission_ids)
    return role


@router.post(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=RoleResponse,
    operation_id="addPermissionToRole",
)
def add_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Add a single permission to a role (admin only)."""
    role_service = RoleService(db)
    role = role_service.add_permission(role_id, permission_id)
    return role


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=RoleResponse,
    operation_id="removePermissionFromRole",
)
def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Remove a permission from a role (admin only)."""
    role_service = RoleService(db)
    role = role_service.remove_permission(role_id, permission_id)
    return role
