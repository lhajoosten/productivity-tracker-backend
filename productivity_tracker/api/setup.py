from fastapi import FastAPI

from productivity_tracker.api.auth import router as auth_router
from productivity_tracker.api.health import router as health_router
from productivity_tracker.api.permissions import router as permissions_router
from productivity_tracker.api.roles import router as roles_router
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.versioning.versioning import (
    CURRENT_VERSION,
    is_feature_enabled,
)

logger = get_logger(__name__)


def setup_versioned_routers(app: FastAPI) -> None:
    """
    Configure all versioned routers for the application based on feature flags.
    Routers are included conditionally based on the features enabled for the current API version.
    """

    if is_feature_enabled(CURRENT_VERSION, "health"):
        logger.info("Adding health router")
        app.include_router(health_router, prefix=CURRENT_VERSION.prefix, tags=["Health"])

    if is_feature_enabled(CURRENT_VERSION, "auth"):
        logger.info("Adding auth router")
        app.include_router(auth_router, prefix=CURRENT_VERSION.prefix, tags=["Authentication"])

    if is_feature_enabled(CURRENT_VERSION, "roles"):
        logger.info("Adding roles router")
        app.include_router(roles_router, prefix=CURRENT_VERSION.prefix, tags=["Roles"])

    if is_feature_enabled(CURRENT_VERSION, "permissions"):
        logger.info("Adding permissions router")
        app.include_router(permissions_router, prefix=CURRENT_VERSION.prefix, tags=["Permissions"])
