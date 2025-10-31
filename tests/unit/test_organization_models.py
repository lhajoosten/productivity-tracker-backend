"""Unit tests for organization models/schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from productivity_tracker.models.organization import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    TeamCreate,
    TeamMemberAdd,
    TeamMemberRemove,
    TeamUpdate,
    TeamWithLeadResponse,
)

pytestmark = [pytest.mark.unit]


class TestOrganizationSchemas:
    """Test organization Pydantic schemas."""

    def test_organization_create_valid(self):
        """Should create valid OrganizationCreate schema."""
        data = {
            "name": "Test Org",
            "slug": "test-org",
            "description": "Test description",
        }

        schema = OrganizationCreate(**data)

        assert schema.name == data["name"]
        assert schema.slug == data["slug"]
        assert schema.description == data["description"]

    def test_organization_create_minimal(self):
        """Should create schema with minimal required fields."""
        data = {"name": "Test Org", "slug": "test-org"}

        schema = OrganizationCreate(**data)

        assert schema.name == data["name"]
        assert schema.slug == data["slug"]
        assert schema.description is None

    def test_organization_create_invalid_empty_name(self):
        """Should reject empty name."""
        data = {"name": "", "slug": "test"}

        with pytest.raises(ValidationError):
            OrganizationCreate(**data)

    def test_organization_update_valid(self):
        """Should create valid OrganizationUpdate schema."""
        data = {"name": "Updated", "description": "Updated description"}

        schema = OrganizationUpdate(**data)

        assert schema.name == data["name"]
        assert schema.description == data["description"]

    def test_organization_update_partial(self):
        """Should allow partial updates."""
        data = {"name": "Updated"}

        schema = OrganizationUpdate(**data)

        assert schema.name == "Updated"
        assert schema.description is None

    def test_organization_response_valid(self):
        """Should create valid OrganizationResponse schema."""
        data = {
            "id": uuid4(),
            "name": "Test Org",
            "slug": "test-org",
            "description": "Test",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "is_deleted": False,
        }

        schema = OrganizationResponse(**data)

        assert str(schema.id) == str(data["id"])
        assert schema.name == data["name"]


class TestDepartmentSchemas:
    """Test department Pydantic schemas."""

    def test_department_create_valid(self):
        """Should create valid DepartmentCreate schema."""
        org_id = uuid4()
        data = {
            "name": "Engineering",
            "organization_id": org_id,
            "description": "Engineering department",
        }

        schema = DepartmentCreate(**data)

        assert schema.name == data["name"]
        assert schema.organization_id == org_id
        assert schema.description == data["description"]

    def test_department_create_minimal(self):
        """Should create schema with minimal required fields."""
        org_id = uuid4()
        data = {"name": "Engineering", "organization_id": org_id}

        schema = DepartmentCreate(**data)

        assert schema.name == data["name"]
        assert schema.organization_id == org_id
        assert schema.description is None

    def test_department_create_invalid_empty_name(self):
        """Should reject empty name."""
        data = {"name": "", "organization_id": uuid4()}

        with pytest.raises(ValidationError):
            DepartmentCreate(**data)

    def test_department_update_valid(self):
        """Should create valid DepartmentUpdate schema."""
        data = {"name": "Updated", "description": "Updated description"}

        schema = DepartmentUpdate(**data)

        assert schema.name == data["name"]
        assert schema.description == data["description"]

    def test_department_response_valid(self):
        """Should create valid DepartmentResponse schema."""
        data = {
            "id": uuid4(),
            "name": "Engineering",
            "organization_id": uuid4(),
            "description": "Test",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "is_deleted": False,
        }

        schema = DepartmentResponse(**data)

        assert str(schema.id) == str(data["id"])
        assert schema.name == data["name"]


class TestTeamSchemas:
    """Test team Pydantic schemas."""

    def test_team_create_valid(self):
        """Should create valid TeamCreate schema."""
        dept_id = uuid4()
        lead_id = uuid4()
        data = {
            "name": "Backend Team",
            "department_id": dept_id,
            "lead_id": lead_id,
            "description": "Backend development",
        }

        schema = TeamCreate(**data)

        assert schema.name == data["name"]
        assert schema.department_id == dept_id
        assert schema.lead_id == lead_id
        assert schema.description == data["description"]

    def test_team_create_minimal(self):
        """Should create schema with minimal required fields."""
        dept_id = uuid4()
        data = {"name": "Backend Team", "department_id": dept_id}

        schema = TeamCreate(**data)

        assert schema.name == data["name"]
        assert schema.department_id == dept_id
        assert schema.lead_id is None
        assert schema.description is None

    def test_team_create_invalid_empty_name(self):
        """Should reject empty name."""
        data = {"name": "", "department_id": uuid4()}

        with pytest.raises(ValidationError):
            TeamCreate(**data)

    def test_team_update_valid(self):
        """Should create valid TeamUpdate schema."""
        data = {
            "name": "Updated Team",
            "description": "Updated description",
            "lead_id": uuid4(),
        }

        schema = TeamUpdate(**data)

        assert schema.name == data["name"]
        assert schema.description == data["description"]
        assert schema.lead_id == data["lead_id"]

    def test_team_with_lead_response_valid(self):
        """Should create valid TeamWithLeadResponse schema."""
        data = {
            "id": uuid4(),
            "name": "Backend Team",
            "department_id": uuid4(),
            "lead_id": uuid4(),
            "description": "Test",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "is_deleted": False,
        }

        schema = TeamWithLeadResponse(**data)

        assert str(schema.id) == str(data["id"])
        assert schema.name == data["name"]
        assert str(schema.lead_id) == str(data["lead_id"])

    def test_team_member_add_valid(self):
        """Should create valid TeamMemberAdd schema."""
        user_id = uuid4()
        data = {"user_id": user_id}

        schema = TeamMemberAdd(**data)

        assert schema.user_id == user_id

    def test_team_member_remove_valid(self):
        """Should create valid TeamMemberRemove schema."""
        user_id = uuid4()
        data = {"user_id": user_id}

        schema = TeamMemberRemove(**data)

        assert schema.user_id == user_id


class TestSchemaFieldValidation:
    """Test schema field validation rules."""

    def test_name_min_length(self):
        """Should enforce minimum name length."""
        # Most schemas require at least 1 character
        data = {"name": "", "slug": "test"}

        with pytest.raises(ValidationError):
            OrganizationCreate(**data)

    def test_slug_format(self):
        """Should validate slug format."""
        # Test with valid slug
        data = {"name": "Test", "slug": "test-org-123"}
        schema = OrganizationCreate(**data)
        assert schema.slug == "test-org-123"

    def test_uuid_validation(self):
        """Should validate UUID fields."""
        # Invalid UUID should raise error
        data = {"name": "Test", "organization_id": "not-a-uuid"}

        with pytest.raises(ValidationError):
            DepartmentCreate(**data)
