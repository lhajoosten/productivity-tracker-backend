"""
Versioning and Feature Flag Management System

This module provides enums and utilities for the database-backed versioning system.
The actual version and feature data is stored in the database.

Key Components:
- Feature enum: All available features
- VersionStatus enum: Version lifecycle statuses
- Helper functions: For working with database version data
"""

from enum import Enum

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
    Each feature can be enabled/disabled independently via the database.
    """

    # ========================================================================
    # Version 0.1.0-beta - Foundation (ACTIVE)
    # ========================================================================
    ORGANIZATION_MANAGEMENT = "organization_management"
    DEPARTMENT_MANAGEMENT = "department_management"
    TEAM_MANAGEMENT = "team_management"
    USER_MANAGEMENT = "user_management"
    RBAC_SYSTEM = "rbac_system"
    PERMISSION_SYSTEM = "permission_system"
    COOKIE_AUTHENTICATION = "cookie_authentication"
    HEALTH_CHECKS = "health_checks"
    API_DOCUMENTATION = "api_documentation"
    ERROR_HANDLING = "error_handling"
    DATABASE_MIGRATIONS = "database_migrations"

    # ========================================================================
    # Version 0.2.0-beta - Security Hardening (PLANNED)
    # ========================================================================
    RATE_LIMITING = "rate_limiting"
    PASSWORD_COMPLEXITY = "password_complexity"  # nosec
    ACCOUNT_LOCKOUT = "account_lockout"  # nosec
    PASSWORD_RESET = "password_reset"  # nosec
    API_KEY_AUTH = "api_key_auth"
    INPUT_SANITIZATION = "input_sanitization"
    AUDIT_LOGGING = "audit_logging"
    LOGIN_ACTIVITY_TRACKING = "login_activity_tracking"
    TWOFA_AUTH = "two_factor_auth"

    # ========================================================================
    # Version 0.3.0-beta - Collaboration and Feedback (PLANNED)
    # ========================================================================
    SHARED_WORKSPACES = "shared_workspaces"
    FEEDBACK_SYSTEM = "feedback_system"
    COMMENTS_SYSTEM = "comments_system"

    # ========================================================================
    # Version 0.4.0-beta - Time Tracking Core (PLANNED)
    # ========================================================================
    TIME_TRACKING = "time_tracking"
    REPORTING_SYSTEM = "reporting_system"

    # ========================================================================
    # Version 0.5.0-beta - Task & Project Management (PLANNED)
    # ========================================================================
    TASK_MANAGEMENT = "task_management"
    PROJECT_MANAGEMENT = "project_management"
    TASK_DEPENDENCIES = "task_dependencies"
    SUBTASKS = "subtasks"
    TAGS_SYSTEM = "tags_system"
    CATEGORIES = "categories"
    TEAM_CALENDAR = "team_calendar"
    GOAL_TRACKING = "goal_tracking"

    # ========================================================================
    # Version 0.6.0-beta - Analytics & Notifications (PLANNED)
    # ========================================================================
    ANALYTICS_DASHBOARD = "analytics_dashboard"
    PRODUCTIVITY_TRENDS = "productivity_trends"
    TASK_COMPLETION_ANALYTICS = "task_completion_analytics"
    CUSTOM_REPORTS = "custom_reports"
    REPORT_EXPORT = "report_export"
    SCHEDULED_REPORTS = "scheduled_reports"
    KPI_TRACKING = "kpi_tracking"
    NOTIFICATIONS = "notifications"
    EMAIL_NOTIFICATIONS = "email_notifications"

    # ========================================================================
    # Version 0.7.0-beta - Search & Filtering (PLANNED)
    # ========================================================================
    ADVANCED_SEARCH = "advanced_search"
    FULL_TEXT_SEARCH = "full_text_search"
    SAVED_SEARCHES = "saved_searches"

    # ========================================================================
    # Version 0.8.0-beta - Integration & Extensions (PLANNED)
    # ========================================================================
    WEBHOOKS = "webhooks"
    CALENDAR_SYNC = "calendar_sync"
    EMAIL_INTEGRATION = "email_integration"
    SLACK_INTEGRATION = "slack_integration"

    # ========================================================================
    # Version 0.9.0-beta - Performance & Scalability (PLANNED)
    # ========================================================================
    REDIS_CACHING = "redis_caching"
    QUERY_OPTIMIZATION = "query_optimization"
    BULK_OPERATIONS = "bulk_operations"
    ASYNC_TASK_PROCESSING = "async_task_processing"
    DATABASE_PARTITIONING = "database_partitioning"
    READ_REPLICAS = "read_replicas"

    # ========================================================================
    # Version 1.1.0 - Collaboration Enhancements (PLANNED)
    # ========================================================================
    REAL_TIME_NOTIFICATIONS = "real_time_notifications"
    MENTIONS = "mentions"
    FILE_ATTACHMENTS = "file_attachments"
    FILE_VERSIONING = "file_versioning"

    # ========================================================================
    # Version 1.2.0 - Mobile Optimization (PLANNED)
    # ========================================================================
    MOBILE_API = "mobile_api"
    OFFLINE_SYNC = "offline_sync"
    PUSH_NOTIFICATIONS = "push_notifications"

    # ========================================================================
    # Version 1.6.0 - Integration & Extensibility (PLANNED)
    # ========================================================================
    OAUTH2_INTEGRATION = "oauth2_integration"
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

    # ========================================================================
    # Version 2.1.0+ - AI & Machine Learning (PLANNED)
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


class FeatureCategory(str, Enum):
    """Feature categories for organization."""

    FOUNDATION = "foundation"
    SECURITY = "security"
    PRODUCTIVITY = "productivity"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    ENTERPRISE = "enterprise"
    AI_ML = "ai_ml"
    ACCESSIBILITY = "accessibility"
    OBSERVABILITY = "observability"


# Map features to their categories
FEATURE_CATEGORIES: dict[Feature, FeatureCategory] = {
    # Foundation
    Feature.ORGANIZATION_MANAGEMENT: FeatureCategory.FOUNDATION,
    Feature.DEPARTMENT_MANAGEMENT: FeatureCategory.FOUNDATION,
    Feature.TEAM_MANAGEMENT: FeatureCategory.FOUNDATION,
    Feature.USER_MANAGEMENT: FeatureCategory.FOUNDATION,
    Feature.RBAC_SYSTEM: FeatureCategory.FOUNDATION,
    Feature.PERMISSION_SYSTEM: FeatureCategory.FOUNDATION,
    Feature.HEALTH_CHECKS: FeatureCategory.FOUNDATION,
    Feature.API_DOCUMENTATION: FeatureCategory.FOUNDATION,
    Feature.DATABASE_MIGRATIONS: FeatureCategory.FOUNDATION,
    # Security
    Feature.COOKIE_AUTHENTICATION: FeatureCategory.SECURITY,
    Feature.RATE_LIMITING: FeatureCategory.SECURITY,
    Feature.PASSWORD_COMPLEXITY: FeatureCategory.SECURITY,
    Feature.ACCOUNT_LOCKOUT: FeatureCategory.SECURITY,
    Feature.PASSWORD_RESET: FeatureCategory.SECURITY,
    Feature.API_KEY_AUTH: FeatureCategory.SECURITY,
    Feature.INPUT_SANITIZATION: FeatureCategory.SECURITY,
    Feature.AUDIT_LOGGING: FeatureCategory.SECURITY,
    Feature.LOGIN_ACTIVITY_TRACKING: FeatureCategory.SECURITY,
    Feature.TWOFA_AUTH: FeatureCategory.SECURITY,
    # Productivity
    Feature.TIME_TRACKING: FeatureCategory.PRODUCTIVITY,
    Feature.TASK_MANAGEMENT: FeatureCategory.PRODUCTIVITY,
    Feature.PROJECT_MANAGEMENT: FeatureCategory.PRODUCTIVITY,
    Feature.TASK_DEPENDENCIES: FeatureCategory.PRODUCTIVITY,
    Feature.SUBTASKS: FeatureCategory.PRODUCTIVITY,
    Feature.TAGS_SYSTEM: FeatureCategory.PRODUCTIVITY,
    Feature.CATEGORIES: FeatureCategory.PRODUCTIVITY,
    Feature.TEAM_CALENDAR: FeatureCategory.PRODUCTIVITY,
    Feature.GOAL_TRACKING: FeatureCategory.PRODUCTIVITY,
    # Analytics
    Feature.ANALYTICS_DASHBOARD: FeatureCategory.ANALYTICS,
    Feature.PRODUCTIVITY_TRENDS: FeatureCategory.ANALYTICS,
    Feature.TASK_COMPLETION_ANALYTICS: FeatureCategory.ANALYTICS,
    Feature.REPORTING_SYSTEM: FeatureCategory.ANALYTICS,
    Feature.CUSTOM_REPORTS: FeatureCategory.ANALYTICS,
    Feature.REPORT_EXPORT: FeatureCategory.ANALYTICS,
    Feature.SCHEDULED_REPORTS: FeatureCategory.ANALYTICS,
    Feature.KPI_TRACKING: FeatureCategory.ANALYTICS,
    Feature.ADVANCED_SEARCH: FeatureCategory.ANALYTICS,
    Feature.FULL_TEXT_SEARCH: FeatureCategory.ANALYTICS,
    Feature.SAVED_SEARCHES: FeatureCategory.ANALYTICS,
    # Collaboration
    Feature.SHARED_WORKSPACES: FeatureCategory.COLLABORATION,
    Feature.FEEDBACK_SYSTEM: FeatureCategory.COLLABORATION,
    Feature.COMMENTS_SYSTEM: FeatureCategory.COLLABORATION,
    Feature.NOTIFICATIONS: FeatureCategory.COLLABORATION,
    Feature.EMAIL_NOTIFICATIONS: FeatureCategory.COLLABORATION,
    Feature.REAL_TIME_NOTIFICATIONS: FeatureCategory.COLLABORATION,
    Feature.MENTIONS: FeatureCategory.COLLABORATION,
    Feature.FILE_ATTACHMENTS: FeatureCategory.COLLABORATION,
    Feature.FILE_VERSIONING: FeatureCategory.COLLABORATION,
    # Performance
    Feature.REDIS_CACHING: FeatureCategory.PERFORMANCE,
    Feature.QUERY_OPTIMIZATION: FeatureCategory.PERFORMANCE,
    Feature.BULK_OPERATIONS: FeatureCategory.PERFORMANCE,
    Feature.ASYNC_TASK_PROCESSING: FeatureCategory.PERFORMANCE,
    Feature.DATABASE_PARTITIONING: FeatureCategory.PERFORMANCE,
    Feature.READ_REPLICAS: FeatureCategory.PERFORMANCE,
    # Integration
    Feature.WEBHOOKS: FeatureCategory.INTEGRATION,
    Feature.CALENDAR_SYNC: FeatureCategory.INTEGRATION,
    Feature.EMAIL_INTEGRATION: FeatureCategory.INTEGRATION,
    Feature.SLACK_INTEGRATION: FeatureCategory.INTEGRATION,
    Feature.OAUTH2_INTEGRATION: FeatureCategory.INTEGRATION,
    Feature.PLUGIN_FRAMEWORK: FeatureCategory.INTEGRATION,
    Feature.GRAPHQL_ENDPOINT: FeatureCategory.INTEGRATION,
    Feature.API_ANALYTICS: FeatureCategory.INTEGRATION,
    # Enterprise
    Feature.MOBILE_API: FeatureCategory.ENTERPRISE,
    Feature.OFFLINE_SYNC: FeatureCategory.ENTERPRISE,
    Feature.PUSH_NOTIFICATIONS: FeatureCategory.ENTERPRISE,
    Feature.SSO_SAML: FeatureCategory.ENTERPRISE,
    Feature.MULTI_REGION: FeatureCategory.ENTERPRISE,
    Feature.GDPR_COMPLIANCE: FeatureCategory.ENTERPRISE,
    Feature.SOC2_COMPLIANCE: FeatureCategory.ENTERPRISE,
    Feature.ENCRYPTION_AT_REST: FeatureCategory.ENTERPRISE,
    Feature.FIELD_LEVEL_ENCRYPTION: FeatureCategory.ENTERPRISE,
    # AI & ML
    Feature.AI_PRODUCTIVITY_PATTERNS: FeatureCategory.AI_ML,
    Feature.AUTO_TIME_CATEGORIZATION: FeatureCategory.AI_ML,
    Feature.SMART_TASK_SUGGESTIONS: FeatureCategory.AI_ML,
    Feature.WORKLOAD_BALANCING: FeatureCategory.AI_ML,
    Feature.PREDICTIVE_ANALYTICS: FeatureCategory.AI_ML,
    Feature.NLP_QUERY: FeatureCategory.AI_ML,
    Feature.AUTOMATION_ENGINE: FeatureCategory.AI_ML,
    # Accessibility
    Feature.INTERNATIONALIZATION: FeatureCategory.ACCESSIBILITY,
    Feature.MULTI_LANGUAGE: FeatureCategory.ACCESSIBILITY,
    Feature.RTL_SUPPORT: FeatureCategory.ACCESSIBILITY,
    Feature.WCAG_COMPLIANCE: FeatureCategory.ACCESSIBILITY,
    Feature.REGIONAL_CUSTOMIZATION: FeatureCategory.ACCESSIBILITY,
    # Observability
    Feature.DISTRIBUTED_TRACING: FeatureCategory.OBSERVABILITY,
    Feature.METRICS_COLLECTION: FeatureCategory.OBSERVABILITY,
    Feature.APM: FeatureCategory.OBSERVABILITY,
    Feature.CHAOS_ENGINEERING: FeatureCategory.OBSERVABILITY,
    Feature.SLO_TRACKING: FeatureCategory.OBSERVABILITY,
}


# ============================================================================
# HELPER FUNCTIONS (for working with database entities)
# ============================================================================


def get_feature_category(feature: Feature) -> FeatureCategory:
    """Get the category for a feature."""
    return FEATURE_CATEGORIES.get(feature, FeatureCategory.FOUNDATION)
