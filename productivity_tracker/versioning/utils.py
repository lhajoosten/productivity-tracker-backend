"""Versioning utility functions and decorators."""

from typing import TYPE_CHECKING

from fastapi import Request, Response

from productivity_tracker.versioning.versioning import (
    CURRENT_VERSION,
    DEPRECATED_VERSIONS,
    REGISTERED_VERSIONS,
    APIVersion,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


def add_version_headers(response: Response, version: APIVersion) -> Response:
    """Add version-related headers to response."""
    response.headers["X-API-Version"] = version.__str__()

    if version in DEPRECATED_VERSIONS:
        response.headers["Warning"] = (
            f'299 - "API version {version.__str__()} is deprecated. '
            f'Please migrate to the latest version."'
        )

    return response


def get_api_version_from_request(request: Request) -> APIVersion:
    """Extract API version from request path."""
    path = request.url.path
    for version in REGISTERED_VERSIONS.values():
        if version.prefix in path:
            return version
    return CURRENT_VERSION  # Default to current version


def get_all_versions() -> list[APIVersion]:
    """Get all registered API versions."""
    return list(REGISTERED_VERSIONS.values())


def get_latest_version() -> APIVersion:
    """Get the latest API version."""
    versions = get_all_versions()
    if not versions:
        raise ValueError("No API versions registered")

    # Sort by version number (major, minor, patch)
    return max(versions, key=lambda v: (v.major, v.minor))


def get_version_by_prefix(prefix: str) -> APIVersion | None:
    """Get API version by prefix (e.g., '/api/v1.0')."""
    for version in REGISTERED_VERSIONS.values():
        if version.prefix == prefix:
            return version
    return None


def iter_versions() -> "Iterator[APIVersion]":
    """Iterate over all registered versions."""
    return iter(REGISTERED_VERSIONS.values())
