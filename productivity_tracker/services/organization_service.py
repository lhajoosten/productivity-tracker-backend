"""Service for organization management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    BusinessLogicError,
    ResourceNotFoundError,
)
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.database.entities.organization import Organization
from productivity_tracker.models.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)

logger = get_logger(__name__)


class OrganizationService:
    """Service for organization-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = OrganizationRepository(db)

    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """Create a new organization."""
        logger.info(f"Creating new organization: {org_data.name}")

        # Check if slug already exists
        existing_org = self.repository.get_by_slug(org_data.slug)
        if existing_org:
            logger.warning(f"Organization creation failed: Slug {org_data.slug} already exists")
            raise BusinessLogicError(
                message=f"Organization with slug '{org_data.slug}' already exists",
                user_message=f"An organization with the slug '{org_data.slug}' already exists. Please use a different slug.",
                context={"field": "slug", "value": org_data.slug},
            )

        new_org = Organization(
            name=org_data.name,
            description=org_data.description,
            slug=org_data.slug,
        )

        created_org = self.repository.create(new_org)
        logger.info(f"Organization created successfully: {created_org.name} (ID: {created_org.id})")
        return created_org

    def get_organization(self, org_id: UUID) -> Organization:
        """Get organization by ID."""
        org = self.repository.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError(resource_type="Organization", resource_id=str(org_id))
        return org

    def get_organization_by_slug(self, slug: str) -> Organization:
        """Get organization by slug."""
        org = self.repository.get_by_slug(slug)
        if not org:
            raise ResourceNotFoundError(resource_type="Organization", resource_id=slug)
        return org

    def get_all_organizations(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        """Get all organizations."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_organization(self, org_id: UUID, org_data: OrganizationUpdate) -> Organization:
        """Update an organization."""
        logger.info(f"Updating organization: {org_id}")

        org = self.get_organization(org_id)

        # Check if slug is being changed and if it's already taken
        if org_data.slug and org_data.slug != org.slug:
            existing_org = self.repository.get_by_slug(org_data.slug)
            if existing_org:
                logger.warning(f"Organization update failed: Slug {org_data.slug} already exists")
                raise BusinessLogicError(
                    message=f"Organization with slug '{org_data.slug}' already exists",
                    user_message=f"An organization with the slug '{org_data.slug}' already exists. Please use a different slug.",
                    context={"field": "slug", "value": org_data.slug},
                )

        # Update fields
        if org_data.name is not None:
            org.name = org_data.name
        if org_data.description is not None:
            org.description = org_data.description
        if org_data.slug is not None:
            org.slug = org_data.slug

        updated_org = self.repository.update(org)
        logger.info(f"Organization updated successfully: {updated_org.id}")
        return updated_org

    def delete_organization(self, org_id: UUID, soft: bool = True) -> bool:
        """Delete an organization."""
        logger.info(f"Deleting organization: {org_id} (soft={soft})")

        # Verify organization exists before attempting delete
        self.get_organization(org_id)  # This will raise ResourceNotFoundError if not found

        result = self.repository.delete(org_id, soft=soft)
        if result:
            logger.info(f"Organization deleted successfully: {org_id}")
        return result

    def add_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Add a member to an organization."""
        logger.info(f"Adding user {user_id} to organization {org_id}")

        # Verify organization exists
        self.get_organization(org_id)

        result = self.repository.add_member(org_id, user_id)
        if result:
            logger.info(f"User {user_id} added to organization {org_id}")
        return result

    def remove_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Remove a member from an organization."""
        logger.info(f"Removing user {user_id} from organization {org_id}")

        result = self.repository.remove_member(org_id, user_id)
        if result:
            logger.info(f"User {user_id} removed from organization {org_id}")
        return result

    def get_members(self, org_id: UUID, skip: int = 0, limit: int = 100):
        """Get all members of an organization."""
        # Verify organization exists
        self.get_organization(org_id)

        return self.repository.get_members(org_id, skip=skip, limit=limit)
