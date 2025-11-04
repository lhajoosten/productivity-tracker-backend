"""Integration tests for organization endpoints."""

import pytest
from fastapi import status

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestOrganizationCreation:
    """Test organization creation endpoints."""

    async def test_create_organization_success(self, authenticated_client, test_user):
        """Should create organization successfully."""
        data = {
            "name": "Test Organization",
            "slug": "test-org",
            "description": "A test organization",
        }

        response = authenticated_client.post("/api/v1.1/organizations", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        org = response.json()
        assert org["name"] == data["name"]
        assert org["slug"] == data["slug"]
        assert org["description"] == data["description"]
        assert "id" in org
        assert "created_at" in org

    async def test_create_organization_duplicate_slug(
        self, authenticated_client, test_organization
    ):
        """Should reject duplicate slug."""
        data = {
            "name": "Another Organization",
            "slug": test_organization.slug,
            "description": "Another org",
        }

        response = authenticated_client.post("/api/v1.1/organizations", json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_organization_invalid_data(self, authenticated_client):
        """Should reject invalid data."""
        data = {"name": ""}  # Empty name

        response = authenticated_client.post("/api/v1.1/organizations", json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_organization_unauthorized(self, client_integration):
        """Should reject unauthorized request."""
        data = {
            "name": "Test Organization",
            "slug": "test-org",
        }

        response = client_integration.post("/api/v1.1/organizations", json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrganizationRetrieval:
    """Test organization retrieval endpoints."""

    async def test_get_all_organizations(self, authenticated_client, test_organization):
        """Should get all organizations."""
        response = authenticated_client.get("/api/v1.1/organizations")

        assert response.status_code == status.HTTP_200_OK
        orgs = response.json()
        assert isinstance(orgs, list)
        assert len(orgs) >= 1
        assert any(org["id"] == str(test_organization.id) for org in orgs)

    async def test_get_organization_by_id(self, authenticated_client, test_organization):
        """Should get organization by ID."""
        response = authenticated_client.get(f"/api/v1.1/organizations/{test_organization.id}")

        assert response.status_code == status.HTTP_200_OK
        org = response.json()
        assert org["id"] == str(test_organization.id)
        assert org["name"] == test_organization.name
        assert org["slug"] == test_organization.slug

    async def test_get_current_organization(
        self, authenticated_client, test_organization, test_user, db_session
    ):
        """Should get current user's organization."""
        # Add user to organization
        from productivity_tracker.database.entities.organization import (
            user_organizations,
        )

        db_session.execute(
            user_organizations.insert().values(
                user_id=test_user.id, organization_id=test_organization.id
            )
        )
        db_session.commit()

        response = authenticated_client.get("/api/v1.1/organizations/current")

        assert response.status_code == status.HTTP_200_OK
        org = response.json()
        assert org["id"] == str(test_organization.id)

    async def test_get_organization_not_found(self, authenticated_client):
        """Should return 404 for non-existent organization."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.get(f"/api/v1.1/organizations/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrganizationUpdate:
    """Test organization update endpoints."""

    async def test_update_organization_success(self, authenticated_client, test_organization):
        """Should update organization successfully."""
        data = {
            "name": "Updated Organization",
            "description": "Updated description",
        }

        response = authenticated_client.put(
            f"/api/v1.1/organizations/{test_organization.id}", json=data
        )

        assert response.status_code == status.HTTP_200_OK
        org = response.json()
        assert org["name"] == data["name"]
        assert org["description"] == data["description"]
        assert org["slug"] == test_organization.slug  # Slug unchanged

    async def test_update_organization_not_found(self, authenticated_client):
        """Should return 404 for non-existent organization."""
        from uuid import uuid4

        fake_id = uuid4()
        data = {"name": "Updated"}

        response = authenticated_client.put(f"/api/v1.1/organizations/{fake_id}", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrganizationDeletion:
    """Test organization deletion endpoints."""

    async def test_delete_organization_success(self, authenticated_client, test_organization):
        """Should soft delete organization successfully."""
        response = authenticated_client.delete(f"/api/v1.1/organizations/{test_organization.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_organization_not_found(self, authenticated_client):
        """Should return 404 for non-existent organization."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.delete(f"/api/v1.1/organizations/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrganizationMembers:
    """Test organization member management endpoints."""

    async def test_add_member_to_organization(
        self, authenticated_client, test_organization, db_session
    ):
        """Should add member to organization."""
        # Create a user to add
        from productivity_tracker.core.security import hash_password
        from productivity_tracker.database.entities.user import User

        new_user = User(
            username="newmember",
            email="newmember@example.com",
            hashed_password=hash_password("password123"),
            first_name="New",
            last_name="Member",
        )
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)

        response = authenticated_client.post(
            f"/api/v1.1/organizations/{test_organization.id}/members/{new_user.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        org = response.json()
        assert org["id"] == str(test_organization.id)

    async def test_remove_member_from_organization(
        self, authenticated_client, test_organization, test_user, db_session
    ):
        """Should remove member from organization."""
        # Add user first
        from productivity_tracker.database.entities.organization import (
            user_organizations,
        )

        db_session.execute(
            user_organizations.insert().values(
                user_id=test_user.id, organization_id=test_organization.id
            )
        )
        db_session.commit()

        response = authenticated_client.delete(
            f"/api/v1.1/organizations/{test_organization.id}/members/{test_user.id}"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_organization_members(
        self, authenticated_client, test_organization, test_user, db_session
    ):
        """Should get all organization members."""
        # Add user to organization
        from productivity_tracker.database.entities.organization import (
            user_organizations,
        )

        db_session.execute(
            user_organizations.insert().values(
                user_id=test_user.id, organization_id=test_organization.id
            )
        )
        db_session.commit()

        response = authenticated_client.get(
            f"/api/v1.1/organizations/{test_organization.id}/members"
        )

        assert response.status_code == status.HTTP_200_OK
        members = response.json()
        assert isinstance(members, list)
        assert len(members) >= 1
        assert any(member["id"] == str(test_user.id) for member in members)
