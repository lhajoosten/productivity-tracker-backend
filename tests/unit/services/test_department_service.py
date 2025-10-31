"""Unit tests for department service."""

from uuid import uuid4

import pytest

from productivity_tracker.core.exceptions import ResourceNotFoundError
from productivity_tracker.database.entities.department import Department
from productivity_tracker.database.entities.organization import Organization
from productivity_tracker.models.organization import DepartmentCreate, DepartmentUpdate
from productivity_tracker.repositories.department_repository import DepartmentRepository
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)
from productivity_tracker.services.department_service import DepartmentService

pytestmark = [pytest.mark.unit]


class TestDepartmentServiceCreate:
    """Test department creation in service layer."""

    def test_create_department_success(self, db_session_unit):
        """Should create department successfully."""
        # Create organization first
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org", slug="test-org")
        created_org = org_repo.create(org)

        # Create department
        service = DepartmentService(db_session_unit)
        dept_data = DepartmentCreate(
            name="Engineering",
            organization_id=created_org.id,
            description="Engineering department",
        )

        dept = service.create_department(dept_data)
        assert dept.name == dept_data.name
        assert dept.organization_id == dept_data.organization_id
        assert dept.description == dept_data.description
        assert dept.id is not None

    def test_create_department_minimal_data(self, db_session_unit):
        """Should create department with minimal data."""
        from uuid import uuid4 as gen_uuid

        # Create organization first
        org_repo = OrganizationRepository(db_session_unit)
        unique_slug = f"test-org-min-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org", slug=unique_slug)
        created_org = org_repo.create(org)

        # Create department
        service = DepartmentService(db_session_unit)
        dept_data = DepartmentCreate(name="Sales", organization_id=created_org.id)

        dept = service.create_department(dept_data)
        assert dept.name == dept_data.name
        assert dept.description is None

    def test_create_department_invalid_organization(self, db_session_unit):
        """Should raise ResourceNotFoundError for invalid organization."""
        service = DepartmentService(db_session_unit)
        dept_data = DepartmentCreate(name="Engineering", organization_id=uuid4())

        with pytest.raises(ResourceNotFoundError):
            service.create_department(dept_data)


class TestDepartmentServiceRead:
    """Test department retrieval in service layer."""

    def test_get_department_by_id(self, db_session_unit):
        """Should get department by ID."""

        from uuid import uuid4 as gen_uuid

        unique_slug = f"test-org-3-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org 3", slug=unique_slug)
        org_repo = OrganizationRepository(db_session_unit)
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Get via service
        service = DepartmentService(db_session_unit)
        retrieved = service.get_department(created_dept.id)

        assert retrieved.id == created_dept.id
        assert retrieved.name == created_dept.name

    def test_get_department_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent department."""
        service = DepartmentService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.get_department(uuid4())

    def test_get_all_departments(self, db_session_unit):
        """Should get all departments."""

        from uuid import uuid4 as gen_uuid

        unique_slug = f"test-org-4-{gen_uuid().hex[:8]}"
        org = Organization(name="Test Org 4", slug=unique_slug)
        org_repo = OrganizationRepository(db_session_unit)
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept1 = Department(name="Engineering", organization_id=created_org.id)
        dept2 = Department(name="Sales", organization_id=created_org.id)
        dept_repo.create(dept1)
        dept_repo.create(dept2)

        # Get all via service
        service = DepartmentService(db_session_unit)
        depts = service.get_all_departments()

        assert len(depts) >= 2
        assert any(d.name == "Engineering" for d in depts)
        assert any(d.name == "Sales" for d in depts)

    def test_get_departments_by_organization(self, db_session_unit):
        """Should get departments by organization."""
        # Create orgs and depts
        org_repo = OrganizationRepository(db_session_unit)
        org1 = Organization(name="Org 1", slug="org-1")
        org2 = Organization(name="Org 2", slug="org-2")
        created_org1 = org_repo.create(org1)
        created_org2 = org_repo.create(org2)

        dept_repo = DepartmentRepository(db_session_unit)
        dept1 = Department(name="Dept 1", organization_id=created_org1.id)
        dept2 = Department(name="Dept 2", organization_id=created_org2.id)
        dept_repo.create(dept1)
        dept_repo.create(dept2)

        # Get depts for org1
        service = DepartmentService(db_session_unit)
        depts = service.get_departments_by_organization(created_org1.id)

        assert len(depts) >= 1
        assert all(d.organization_id == created_org1.id for d in depts)


class TestDepartmentServiceUpdate:
    """Test department update in service layer."""

    def test_update_department_success(self, db_session_unit):
        """Should update department successfully."""
        # Create org and dept
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org 5", slug="test-org-5")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Original", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Update via service
        service = DepartmentService(db_session_unit)
        update_data = DepartmentUpdate(name="Updated", description="New description")
        updated = service.update_department(created_dept.id, update_data)

        assert updated.name == "Updated"
        assert updated.description == "New description"

    def test_update_department_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent department."""
        service = DepartmentService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.update_department(uuid4(), DepartmentUpdate(name="Updated"))


class TestDepartmentServiceDelete:
    """Test department deletion in service layer."""

    def test_delete_department_success(self, db_session_unit):
        """Should soft delete department successfully."""
        # Create org and dept
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org 6", slug="test-org-6")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="To Delete", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Delete via service
        service = DepartmentService(db_session_unit)
        service.delete_department(created_dept.id)

        # Verify soft deleted
        deleted_dept = dept_repo.get_by_id(created_dept.id, include_deleted=True)
        assert deleted_dept.is_deleted is True

    def test_delete_department_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent department."""
        service = DepartmentService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.delete_department(uuid4())
