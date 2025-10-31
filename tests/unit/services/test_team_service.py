"""Unit tests for team service."""

from uuid import uuid4

import pytest

from productivity_tracker.core.exceptions import ResourceNotFoundError
from productivity_tracker.database.entities.department import Department
from productivity_tracker.database.entities.organization import Organization
from productivity_tracker.database.entities.team import Team
from productivity_tracker.models.organization import TeamCreate, TeamUpdate
from productivity_tracker.repositories.department_repository import DepartmentRepository
from productivity_tracker.repositories.organization_repository import (
    OrganizationRepository,
)
from productivity_tracker.repositories.team_repository import TeamRepository
from productivity_tracker.services.team_service import TeamService

pytestmark = [pytest.mark.unit]


class TestTeamServiceCreate:
    """Test team creation in service layer."""

    def test_create_team_success(self, db_session_unit):
        """Should create team successfully."""
        # Create org and dept first
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 1", slug="test-org-team-1")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Create team
        service = TeamService(db_session_unit)
        team_data = TeamCreate(
            name="Backend Team",
            department_id=created_dept.id,
            description="Backend development team",
        )

        team = service.create_team(team_data)

        assert team.name == team_data.name
        assert team.department_id == team_data.department_id
        assert team.description == team_data.description
        assert team.id is not None

    def test_create_team_with_lead(self, db_session_unit, sample_user):
        """Should create team with lead."""
        # Create org and dept
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 2", slug="test-org-team-2")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Create team
        service = TeamService(db_session_unit)
        team_data = TeamCreate(
            name="Frontend Team",
            department_id=created_dept.id,
            lead_id=sample_user.id,
        )

        team = service.create_team(team_data)

        assert team.name == team_data.name
        assert team.lead_id == sample_user.id

    def test_create_team_minimal_data(self, db_session_unit):
        """Should create team with minimal data."""
        # Create org and dept
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 3", slug="test-org-team-3")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        # Create team
        service = TeamService(db_session_unit)
        team_data = TeamCreate(name="Test Team", department_id=created_dept.id)

        team = service.create_team(team_data)

        assert team.name == team_data.name
        assert team.description is None
        assert team.lead_id is None

    def test_create_team_invalid_department(self, db_session_unit):
        """Should raise ResourceNotFoundError for invalid department."""
        service = TeamService(db_session_unit)
        team_data = TeamCreate(name="Test Team", department_id=uuid4())

        with pytest.raises(ResourceNotFoundError):
            service.create_team(team_data)


class TestTeamServiceRead:
    """Test team retrieval in service layer."""

    def test_get_team_by_id(self, db_session_unit):
        """Should get team by ID."""
        # Create org, dept, and team
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 4", slug="test-org-team-4")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="Backend Team", department_id=created_dept.id)
        created_team = team_repo.create(team)

        # Get via service
        service = TeamService(db_session_unit)
        retrieved = service.get_team(created_team.id)

        assert retrieved.id == created_team.id
        assert retrieved.name == created_team.name

    def test_get_team_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent team."""
        service = TeamService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.get_team(uuid4())

    def test_get_all_teams(self, db_session_unit):
        """Should get all teams."""
        # Create org, dept, and teams
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 5", slug="test-org-team-5")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team1 = Team(name="Backend Team", department_id=created_dept.id)
        team2 = Team(name="Frontend Team", department_id=created_dept.id)
        team_repo.create(team1)
        team_repo.create(team2)

        # Get all via service
        service = TeamService(db_session_unit)
        teams = service.get_all_teams()

        assert len(teams) >= 2
        assert any(t.name == "Backend Team" for t in teams)
        assert any(t.name == "Frontend Team" for t in teams)

    def test_get_teams_by_department(self, db_session_unit):
        """Should get teams by department."""
        # Create orgs, depts, and teams
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 6", slug="test-org-team-6")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept1 = Department(name="Engineering", organization_id=created_org.id)
        dept2 = Department(name="Sales", organization_id=created_org.id)
        created_dept1 = dept_repo.create(dept1)
        created_dept2 = dept_repo.create(dept2)

        team_repo = TeamRepository(db_session_unit)
        team1 = Team(name="Backend Team", department_id=created_dept1.id)
        team2 = Team(name="Sales Team", department_id=created_dept2.id)
        team_repo.create(team1)
        team_repo.create(team2)

        # Get teams for dept1
        service = TeamService(db_session_unit)
        teams = service.get_teams_by_department(created_dept1.id)

        assert len(teams) >= 1
        assert all(t.department_id == created_dept1.id for t in teams)


class TestTeamServiceUpdate:
    """Test team update in service layer."""

    def test_update_team_success(self, db_session_unit):
        """Should update team successfully."""
        # Create org, dept, and team
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 7", slug="test-org-team-7")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="Original", department_id=created_dept.id)
        created_team = team_repo.create(team)

        # Update via service
        service = TeamService(db_session_unit)
        update_data = TeamUpdate(name="Updated Team", description="New description")
        updated = service.update_team(created_team.id, update_data)

        assert updated.name == "Updated Team"
        assert updated.description == "New description"

    def test_update_team_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent team."""
        service = TeamService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.update_team(uuid4(), TeamUpdate(name="Updated"))


class TestTeamServiceDelete:
    """Test team deletion in service layer."""

    def test_delete_team_success(self, db_session_unit):
        """Should soft delete team successfully."""
        # Create org, dept, and team
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 8", slug="test-org-team-8")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="To Delete", department_id=created_dept.id)
        created_team = team_repo.create(team)

        # Delete via service
        service = TeamService(db_session_unit)
        service.delete_team(created_team.id)

        # Verify soft deleted
        deleted_team = team_repo.get_by_id(created_team.id, include_deleted=True)
        assert deleted_team.is_deleted is True

    def test_delete_team_not_found(self, db_session_unit):
        """Should raise ResourceNotFoundError for non-existent team."""
        service = TeamService(db_session_unit)

        with pytest.raises(ResourceNotFoundError):
            service.delete_team(uuid4())


class TestTeamServiceMembers:
    """Test team member management in service layer."""

    def test_add_member_to_team(self, db_session_unit, sample_user):
        """Should add member to team."""
        # Create org, dept, and team
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 9", slug="test-org-team-9")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="Test Team", department_id=created_dept.id)
        created_team = team_repo.create(team)

        # Add member via service
        service = TeamService(db_session_unit)
        result = service.add_member(created_team.id, sample_user.id)

        assert result is True

        # Verify member was added
        members = team_repo.get_members(created_team.id)
        assert any(m.id == sample_user.id for m in members)

    def test_remove_member_from_team(self, db_session_unit, sample_user):
        """Should remove member from team."""
        # Create org, dept, team, and add member
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 10", slug="test-org-team-10")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="Test Team", department_id=created_dept.id)
        created_team = team_repo.create(team)
        team_repo.add_member(created_team.id, sample_user.id)

        # Remove member via service
        service = TeamService(db_session_unit)
        service.remove_member(created_team.id, sample_user.id)

        # Verify member was removed
        members = team_repo.get_members(created_team.id)
        assert not any(m.id == sample_user.id for m in members)

    def test_get_team_members(self, db_session_unit, sample_user):
        """Should get all team members."""
        # Create org, dept, team, and add member
        org_repo = OrganizationRepository(db_session_unit)
        org = Organization(name="Test Org Team 11", slug="test-org-team-11")
        created_org = org_repo.create(org)

        dept_repo = DepartmentRepository(db_session_unit)
        dept = Department(name="Engineering", organization_id=created_org.id)
        created_dept = dept_repo.create(dept)

        team_repo = TeamRepository(db_session_unit)
        team = Team(name="Test Team", department_id=created_dept.id)
        created_team = team_repo.create(team)
        team_repo.add_member(created_team.id, sample_user.id)

        # Get members via service
        service = TeamService(db_session_unit)
        members = service.get_members(created_team.id)

        assert len(members) >= 1
        assert any(m.id == sample_user.id for m in members)
