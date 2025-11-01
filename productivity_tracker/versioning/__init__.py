"""
Versioning Module

Provides version management and feature flag functionality for the API.
"""

from productivity_tracker.versioning.version import (
    RELEASE_DATE,
    RELEASE_NAME,
    __version__,
    __version_info__,
    get_version,
)
from productivity_tracker.versioning.version import (
    get_version_info as get_detailed_version_info,
)
from productivity_tracker.versioning.versioning import (  # Version constants; Mappings; Classes; Functions
    ALL_VERSIONS,
    CURRENT_VERSION,
    DEPRECATED_FEATURES,
    ENVIRONMENT_FEATURES,
    FEATURE_DEPENDENCIES,
    LATEST_VERSION,
    V1_0,
    V1_1,
    V1_2,
    V1_3,
    V1_4,
    V1_5,
    V1_6,
    V2_0,
    V2_1,
    V2_2,
    V2_3,
    VERSION_FEATURES,
    DeprecationInfo,
    Feature,
    Version,
    VersionStatus,
    check_feature_dependencies,
    get_all_features_up_to_version,
    get_enabled_features,
    get_migration_path,
    get_supported_versions,
    get_version_from_string,
    get_version_headers,
    get_version_info,
    is_feature_enabled,
    require_feature,
)

__all__ = [
    # Version information
    "__version__",
    "__version_info__",
    "RELEASE_DATE",
    "RELEASE_NAME",
    "get_version",
    "get_detailed_version_info",
    # Classes
    "Version",
    "VersionStatus",
    "Feature",
    "DeprecationInfo",
    # Version constants
    "V1_0",
    "V1_1",
    "V1_2",
    "V1_3",
    "V1_4",
    "V1_5",
    "V1_6",
    "V2_0",
    "V2_1",
    "V2_2",
    "V2_3",
    "CURRENT_VERSION",
    "LATEST_VERSION",
    "ALL_VERSIONS",
    # Mappings
    "VERSION_FEATURES",
    "FEATURE_DEPENDENCIES",
    "DEPRECATED_FEATURES",
    "ENVIRONMENT_FEATURES",
    # Functions
    "get_all_features_up_to_version",
    "get_enabled_features",
    "is_feature_enabled",
    "check_feature_dependencies",
    "require_feature",
    "get_supported_versions",
    "get_version_from_string",
    "get_version_info",
    "get_version_headers",
    "get_migration_path",
]
