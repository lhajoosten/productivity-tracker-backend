"""
Versioning and Feature Flag Management System

This module provides comprehensive version management and feature flagging
capabilities for the Productivity Tracker API. It implements the versioning
strategy defined in docs/VERSIONING_STRATEGY.md and the roadmap from
docs/VERSION_ROADMAP.md.

Key Features:
- Semantic versioning (MAJOR.MINOR.PATCH)
- Feature flags per version
- Version lifecycle management
- Deprecation tracking
- Version comparison utilities
- Environment-based feature toggles
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from functools import wraps
from typing import Any

from fastapi import HTTPException, Request, status

# ============================================================================
# ENUMS
# ============================================================================


class VersionStatus(str, Enum):
    """Lifecycle status of an API version."""

    PLANNED = "planned"  # Version is planned but not yet in development
    IN_DEVELOPMENT = "in_development"  # Active development
    ALPHA = "alpha"  # Early testing, may be unstable
    BETA = "beta"  # Feature complete, in testing
    RC = "rc"  # Release candidate, final testing
    ACTIVE = "active"  # Current production version
    MAINTENANCE = "maintenance"  # Supported but not actively developed
    DEPRECATED = "deprecated"  # Supported but will be removed soon
    EOL = "end_of_life"  # No longer supported


class Feature(str, Enum):
    """
    Feature flags for all versions.

    Features are organized by the version that introduces them.
    Each feature can be enabled/disabled independently.
    """

    # ========================================================================
    # Version 1.0.0-beta - Foundation (COMPLETED)
    # ========================================================================
    ORGANIZATION_MANAGEMENT = "organization_management"
    DEPARTMENT_MANAGEMENT = "department_management"
    TEAM_MANAGEMENT = "team_management"
    USER_MANAGEMENT = "user_management"
    RBAC_SYSTEM = "rbac_system"
    PERMISSION_SYSTEM = "permission_system"
    JWT_AUTHENTICATION = "jwt_authentication"
    HEALTH_CHECKS = "health_checks"
    API_DOCUMENTATION = "api_documentation"
    ERROR_HANDLING = "error_handling"
    DATABASE_MIGRATIONS = "database_migrations"
    RATE_LIMITING = "rate_limiting"

    # ========================================================================
    # Version 1.1.1-alpha - Security update (COMPLETED)
    # ========================================================================
    REDIS_CACHING = "redis_caching"
    COOKIE_AUTHENTICATION = "cookie_authentication"
    HTTPS_CONFIGURATION = "https_configuration"
    XSS_PROTECTION = "xss_protection"

    # ========================================================================
    # Version 1.1.1-beta - Security & Validation Enhancement (PLANNED)
    # ========================================================================
    PASSWORD_COMPLEXITY = "password_complexity"  # nosec
    ACCOUNT_LOCKOUT = "account_lockout"  # nosec
    PASSWORD_RESET = "password_reset"  # nosec
    API_KEY_AUTH = "api_key_auth"
    INPUT_SANITIZATION = "input_sanitization"
    AUDIT_LOGGING = "audit_logging"
    LOGIN_ACTIVITY_TRACKING = "login_activity_tracking"

    # ========================================================================
    # Version 1.2.0 - Productivity Tracking Core (PLANNED)
    # ========================================================================
    TIME_TRACKING = "time_tracking"
    TASK_MANAGEMENT = "task_management"
    PROJECT_MANAGEMENT = "project_management"
    TASK_DEPENDENCIES = "task_dependencies"
    SUBTASKS = "subtasks"
    TAGS_SYSTEM = "tags_system"
    CATEGORIES = "categories"

    # ========================================================================
    # Version 1.3.0 - Analytics & Reporting (PLANNED)
    # ========================================================================
    ANALYTICS_DASHBOARD = "analytics_dashboard"
    PRODUCTIVITY_TRENDS = "productivity_trends"
    TASK_COMPLETION_ANALYTICS = "task_completion_analytics"
    REPORTING_SYSTEM = "reporting_system"
    CUSTOM_REPORTS = "custom_reports"
    REPORT_EXPORT = "report_export"
    SCHEDULED_REPORTS = "scheduled_reports"
    KPI_TRACKING = "kpi_tracking"
    GOAL_TRACKING = "goal_tracking"
    ADVANCED_SEARCH = "advanced_search"
    FULL_TEXT_SEARCH = "full_text_search"
    SAVED_SEARCHES = "saved_searches"

    # ========================================================================
    # Version 1.4.0 - Collaboration & Communication (PLANNED)
    # ========================================================================
    COMMENTS_SYSTEM = "comments_system"
    MENTIONS = "mentions"
    NOTIFICATIONS = "notifications"
    EMAIL_NOTIFICATIONS = "email_notifications"
    REAL_TIME_NOTIFICATIONS = "real_time_notifications"
    SHARED_WORKSPACES = "shared_workspaces"
    TEAM_CALENDAR = "team_calendar"
    FILE_ATTACHMENTS = "file_attachments"
    FILE_VERSIONING = "file_versioning"

    # ========================================================================
    # Version 1.5.0 - Performance & Scalability (PLANNED)
    # ========================================================================
    QUERY_OPTIMIZATION = "query_optimization"
    BULK_OPERATIONS = "bulk_operations"
    ASYNC_TASK_PROCESSING = "async_task_processing"
    DATABASE_PARTITIONING = "database_partitioning"
    READ_REPLICAS = "read_replicas"

    # ========================================================================
    # Version 1.6.0 - Integration & Extensibility (PLANNED)
    # ========================================================================
    WEBHOOKS = "webhooks"
    OAUTH2_INTEGRATION = "oauth2_integration"
    CALENDAR_SYNC = "calendar_sync"
    SLACK_INTEGRATION = "slack_integration"
    EMAIL_INTEGRATION = "email_integration"
    PLUGIN_FRAMEWORK = "plugin_framework"
    GRAPHQL_ENDPOINT = "graphql_endpoint"
    API_ANALYTICS = "api_analytics"

    # ========================================================================
    # Version 2.0.0 - Enterprise Features (PLANNED)
    # ========================================================================
    SSO_SAML = "sso_saml"
    MULTI_REGION = "multi_region"
    GDPR_COMPLIANCE = "gdpr_compliance"
    SOC2_COMPLIANCE = "soc2_compliance"
    ENCRYPTION_AT_REST = "encryption_at_rest"
    FIELD_LEVEL_ENCRYPTION = "field_level_encryption"
    MOBILE_API = "mobile_api"
    OFFLINE_SYNC = "offline_sync"
    PUSH_NOTIFICATIONS = "push_notifications"

    # ========================================================================
    # Version 2.1.0 - AI & Machine Learning (PLANNED)
    # ========================================================================
    AI_PRODUCTIVITY_PATTERNS = "ai_productivity_patterns"
    AUTO_TIME_CATEGORIZATION = "auto_time_categorization"
    SMART_TASK_SUGGESTIONS = "smart_task_suggestions"
    WORKLOAD_BALANCING = "workload_balancing"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    NLP_QUERY = "nlp_query"
    AUTOMATION_ENGINE = "automation_engine"

    # ========================================================================
    # Version 2.2.0 - Accessibility & Internationalization (PLANNED)
    # ========================================================================
    INTERNATIONALIZATION = "internationalization"
    MULTI_LANGUAGE = "multi_language"
    RTL_SUPPORT = "rtl_support"
    WCAG_COMPLIANCE = "wcag_compliance"
    REGIONAL_CUSTOMIZATION = "regional_customization"

    # ========================================================================
    # Version 2.3.0 - Advanced Quality & Observability (PLANNED)
    # ========================================================================
    DISTRIBUTED_TRACING = "distributed_tracing"
    METRICS_COLLECTION = "metrics_collection"
    APM = "apm"
    CHAOS_ENGINEERING = "chaos_engineering"
    SLO_TRACKING = "slo_tracking"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class Version:
    """Represents a semantic version with lifecycle management."""

    major: int
    minor: int
    patch: int = 0
    prerelease: str | None = None  # e.g., "beta", "rc.1"
    build_metadata: str | None = None  # e.g., build date
    status: VersionStatus = VersionStatus.PLANNED
    release_date: date | None = None
    eol_date: date | None = None  # End-of-life date
    docs_url: str | None = None
    migration_guide_url: str | None = None
    changelog_url: str | None = None

    def __post_init__(self):
        """Generate version string after initialization."""
        parts = [f"{self.major}.{self.minor}.{self.patch}"]

        if self.prerelease:
            parts.append(f"-{self.prerelease}")

        if self.build_metadata:
            parts.append(f"+{self.build_metadata}")

        self.version_string = "".join(parts)
        self.api_prefix = f"/api/v{self.major}.{self.minor}"

    def __str__(self) -> str:
        return str(self.version_string)

    def __repr__(self) -> str:
        return f"Version({self.version_string}, status={self.status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: "Version") -> bool:
        """Compare versions for sorting."""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # Handle prerelease: 1.0.0 > 1.0.0-beta
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease

        return False

    def __le__(self, other: "Version") -> bool:
        return self == other or self < other

    def __gt__(self, other: "Version") -> bool:
        return not self <= other

    def __ge__(self, other: "Version") -> bool:
        return not self < other

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.prerelease))

    def is_compatible_with(self, other: "Version") -> bool:
        """
        Check if versions are compatible.

        Versions are compatible if they share the same major version.
        This follows semantic versioning principles.
        """
        return self.major == other.major

    def is_breaking_change_from(self, other: "Version") -> bool:
        """Check if this version introduces breaking changes from another."""
        return self.major > other.major

    def is_supported(self) -> bool:
        """Check if version is currently supported."""
        return self.status in [
            VersionStatus.ALPHA,
            VersionStatus.BETA,
            VersionStatus.RC,
            VersionStatus.ACTIVE,
            VersionStatus.MAINTENANCE,
        ]

    def is_deprecated(self) -> bool:
        """Check if version is deprecated."""
        return self.status == VersionStatus.DEPRECATED

    def is_eol(self) -> bool:
        """Check if version has reached end-of-life."""
        if self.status == VersionStatus.EOL:
            return True
        if self.eol_date and datetime.now().date() >= self.eol_date:
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            "version": self.version_string,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "prerelease": self.prerelease,
            "status": self.status.value,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "eol_date": self.eol_date.isoformat() if self.eol_date else None,
            "api_prefix": self.api_prefix,
            "docs_url": self.docs_url,
            "migration_guide_url": self.migration_guide_url,
            "changelog_url": self.changelog_url,
        }


@dataclass
class DeprecationInfo:
    """Information about deprecated features or versions."""

    sunset_date: date  # When feature/version will be removed
    replacement: str  # What to use instead
    migration_guide: str  # URL or description of migration steps
    reason: str = ""  # Why it's being deprecated


# ============================================================================
# VERSION DEFINITIONS
# ============================================================================

# All versions in chronological order
V1_0 = Version(
    major=1,
    minor=0,
    patch=0,
    prerelease="beta",
    status=VersionStatus.ACTIVE,
    release_date=date(2025, 10, 31),
    eol_date=date(2025, 12, 31),
    docs_url="/docs",
)

V1_1 = Version(
    major=1,
    minor=1,
    patch=1,
    prerelease="alpha",
    build_metadata="2025-11-03",
    status=VersionStatus.ACTIVE,
    release_date=date(2025, 11, 4),
    docs_url="/docs",
)

V1_2 = Version(
    major=1,
    minor=2,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.2",
)

V1_3 = Version(
    major=1,
    minor=3,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.3",
)

V1_4 = Version(
    major=1,
    minor=4,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.4",
)

V1_5 = Version(
    major=1,
    minor=5,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.5",
)

V1_6 = Version(
    major=1,
    minor=6,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.6",
)

V2_0 = Version(
    major=2,
    minor=0,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v2.0",
)

V2_1 = Version(
    major=2,
    minor=1,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v2.1",
)

V2_2 = Version(
    major=2,
    minor=2,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v2.2",
)

V2_3 = Version(
    major=2,
    minor=3,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v2.3",
)

# Current version (what's deployed)
CURRENT_VERSION = V1_1

# Latest version (may be in development)
LATEST_VERSION = V1_1

# All versions
ALL_VERSIONS = [V1_0, V1_1, V1_2, V1_3, V1_4, V1_5, V1_6, V2_0, V2_1, V2_2, V2_3]


# ============================================================================
# FEATURE MAPPINGS
# ============================================================================

# Map versions to their features
VERSION_FEATURES: dict[Version, set[Feature]] = {
    V1_0: {
        Feature.ORGANIZATION_MANAGEMENT,
        Feature.DEPARTMENT_MANAGEMENT,
        Feature.TEAM_MANAGEMENT,
        Feature.USER_MANAGEMENT,
        Feature.RBAC_SYSTEM,
        Feature.PERMISSION_SYSTEM,
        Feature.JWT_AUTHENTICATION,
        Feature.HEALTH_CHECKS,
        Feature.API_DOCUMENTATION,
        Feature.ERROR_HANDLING,
        Feature.DATABASE_MIGRATIONS,
    },
    V1_1: {
        Feature.RATE_LIMITING,
        Feature.PASSWORD_COMPLEXITY,
        Feature.ACCOUNT_LOCKOUT,
        Feature.PASSWORD_RESET,
        Feature.API_KEY_AUTH,
        Feature.INPUT_SANITIZATION,
        Feature.XSS_PROTECTION,
        Feature.AUDIT_LOGGING,
        Feature.LOGIN_ACTIVITY_TRACKING,
    },
    V1_2: {
        Feature.TIME_TRACKING,
        Feature.TASK_MANAGEMENT,
        Feature.PROJECT_MANAGEMENT,
        Feature.TASK_DEPENDENCIES,
        Feature.SUBTASKS,
        Feature.TAGS_SYSTEM,
        Feature.CATEGORIES,
    },
    V1_3: {
        Feature.ANALYTICS_DASHBOARD,
        Feature.PRODUCTIVITY_TRENDS,
        Feature.TASK_COMPLETION_ANALYTICS,
        Feature.REPORTING_SYSTEM,
        Feature.CUSTOM_REPORTS,
        Feature.REPORT_EXPORT,
        Feature.SCHEDULED_REPORTS,
        Feature.KPI_TRACKING,
        Feature.GOAL_TRACKING,
        Feature.ADVANCED_SEARCH,
        Feature.FULL_TEXT_SEARCH,
        Feature.SAVED_SEARCHES,
    },
    V1_4: {
        Feature.COMMENTS_SYSTEM,
        Feature.MENTIONS,
        Feature.NOTIFICATIONS,
        Feature.EMAIL_NOTIFICATIONS,
        Feature.REAL_TIME_NOTIFICATIONS,
        Feature.SHARED_WORKSPACES,
        Feature.TEAM_CALENDAR,
        Feature.FILE_ATTACHMENTS,
        Feature.FILE_VERSIONING,
    },
    V1_5: {
        Feature.REDIS_CACHING,
        Feature.QUERY_OPTIMIZATION,
        Feature.BULK_OPERATIONS,
        Feature.ASYNC_TASK_PROCESSING,
        Feature.DATABASE_PARTITIONING,
        Feature.READ_REPLICAS,
    },
    V1_6: {
        Feature.WEBHOOKS,
        Feature.OAUTH2_INTEGRATION,
        Feature.CALENDAR_SYNC,
        Feature.SLACK_INTEGRATION,
        Feature.EMAIL_INTEGRATION,
        Feature.PLUGIN_FRAMEWORK,
        Feature.GRAPHQL_ENDPOINT,
        Feature.API_ANALYTICS,
    },
    V2_0: {
        Feature.SSO_SAML,
        Feature.MULTI_REGION,
        Feature.GDPR_COMPLIANCE,
        Feature.SOC2_COMPLIANCE,
        Feature.ENCRYPTION_AT_REST,
        Feature.FIELD_LEVEL_ENCRYPTION,
        Feature.MOBILE_API,
        Feature.OFFLINE_SYNC,
        Feature.PUSH_NOTIFICATIONS,
    },
    V2_1: {
        Feature.AI_PRODUCTIVITY_PATTERNS,
        Feature.AUTO_TIME_CATEGORIZATION,
        Feature.SMART_TASK_SUGGESTIONS,
        Feature.WORKLOAD_BALANCING,
        Feature.PREDICTIVE_ANALYTICS,
        Feature.NLP_QUERY,
        Feature.AUTOMATION_ENGINE,
    },
    V2_2: {
        Feature.INTERNATIONALIZATION,
        Feature.MULTI_LANGUAGE,
        Feature.RTL_SUPPORT,
        Feature.WCAG_COMPLIANCE,
        Feature.REGIONAL_CUSTOMIZATION,
    },
    V2_3: {
        Feature.DISTRIBUTED_TRACING,
        Feature.METRICS_COLLECTION,
        Feature.APM,
        Feature.CHAOS_ENGINEERING,
        Feature.SLO_TRACKING,
    },
}

# Feature dependencies (features that require other features)
FEATURE_DEPENDENCIES: dict[Feature, set[Feature]] = {
    Feature.SMART_TASK_SUGGESTIONS: {Feature.TASK_MANAGEMENT, Feature.AI_PRODUCTIVITY_PATTERNS},
    Feature.WORKLOAD_BALANCING: {Feature.TASK_MANAGEMENT, Feature.AI_PRODUCTIVITY_PATTERNS},
    Feature.AUTO_TIME_CATEGORIZATION: {Feature.TIME_TRACKING, Feature.AI_PRODUCTIVITY_PATTERNS},
    Feature.SCHEDULED_REPORTS: {Feature.REPORTING_SYSTEM},
    Feature.CUSTOM_REPORTS: {Feature.REPORTING_SYSTEM},
    Feature.REPORT_EXPORT: {Feature.REPORTING_SYSTEM},
    Feature.TASK_COMPLETION_ANALYTICS: {Feature.TASK_MANAGEMENT, Feature.ANALYTICS_DASHBOARD},
    Feature.PRODUCTIVITY_TRENDS: {Feature.TIME_TRACKING, Feature.ANALYTICS_DASHBOARD},
    Feature.FILE_VERSIONING: {Feature.FILE_ATTACHMENTS},
    Feature.REAL_TIME_NOTIFICATIONS: {Feature.NOTIFICATIONS},
    Feature.EMAIL_NOTIFICATIONS: {Feature.NOTIFICATIONS},
    Feature.SAVED_SEARCHES: {Feature.ADVANCED_SEARCH},
    Feature.FULL_TEXT_SEARCH: {Feature.ADVANCED_SEARCH},
    Feature.OFFLINE_SYNC: {Feature.MOBILE_API},
    Feature.PUSH_NOTIFICATIONS: {Feature.MOBILE_API, Feature.NOTIFICATIONS},
}

# Deprecated features (features being phased out)
DEPRECATED_FEATURES: dict[Feature, DeprecationInfo] = {
    # Example: If we deprecate something in the future
    # Feature.BASIC_AUTH: DeprecationInfo(
    #     sunset_date=date(2026, 12, 31),
    #     replacement="JWT_AUTHENTICATION",
    #     migration_guide="/docs/migration/auth",
    #     reason="Enhanced security with JWT tokens"
    # )
}

# Environment-specific feature toggles
ENVIRONMENT_FEATURES: dict[str, set[Feature]] = {
    "development": set(Feature),  # All features enabled in development
    "staging": VERSION_FEATURES[V1_0],  # Only stable features in staging
    "production": VERSION_FEATURES[V1_0],  # Only production-ready features
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_all_features_up_to_version(version: Version) -> set[Feature]:
    """
    Get all features available up to and including the specified version.

    This cumulative approach means v1.2 includes features from v1.0, v1.1, and v1.2.
    """
    features: set[Feature] = set()

    for ver in sorted(ALL_VERSIONS):
        if ver <= version:
            features.update(VERSION_FEATURES.get(ver, set()))
        else:
            break

    return features


def get_enabled_features(
    version: Version | None = None, environment: str | None = None
) -> set[str] | set[Feature]:
    """
    Get enabled features for a version and environment.

    Args:
        version: Version to check (defaults to CURRENT_VERSION)
        environment: Environment name (defaults to production behavior)

    Returns:
        Set of enabled features
    """
    if version is None:
        version = CURRENT_VERSION

    # Get features for this version
    version_features = get_all_features_up_to_version(version)

    # Apply environment filter if specified
    if environment:
        if environment == "development":
            # Development: ALL features available, ignore version restrictions
            return set(Feature)
        elif environment in ["staging", "production"]:
            # Staging/Production: Only features from supported versions
            # Return features for the requested version (respecting version limits)
            return version_features
        else:
            # Unknown environment: default to version features
            return version_features

    return version_features


def is_feature_enabled(
    feature: Feature,
    version: Version | None = None,
    environment: str | None = None,
) -> bool:
    """
    Check if a feature is enabled.

    Args:
        feature: Feature to check
        version: Version to check against (defaults to CURRENT_VERSION)
        environment: Environment name (optional)

    Returns:
        True if feature is enabled
    """
    enabled_features = get_enabled_features(version=version, environment=environment)
    return feature in enabled_features


def check_feature_dependencies(feature: Feature, version: Version | None = None) -> bool:
    """
    Check if all dependencies for a feature are enabled.

    Args:
        feature: Feature to check
        version: Version to check against (defaults to CURRENT_VERSION)

    Returns:
        True if all dependencies are satisfied
    """
    deps = FEATURE_DEPENDENCIES.get(feature, set())
    return all(is_feature_enabled(dep, version=version) for dep in deps)


def require_feature(feature: Feature) -> Callable:
    """
    Decorator to require a feature to be enabled.

    Usage:
        @require_feature(Feature.TASK_MANAGEMENT)
        async def create_task(...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get version from request if available
            version = CURRENT_VERSION
            for arg in args:
                if isinstance(arg, Request):
                    version = getattr(arg.state, "api_version", CURRENT_VERSION)
                    break

            if not is_feature_enabled(feature, version=version):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Feature '{feature.value}' is not available in version {version}",
                )

            # Check dependencies
            if not check_feature_dependencies(feature, version=version):
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail=f"Feature '{feature.value}' has unmet dependencies",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_supported_versions() -> list[Version]:
    """Get currently supported versions (active + maintenance)."""
    return [v for v in ALL_VERSIONS if v.is_supported()]


def get_version_from_string(version_string: str) -> Version | None:
    """
    Parse version string and return matching Version object.

    Args:
        version_string: String like "1.0", "1.0.0", "1.0.0-beta"

    Returns:
        Matching Version object or None
    """
    # Normalize version string
    parts = version_string.replace("v", "").split(".")
    if len(parts) < 2:
        return None

    try:
        major = int(parts[0])
        minor = int(parts[1])

        # Find matching version
        for version in ALL_VERSIONS:
            if version.major == major and version.minor == minor:
                return version
    except ValueError:
        pass

    return None


def get_version_headers(version: Version) -> dict[str, str]:
    """
    Generate standard version headers for API responses.

    Args:
        version: Version to generate headers for

    Returns:
        Dictionary of headers
    """
    headers = {
        "API-Version": version.version_string,
        "API-Status": version.status.value,
        "API-Deprecated": str(version.is_deprecated()).lower(),
    }

    if version.is_deprecated() and version.eol_date:
        # RFC 8594 Sunset header
        headers["Sunset"] = version.eol_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    if version.docs_url:
        headers["Link"] = f'<{version.docs_url}>; rel="documentation"'

    return headers


def get_version_info(version: Version | None = None) -> dict[str, Any]:
    """
    Get detailed information about a version.

    Args:
        version: Version to get info for (defaults to CURRENT_VERSION)

    Returns:
        Dictionary with version information
    """
    if version is None:
        version = CURRENT_VERSION

    features = get_all_features_up_to_version(version)
    new_features = VERSION_FEATURES.get(version, set())

    return {
        "version": version.to_dict(),
        "features": {
            "total": len(features),
            "new_in_version": len(new_features),
            "all": [f.value for f in sorted(features, key=lambda x: x.value)],
            "new": [f.value for f in sorted(new_features, key=lambda x: x.value)],
        },
        "compatibility": {
            "supported": version.is_supported(),
            "deprecated": version.is_deprecated(),
            "eol": version.is_eol(),
        },
    }


def get_migration_path(from_version: Version, to_version: Version) -> dict[str, Any]:
    """
    Get migration information between versions.

    Args:
        from_version: Source version
        to_version: Target version

    Returns:
        Dictionary with migration information
    """
    if from_version >= to_version:
        return {"error": "Target version must be newer than source version"}

    breaking_change = from_version.major != to_version.major

    # Get features added between versions
    from_features = get_all_features_up_to_version(from_version)
    to_features = get_all_features_up_to_version(to_version)
    new_features = to_features - from_features

    # Get versions in between
    intermediate_versions = [v for v in sorted(ALL_VERSIONS) if from_version < v <= to_version]

    return {
        "from_version": from_version.version_string,
        "to_version": to_version.version_string,
        "breaking_change": breaking_change,
        "new_features_count": len(new_features),
        "new_features": [f.value for f in sorted(new_features, key=lambda x: x.value)],
        "intermediate_versions": [v.version_string for v in intermediate_versions],
        "migration_guide_url": to_version.migration_guide_url,
        "rollback_supported": not breaking_change,
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "VersionStatus",
    "Feature",
    # Classes
    "Version",
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
    "get_version_headers",
    "get_version_info",
    "get_migration_path",
]
