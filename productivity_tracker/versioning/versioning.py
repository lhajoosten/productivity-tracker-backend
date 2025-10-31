"""
API Versioning Configuration
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class APIVersion:
    """Represents an API version with major and minor components."""

    major: int
    minor: int

    @property
    def prefix(self) -> str:
        """Returns the API prefix for this version (e.g., /api/v1.0)"""
        return f"/api/v{self.major}.{self.minor}"

    @property
    def major_prefix(self) -> str:
        """Returns the major version prefix (e.g., /api/v1)"""
        return f"/api/v{self.major}"

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}"

    def __repr__(self) -> str:
        return f"APIVersion({self.major}.{self.minor})"

    def __hash__(self) -> int:
        return hash((self.major, self.minor))


# Define versions
V1_0 = APIVersion(1, 0)  # Initial core features
V1_1 = APIVersion(1, 1)  # Core features patches/updates
V1_2 = APIVersion(1, 2)  # Core features patches/updates

V2_0 = APIVersion(2, 0)  # Advanced features
V2_1 = APIVersion(2, 1)  # Advanced features patches/updates
V2_2 = APIVersion(2, 2)  # Advanced features patches/updates

V3_0 = APIVersion(3, 0)  # AI/LLM/MCP features (future)
V3_1 = APIVersion(3, 1)  # AI features patches/updates (future)
V3_2 = APIVersion(3, 2)  # AI features patches/updates (future)
V3_3 = APIVersion(3, 3)  # AI features patches/updates (future)

V4_0 = APIVersion(4, 0)  # Future major version

# Current active version
CURRENT_VERSION = V1_0

# Only these versions are accessible via the API
ACTIVE_VERSIONS: set[APIVersion] = {
    V1_0,
    # V1_1,
}

# Versions that are deprecated but still accessible (with warning headers)
DEPRECATED_VERSIONS: set[APIVersion] = set()

# All versions that can be accessed (active + deprecated)
ACCESSIBLE_VERSIONS: set[APIVersion] = set(ACTIVE_VERSIONS) | set(DEPRECATED_VERSIONS)

_BASE_FEATURES = {
    "auth": False,
    "rbac": False,
    "users": False,
    "roles": False,
    "permissions": False,
    "health": False,
    "organizations": False,
    "departments": False,
    "teams": False,
    "time_tracking": False,
    "tasks": False,
    "projects": False,
    "analytics": False,
    "ai_integration": False,
    "llm_features": False,
    "mcp_support": False,
}

# Version feature flags
_VERSION_FEATURE_CHANGES = {
    # Core features
    V1_0: {
        "auth": True,
        "rbac": True,
        "users": True,
        "roles": True,
        "permissions": True,
        "health": True,
        "organizations": True,
        "departments": True,
        "teams": True,
    },
    V1_1: {
        "audit_logging": True,  # Track all system changes and user actions
        "bulk_operations": True,  # Bulk import/export/update for users and teams
        "data_export": True,  # Export data to CSV/JSON formats
        "search": True,  # Global search across all entities
    },
    V1_2: {
        "advanced_permissions": True,  # Granular role-based permissions
        "organization_settings": True,  # Configurable organization policies
        "user_preferences": True,  # User settings for theme, locale, timezone
        "basic_integrations": True,  # Webhook support for external systems
        "notifications": True,  # In-app and email notifications
    },
    # Advanced productivity features
    V2_0: {
        "workspaces": True,  # Isolated work environments
        "projects": True,  # Project management capabilities
        "tasks": True,  # Task creation and management
        "time_tracking": True,  # Track time spent on tasks/projects
        "file_management": True,  # Document attachments and storage
    },
    V2_1: {
        "task_dependencies": True,  # Task relationship and blocking
        "project_templates": True,  # Reusable project structures
        "calendar_integration": True,  # Calendar sync and scheduling
        "task_comments": True,  # Collaborative task discussions
        "milestone_tracking": True,  # Project milestone management
    },
    V2_2: {
        "analytics": True,  # Basic productivity analytics
        "reporting": True,  # Advanced reporting and dashboards
        "workflow_automation": True,  # Automated task and project workflows
        "performance_metrics": True,  # Individual and team performance tracking
    },
    # AI and machine learning features
    V3_0: {
        "ai_integration": True,  # Core AI service integration
        "smart_insights": True,  # AI-driven productivity insights
        "auto_categorization": True,  # AI-powered task/project categorization
        "predictive_analytics": True,  # AI predictions for project completion
    },
    V3_1: {
        "mcp_support": True,  # Model Context Protocol for AI agents
        "intelligent_scheduling": True,  # AI-optimized task scheduling
        "smart_recommendations": True,  # AI-powered task and resource suggestions
    },
    V3_2: {
        "natural_language_queries": True,  # Query data using natural language
        "ai_assistants": True,  # Conversational AI helpers
        "automated_reporting": True,  # AI-generated reports and summaries
    },
    V3_3: {
        "sentiment_analysis": True,  # Analyze team communication sentiment
        "risk_detection": True,  # AI-powered project risk identification
    },
}


def _build_version_features() -> dict[APIVersion, dict[str, bool]]:
    """
    Build the complete VERSION_FEATURES dictionary by merging base features
    with version-specific changes, inheriting from previous versions.
    """
    result = {}

    # Get all versions sorted by major.minor
    versions = sorted(_VERSION_FEATURE_CHANGES.keys(), key=lambda v: (v.major, v.minor))

    for version in versions:
        # Start with base features
        features = _BASE_FEATURES.copy()

        # Find all previous versions to build inheritance chain
        for prev in versions:
            if prev.major < version.major or (
                prev.major == version.major and prev.minor < version.minor
            ):
                # Apply changes from this previous version
                features.update(_VERSION_FEATURE_CHANGES[prev])

        # Apply version-specific changes
        features.update(_VERSION_FEATURE_CHANGES[version])

        result[version] = features

    return result


# Build the complete feature dictionary
VERSION_FEATURES = _build_version_features()

# All versions registered for testing/validation
REGISTERED_VERSIONS: dict[str, APIVersion] = {
    "v1.0": V1_0,
    "v1.1": V1_1,
    "v1.2": V1_2,
    "v2.0": V2_0,
    "v2.1": V2_1,
    "v2.2": V2_2,
    "v3.0": V3_0,
    "v3.1": V3_1,
    "v3.2": V3_2,
    "v3.3": V3_3,
}


def is_feature_enabled(version: APIVersion, feature: str) -> bool:
    """Check if a feature is enabled for a specific version."""
    return VERSION_FEATURES.get(version, {}).get(feature, False)


def get_latest_minor_version(major: int) -> APIVersion | None:
    """Get the latest minor version for a given major version."""
    versions = [v for v in VERSION_FEATURES.keys() if v.major == major]
    return max(versions, key=lambda v: v.minor) if versions else None


def is_version_supported(version: APIVersion) -> bool:
    """Check if a version is currently supported."""
    return version in ACCESSIBLE_VERSIONS


def is_version_deprecated(version: APIVersion) -> bool:
    """Check if a version is deprecated."""
    return version in DEPRECATED_VERSIONS
