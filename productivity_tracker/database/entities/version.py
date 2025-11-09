"""
Version and Feature Flag Database Entities

These entities store version information and feature flags in the database,
allowing both frontend and backend to query the single source of truth.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from productivity_tracker.core.database import Base

if TYPE_CHECKING:
    from productivity_tracker.database.entities.feature_flag import FeatureFlag


class Version(Base):
    """
    Application version entity.

    Stores all version information including lifecycle status, release dates,
    and metadata. This serves as the source of truth for versioning across
    the entire application stack.
    """

    __tablename__ = "versions"

    # Primary identification
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Semantic version string (e.g., '0.1.0-beta')",
    )

    # Version components
    major: Mapped[int] = mapped_column(nullable=False, comment="Major version number")
    minor: Mapped[int] = mapped_column(nullable=False, comment="Minor version number")
    patch: Mapped[int] = mapped_column(nullable=False, comment="Patch version number")
    prerelease: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Prerelease identifier (e.g., 'beta', 'rc.1')"
    )

    # Version metadata
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Human-readable version name"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Lifecycle status (planned, active, deprecated, etc.)",
    )
    api_prefix: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="API route prefix (e.g., '/api/v0.1')"
    )

    # Dates
    release_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Official release date"
    )
    eol_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="End-of-life date")

    # Flags and metadata
    breaking: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Whether this version has breaking changes"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Release notes or additional information"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    feature_flags: Mapped[list["FeatureFlag"]] = relationship(
        "FeatureFlag", back_populates="version", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("major", "minor", "patch", "prerelease", name="uq_version_components"),
    )

    def __repr__(self) -> str:
        return f"<Version(version='{self.version}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if this is the active version."""
        return self.status == "active"

    @property
    def is_supported(self) -> bool:
        """Check if this version is currently supported."""
        return self.status in ["active", "beta", "rc", "maintenance"]

    @property
    def is_deprecated(self) -> bool:
        """Check if this version is deprecated."""
        return self.status == "deprecated"

    @property
    def is_eol(self) -> bool:
        """Check if this version has reached end-of-life."""
        if self.status == "eol":
            return True
        if self.eol_date and datetime.now().date() >= self.eol_date:
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "version": self.version,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "prerelease": self.prerelease,
            "name": self.name,
            "status": self.status,
            "api_prefix": self.api_prefix,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "eol_date": self.eol_date.isoformat() if self.eol_date else None,
            "breaking": self.breaking,
            "notes": self.notes,
            "is_active": self.is_active,
            "is_supported": self.is_supported,
            "is_deprecated": self.is_deprecated,
            "is_eol": self.is_eol,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
