"""Repository for Department entity."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from productivity_tracker.database.entities.department import Department
from productivity_tracker.database.entities.team import Team, user_teams
from productivity_tracker.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(Department, db)

    def get_by_organization(
        self, org_id: UUID, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> list[Department]:
        """Get all departments for a specific organization."""
        self.db.flush()
        query = self.db.query(self.model).filter(self.model.organization_id == org_id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return list(query.offset(skip).limit(limit).all())  # type: ignore[return-value]

    def get_team_count(self, dept_id: UUID) -> int:
        """Get the count of teams in a department."""
        result = (
            self.db.query(func.count(Team.id))
            .filter(Team.department_id == dept_id)
            .filter(Team.is_deleted == False)  # noqa: E712
            .scalar()
        )
        return int(result or 0)

    def get_member_count(self, dept_id: UUID) -> int:
        """Get the count of unique members across all teams in a department."""
        return (
            self.db.query(func.count(func.distinct(user_teams.c.user_id)))
            .join(Team, user_teams.c.team_id == Team.id)  # type: ignore[arg-type]
            .filter(Team.department_id == dept_id)
            .filter(Team.is_deleted == False)  # noqa: E712
            .scalar()
            or 0
        )

    def count_by_organization(self, org_id: UUID, include_deleted: bool = False) -> int:
        """Count departments in an organization."""
        self.db.flush()
        query = self.db.query(self.model).filter(self.model.organization_id == org_id)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return query.count()  # type: ignore[no-any-return]
