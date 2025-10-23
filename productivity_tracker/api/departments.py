"""API routes for department management."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import get_current_user
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.organization import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from productivity_tracker.repositories.department_repository import DepartmentRepository
from productivity_tracker.services.department_service import DepartmentService

router = APIRouter()


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createDepartment",
)
def create_department(
    dept_data: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new department."""
    dept_service = DepartmentService(db)
    new_dept = dept_service.create_department(dept_data)

    # Enrich response with counts
    dept_repo = DepartmentRepository(db)
    response = DepartmentResponse.model_validate(new_dept)
    response.team_count = dept_repo.get_team_count(new_dept.id)
    response.member_count = dept_repo.get_member_count(new_dept.id)

    return response


@router.get(
    "/departments",
    response_model=list[DepartmentResponse],
    operation_id="getAllDepartments",
)
def get_all_departments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all departments."""
    dept_service = DepartmentService(db)
    depts = dept_service.get_all_departments(skip, limit)

    # Enrich responses with counts
    dept_repo = DepartmentRepository(db)
    responses = []
    for dept in depts:
        response = DepartmentResponse.model_validate(dept)
        response.team_count = dept_repo.get_team_count(dept.id)
        response.member_count = dept_repo.get_member_count(dept.id)
        responses.append(response)

    return responses


@router.get(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    operation_id="getDepartment",
)
def get_department(
    dept_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get department by ID."""
    dept_service = DepartmentService(db)
    dept = dept_service.get_department(dept_id)

    # Enrich response with counts
    dept_repo = DepartmentRepository(db)
    response = DepartmentResponse.model_validate(dept)
    response.team_count = dept_repo.get_team_count(dept.id)
    response.member_count = dept_repo.get_member_count(dept.id)

    return response


@router.get(
    "/organizations/{org_id}/departments",
    response_model=list[DepartmentResponse],
    operation_id="getDepartmentsByOrganization",
)
def get_departments_by_organization(
    org_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all departments for a specific organization."""
    dept_service = DepartmentService(db)
    depts = dept_service.get_departments_by_organization(org_id, skip, limit)

    # Enrich responses with counts
    dept_repo = DepartmentRepository(db)
    responses = []
    for dept in depts:
        response = DepartmentResponse.model_validate(dept)
        response.team_count = dept_repo.get_team_count(dept.id)
        response.member_count = dept_repo.get_member_count(dept.id)
        responses.append(response)

    return responses


@router.put(
    "/departments/{dept_id}",
    response_model=DepartmentResponse,
    operation_id="updateDepartment",
)
def update_department(
    dept_id: UUID,
    dept_data: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update department."""
    dept_service = DepartmentService(db)
    updated_dept = dept_service.update_department(dept_id, dept_data)

    # Enrich response with counts
    dept_repo = DepartmentRepository(db)
    response = DepartmentResponse.model_validate(updated_dept)
    response.team_count = dept_repo.get_team_count(updated_dept.id)
    response.member_count = dept_repo.get_member_count(updated_dept.id)

    return response


@router.delete(
    "/departments/{dept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteDepartment",
)
def delete_department(
    dept_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete department."""
    dept_service = DepartmentService(db)
    dept_service.delete_department(dept_id)
    return None
