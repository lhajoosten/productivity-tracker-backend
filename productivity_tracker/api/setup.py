from fastapi import FastAPI
from sqlalchemy.orm import Session

from productivity_tracker.api.auth import router as auth_router
from productivity_tracker.api.departments import router as departments_router
from productivity_tracker.api.health import router as health_router
from productivity_tracker.api.organizations import router as organizations_router
from productivity_tracker.api.permissions import router as permissions_router
from productivity_tracker.api.roles import router as roles_router
from productivity_tracker.api.sessions import router as sessions_router
from productivity_tracker.api.teams import router as teams_router
from productivity_tracker.api.versioning import router as version_router
from productivity_tracker.core.database import SessionLocal
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.database.entities.version import Version as VersionEntity

logger = get_logger(__name__)


def setup_versioned_routers(app: FastAPI) -> None:
    """
    Configure all versioned routers for the application based on feature flags.
    Routers are included conditionally based on the features enabled for the current API version.
    """
    db: Session = SessionLocal()
    try:
        current_version = db.query(VersionEntity).filter(VersionEntity.status == "active").first()

        if not current_version:
            logger.warning("No active version found in database")
            return

        logger.info(f"Setting up versioned routers for {current_version.version}")


        # Versioning (super_user only)
        logger.info("Adding version router")
        api_prefix = (
            current_version.api_prefix
            if current_version.api_prefix.startswith("/")
            else f"/{current_version.api_prefix}"
        )
        app.include_router(version_router, prefix=api_prefix, tags=["Version"])

        # Health checks - always available
        if any(
            f.feature_key == "HEALTH_CHECKS" for f in current_version.feature_flags if f.enabled
        ):
            logger.info("Adding health router")
            app.include_router(health_router, prefix=api_prefix, tags=["Health"])

        # Authentication
        if any(
            f.feature_key == "COOKIE_AUTHENTICATION"
            for f in current_version.feature_flags
            if f.enabled
        ):
            logger.info("Adding auth router")
            app.include_router(auth_router, prefix=api_prefix, tags=["Authentication"])
            logger.info("Adding sessions router")
            app.include_router(sessions_router, prefix=api_prefix, tags=["Authentication"])

        # RBAC - Roles
        if any(f.feature_key == "ROLE_MANAGEMENT" for f in current_version.feature_flags if f.enabled):
            logger.info("Adding roles router")
            app.include_router(roles_router, prefix=api_prefix, tags=["Roles"])

        # RBAC - Permissions
        if any(
            f.feature_key == "PERMISSION_MANAGEMENT" for f in current_version.feature_flags if f.enabled
        ):
            logger.info("Adding permissions router")
            app.include_router(permissions_router, prefix=api_prefix, tags=["Permissions"])

        # Organization Management
        if any(
            f.feature_key == "ORGANIZATION_MANAGEMENT"
            for f in current_version.feature_flags
            if f.enabled
        ):
            logger.info("Adding organizations router")
            app.include_router(organizations_router, prefix=api_prefix, tags=["Organizations"])

        # Department Management
        if any(
            f.feature_key == "DEPARTMENT_MANAGEMENT"
            for f in current_version.feature_flags
            if f.enabled
        ):
            logger.info("Adding departments router")
            app.include_router(departments_router, prefix=api_prefix, tags=["Departments"])

        # Team Management
        if any(
            f.feature_key == "TEAM_MANAGEMENT" for f in current_version.feature_flags if f.enabled
        ):
            logger.info("Adding teams router")
            app.include_router(teams_router, prefix=api_prefix, tags=["Teams"])

        logger.info(f"Versioned routers setup complete for {current_version.version}")

    finally:
        db.close()
