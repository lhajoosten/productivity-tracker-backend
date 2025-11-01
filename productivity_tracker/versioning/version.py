"""
Version Information - Single Source of Truth

This module contains the version number for the entire application.
All version references should import from here to maintain consistency.

Version Format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
Following Semantic Versioning 2.0.0 (https://semver.org/)
"""

from datetime import date

# Single source of truth for version
__version__ = "1.0.0-beta"

# Version as tuple for programmatic comparison
__version_info__ = (1, 0, 0, "beta", 0)

# Release metadata
RELEASE_DATE = date(2025, 11, 1)
RELEASE_NAME = "Foundation - First Beta"

# Version history for reference
VERSION_HISTORY = [
    {
        "version": "1.0.0-beta",
        "release_date": "2025-11-01",
        "release_name": "Foundation - First Beta",
        "status": "current",
    },
    # Future versions will be added here
]


def get_version() -> str:
    """
    Get the current version string

    Returns:
        Version string (e.g., "1.0.0-beta")
    """
    return __version__


def get_version_info() -> dict:
    """
    Get detailed version information

    Returns:
        Dictionary containing version details
    """
    return {
        "version": __version__,
        "version_tuple": __version_info__,
        "release_date": RELEASE_DATE.isoformat(),
        "release_name": RELEASE_NAME,
        "major": __version_info__[0],
        "minor": __version_info__[1],
        "patch": __version_info__[2],
        "prerelease": __version_info__[3] if len(__version_info__) > 3 else None,
    }


# Export public API
__all__ = [
    "__version__",
    "__version_info__",
    "RELEASE_DATE",
    "RELEASE_NAME",
    "get_version",
    "get_version_info",
]
