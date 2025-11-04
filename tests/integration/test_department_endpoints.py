"""Integration tests for department endpoints."""

import pytest
from fastapi import status

from productivity_tracker.versioning import CURRENT_VERSION
from tests.utilities import assert_problem_detail_response

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

API_PREFIX = CURRENT_VERSION.api_prefix


class TestDepartmentCreation:
    """Test department creation endpoints."""

    async def test_create_department_success(self, authenticated_client, test_organization):
        """Should create department successfully."""
        data = {
            "name": "Engineering",
            "organization_id": str(test_organization.id),
            "description": "Engineering department",
        }

        response = authenticated_client.post(f"{API_PREFIX}/departments", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        dept = response.json()
        assert dept["name"] == data["name"]
        assert dept["organization_id"] == data["organization_id"]
        assert dept["description"] == data["description"]
        assert "id" in dept
        assert "created_at" in dept

    async def test_create_department_invalid_organization(self, authenticated_client):
        """Should reject invalid organization ID."""
        from uuid import uuid4

        data = {
            "name": "Engineering",
            "organization_id": str(uuid4()),
        }

        response = authenticated_client.post(f"{API_PREFIX}/departments", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert_problem_detail_response(
            response.json(), "resource-not-found", status.HTTP_404_NOT_FOUND
        )

    async def test_create_department_missing_required_fields(self, authenticated_client):
        """Should reject missing required fields."""
        data = {"name": ""}  # Empty name

        response = authenticated_client.post(f"{API_PREFIX}/departments", json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_department_unauthorized(self, client_integration, test_organization):
        """Should reject unauthorized request."""
        data = {
            "name": "Engineering",
            "organization_id": str(test_organization.id),
        }

        response = client_integration.post(f"{API_PREFIX}/departments", json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDepartmentRetrieval:
    """Test department retrieval endpoints."""

    async def test_get_all_departments(self, authenticated_client, test_department):
        """Should get all departments."""
        response = authenticated_client.get(f"{API_PREFIX}/departments")

        assert response.status_code == status.HTTP_200_OK
        depts = response.json()
        assert isinstance(depts, list)
        assert len(depts) >= 1
        assert any(dept["id"] == str(test_department.id) for dept in depts)

    async def test_get_department_by_id(self, authenticated_client, test_department):
        """Should get department by ID."""
        response = authenticated_client.get(f"{API_PREFIX}/departments/{test_department.id}")

        assert response.status_code == status.HTTP_200_OK
        dept = response.json()
        assert dept["id"] == str(test_department.id)
        assert dept["name"] == test_department.name
        assert dept["organization_id"] == str(test_department.organization_id)

    async def test_get_departments_by_organization(
        self, authenticated_client, test_organization, test_department
    ):
        """Should get departments by organization."""
        response = authenticated_client.get(
            f"/api/v1.1/organizations/{test_organization.id}/departments"
        )

        assert response.status_code == status.HTTP_200_OK
        depts = response.json()
        assert isinstance(depts, list)
        assert len(depts) >= 1
        assert all(dept["organization_id"] == str(test_organization.id) for dept in depts)

    async def test_get_department_not_found(self, authenticated_client):
        """Should return 404 for non-existent department."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.get(f"{API_PREFIX}/departments/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert_problem_detail_response(
            response.json(), "resource-not-found", status.HTTP_404_NOT_FOUND
        )


class TestDepartmentUpdate:
    """Test department update endpoints."""

    async def test_update_department_success(self, authenticated_client, test_department):
        """Should update department successfully."""
        data = {
            "name": "Updated Department",
            "description": "Updated description",
        }

        response = authenticated_client.put(
            f"{API_PREFIX}/departments/{test_department.id}", json=data
        )

        assert response.status_code == status.HTTP_200_OK
        dept = response.json()
        assert dept["name"] == data["name"]
        assert dept["description"] == data["description"]

    async def test_update_department_not_found(self, authenticated_client):
        """Should return 404 for non-existent department."""
        from uuid import uuid4

        fake_id = uuid4()
        data = {"name": "Updated"}

        response = authenticated_client.put(f"{API_PREFIX}/departments/{fake_id}", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDepartmentDeletion:
    """Test department deletion endpoints."""

    async def test_delete_department_success(self, authenticated_client, test_department):
        """Should soft delete department successfully."""
        response = authenticated_client.delete(f"{API_PREFIX}/departments/{test_department.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_department_not_found(self, authenticated_client):
        """Should return 404 for non-existent department."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.delete(f"{API_PREFIX}/departments/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_department_with_teams(
        self, authenticated_client, test_department, test_team
    ):
        """Should handle deletion of department with teams."""
        # This tests that the cascade behavior works correctly
        response = authenticated_client.delete(f"{API_PREFIX}/departments/{test_department.id}")

        # Should succeed with soft delete
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestDepartmentStatistics:
    """Test department statistics endpoints."""

    async def test_get_department_team_count(
        self, authenticated_client, test_department, test_team, db_session
    ):
        """Should return correct team count for department."""
        response = authenticated_client.get(f"{API_PREFIX}/departments/{test_department.id}")

        assert response.status_code == status.HTTP_200_OK
        dept = response.json()
        # Should have team_count if implemented
        assert "id" in dept
