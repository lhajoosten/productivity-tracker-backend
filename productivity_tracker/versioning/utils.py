"""
Versioning utility functions.

Provides helper functions for working with the database-backed versioning system.
"""

from fastapi import Request, Response
from sqlalchemy.orm import Session

from productivity_tracker.database.entities.feature_flag import FeatureFlag
from productivity_tracker.database.entities.version import Version
from productivity_tracker.database.entities.version import Version as VersionEntity


def add_version_headers(response: Response, version: VersionEntity) -> Response:
    """
    Add version-related headers to response.

    Args:
        response: FastAPI Response object
        version: Version entity from database

    Returns:
        Response with version headers added
    """
    response.headers["X-API-Version"] = version.version
    response.headers["X-API-Version-Name"] = version.name
    response.headers["X-API-Version-Status"] = version.status
    response.headers["X-API-Prefix"] = version.api_prefix

    if version.is_deprecated:
        response.headers["X-API-Deprecated"] = "true"
        if version.eol_date:
            response.headers["X-API-EOL-Date"] = version.eol_date.isoformat()

    return response


def get_all_versions(db: Session) -> list[type[Version]]:
    """
    Get all supported API versions (active, beta, rc, maintenance).

    Args:
        db: Database session

    Returns:
        List of supported version entities
    """
    return (
        db.query(VersionEntity)
        .filter(VersionEntity.status.in_(["active", "beta", "rc", "maintenance"]))
        .order_by(
            VersionEntity.major.desc(), VersionEntity.minor.desc(), VersionEntity.patch.desc()
        )
        .all()
    )


def get_all_registered_versions(db: Session) -> list[type[Version]]:
    """
    Get ALL registered versions (including planned and deprecated ones).

    Args:
        db: Database session

    Returns:
        List of all version entities
    """
    return (
        db.query(VersionEntity)
        .order_by(
            VersionEntity.major.desc(), VersionEntity.minor.desc(), VersionEntity.patch.desc()
        )
        .all()
    )


def get_active_version(db: Session) -> VersionEntity | None:
    """
    Get the current active version (production-ready).

    Args:
        db: Database session

    Returns:
        Active version entity or None
    """
    return db.query(VersionEntity).filter(VersionEntity.status == "active").first()


def get_deprecated_versions(db: Session) -> list[type[Version]]:
    """
    Get deprecated versions.

    Args:
        db: Database session

    Returns:
        List of deprecated version entities
    """
    return db.query(VersionEntity).filter(VersionEntity.status == "deprecated").all()


def get_api_version_from_request(request: Request) -> VersionEntity | None:
    """
    Get the API version for the current request.

    Args:
        request: FastAPI Request object

    Returns:
        Active version or None
    """
    from productivity_tracker.core.database import SessionLocal

    db = SessionLocal()
    try:
        version = db.query(VersionEntity).filter(VersionEntity.status == "active").first()
        return version
    finally:
        db.close()


def get_current_api_version(db: Session | None = None) -> VersionEntity | None:
    """
    Get the current active API version.

    Creates its own session if not provided (useful for middleware).

    Args:
        db: Optional database session

    Returns:
        Active version or None
    """
    from productivity_tracker.core.database import SessionLocal

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        version = db.query(VersionEntity).filter(VersionEntity.status == "active").first()
        return version
    finally:
        if should_close:
            db.close()


def get_latest_version(db: Session) -> VersionEntity | None:
    """
    Get the latest supported API version.

    Args:
        db: Database session

    Returns:
        Latest version entity
    """
    return (
        db.query(VersionEntity)
        .filter(VersionEntity.status.in_(["active", "beta", "rc"]))
        .order_by(
            VersionEntity.major.desc(), VersionEntity.minor.desc(), VersionEntity.patch.desc()
        )
        .first()
    )


def get_version_by_prefix(prefix: str, db: Session) -> VersionEntity | None:
    """
    Get API version by prefix (e.g., '/api/v0.1').

    Args:
        prefix: API prefix string
        db: Database session

    Returns:
        Version entity or None
    """
    return db.query(VersionEntity).filter(VersionEntity.api_prefix == prefix).first()


def get_version_by_string(version_string: str, db: Session) -> VersionEntity | None:
    """
    Get version by string (e.g., '0.1.0-beta').

    Args:
        version_string: Version string
        db: Database session

    Returns:
        Version entity or None
    """
    return db.query(VersionEntity).filter(VersionEntity.version == version_string).first()


def is_version_accessible(version: VersionEntity) -> bool:
    """
    Check if a version can be accessed (supported or deprecated but not EOL).

    Args:
        version: Version entity

    Returns:
        True if version is accessible
    """
    return version.is_supported or (version.is_deprecated and not version.is_eol)


def get_version_features(version: VersionEntity, db: Session) -> list[type[FeatureFlag]]:
    """
    Get all enabled features for a version.

    Args:
        version: Version entity
        db: Database session

    Returns:
        List of enabled feature flags
    """
    return (
        db.query(FeatureFlag)
        .filter(FeatureFlag.version_id == version.id, FeatureFlag.enabled)
        .all()
    )


def is_feature_enabled_in_version(
    version: VersionEntity, feature_key: str, db: Session, environment: str = "production"
) -> bool:
    """
    Check if a feature is enabled in a specific version.

    Args:
        version: Version entity
        feature_key: Feature key to check
        db: Database session
        environment: Environment name (development, staging, production)

    Returns:
        True if feature is enabled
    """
    feature = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.version_id == version.id, FeatureFlag.feature_key == feature_key.upper()
        )
        .first()
    )

    if not feature:
        return False

    return feature.is_enabled_for_env(environment)
