"""Admin endpoints for system management."""

from fastapi import APIRouter, Depends

from productivity_tracker.core.dependencies import get_current_superuser
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import VersionResponse
from productivity_tracker.versioning.utils import get_all_versions, get_latest_version
from productivity_tracker.versioning.versioning import DEPRECATED_VERSIONS

router = APIRouter()


@router.get(
    "/versions",
    response_model=VersionResponse,
    operation_id="listApiVersions",
)
async def list_api_versions(current_user: User = Depends(get_current_superuser)):
    """Get all available API versions."""

    versions = get_all_versions()
    latest = get_latest_version()

    return {
        "versions": [
            {
                "version": v.__str__(),
                "prefix": v.prefix,
                "is_latest": v == latest,
                "is_deprecated": v in DEPRECATED_VERSIONS,
            }
            for v in versions
        ],
        "latest": latest.__str__(),
        "current": latest.prefix,
        "migration_url": f"/docs/{latest.prefix}",
        "deprecated": [v.__str__() for v in versions if v in DEPRECATED_VERSIONS],
    }
