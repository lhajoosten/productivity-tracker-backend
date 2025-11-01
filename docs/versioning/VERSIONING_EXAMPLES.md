"""
Example Usage of Versioning and Feature Flags

This file demonstrates how to use the versioning system and feature flags
in your API endpoints and services.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from productivity_tracker.versioning import (
    Feature,
    is_feature_enabled,
    require_feature,
    get_version_info,
    get_enabled_features,
    CURRENT_VERSION,
)

# Example router
router = APIRouter(prefix="/api/v1", tags=["examples"])


# =============================================================================
# Example 1: Check feature flag manually
# =============================================================================

@router.get("/tasks")
async def get_tasks():
    """
    Example endpoint that checks if task management feature is enabled
    """
    if not is_feature_enabled(Feature.TASK_MANAGEMENT):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task management feature is not available in this version. "
                   "This feature will be available in v1.2.0"
        )

    # Your task management logic here
    return {"tasks": []}


# =============================================================================
# Example 2: Using the decorator (recommended)
# =============================================================================

@router.get("/time-entries")
@require_feature(Feature.TIME_TRACKING)
async def get_time_entries():
    """
    Example endpoint using decorator for feature flag checking
    The decorator automatically returns 404 if feature is not enabled
    """
    # Your time tracking logic here
    return {"time_entries": []}


# =============================================================================
# Example 3: Conditional feature availability
# =============================================================================

@router.get("/dashboard")
async def get_dashboard():
    """
    Example endpoint with conditional features
    """
    response = {
        "basic_stats": {"users": 10, "organizations": 5},
    }

    # Add analytics if feature is enabled
    if is_feature_enabled(Feature.ANALYTICS_DASHBOARD):
        response["analytics"] = {
            "productivity_score": 85,
            "trends": ["up", "up", "stable"]
        }

    # Add notifications if feature is enabled
    if is_feature_enabled(Feature.NOTIFICATION_SYSTEM):
        response["notifications"] = {
            "unread_count": 3,
            "latest": "New task assigned"
        }

    return response


# =============================================================================
# Example 4: Version information endpoint
# =============================================================================

@router.get("/version")
async def get_api_version():
    """
    Return current API version and available features
    """
    return get_version_info()


# =============================================================================
# Example 5: Feature discovery endpoint
# =============================================================================

@router.get("/features")
async def get_available_features():
    """
    Return all features available in current version
    """
    enabled_features = get_enabled_features()

    return {
        "version": CURRENT_VERSION.version_string,
        "api_prefix": CURRENT_VERSION.prefix,
        "features": [f.value for f in enabled_features],
        "feature_count": len(enabled_features),
    }


# =============================================================================
# Example 6: Service layer usage
# =============================================================================

class TaskService:
    """Example service class using feature flags"""

    def __init__(self):
        # Check if required features are available
        if not is_feature_enabled(Feature.TASK_MANAGEMENT):
            raise RuntimeError(
                "TaskService requires TASK_MANAGEMENT feature to be enabled"
            )

    async def create_task(self, task_data: dict):
        """Create a new task"""
        # Basic task creation
        task = {"id": 1, **task_data}

        # Add AI suggestions if feature is enabled
        if is_feature_enabled(Feature.SMART_TASK_SUGGESTIONS):
            task["ai_suggestions"] = self._get_ai_suggestions(task)

        return task

    def _get_ai_suggestions(self, task: dict):
        """Get AI-powered suggestions (only available in v2.1+)"""
        return {
            "estimated_time": "2 hours",
            "similar_tasks": [1, 2, 3],
            "recommended_assignee": "user@example.com"
        }


# =============================================================================
# Example 7: Environment-based feature flags
# =============================================================================

from productivity_tracker.core.settings import settings

@router.get("/experimental-features")
async def get_experimental_features():
    """
    Example of environment-based feature availability
    In development, all features are enabled for testing
    """
    # This will return all features in development environment
    features = get_enabled_features(environment=settings.ENVIRONMENT)

    return {
        "environment": settings.ENVIRONMENT,
        "all_features_enabled": settings.is_development,
        "features": [f.value for f in features],
    }


# =============================================================================
# Example 8: Version-specific endpoint behavior
# =============================================================================

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """
    Example showing how endpoint behavior can evolve across versions
    """
    # Basic user data (available in all versions)
    user = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
    }

    # Add audit trail if feature is enabled (v1.1+)
    if is_feature_enabled(Feature.AUDIT_LOGGING):
        user["audit"] = {
            "created_at": "2025-01-01",
            "last_modified": "2025-01-15",
            "modified_by": "admin"
        }

    # Add performance metrics if feature is enabled (v1.3+)
    if is_feature_enabled(Feature.PERFORMANCE_METRICS):
        user["performance"] = {
            "tasks_completed": 42,
            "productivity_score": 85,
            "average_completion_time": "2.5 hours"
        }

    # Add AI insights if feature is enabled (v2.1+)
    if is_feature_enabled(Feature.AI_PRODUCTIVITY_PATTERNS):
        user["ai_insights"] = {
            "work_pattern": "morning_person",
            "peak_productivity": "9am-11am",
            "burnout_risk": "low"
        }

    return user


# =============================================================================
# Example 9: Migration helper for deprecated features
# =============================================================================

@router.get("/old-endpoint")
async def deprecated_endpoint():
    """
    Example of handling deprecated endpoints with migration guidance
    """
    # In production, you might want to track deprecation usage
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Deprecated endpoint /old-endpoint accessed")

    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "error": "This endpoint has been deprecated",
            "migration": "Please use /api/v2/new-endpoint instead",
            "sunset_date": "2027-01-01",
            "documentation": "https://docs.productivity-tracker.com/migration/v2"
        }
    )


# =============================================================================
# Usage in your main application
# =============================================================================

"""
# In your main.py or route setup:

from productivity_tracker.versioning import CURRENT_VERSION, get_enabled_features

app = FastAPI(
    title="Productivity Tracker API",
    version=CURRENT_VERSION.version_string,
    docs_url=f"{CURRENT_VERSION.prefix}/docs",
)

# Log enabled features on startup
@app.on_event("startup")
async def log_features():
    features = get_enabled_features()
    logger.info(f"API Version: {CURRENT_VERSION.version_string}")
    logger.info(f"Enabled features: {len(features)}")
    for feature in features:
        logger.debug(f"  - {feature.value}")
"""
