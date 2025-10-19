"""
Versioning utility functions and decorators
"""

from fastapi import Request, Response

from .versioning import DEPRECATED_VERSIONS, APIVersion


def add_version_headers(response: Response, version: APIVersion):
    """Add version-related headers to response"""
    response.headers["X-API-Version"] = version.value

    if version in DEPRECATED_VERSIONS:
        response.headers["Warning"] = (
            f'299 - "API version {version.value} is deprecated. '
            f'Please migrate to the latest version."'
        )

    return response


def get_api_version_from_request(request: Request) -> APIVersion:
    """Extract API version from request path"""
    path = request.url.path
    for version in APIVersion:
        if version.prefix in path:
            return version
    return APIVersion.V1  # Default
