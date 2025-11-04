from fastapi import FastAPI

from productivity_tracker.api.admin import router as admin_router
from productivity_tracker.api.auth import router as auth_router
from productivity_tracker.api.departments import router as departments_router
from productivity_tracker.api.health import router as health_router
from productivity_tracker.api.organizations import router as organizations_router
from productivity_tracker.api.permissions import router as permissions_router
from productivity_tracker.api.roles import router as roles_router
from productivity_tracker.api.sessions import router as sessions_router
from productivity_tracker.api.teams import router as teams_router
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.versioning import (
    CURRENT_VERSION,
    Feature,
    is_feature_enabled,
)

logger = get_logger(__name__)


def setup_versioned_routers(app: FastAPI) -> None:
    """
    Configure all versioned routers for the application based on feature flags.
    Routers are included conditionally based on the features enabled for the current API version.
    """
    logger.info(f"Setting up versioned routers for {CURRENT_VERSION}")

    # Admin route (super_user only, not versioned)
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])

    # Health checks - always available
    if is_feature_enabled(Feature.HEALTH_CHECKS):
        logger.info("Adding health router")
        app.include_router(health_router, prefix=CURRENT_VERSION.api_prefix, tags=["Health"])

    # Authentication
    if is_feature_enabled(Feature.JWT_AUTHENTICATION):
        logger.info("Adding auth router")
        app.include_router(auth_router, prefix=CURRENT_VERSION.api_prefix, tags=["Authentication"])
        logger.info("Adding sessions router")
        app.include_router(
            sessions_router, prefix=CURRENT_VERSION.api_prefix, tags=["Authentication"]
        )

    # RBAC - Roles
    if is_feature_enabled(Feature.RBAC_SYSTEM):
        logger.info("Adding roles router")
        app.include_router(roles_router, prefix=CURRENT_VERSION.api_prefix, tags=["Roles"])

    # RBAC - Permissions
    if is_feature_enabled(Feature.PERMISSION_SYSTEM):
        logger.info("Adding permissions router")
        app.include_router(
            permissions_router, prefix=CURRENT_VERSION.api_prefix, tags=["Permissions"]
        )

    # Organization Management
    if is_feature_enabled(Feature.ORGANIZATION_MANAGEMENT):
        logger.info("Adding organizations router")
        app.include_router(
            organizations_router, prefix=CURRENT_VERSION.api_prefix, tags=["Organizations"]
        )

    # Department Management
    if is_feature_enabled(Feature.DEPARTMENT_MANAGEMENT):
        logger.info("Adding departments router")
        app.include_router(
            departments_router, prefix=CURRENT_VERSION.api_prefix, tags=["Departments"]
        )

    # Team Management
    if is_feature_enabled(Feature.TEAM_MANAGEMENT):
        logger.info("Adding teams router")
        app.include_router(teams_router, prefix=CURRENT_VERSION.api_prefix, tags=["Teams"])

    logger.info(f"Versioned routers setup complete for {CURRENT_VERSION}")
