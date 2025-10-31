"""Repository for Team entity."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from productivity_tracker.database.entities.team import Team, user_teams
from productivity_tracker.database.entities.user import User
from productivity_tracker.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """Repository for Team CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(Team, db)

    def get_by_department(
        self, dept_id: UUID, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Team]:
        """Get all teams for a specific department."""
        self.db.flush()
        query = self.db.query(self.model).filter(self.model.department_id == dept_id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return list(query.offset(skip).limit(limit).all())  # type: ignore[return-value]

    def add_member(self, team_id: UUID, user_id: UUID) -> bool:
        """Add a user to a team."""
        team = self.get_by_id(team_id)
        user = self.db.query(User).filter(User.id == user_id).first()

        if not team or not user:
            return False

        # Check if user is already a member
        exists = (
            self.db.query(user_teams)
            .filter(
                user_teams.c.team_id == team_id,  # type: ignore[arg-type]
                user_teams.c.user_id == user_id,  # type: ignore[arg-type]
            )
            .first()
        )

        if exists:
            return True

        # Add the relationship
        self.db.execute(
            user_teams.insert().values(
                team_id=team_id,
                user_id=user_id,
            )
        )
        self.db.commit()
        return True

    def remove_member(self, team_id: UUID, user_id: UUID) -> bool:
        """Remove a user from a team."""
        result = self.db.execute(
            user_teams.delete().where(
                user_teams.c.team_id == team_id,
                user_teams.c.user_id == user_id,
            )
        )
        self.db.commit()
        return bool(result.rowcount and result.rowcount > 0)  # type: ignore[attr-defined]

    def get_members(self, team_id: UUID, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all members of a team."""
        return list(
            self.db.query(User)
            .join(user_teams)
            .filter(user_teams.c.team_id == team_id)  # type: ignore[arg-type]
            .filter(User.is_deleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )  # type: ignore[return-value]

    def get_member_count(self, team_id: UUID) -> int:
        """Get the count of members in a team."""
        return (
            self.db.query(func.count(user_teams.c.user_id))
            .filter(user_teams.c.team_id == team_id)  # type: ignore[arg-type]
            .scalar()
            or 0
        )

    def count_by_department(self, dept_id: UUID, include_deleted: bool = False) -> int:
        """Count teams in a department."""
        self.db.flush()
        query = self.db.query(self.model).filter(self.model.department_id == dept_id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return query.count()  # type: ignore[no-any-return]

    def set_lead(self, team_id: UUID, user_id: UUID | None) -> bool:
        """Set or update the team lead."""
        team = self.get_by_id(team_id)
        if not team:
            return False

        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

        team.lead_id = user_id
        self.db.commit()
        self.db.refresh(team)
        return True
