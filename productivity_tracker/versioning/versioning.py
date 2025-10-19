"""
API Versioning Configuration
"""

from enum import Enum


class APIVersion(Enum):
    V1 = "v1"
    V2 = "v2"  # For future use

    @property
    def prefix(self) -> str:
        """Returns the API prefix for this version"""
        return f"/api/{self.value}"


# Current active version
CURRENT_VERSION = APIVersion.V1

# Supported versions
SUPPORTED_VERSIONS: list[APIVersion] = [APIVersion.V1]

# Deprecated versions (still accessible but with warnings)
DEPRECATED_VERSIONS: list[APIVersion] = []

# Version feature flags
VERSION_FEATURES = {
    APIVersion.V1: {
        "auth": True,
        "rbac": True,
        "users": True,
        "roles": True,
        "permissions": True,
        "health_check": True,
        "organizations": False,
        "departments": False,
        "teams": False,
        "time_tracking": False,
        "tasks": False,
        "projects": False,
        "analytics": False,
    }
}


def is_feature_enabled(version: APIVersion, feature: str) -> bool:
    """Check if a feature is enabled for a specific version"""
    return VERSION_FEATURES.get(version, {}).get(feature, False)
