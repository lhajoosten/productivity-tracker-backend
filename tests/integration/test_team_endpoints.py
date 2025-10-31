"""Integration tests for team endpoints."""

import pytest
from fastapi import status

from tests.utilities import assert_problem_detail_response

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestTeamCreation:
    """Test team creation endpoints."""

    async def test_create_team_success(self, authenticated_client, test_department):
        """Should create team successfully."""
        data = {
            "name": "Backend Team",
            "department_id": str(test_department.id),
            "description": "Backend development team",
        }

        response = authenticated_client.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        team = response.json()
        assert team["name"] == data["name"]
        assert team["department_id"] == data["department_id"]
        assert team["description"] == data["description"]
        assert "id" in team
        assert "created_at" in team

    async def test_create_team_with_lead(self, authenticated_client, test_department, test_user):
        """Should create team with lead."""
        data = {
            "name": "Frontend Team",
            "department_id": str(test_department.id),
            "lead_id": str(test_user.id),
        }

        response = authenticated_client.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_201_CREATED
        team = response.json()
        assert team["name"] == data["name"]
        assert team["lead_id"] == data["lead_id"]

    async def test_create_team_invalid_department(self, authenticated_client):
        """Should reject invalid department ID."""
        from uuid import uuid4

        data = {
            "name": "Test Team",
            "department_id": str(uuid4()),
        }

        response = authenticated_client.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert_problem_detail_response(
            response.json(), "resource-not-found", status.HTTP_404_NOT_FOUND
        )

    async def test_create_team_invalid_lead(self, authenticated_client, test_department):
        """Should reject invalid lead ID."""
        from uuid import uuid4

        data = {
            "name": "Test Team",
            "department_id": str(test_department.id),
            "lead_id": str(uuid4()),
        }

        response = authenticated_client.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_team_missing_required_fields(self, authenticated_client):
        """Should reject missing required fields."""
        data = {"name": ""}  # Empty name

        response = authenticated_client.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_team_unauthorized(self, client_integration, test_department):
        """Should reject unauthorized request."""
        data = {
            "name": "Test Team",
            "department_id": str(test_department.id),
        }

        response = client_integration.post("/api/v1.0/teams", json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTeamRetrieval:
    """Test team retrieval endpoints."""

    async def test_get_all_teams(self, authenticated_client, test_team):
        """Should get all teams."""
        response = authenticated_client.get("/api/v1.0/teams")

        assert response.status_code == status.HTTP_200_OK
        teams = response.json()
        assert isinstance(teams, list)
        assert len(teams) >= 1
        assert any(team["id"] == str(test_team.id) for team in teams)

    async def test_get_team_by_id(self, authenticated_client, test_team):
        """Should get team by ID."""
        response = authenticated_client.get(f"/api/v1.0/teams/{test_team.id}")

        assert response.status_code == status.HTTP_200_OK
        team = response.json()
        assert team["id"] == str(test_team.id)
        assert team["name"] == test_team.name
        assert team["department_id"] == str(test_team.department_id)

    async def test_get_teams_by_department(self, authenticated_client, test_department, test_team):
        """Should get teams by department."""
        response = authenticated_client.get(f"/api/v1.0/departments/{test_department.id}/teams")

        assert response.status_code == status.HTTP_200_OK
        teams = response.json()
        assert isinstance(teams, list)
        assert len(teams) >= 1
        assert all(team["department_id"] == str(test_department.id) for team in teams)

    async def test_get_team_not_found(self, authenticated_client):
        """Should return 404 for non-existent team."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.get(f"/api/v1.0/teams/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert_problem_detail_response(
            response.json(), "resource-not-found", status.HTTP_404_NOT_FOUND
        )


class TestTeamUpdate:
    """Test team update endpoints."""

    async def test_update_team_success(self, authenticated_client, test_team):
        """Should update team successfully."""
        data = {
            "name": "Updated Team",
            "description": "Updated description",
        }

        response = authenticated_client.put(f"/api/v1.0/teams/{test_team.id}", json=data)

        assert response.status_code == status.HTTP_200_OK
        team = response.json()
        assert team["name"] == data["name"]
        assert team["description"] == data["description"]

    async def test_update_team_lead(self, authenticated_client, test_team, test_user):
        """Should update team lead."""
        data = {"lead_id": str(test_user.id)}

        response = authenticated_client.put(f"/api/v1.0/teams/{test_team.id}", json=data)

        assert response.status_code == status.HTTP_200_OK
        team = response.json()
        assert team["lead_id"] == data["lead_id"]

    async def test_update_team_not_found(self, authenticated_client):
        """Should return 404 for non-existent team."""
        from uuid import uuid4

        fake_id = uuid4()
        data = {"name": "Updated"}

        response = authenticated_client.put(f"/api/v1.0/teams/{fake_id}", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTeamDeletion:
    """Test team deletion endpoints."""

    async def test_delete_team_success(self, authenticated_client, test_team):
        """Should soft delete team successfully."""
        response = authenticated_client.delete(f"/api/v1.0/teams/{test_team.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_team_not_found(self, authenticated_client):
        """Should return 404 for non-existent team."""
        from uuid import uuid4

        fake_id = uuid4()
        response = authenticated_client.delete(f"/api/v1.0/teams/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTeamMembers:
    """Test team member management endpoints."""

    async def test_add_member_to_team(self, authenticated_client, test_team, test_user):
        """Should add member to team."""
        data = {"user_id": str(test_user.id)}

        response = authenticated_client.post(f"/api/v1.0/teams/{test_team.id}/members", json=data)

        assert response.status_code == status.HTTP_200_OK
        team = response.json()
        assert team["id"] == str(test_team.id)

    async def test_add_member_invalid_user(self, authenticated_client, test_team):
        """Should reject invalid user ID."""
        from uuid import uuid4

        data = {"user_id": str(uuid4())}

        response = authenticated_client.post(f"/api/v1.0/teams/{test_team.id}/members", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_member_to_invalid_team(self, authenticated_client, test_user):
        """Should reject invalid team ID."""
        from uuid import uuid4

        fake_id = uuid4()
        data = {"user_id": str(test_user.id)}

        response = authenticated_client.post(f"/api/v1.0/teams/{fake_id}/members", json=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_remove_member_from_team(
        self, authenticated_client, test_team, test_user, db_session
    ):
        """Should remove member from team."""
        # Add user first
        from productivity_tracker.database.entities.team import user_teams

        db_session.execute(user_teams.insert().values(user_id=test_user.id, team_id=test_team.id))
        db_session.commit()

        response = authenticated_client.delete(
            f"/api/v1.0/teams/{test_team.id}/members/{test_user.id}"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_team_members(self, authenticated_client, test_team, test_user, db_session):
        """Should get all team members."""
        # Add user to team
        from productivity_tracker.database.entities.team import user_teams

        db_session.execute(user_teams.insert().values(user_id=test_user.id, team_id=test_team.id))
        db_session.commit()

        response = authenticated_client.get(f"/api/v1.0/teams/{test_team.id}/members")

        assert response.status_code == status.HTTP_200_OK
        members = response.json()
        assert isinstance(members, list)
        assert len(members) >= 1
        assert any(member["id"] == str(test_user.id) for member in members)

    async def test_add_duplicate_member(
        self, authenticated_client, test_team, test_user, db_session
    ):
        """Should handle adding duplicate member gracefully."""
        # Add user first time
        from productivity_tracker.database.entities.team import user_teams

        db_session.execute(user_teams.insert().values(user_id=test_user.id, team_id=test_team.id))
        db_session.commit()

        # Try to add again
        data = {"user_id": str(test_user.id)}

        response = authenticated_client.post(f"/api/v1.0/teams/{test_team.id}/members", json=data)

        # Should succeed (idempotent) or return appropriate status
        # 200 means it succeeded (or was already a member), 400 means duplicate
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]
