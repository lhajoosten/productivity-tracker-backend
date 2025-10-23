"""Repository for Organization entity."""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from productivity_tracker.database.entities.department import Department
from productivity_tracker.database.entities.organization import (
    Organization,
    user_organizations,
)
from productivity_tracker.database.entities.user import User
from productivity_tracker.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(Organization, db)

    def get_by_slug(self, slug: str, include_deleted: bool = False) -> Organization | None:
        """Get an organization by slug."""
        self.db.flush()
        query = self.db.query(self.model).filter(self.model.slug == slug)
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        result = query.first()
        return result if result is not None else None

    def get_with_stats(self, org_id: UUID) -> Organization | None:
        """Get organization with member and department counts."""
        org = self.get_by_id(org_id)
        return org

    def add_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Add a user to an organization."""
        org = self.get_by_id(org_id)
        user = self.db.query(User).filter(User.id == user_id).first()

        if not org or not user:
            return False

        # Check if user is already a member
        exists = (
            self.db.query(user_organizations)
            .filter(
                user_organizations.c.organization_id == org_id,
                user_organizations.c.user_id == user_id,
            )
            .first()
        )

        if exists:
            return True

        # Add the relationship
        self.db.execute(
            user_organizations.insert().values(
                organization_id=org_id,
                user_id=user_id,
            )
        )
        self.db.commit()
        return True

    def remove_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Remove a user from an organization."""
        result = self.db.execute(
            user_organizations.delete().where(
                user_organizations.c.organization_id == org_id,
                user_organizations.c.user_id == user_id,
            )
        )
        self.db.commit()
        return bool(result.rowcount > 0)

    def get_members(self, org_id: UUID, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all members of an organization."""
        return list(
            self.db.query(User)
            .join(user_organizations)
            .filter(user_organizations.c.organization_id == org_id)
            .filter(User.is_deleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_member_count(self, org_id: UUID) -> int:
        """Get the count of members in an organization."""
        return (
            self.db.query(func.count(user_organizations.c.user_id))
            .filter(user_organizations.c.organization_id == org_id)
            .scalar()
            or 0
        )

    def get_department_count(self, org_id: UUID) -> int:
        """Get the count of departments in an organization."""
        return (
            self.db.query(func.count(Department.id))
            .filter(Department.organization_id == org_id)
            .filter(Department.is_deleted == False)  # noqa: E712
            .scalar()
            or 0
        )
