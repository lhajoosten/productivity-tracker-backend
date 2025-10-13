"""API routes for permission management."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import get_current_superuser
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from productivity_tracker.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post(
    "/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED
)
def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Create a new permission (admin only)."""
    permission_service = PermissionService(db)
    new_permission = permission_service.create_permission(permission_data)
    return new_permission


@router.get("/", response_model=list[PermissionResponse])
def get_all_permissions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get all permissions (admin only)."""
    permission_service = PermissionService(db)
    permissions = permission_service.get_all_permissions(skip, limit)
    return permissions


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get permission by ID (admin only)."""
    permission_service = PermissionService(db)
    permission = permission_service.get_permission(permission_id)
    return permission


@router.get("/name/{permission_name}", response_model=PermissionResponse)
def get_permission_by_name(
    permission_name: str,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get permission by name (admin only)."""
    permission_service = PermissionService(db)
    permission = permission_service.get_permission_by_name(permission_name)
    return permission


@router.get("/resource/{resource}", response_model=list[PermissionResponse])
def get_permissions_by_resource(
    resource: str,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Get all permissions for a specific resource (admin only)."""
    permission_service = PermissionService(db)
    permissions = permission_service.get_permissions_by_resource(resource)
    return permissions


@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: UUID,
    permission_data: PermissionUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Update permission (admin only)."""
    permission_service = PermissionService(db)
    updated_permission = permission_service.update_permission(
        permission_id, permission_data
    )
    return updated_permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Delete permission (admin only)."""
    permission_service = PermissionService(db)
    permission_service.delete_permission(permission_id)
    return None
