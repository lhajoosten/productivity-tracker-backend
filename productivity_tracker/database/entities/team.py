from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from productivity_tracker.database.entities.base import BaseEntity

# Association table for many-to-many relationship between users and teams
user_teams = Table(
    "user_teams",
    BaseEntity.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("team_id", ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
)


class Team(BaseEntity):
    """Team model for organizing users within departments."""

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Foreign key to department
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Foreign key to team lead (optional)
    lead_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    department = relationship("Department", back_populates="teams")
    lead = relationship("User", foreign_keys=[lead_id], lazy="selectin")
    members = relationship(
        "User",
        secondary="user_teams",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"
