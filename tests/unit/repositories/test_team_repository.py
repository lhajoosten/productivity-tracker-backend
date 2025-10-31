"""Unit tests for team repository."""

from uuid import uuid4

import pytest

from productivity_tracker.database.entities.department import Department
from productivity_tracker.database.entities.organization import Organization
from productivity_tracker.database.entities.team import Team
from productivity_tracker.repositories.team_repository import TeamRepository

pytestmark = [pytest.mark.unit]


class TestTeamRepository:
    """Test team repository methods."""

    def test_get_by_department(self, db_session_unit):
        """Should get teams by department."""
        repo = TeamRepository(db_session_unit)

        # Create org and department
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        # Create teams
        team1 = Team(name="Team A", department_id=dept.id)
        team2 = Team(name="Team B", department_id=dept.id)
        repo.create(team1)
        repo.create(team2)

        # Get teams by department
        teams = repo.get_by_department(dept.id)

        assert len(teams) >= 2
        team_names = [t.name for t in teams]
        assert "Team A" in team_names
        assert "Team B" in team_names

    def test_add_member(self, db_session_unit, sample_user):
        """Should add member to team."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Add member
        result = repo.add_member(created_team.id, sample_user.id)

        assert result is True

        # Verify member was added
        members = repo.get_members(created_team.id)
        assert len(members) == 1
        assert members[0].id == sample_user.id

    def test_add_member_duplicate(self, db_session_unit, sample_user):
        """Should handle adding duplicate member."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Add member twice
        repo.add_member(created_team.id, sample_user.id)
        result = repo.add_member(created_team.id, sample_user.id)

        assert result is True

        # Should still have only one member
        members = repo.get_members(created_team.id)
        assert len(members) == 1

    def test_add_member_invalid_team(self, db_session_unit, sample_user):
        """Should return False for invalid team."""
        repo = TeamRepository(db_session_unit)

        result = repo.add_member(uuid4(), sample_user.id)

        assert result is False

    def test_add_member_invalid_user(self, db_session_unit):
        """Should return False for invalid user."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        result = repo.add_member(created_team.id, uuid4())

        assert result is False

    def test_remove_member(self, db_session_unit, sample_user):
        """Should remove member from team."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Add and then remove member
        repo.add_member(created_team.id, sample_user.id)
        result = repo.remove_member(created_team.id, sample_user.id)

        assert result is True

        # Verify member was removed
        members = repo.get_members(created_team.id)
        assert len(members) == 0

    def test_remove_member_not_in_team(self, db_session_unit, sample_user):
        """Should return False when removing member not in team."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Try to remove member that was never added
        result = repo.remove_member(created_team.id, sample_user.id)

        assert result is False

    def test_get_member_count(self, db_session_unit, sample_user):
        """Should get correct member count."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Add members
        repo.add_member(created_team.id, sample_user.id)

        count = repo.get_member_count(created_team.id)

        assert count == 1

    def test_count_by_department(self, db_session_unit):
        """Should count teams in department."""
        repo = TeamRepository(db_session_unit)

        # Create org and department
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        # Create teams
        team1 = Team(name="Team A", department_id=dept.id)
        team2 = Team(name="Team B", department_id=dept.id)
        repo.create(team1)
        repo.create(team2)

        count = repo.count_by_department(dept.id)

        assert count == 2

    def test_set_lead(self, db_session_unit, sample_user):
        """Should set team lead."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        # Set lead
        result = repo.set_lead(created_team.id, sample_user.id)

        assert result is True

        # Verify lead was set
        updated_team = repo.get_by_id(created_team.id)
        assert updated_team.lead_id == sample_user.id

    def test_set_lead_to_none(self, db_session_unit, sample_user):
        """Should remove team lead."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team with lead
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id, lead_id=sample_user.id)
        created_team = repo.create(team)

        # Remove lead
        result = repo.set_lead(created_team.id, None)

        assert result is True

        # Verify lead was removed
        updated_team = repo.get_by_id(created_team.id)
        assert updated_team.lead_id is None

    def test_set_lead_invalid_team(self, db_session_unit, sample_user):
        """Should return False for invalid team."""
        repo = TeamRepository(db_session_unit)

        result = repo.set_lead(uuid4(), sample_user.id)

        assert result is False

    def test_set_lead_invalid_user(self, db_session_unit):
        """Should return False for invalid user."""
        repo = TeamRepository(db_session_unit)

        # Create org, department, and team
        org = Organization(name="Test Org", slug=f"test-org-{uuid4().hex[:8]}")
        db_session_unit.add(org)
        db_session_unit.commit()
        db_session_unit.refresh(org)

        dept = Department(name="Engineering", organization_id=org.id)
        db_session_unit.add(dept)
        db_session_unit.commit()
        db_session_unit.refresh(dept)

        team = Team(name="Dev Team", department_id=dept.id)
        created_team = repo.create(team)

        result = repo.set_lead(created_team.id, uuid4())

        assert result is False
