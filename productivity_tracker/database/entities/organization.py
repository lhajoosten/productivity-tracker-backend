from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from productivity_tracker.database.entities.base import BaseEntity

# Association table for many-to-many relationship between users and organizations
user_organizations = Table(
    "user_organizations",
    BaseEntity.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(BaseEntity):
    """Organization model for multi-tenancy and organizational structure."""

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    departments = relationship(
        "Department",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    members = relationship(
        "User",
        secondary="user_organizations",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"
