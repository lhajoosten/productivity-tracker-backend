"""Unit tests for organization service."""

from uuid import uuid4

import pytest

from productivity_tracker.core.exceptions import ResourceNotFoundError
from productivity_tracker.database.entities.organization import Organization
from productivity_tracker.models.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)
from productivity_tracker.services.organization_service import OrganizationService

pytestmark = [pytest.mark.unit]


class TestOrganizationServiceCreate:
    """Test organization creation in service layer."""

    def test_create_organization_success(self, db_session_unit):
        """Should create organization successfully."""
        from uuid import uuid4 as gen_uuid

        service = OrganizationService(db_session_unit)

        unique_slug = f"test-org-{gen_uuid().hex[:8]}"
        org_data = OrganizationCreate(
            name="Test Org",
            slug=unique_slug,
            description="Test description",
        )

        org = service.create_organization(org_data)

        assert org.name == org_data.name
        assert org.slug == org_data.slug
        assert org.description == org_data.description
        assert org.id is not None

    def test_create_organization_minimal_data(self, db_session_unit):
        """Should create organization with minimal data."""
        from uuid import uuid4 as gen_uuid

        service = OrganizationService(db_session_unit)

        unique_slug = f"minimal-org-{gen_uuid().hex[:8]}"
        org_data = OrganizationCreate(name="Minimal Org", slug=unique_slug)

        org = service.create_organization(org_data)

        assert org.name == org_data.name
        assert org.slug == org_data.slug
        assert org.description is None


class TestOrganizationServiceRead:
    """Test organization retrieval in service layer."""

    def test_get_organization_by_id(self, db_session_unit):
        """Should get organization by ID."""
        from uuid import uuid4 as gen_uuid

        # Create org first
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"test-{gen_uuid().hex[:8]}"
        org = Organization(name="Test", slug=unique_slug)
        created_org = repo.create(org)

        # Get via service
        service = OrganizationService(db_session_unit)
        retrieved = service.get_organization(created_org.id)

        assert retrieved.id == created_org.id
        assert retrieved.name == created_org.name

    def test_get_organization_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent org."""
        service = OrganizationService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.get_organization(uuid4())

    def test_get_all_organizations(self, db_session_unit):
        """Should get all organizations."""
        from uuid import uuid4 as gen_uuid

        # Create multiple orgs
        repo = OrganizationRepository(db_session_unit)
        unique_id = gen_uuid().hex[:8]
        org1 = Organization(name="Org 1", slug=f"org-1-{unique_id}")
        org2 = Organization(name="Org 2", slug=f"org-2-{unique_id}")
        repo.create(org1)
        repo.create(org2)

        # Get all via service
        service = OrganizationService(db_session_unit)
        orgs = service.get_all_organizations()

        assert len(orgs) >= 2
        assert any(o.name == "Org 1" for o in orgs)
        assert any(o.name == "Org 2" for o in orgs)


class TestOrganizationServiceUpdate:
    """Test organization update in service layer."""

    def test_update_organization_success(self, db_session_unit):
        """Should update organization successfully."""
        from uuid import uuid4 as gen_uuid

        # Create org
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"original-{gen_uuid().hex[:8]}"
        org = Organization(name="Original", slug=unique_slug)
        created_org = repo.create(org)

        # Update via service
        service = OrganizationService(db_session_unit)
        update_data = OrganizationUpdate(name="Updated", description="New description")
        updated = service.update_organization(created_org.id, update_data)

        assert updated.name == "Updated"
        assert updated.description == "New description"
        assert updated.slug == unique_slug  # Slug unchanged

    def test_update_organization_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent org."""
        service = OrganizationService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.update_organization(uuid4(), OrganizationUpdate(name="Updated"))


class TestOrganizationServiceDelete:
    """Test organization deletion in service layer."""

    def test_delete_organization_success(self, db_session_unit):
        """Should soft delete organization successfully."""
        from uuid import uuid4 as gen_uuid

        # Create org
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"to-delete-{gen_uuid().hex[:8]}"
        org = Organization(name="To Delete", slug=unique_slug)
        created_org = repo.create(org)

        # Delete via service
        service = OrganizationService(db_session_unit)
        service.delete_organization(created_org.id)

        # Verify soft deleted
        deleted_org = repo.get_by_id(created_org.id, include_deleted=True)
        assert deleted_org.is_deleted is True

    def test_delete_organization_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent org."""
        service = OrganizationService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.delete_organization(uuid4())


class TestOrganizationServiceMembers:
    """Test organization member management in service layer."""

    def test_add_member_to_organization(self, db_session_unit, sample_user):
        """Should add member to organization."""
        from uuid import uuid4 as gen_uuid

        # Create org
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"test-org-members-1-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org Members 1", slug=unique_slug)
        created_org = repo.create(org)

        # Add member via service
        service = OrganizationService(db_session_unit)
        result = service.add_member(created_org.id, sample_user.id)

        assert result is True

        # Verify member was added
        members = repo.get_members(created_org.id)
        assert any(m.id == sample_user.id for m in members)

    def test_remove_member_from_organization(self, db_session_unit, sample_user):
        """Should remove member from organization."""
        from uuid import uuid4 as gen_uuid

        # Create org and add member
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"test-org-members-2-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org Members 2", slug=unique_slug)
        created_org = repo.create(org)
        repo.add_member(created_org.id, sample_user.id)

        # Remove member via service
        service = OrganizationService(db_session_unit)
        service.remove_member(created_org.id, sample_user.id)

        # Verify member was removed
        members = repo.get_members(created_org.id)
        assert not any(m.id == sample_user.id for m in members)

    def test_get_organization_members(self, db_session_unit, sample_user):
        """Should get all organization members."""
        from uuid import uuid4 as gen_uuid

        # Create org and add member
        repo = OrganizationRepository(db_session_unit)
        unique_slug = f"test-org-members-3-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org Members 3", slug=unique_slug)
        created_org = repo.create(org)
        repo.add_member(created_org.id, sample_user.id)

        # Get members via service
        service = OrganizationService(db_session_unit)
        members = service.get_members(created_org.id)

        assert len(members) >= 1
        assert any(m.id == sample_user.id for m in members)
