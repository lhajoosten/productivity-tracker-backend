"""Service for team management."""

from uuid import UUID

from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import ResourceNotFoundError
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.database.entities.team import Team
from productivity_tracker.models.organization import TeamCreate, TeamUpdate
from productivity_tracker.repositories.department_repository import DepartmentRepository
from productivity_tracker.repositories.team_repository import TeamRepository
from productivity_tracker.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class TeamService:
    """Service for team-related business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TeamRepository(db)
        self.dept_repository = DepartmentRepository(db)
        self.user_repository = UserRepository(db)

    def create_team(self, team_data: TeamCreate) -> Team:
        """Create a new team."""
        logger.info(f"Creating new team: {team_data.name}")

        # Verify department exists
        dept = self.dept_repository.get_by_id(team_data.department_id)
        if not dept:
            raise ResourceNotFoundError(
                resource_type="Department",
                resource_id=str(team_data.department_id),
            )

        # Verify lead exists if provided
        if team_data.lead_id:
            lead = self.user_repository.get_by_id(team_data.lead_id)
            if not lead:
                raise ResourceNotFoundError(
                    resource_type="User",
                    resource_id=str(team_data.lead_id),
                )

        new_team = Team(
            name=team_data.name,
            description=team_data.description,
            department_id=team_data.department_id,
            lead_id=team_data.lead_id,
        )

        created_team = self.repository.create(new_team)
        logger.info(f"Team created successfully: {created_team.name} (ID: {created_team.id})")
        return created_team

    def get_team(self, team_id: UUID) -> Team:
        """Get team by ID."""
        team = self.repository.get_by_id(team_id)
        if not team:
            raise ResourceNotFoundError(resource_type="Team", resource_id=str(team_id))
        return team

    def get_all_teams(self, skip: int = 0, limit: int = 100) -> list[Team]:
        """Get all teams."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_teams_by_department(self, dept_id: UUID, skip: int = 0, limit: int = 100) -> list[Team]:
        """Get all teams for a specific department."""
        # Verify department exists
        dept = self.dept_repository.get_by_id(dept_id)
        if not dept:
            raise ResourceNotFoundError(resource_type="Department", resource_id=str(dept_id))

        return self.repository.get_by_department(dept_id, skip=skip, limit=limit)

    def update_team(self, team_id: UUID, team_data: TeamUpdate) -> Team:
        """Update a team."""
        logger.info(f"Updating team: {team_id}")

        team = self.get_team(team_id)

        # If department is being changed, verify it exists
        if team_data.department_id and team_data.department_id != team.department_id:
            dept = self.dept_repository.get_by_id(team_data.department_id)
            if not dept:
                raise ResourceNotFoundError(
                    resource_type="Department",
                    resource_id=str(team_data.department_id),
                )

        # If lead is being changed, verify the user exists
        if team_data.lead_id and team_data.lead_id != team.lead_id:
            lead = self.user_repository.get_by_id(team_data.lead_id)
            if not lead:
                raise ResourceNotFoundError(
                    resource_type="User",
                    resource_id=str(team_data.lead_id),
                )

        # Update fields
        if team_data.name is not None:
            team.name = team_data.name
        if team_data.description is not None:
            team.description = team_data.description
        if team_data.department_id is not None:
            team.department_id = team_data.department_id
        if team_data.lead_id is not None:
            team.lead_id = team_data.lead_id

        updated_team = self.repository.update(team)
        logger.info(f"Team updated successfully: {updated_team.id}")
        return updated_team

    def delete_team(self, team_id: UUID, soft: bool = True) -> bool:
        """Delete a team."""
        logger.info(f"Deleting team: {team_id} (soft={soft})")

        # Verify team exists before attempting delete
        self.get_team(team_id)  # This will raise ResourceNotFoundError if not found

        result = self.repository.delete(team_id, soft=soft)
        if result:
            logger.info(f"Team deleted successfully: {team_id}")
        return result

    def add_member(self, team_id: UUID, user_id: UUID) -> bool:
        """Add a member to a team."""
        logger.info(f"Adding user {user_id} to team {team_id}")

        # Verify team exists
        self.get_team(team_id)

        # Verify user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))

        result = self.repository.add_member(team_id, user_id)
        if result:
            logger.info(f"User {user_id} added to team {team_id}")
        return result

    def remove_member(self, team_id: UUID, user_id: UUID) -> bool:
        """Remove a member from a team."""
        logger.info(f"Removing user {user_id} from team {team_id}")

        result = self.repository.remove_member(team_id, user_id)
        if result:
            logger.info(f"User {user_id} removed from team {team_id}")
        return result

    def get_members(self, team_id: UUID, skip: int = 0, limit: int = 100):
        """Get all members of a team."""
        # Verify team exists
        self.get_team(team_id)

        return self.repository.get_members(team_id, skip=skip, limit=limit)

    def set_lead(self, team_id: UUID, user_id: UUID | None) -> bool:
        """Set or update the team lead."""
        logger.info(f"Setting team lead for {team_id} to user {user_id}")

        # Verify team exists
        self.get_team(team_id)

        # Verify user exists if provided
        if user_id:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))

        result = self.repository.set_lead(team_id, user_id)
        if result:
            logger.info(f"Team lead set successfully for team {team_id}")
        return result
