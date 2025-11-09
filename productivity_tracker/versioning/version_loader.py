"""
Version Configuration Loader

This module loads version configuration from the shared versions.json file,
which serves as the single source of truth for both frontend and backend.
"""

import json
from datetime import date, datetime
from pathlib import Path

from productivity_tracker.database.entities.version import Version
from productivity_tracker.versioning.versioning import Feature, VersionStatus

# Path to the shared versions.json (at project root)
VERSIONS_JSON_PATH = Path(__file__).parent.parent.parent.parent / "versions.json"


# ============================================================================
# FEATURE NAME MAPPING
# ============================================================================

# Map human-readable feature names from JSON to Feature enum values
FEATURE_NAME_MAP: dict[str, Feature] = {
    # v0.1.0-alpha
    "Basic API structure": Feature.API_DOCUMENTATION,
    "Database setup": Feature.DATABASE_MIGRATIONS,
    "Cookie authentication scaffold": Feature.COOKIE_AUTHENTICATION,
    # v0.1.0-beta (Current)
    "API Docs & Health checks": Feature.HEALTH_CHECKS,
    "Cookie authentication": Feature.COOKIE_AUTHENTICATION,
    "Organization management": Feature.ORGANIZATION_MANAGEMENT,
    "Department management": Feature.DEPARTMENT_MANAGEMENT,
    "Team management": Feature.TEAM_MANAGEMENT,
    "User management": Feature.USER_MANAGEMENT,
    "RBAC & Permission system": Feature.RBAC_SYSTEM,
    "Database migrations": Feature.DATABASE_MIGRATIONS,
    # v0.2.0-alpha/beta - Security Hardening
    "Rate limiting prototype": Feature.RATE_LIMITING,
    "Password rules testing": Feature.PASSWORD_COMPLEXITY,
    "MFA exploration": Feature.ACCOUNT_LOCKOUT,
    "Rate limiting": Feature.RATE_LIMITING,
    "Password complexity rules": Feature.PASSWORD_COMPLEXITY,
    "Multifactor authentication with OTP": Feature.ACCOUNT_LOCKOUT,
    "Account lockout": Feature.ACCOUNT_LOCKOUT,
    "Password reset flow": Feature.PASSWORD_RESET,
    "Input sanitization": Feature.INPUT_SANITIZATION,
    "Audit logging": Feature.AUDIT_LOGGING,
    # v0.3.0-beta - Collaboration
    "Workspace management": Feature.SHARED_WORKSPACES,
    "Feedback system": Feature.COMMENTS_SYSTEM,
    "Comment system": Feature.COMMENTS_SYSTEM,
    # v0.4.0-beta - Time Tracking
    "Time tracking": Feature.TIME_TRACKING,
    "Time sheets": Feature.TIME_TRACKING,
    "Basic reporting": Feature.REPORTING_SYSTEM,
    # v0.5.0-beta - Task & Project Management
    "Task management": Feature.TASK_MANAGEMENT,
    "Task dependencies": Feature.TASK_DEPENDENCIES,
    "Kanban Board": Feature.TASK_MANAGEMENT,
    "Task Calendar": Feature.TEAM_CALENDAR,
    "Project management": Feature.PROJECT_MANAGEMENT,
    "Milestones": Feature.GOAL_TRACKING,
    "Archiving": Feature.TASK_MANAGEMENT,
    # v0.6.0-beta - Analytics & Notifications
    "Notifications system": Feature.NOTIFICATIONS,
    "Email notifications": Feature.EMAIL_NOTIFICATIONS,
    "Analytics dashboard": Feature.ANALYTICS_DASHBOARD,
    "Productivity trends": Feature.PRODUCTIVITY_TRENDS,
    # v0.7.0-beta - Search & Filtering
    "Advanced search": Feature.ADVANCED_SEARCH,
    "Full-text search": Feature.FULL_TEXT_SEARCH,
    "Saved searches": Feature.SAVED_SEARCHES,
    "Custom filters": Feature.ADVANCED_SEARCH,
    "Tags system": Feature.TAGS_SYSTEM,
    # v0.8.0-beta - Integration & Extensions
    "Webhooks": Feature.WEBHOOKS,
    "API key authentication": Feature.API_KEY_AUTH,
    "Calendar sync (Google, Outlook)": Feature.CALENDAR_SYNC,
    "Email integration": Feature.EMAIL_INTEGRATION,
    "Slack notifications": Feature.SLACK_INTEGRATION,
    # v0.9.0-beta - Performance & Scalability
    "Redis caching": Feature.REDIS_CACHING,
    "Query optimization": Feature.QUERY_OPTIMIZATION,
    "Bulk operations": Feature.BULK_OPERATIONS,
    "Async task processing": Feature.ASYNC_TASK_PROCESSING,
    "Database indexing": Feature.DATABASE_PARTITIONING,
    # v1.1.0 - Collaboration Enhancements
    "Real-time collaboration": Feature.REAL_TIME_NOTIFICATIONS,
    "Live cursors": Feature.REAL_TIME_NOTIFICATIONS,
    "Mentions system": Feature.MENTIONS,
    "Activity feed": Feature.NOTIFICATIONS,
    # v1.2.0 - Mobile Optimization
    "Mobile-optimized endpoints": Feature.MOBILE_API,
    "Offline sync": Feature.OFFLINE_SYNC,
    "Push notifications": Feature.PUSH_NOTIFICATIONS,
    "Mobile app support": Feature.MOBILE_API,
    # v2.0.0+ - AI/ML Features
    "Vector database integration (Pinecone/Qdrant/Weaviate)": Feature.AI_PRODUCTIVITY_PATTERNS,
    "LLM provider abstraction layer (OpenAI, Anthropic, Azure OpenAI)": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Embedding service infrastructure": Feature.AI_PRODUCTIVITY_PATTERNS,
    "AI request queue and job processing": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Token usage tracking and billing": Feature.API_ANALYTICS,
    "AI model configuration management": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Document ingestion pipeline": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Text chunking strategies": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Semantic search implementation": Feature.FULL_TEXT_SEARCH,
    "Context retrieval service": Feature.AI_PRODUCTIVITY_PATTERNS,
    "RAG prompt engineering templates": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Citation and source tracking": Feature.AUDIT_LOGGING,
    "AI chat assistant for tasks and projects": Feature.SMART_TASK_SUGGESTIONS,
    "Natural language task creation": Feature.NLP_QUERY,
    "Intelligent task suggestions": Feature.SMART_TASK_SUGGESTIONS,
    "Context-aware recommendations": Feature.SMART_TASK_SUGGESTIONS,
    "Meeting notes summarization": Feature.NLP_QUERY,
    "Action item extraction from text": Feature.NLP_QUERY,
    "Task duration prediction (ML models)": Feature.PREDICTIVE_ANALYTICS,
    "Project timeline forecasting": Feature.PREDICTIVE_ANALYTICS,
    "Workload balancing recommendations": Feature.WORKLOAD_BALANCING,
    "Burnout risk detection": Feature.PREDICTIVE_ANALYTICS,
    "Productivity pattern analysis": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Anomaly detection in time tracking": Feature.PREDICTIVE_ANALYTICS,
    "Organization knowledge base (RAG-powered)": Feature.AI_PRODUCTIVITY_PATTERNS,
    "Semantic document search": Feature.FULL_TEXT_SEARCH,
    "Automatic documentation generation": Feature.AUTOMATION_ENGINE,
    "Knowledge graph construction": Feature.AI_PRODUCTIVITY_PATTERNS,
}


def parse_version_string(version_str: str) -> tuple[int, int, int, str | None]:
    """
    Parse version string into components.

    Examples:
        "0.1.0-beta" -> (0, 1, 0, "beta")
        "1.0.0" -> (1, 0, 0, None)
        "2.0.0-alpha.1" -> (2, 0, 0, "alpha.1")
    """
    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")

    # Split on '-' to separate version from prerelease
    parts = version_str.split("-", 1)
    core_version = parts[0]
    prerelease = parts[1] if len(parts) > 1 else None

    # Split core version
    major, minor, patch = map(int, core_version.split("."))

    return major, minor, patch, prerelease


def parse_date(date_str: str | None) -> date | None:
    """Parse ISO date string to date object."""
    if not date_str:
        return None
    return datetime.fromisoformat(date_str).date()


def map_features(feature_names: list[str]) -> set[Feature]:
    """Map human-readable feature names to Feature enum values."""
    features = set()

    for name in feature_names:
        if name in FEATURE_NAME_MAP:
            features.add(FEATURE_NAME_MAP[name])
        else:
            # Log warning but don't fail - allows for descriptive features
            # that don't map to specific Feature enum values
            print(f"Warning: Feature '{name}' not mapped to enum value")

    return features


def load_versions_from_json() -> tuple[list[Version], Version, Version]:
    """
    Load all versions from versions.json.

    Returns:
        Tuple of (all_versions, current_version, latest_version)
    """
    if not VERSIONS_JSON_PATH.exists():
        raise FileNotFoundError(
            f"versions.json not found at {VERSIONS_JSON_PATH}. "
            "This file serves as the single source of truth for versioning."
        )

    with open(VERSIONS_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    versions_data = data.get("versions", [])
    all_versions: list[Version] = []
    current_version: Version | None = None
    latest_version: Version | None = None

    for version_data in versions_data:
        major, minor, patch, prerelease = parse_version_string(version_data["version"])

        # Map status
        status_str = version_data.get("status", "planned")
        try:
            status = VersionStatus(status_str)
        except ValueError:
            # Handle special statuses
            if status_str == "completed":
                status = VersionStatus.ACTIVE
            else:
                status = VersionStatus.PLANNED

        # Map features
        feature_names = version_data.get("features", [])
        features = map_features(feature_names)

        # Create Version object
        version = Version(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=prerelease,
            status=status,
            feature_flags=features,
            release_date=parse_date(version_data.get("releaseDate")),
            eol_date=parse_date(version_data.get("eolDate")),
            docs_url=f"/docs/{version_data['version']}",
        )

        all_versions.append(version)

        # Track current and latest
        if status_str == "active":
            current_version = version

        latest_version = version  # Last one processed

    # Default current to first active or latest
    if current_version is None:
        current_version = latest_version or all_versions[0]

    return all_versions, current_version, latest_version


def generate_version_features_map(versions: list[Version]) -> dict[Version, set[Feature]]:
    """
    Generate cumulative feature map for all versions.

    Each version includes all features from previous versions plus its own.
    """
    version_features: dict[Version, set[Feature]] = {}
    cumulative_features: set[Feature] = set()

    # Load versions.json to get features per version
    with open(VERSIONS_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for idx, version in enumerate(versions):
        version_data = data["versions"][idx]
        feature_names = version_data.get("features", [])
        new_features = map_features(feature_names)

        # Add to cumulative
        cumulative_features.update(new_features)

        # Store cumulative features for this version
        version_features[version] = cumulative_features.copy()

    return version_features
