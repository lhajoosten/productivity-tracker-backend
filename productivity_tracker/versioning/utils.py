"""Versioning utility functions and decorators."""

from typing import TYPE_CHECKING

from fastapi import Request, Response

from productivity_tracker.versioning.versioning import (
    ALL_VERSIONS,
    CURRENT_VERSION,
    LATEST_VERSION,
    Version,
    VersionStatus,
)
from productivity_tracker.versioning.versioning import (
    get_version_headers as get_headers,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


def add_version_headers(response: Response, version: Version) -> Response:
    """Add version-related headers to response."""
    headers = get_headers(version)
    for key, value in headers.items():
        response.headers[key] = value

    # Legacy header for backward compatibility
    response.headers["X-API-Version"] = str(version)

    return response


def get_all_versions() -> list[Version]:
    """Get all supported API versions (active, beta, rc, maintenance)."""
    return [v for v in ALL_VERSIONS if v.is_supported()]


def get_all_registered_versions() -> list[Version]:
    """Get ALL registered versions (including planned and deprecated ones)."""
    return ALL_VERSIONS.copy()


def get_active_versions() -> list[Version]:
    """Get only active versions (production-ready)."""
    return [v for v in ALL_VERSIONS if v.status == VersionStatus.ACTIVE]


def get_deprecated_versions() -> list[Version]:
    """Get deprecated versions."""
    return [v for v in ALL_VERSIONS if v.is_deprecated()]


def get_api_version_from_request(request: Request) -> Version:
    """Extract API version from request path."""
    path = request.url.path

    # Try to match against supported versions
    supported = get_all_versions()
    for version in supported:
        if version.api_prefix in path:
            return version

    return CURRENT_VERSION


def get_latest_version() -> Version:
    """Get the latest supported API version."""
    return LATEST_VERSION


def get_version_by_prefix(prefix: str) -> Version | None:
    """Get API version by prefix (e.g., '/api/v1.1')."""
    for version in ALL_VERSIONS:
        if version.api_prefix == prefix:
            return version
    return None


def get_version_by_string(version_string: str) -> Version | None:
    """Get version by string (e.g., '1.0', '1.0.0-beta')."""
    from productivity_tracker.versioning.versioning import get_version_from_string

    return get_version_from_string(version_string)


def iter_versions() -> "Iterator[Version]":
    """Iterate over all registered versions."""
    return iter(ALL_VERSIONS)


def is_version_accessible(version: Version) -> bool:
    """Check if a version can be accessed (supported or deprecated but not EOL)."""
    return version.is_supported() or (version.is_deprecated() and not version.is_eol())
