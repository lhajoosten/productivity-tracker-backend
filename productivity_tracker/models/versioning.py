"""
Versioning Response Models

Pydantic models for versioning API responses.
These ensure proper OpenAPI schema generation and type safety.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


# ==============================================================================
# VERSION MODELS
# ==============================================================================

class VersionResponse(BaseModel):
    """Version data response model."""

    id: int = Field(..., description="Version ID")
    version: str = Field(..., description="Version string (e.g., '0.1.0-beta')")
    major: int = Field(..., description="Major version number")
    minor: int = Field(..., description="Minor version number")
    patch: int = Field(..., description="Patch version number")
    prerelease: str | None = Field(None, description="Prerelease identifier (e.g., 'beta', 'rc.1')")

    name: str = Field(..., description="Version name/title")
    status: str = Field(..., description="Version status (active, beta, planned, etc.)")
    api_prefix: str = Field(..., description="API prefix (e.g., '/api/v0.1')")

    release_date: date | None = Field(None, description="Release date")
    eol_date: date | None = Field(None, description="End-of-life date")

    breaking: bool = Field(..., description="Whether this version has breaking changes")
    notes: str | None = Field(None, description="Release notes or additional information")

    is_active: bool = Field(..., description="Whether this is the active version")
    is_supported: bool = Field(..., description="Whether this version is currently supported")
    is_deprecated: bool = Field(..., description="Whether this version is deprecated")
    is_eol: bool = Field(..., description="Whether this version has reached end-of-life")

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class VersionListResponse(BaseModel):
    """List of versions response."""

    versions: list[VersionResponse] = Field(..., description="List of versions")
    total: int = Field(..., description="Total number of versions")

class CreateVersionRequest(BaseModel):
    version: str
    name: str
    status: str
    api_prefix: str
    breaking: bool = False
    notes: str | None = None
    release_date: str | None = None

# ==============================================================================
# FEATURE FLAG MODELS
# ==============================================================================

class FeatureFlagResponse(BaseModel):
    """Feature flag data response model."""

    id: int = Field(..., description="Feature flag ID")
    feature_key: str = Field(..., description="Feature key (uppercase identifier)")
    feature_name: str = Field(..., description="Human-readable feature name")
    version_id: int = Field(..., description="Associated version ID")

    enabled: bool = Field(..., description="Whether feature is enabled by default")
    category: str | None = Field(None, description="Feature category")
    description: str | None = Field(None, description="Feature description")

    overrides: dict[str, bool] = Field(
        default_factory=dict,
        description="Environment-specific overrides (development, staging, production)"
    )
    enabled_for_env: bool | None = Field(
        None,
        description="Whether feature is enabled for the requested environment"
    )

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class FeatureFlagListResponse(BaseModel):
    """List of feature flags response."""

    features: list[FeatureFlagResponse] = Field(..., description="List of feature flags")
    total: int = Field(..., description="Total number of features")
    version: str = Field(..., description="Version these features belong to")


class FeatureStatusResponse(BaseModel):
    """Feature status check response."""

    feature_key: str = Field(..., description="Feature key")
    exists: bool = Field(..., description="Whether the feature exists")
    enabled: bool = Field(..., description="Whether feature is enabled by default")
    enabled_for_env: bool = Field(..., description="Whether feature is enabled for environment")
    version: str = Field(..., description="Version the feature belongs to")
    category: str | None = Field(None, description="Feature category")

class AddFeatureRequest(BaseModel):
    feature_key: str
    feature_name: str
    category: str = "core"
    enabled: bool = True
    description: str | None = None

# ==============================================================================
# HEALTH CHECK MODELS
# ==============================================================================

class VersioningHealthResponse(BaseModel):
    """Versioning system health check response."""

    status: str = Field(..., description="Overall health status")
    versions: dict[str, Any] = Field(
        ...,
        description="Version statistics",
        example={
            "total": 10,
            "supported": 5,
            "active": "0.1.0-beta"
        }
    )
    features: dict[str, int] = Field(
        ...,
        description="Feature statistics",
        example={
            "total": 150,
            "active_version": 25
        }
    )
    message: str = Field(..., description="Health status message")

