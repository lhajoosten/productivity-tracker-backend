"""
Versioning Module

Database-backed versioning and feature flag system.
"""

# Current version info
from .version import __version__, get_version, get_version_info

# Version loader (for seeding database)
from .version_loader import (
    FEATURE_NAME_MAP,
    load_versions_from_json,
    map_features,
    parse_version_string,
)

# Enums (used throughout the application)
from .versioning import (
    FEATURE_CATEGORIES,
    Feature,
    FeatureCategory,
    VersionStatus,
    get_feature_category,
)

__all__ = [
    # Enums
    "Feature",
    "FeatureCategory",
    "VersionStatus",
    "FEATURE_CATEGORIES",
    "get_feature_category",
    # Version loader
    "load_versions_from_json",
    "parse_version_string",
    "map_features",
    "FEATURE_NAME_MAP",
    # Version info
    "__version__",
    "get_version",
    "get_version_info",
]
