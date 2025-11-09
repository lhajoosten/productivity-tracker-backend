"""
Versioning API Endpoints

Provides API endpoints for frontend to query version information
and feature flags from the database.
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from productivity_tracker.core.database import get_db
from productivity_tracker.database.entities.feature_flag import FeatureFlag
from productivity_tracker.database.entities.version import Version
from productivity_tracker.models.versioning import (
    FeatureFlagListResponse,
    FeatureFlagResponse,
    FeatureStatusResponse,
    VersionListResponse,
    VersionResponse,
    VersioningHealthResponse, CreateVersionRequest, AddFeatureRequest,
)

router = APIRouter()



# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/versions", response_model=VersionListResponse)
async def get_all_versions(
    status: str | None = Query(None, description="Filter by status"),
    supported_only: bool = Query(False, description="Only return supported versions"),
    db: Session = Depends(get_db),
) -> VersionListResponse:
    """
    Get all versions.

    Query params:
        - status: Filter by lifecycle status (active, planned, etc.)
        - supported_only: Only return currently supported versions
    """
    query = db.query(Version)

    # Apply filters
    if status:
        query = query.filter(Version.status == status)

    if supported_only:
        query = query.filter(Version.status.in_(["active", "beta", "rc", "maintenance"]))

    # Order by version (newest first)
    query = query.order_by(
        Version.major.desc(),
        Version.minor.desc(),
        Version.patch.desc(),
    )

    versions = query.all()
    return VersionListResponse(
        versions=[VersionResponse.from_orm(v) for v in versions],
        total=len(versions),
    )


@router.get("/versions/health", response_model=VersioningHealthResponse)
async def version_health_check(
    db: Session = Depends(get_db),
) -> VersioningHealthResponse:
    """
    Health check endpoint for versioning system.

    Returns information about the versioning system status.
    """
    # Count versions by status
    total_versions = db.query(Version).count()
    active_version = db.query(Version).filter(Version.status == "active").first()
    supported_versions = (
        db.query(Version)
        .filter(Version.status.in_(["active", "beta", "rc", "maintenance"]))
        .count()
    )

    # Count features
    total_features = db.query(FeatureFlag).count()
    if active_version:
        active_features = (
            db.query(FeatureFlag)
            .filter(
                FeatureFlag.version_id == active_version.id,
                FeatureFlag.enabled,
            )
            .count()
        )
    else:
        active_features = 0

    return VersioningHealthResponse(
        status="healthy" if active_version else "unhealthy",
        versions={
            "total": total_versions,
            "supported": supported_versions,
            "active": active_version.version if active_version else None,
        },
        features={
            "total": total_features,
            "active_version": active_features,
        },
        message="Versioning system operational" if active_version else "No active version found",
    )


@router.get("/versions/current", response_model=VersionResponse)
async def get_current_version(
    db: Session = Depends(get_db),
) -> VersionResponse:
    """
    Get the current active version.

    This is the version that both frontend and backend should be using.
    """
    version = db.query(Version).filter(Version.status == "active").first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active version found. Please contact administrator.",
        )

    return VersionResponse.from_orm(version)


@router.get("/versions/current/features", response_model=FeatureFlagListResponse)
async def get_current_features(
    environment: str = Query("production", description="Environment (dev, staging, prod)"),
    category: str | None = Query(None, description="Filter by category"),
    enabled_only: bool = Query(True, description="Only return enabled features"),
    db: Session = Depends(get_db),
) -> FeatureFlagListResponse:
    """
    Get feature flags for the current active version.

    This is the primary endpoint the frontend uses to determine
    which features are available.

    Query params:
        - environment: Environment name for environment-specific overrides
        - category: Filter by feature category
        - enabled_only: Only return enabled features
    """
    # Get current version
    version = db.query(Version).filter(Version.status == "active").first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active version found",
        )

    # Query feature flags
    query = db.query(FeatureFlag).filter(FeatureFlag.version_id == version.id)

    # Apply filters
    if category:
        query = query.filter(FeatureFlag.category == category)

    if enabled_only:
        query = query.filter(FeatureFlag.enabled)

    features = query.all()

    # Apply environment-specific filtering
    result = []
    for feature in features:
        if enabled_only and not feature.is_enabled_for_env(environment):
            continue

        feature_obj = FeatureFlagResponse.from_orm(feature)
        feature_obj.enabled_for_env = feature.is_enabled_for_env(environment)
        result.append(feature_obj)

    return FeatureFlagListResponse(
        features=result,
        total=len(result),
        version=version.version,
    )


@router.get("/versions/{version_string}", response_model=VersionResponse)
async def get_version(
    version_string: str,
    db: Session = Depends(get_db),
) -> VersionResponse:
    """
    Get a specific version by version string.

    Args:
        version_string: Version string (e.g., "0.1.0-beta")
    """
    version = db.query(Version).filter(Version.version == version_string).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version_string}' not found",
        )

    return VersionResponse.from_orm(version)


@router.get("/versions/{version_string}/features", response_model=FeatureFlagListResponse)
async def get_version_features(
    version_string: str,
    environment: str = Query("production", description="Environment"),
    category: str | None = Query(None, description="Filter by category"),
    enabled_only: bool = Query(True, description="Only return enabled features"),
    db: Session = Depends(get_db),
) -> FeatureFlagListResponse:
    """
    Get feature flags for a specific version.

    Args:
        version_string: Version string (e.g., "0.1.0-beta")
    """
    # Get version
    version = db.query(Version).filter(Version.version == version_string).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version_string}' not found",
        )

    # Query feature flags
    query = db.query(FeatureFlag).filter(FeatureFlag.version_id == version.id)

    # Apply filters
    if category:
        query = query.filter(FeatureFlag.category == category)

    if enabled_only:
        query = query.filter(FeatureFlag.enabled)

    features = query.all()

    # Apply environment-specific filtering
    result = []
    for feature in features:
        if enabled_only and not feature.is_enabled_for_env(environment):
            continue

        feature_obj = FeatureFlagResponse.from_orm(feature)
        feature_obj.enabled_for_env = feature.is_enabled_for_env(environment)
        result.append(feature_obj)

    return FeatureFlagListResponse(
        features=result,
        total=len(result),
        version=version.version,
    )


@router.get("/versions/features/{feature_key}", response_model=FeatureStatusResponse)
async def get_feature_status(
    feature_key: str,
    version_string: str | None = Query(None, description="Version to check (defaults to current)"),
    environment: str = Query("production", description="Environment"),
    db: Session = Depends(get_db),
) -> FeatureStatusResponse:
    """
    Check if a specific feature is enabled.

    Args:
        feature_key: Feature key (e.g., "TIME_TRACKING")
        version_string: Optional version to check (defaults to current active)
        environment: Environment name
    """
    # Get version
    if version_string:
        version = db.query(Version).filter(Version.version == version_string).first()
    else:
        version = db.query(Version).filter(Version.status == "active").first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    # Get feature flag
    feature = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.version_id == version.id,
            FeatureFlag.feature_key == feature_key.upper(),
        )
        .first()
    )

    if not feature:
        # Feature doesn't exist in this version
        return FeatureStatusResponse(
            feature_key=feature_key.upper(),
            enabled=False,
            enabled_for_env=False,
            exists=False,
            version=version.version,
            category=None,
        )

    return FeatureStatusResponse(
        feature_key=feature.feature_key,
        enabled=feature.enabled,
        enabled_for_env=feature.is_enabled_for_env(environment),
        exists=True,
        version=version.version,
        category=feature.category,
    )


@router.post("/versions", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
        request: CreateVersionRequest,
        db: Session = Depends(get_db),
) -> VersionResponse:
    """Create a new version."""
    # Parse version string
    parts = request.version.split("-")
    version_nums = parts[0].split(".")

    version = Version(
        version=request.version,
        major=int(version_nums[0]),
        minor=int(version_nums[1]),
        patch=int(version_nums[2]),
        prerelease=parts[1] if len(parts) > 1 else None,
        name=request.name,
        status=request.status,
        api_prefix=request.api_prefix,
        breaking=request.breaking,
        notes=request.notes,
        release_date=datetime.fromisoformat(request.release_date).date() if request.release_date else None,
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    return VersionResponse.from_orm(version)


@router.post("/versions/{version_string}/features", response_model=FeatureFlagResponse,
             status_code=status.HTTP_201_CREATED)
async def add_feature_to_version(
        version_string: str,
        request: AddFeatureRequest,
        db: Session = Depends(get_db),
) -> FeatureFlagResponse:
    """Add a new feature to a version."""
    version = db.query(Version).filter(Version.version == version_string).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version_string}' not found",
        )

    # Check if feature already exists for this version
    existing = db.query(FeatureFlag).filter(
        FeatureFlag.version_id == version.id,
        FeatureFlag.feature_key == request.feature_key.upper(),
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Feature '{request.feature_key}' already exists in version '{version_string}'",
        )

    feature = FeatureFlag(
        version_id=version.id,
        feature_key=request.feature_key.upper(),
        feature_name=request.feature_name,
        enabled=request.enabled,
        category=request.category,
        description=request.description,
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)

    return FeatureFlagResponse.from_orm(feature)


@router.patch("/versions/{version_string}/features/{feature_key}", response_model=FeatureFlagResponse)
async def toggle_feature(
        version_string: str,
        feature_key: str,
        enabled: bool = Query(..., description="Enable or disable feature"),
        db: Session = Depends(get_db),
) -> FeatureFlagResponse:
    """Toggle a feature on/off for a specific version."""
    version = db.query(Version).filter(Version.version == version_string).first()

    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    feature = db.query(FeatureFlag).filter(
        FeatureFlag.version_id == version.id,
        FeatureFlag.feature_key == feature_key.upper(),
    ).first()

    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found")

    feature.enabled = enabled
    db.commit()
    db.refresh(feature)

    return FeatureFlagResponse.from_orm(feature)