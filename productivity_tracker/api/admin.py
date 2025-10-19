"""Admin endpoints for system management."""

from fastapi import APIRouter

from productivity_tracker.versioning.utils import get_all_versions, get_latest_version

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/versions")
async def list_api_versions():
    """Get all available API versions."""
    versions = get_all_versions()
    latest = get_latest_version()

    return {
        "versions": [
            {
                "version": v.version,
                "prefix": v.prefix,
                "is_latest": v == latest,
                "is_deprecated": v.is_deprecated,
            }
            for v in versions
        ],
        "latest": latest.version,
        "current": latest.prefix,
    }
