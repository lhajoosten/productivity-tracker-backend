from fastapi import FastAPI

from productivity_tracker.api.admin import router as admin_router
from productivity_tracker.api.auth import router as auth_router
from productivity_tracker.api.health import router as health_router
from productivity_tracker.api.permissions import router as permissions_router
from productivity_tracker.api.roles import router as roles_router
from productivity_tracker.core.logging_config import get_logger
from productivity_tracker.versioning.utils import (
    get_latest_version,
    get_version_by_prefix,
)
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
    logger.info("Setting up versioned routers")

    # super_user only /admin route
    app.include_router(admin_router, prefix="/admin")

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


def check_client_version(client_prefix: str) -> dict:
    """Check if client is using latest version."""
    client_version = get_version_by_prefix(client_prefix)
    latest = get_latest_version()

    if not client_version:
        return {"error": "Invalid API version"}

    if client_version == latest:
        return {"status": "up_to_date"}

    return {
        "status": "outdated",
        "current": client_version.__str__(),
        "latest": latest.__str__(),
        "migration_url": f"/docs/{latest.prefix}",
    }
