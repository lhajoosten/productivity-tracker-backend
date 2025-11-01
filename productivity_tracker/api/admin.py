"""Admin endpoints for system management."""

from fastapi import APIRouter, Depends

from productivity_tracker.core.dependencies import get_current_superuser
from productivity_tracker.database.entities.user import User
from productivity_tracker.models.auth import VersionResponse
from productivity_tracker.versioning.utils import get_all_versions, get_latest_version

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
                "version": str(v),
                "prefix": v.api_prefix,
                "is_latest": v == latest,
                "is_deprecated": v.is_deprecated,
            }
            for v in versions
        ],
        "latest": str(latest),
        "current": latest.api_prefix,
        "migration_url": f"/docs/{latest.api_prefix}",
        "deprecated": [str(v) for v in versions if v.is_deprecated()],
    }
