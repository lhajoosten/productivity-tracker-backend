"""
Feature Flag Database Entity

Stores feature flags and their enabled/disabled state per version.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from productivity_tracker.core.database import Base

if TYPE_CHECKING:
    from productivity_tracker.database.entities.version import Version


class FeatureFlag(Base):
    """
    Feature flag entity.

    Stores which features are enabled for which versions.
    Features are cumulative - each version inherits features from previous versions.
    """

    __tablename__ = "feature_flags"

    # Primary identification
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Feature identification
    feature_key: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Feature enum key (e.g., 'TIME_TRACKING')"
    )
    feature_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Human-readable feature name"
    )

    # Version relationship
    version_id: Mapped[int] = mapped_column(
        ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped["Version"] = relationship("Version", back_populates="feature_flags")

    # Feature state
    enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Whether the feature is enabled"
    )

    # Feature metadata
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Feature category (foundation, security, productivity, etc.)",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Feature description"
    )

    # Environment overrides (JSON field in future)
    override_dev: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Override for development environment"
    )
    override_staging: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Override for staging environment"
    )
    override_prod: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="Override for production environment"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Constraints
    __table_args__ = (UniqueConstraint("version_id", "feature_key", name="uq_version_feature"),)

    def __repr__(self) -> str:
        return f"<FeatureFlag(feature='{self.feature_key}', version='{self.version.version}', enabled={self.enabled})>"

    def is_enabled_for_env(self, environment: str = "production") -> bool:
        """
        Check if feature is enabled for a specific environment.

        Args:
            environment: Environment name (development, staging, production)

        Returns:
            Whether the feature is enabled for that environment
        """
        # Check environment-specific override
        if environment == "development" and self.override_dev is not None:
            return self.override_dev
        if environment == "staging" and self.override_staging is not None:
            return self.override_staging
        if environment == "production" and self.override_prod is not None:
            return self.override_prod

        # Fall back to default enabled state
        return self.enabled

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "feature_key": self.feature_key,
            "feature_name": self.feature_name,
            "version_id": self.version_id,
            "enabled": self.enabled,
            "category": self.category,
            "description": self.description,
            "overrides": {
                "development": self.override_dev,
                "staging": self.override_staging,
                "production": self.override_prod,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
