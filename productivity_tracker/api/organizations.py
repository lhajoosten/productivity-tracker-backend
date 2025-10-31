"""API routes for organization management."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from productivity_tracker.core.dependencies import get_current_user
from productivity_tracker.database import get_db
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import UserResponse
from productivity_tracker.models.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)
from productivity_tracker.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createOrganization",
)
def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new organization."""
    org_service = OrganizationService(db)
    new_org = org_service.create_organization(org_data)

    # Enrich response with counts
    org_repo = OrganizationRepository(db)
    response = OrganizationResponse.model_validate(new_org)
    response.member_count = org_repo.get_member_count(new_org.id)
    response.department_count = org_repo.get_department_count(new_org.id)

    return response


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse],
    operation_id="getAllOrganizations",
)
def get_all_organizations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all organizations."""
    org_service = OrganizationService(db)
    orgs = org_service.get_all_organizations(skip, limit)

    # Enrich responses with counts
    org_repo = OrganizationRepository(db)
    responses = []
    for org in orgs:
        response = OrganizationResponse.model_validate(org)
        response.member_count = org_repo.get_member_count(org.id)
        response.department_count = org_repo.get_department_count(org.id)
        responses.append(response)

    return responses


@router.get(
    "/organizations/current",
    response_model=OrganizationResponse,
    operation_id="getCurrentOrganization",
)
def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's organization."""
    from productivity_tracker.core.exceptions import ResourceNotFoundError

    org_repo = OrganizationRepository(db)

    # Get user's organizations
    orgs = org_repo.get_by_user(current_user.id)
    if not orgs:
        raise ResourceNotFoundError(
            resource_type="Organization", resource_id=f"for user {current_user.id}"
        )

    # Return first organization (assuming user belongs to one organization)
    org = orgs[0]
    response = OrganizationResponse.model_validate(org)
    response.member_count = org_repo.get_member_count(org.id)
    response.department_count = org_repo.get_department_count(org.id)
    return response


@router.get(
    "/organizations/{org_id}",
    response_model=OrganizationResponse,
    operation_id="getOrganization",
)
def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get organization by ID."""
    org_service = OrganizationService(db)
    org = org_service.get_organization(org_id)

    # Enrich response with counts
    org_repo = OrganizationRepository(db)
    response = OrganizationResponse.model_validate(org)
    response.member_count = org_repo.get_member_count(org.id)
    response.department_count = org_repo.get_department_count(org.id)

    return response


@router.get(
    "/organizations/slug/{slug}",
    response_model=OrganizationResponse,
    operation_id="getOrganizationBySlug",
)
def get_organization_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get organization by slug."""
    org_service = OrganizationService(db)
    org = org_service.get_organization_by_slug(slug)

    # Enrich response with counts
    org_repo = OrganizationRepository(db)
    response = OrganizationResponse.model_validate(org)
    response.member_count = org_repo.get_member_count(org.id)
    response.department_count = org_repo.get_department_count(org.id)

    return response


@router.put(
    "/organizations/{org_id}",
    response_model=OrganizationResponse,
    operation_id="updateOrganization",
)
def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update organization."""
    org_service = OrganizationService(db)
    updated_org = org_service.update_organization(org_id, org_data)

    # Enrich response with counts
    org_repo = OrganizationRepository(db)
    response = OrganizationResponse.model_validate(updated_org)
    response.member_count = org_repo.get_member_count(updated_org.id)
    response.department_count = org_repo.get_department_count(updated_org.id)

    return response


@router.delete(
    "/organizations/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteOrganization",
)
def delete_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete organization."""
    org_service = OrganizationService(db)
    org_service.delete_organization(org_id)
    return None


@router.post(
    "/organizations/{org_id}/members/{user_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    operation_id="addOrganizationMember",
)
def add_organization_member(
    org_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a member to an organization."""
    org_service = OrganizationService(db)
    org_service.add_member(org_id, user_id)

    # Return updated organization
    org = org_service.get_organization(org_id)
    org_repo = OrganizationRepository(db)
    response = OrganizationResponse.model_validate(org)
    response.member_count = org_repo.get_member_count(org.id)
    response.department_count = org_repo.get_department_count(org.id)
    return response


@router.delete(
    "/organizations/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="removeOrganizationMember",
)
def remove_organization_member(
    org_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from an organization."""
    org_service = OrganizationService(db)
    org_service.remove_member(org_id, user_id)
    return None


@router.get(
    "/organizations/{org_id}/members",
    response_model=list[UserResponse],
    operation_id="getOrganizationMembers",
)
def get_organization_members(
    org_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all members of an organization."""
    org_service = OrganizationService(db)
    members = org_service.get_members(org_id, skip, limit)
    return members
