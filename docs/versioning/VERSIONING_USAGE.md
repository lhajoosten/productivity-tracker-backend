# Versioning System Usage Guide

This document explains how to use the versioning and feature flag system in the Productivity Tracker API.

## Overview

The versioning system is based on **Semantic Versioning 2.0.0** and provides:
- Version lifecycle management (planned, beta, active, deprecated, EOL)
- Feature flags tied to specific versions
- Feature dependencies
- Environment-specific feature toggles
- CLI commands for version/roadmap inspection

## Architecture

### Core Components

1. **`productivity_tracker/versioning/version.py`** - Single source of truth for app version
   - `__version__` = "1.0.0-beta"
   - Contains release metadata

2. **`productivity_tracker/versioning/versioning.py`** - Version & feature management
   - `Version` class with lifecycle management
   - `Feature` enum with all features across versions
   - `VERSION_FEATURES` mapping of versions to their features
   - Helper functions for feature checking

3. **`productivity_tracker/versioning/utils.py`** - Utility functions
   - Version extraction from requests
   - Response header management
   - Version filtering helpers

4. **`productivity_tracker/versioning/__init__.py`** - Public API exports

## CLI Commands

### Show Current Version
```bash
poetry run pt version
```

Shows:
- Current application version
- Release date
- Release name
- API version

### View Roadmap
```bash
# Show full roadmap
poetry run pt roadmap

# Show specific version details
poetry run pt roadmap --version 1.0
poetry run pt roadmap -v 1.1

# Show all features across versions
poetry run pt roadmap --features
```

## Using Feature Flags

### Check if Feature is Enabled

```python
from productivity_tracker.versioning import is_feature_enabled, Feature, CURRENT_VERSION

# Check against current version
if is_feature_enabled(Feature.TASK_MANAGEMENT):
    # Task management is available
    pass

# Check against specific version
if is_feature_enabled(Feature.RATE_LIMITING, version=V1_1):
    # Rate limiting available in v1.1
    pass

# Check with environment override
if is_feature_enabled(Feature.TASK_MANAGEMENT, environment="development"):
    # In dev, all features are enabled
    pass
```

### Protect Endpoints with Feature Flags

```python
from fastapi import APIRouter
from productivity_tracker.versioning import require_feature, Feature

router = APIRouter()

@router.post("/tasks")
@require_feature(Feature.TASK_MANAGEMENT)
async def create_task():
    """This endpoint only works if TASK_MANAGEMENT feature is enabled."""
    pass
```

### Get All Features for a Version

```python
from productivity_tracker.versioning import get_all_features_up_to_version, V1_2

# Get cumulative features (v1.0 + v1.1 + v1.2)
features = get_all_features_up_to_version(V1_2)
```

### Check Feature Dependencies

```python
from productivity_tracker.versioning import check_feature_dependencies, Feature

# Check if all dependencies are satisfied
if check_feature_dependencies(Feature.SMART_TASK_SUGGESTIONS):
    # TASK_MANAGEMENT and AI_PRODUCTIVITY_PATTERNS are enabled
    pass
```

## Version Lifecycle States

- **PLANNED** - Version planned but not started
- **IN_DEVELOPMENT** - Active development
- **BETA** - Feature complete, in testing
- **RC** - Release candidate
- **ACTIVE** - Current production version
- **MAINTENANCE** - Supported but not actively developed
- **DEPRECATED** - Scheduled for removal
- **EOL** - No longer supported

## Version Definitions

All versions are defined in `versioning.py`:

```python
V1_0 = Version(
    major=1,
    minor=0,
    patch=0,
    prerelease="beta",
    status=VersionStatus.ACTIVE,
    release_date=date(2025, 11, 1),
    docs_url="/docs",
)

V1_1 = Version(
    major=1,
    minor=1,
    patch=0,
    status=VersionStatus.PLANNED,
    docs_url="/docs/v1.1",
)
```

## Adding New Features

### 1. Add Feature to Enum

In `versioning.py`, add to the `Feature` enum under the appropriate version section:

```python
class Feature(str, Enum):
    # Version 1.2.0 - Productivity Tracking Core (PLANNED)
    TIME_TRACKING = "time_tracking"
    TASK_MANAGEMENT = "task_management"
    YOUR_NEW_FEATURE = "your_new_feature"  # Add here
```

### 2. Map Feature to Version

```python
VERSION_FEATURES: dict[Version, set[Feature]] = {
    V1_2: {
        Feature.TIME_TRACKING,
        Feature.TASK_MANAGEMENT,
        Feature.YOUR_NEW_FEATURE,  # Add here
    },
}
```

### 3. Add Dependencies (Optional)

```python
FEATURE_DEPENDENCIES: dict[Feature, set[Feature]] = {
    Feature.YOUR_NEW_FEATURE: {Feature.TASK_MANAGEMENT},  # Requires task management
}
```

## Environment-Specific Features

Configure in `ENVIRONMENT_FEATURES`:

```python
ENVIRONMENT_FEATURES: dict[str, set[Feature]] = {
    "development": set(Feature),  # All features
    "staging": VERSION_FEATURES[V1_0],  # Only v1.0
    "production": VERSION_FEATURES[V1_0],  # Only v1.0
}
```

## API Response Headers

The system automatically adds version headers to responses:

```
API-Version: 1.0.0-beta
API-Status: active
API-Deprecated: false
Link: </docs>; rel="documentation"
```

For deprecated versions, adds:
```
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
```

## Version Comparison

```python
from productivity_tracker.versioning import V1_0, V1_1, V2_0

# Version comparison
assert V1_0 < V1_1 < V2_0

# Compatibility check (same major version)
assert V1_0.is_compatible_with(V1_1)  # True
assert not V1_0.is_compatible_with(V2_0)  # False (breaking change)

# Breaking change detection
assert V2_0.is_breaking_change_from(V1_0)  # True
```

## Migration Between Versions

```python
from productivity_tracker.versioning import get_migration_path, V1_0, V1_3

migration_info = get_migration_path(V1_0, V1_3)
# Returns:
# {
#     "from_version": "1.0.0-beta",
#     "to_version": "1.3.0",
#     "breaking_change": False,
#     "new_features_count": 28,
#     "new_features": [...],
#     "intermediate_versions": ["1.1.0", "1.2.0"],
#     "rollback_supported": True
# }
```

## Best Practices

1. **Always use feature flags** for new functionality
2. **Check dependencies** before enabling dependent features
3. **Use environment toggles** for gradual rollouts
4. **Document breaking changes** in version definitions
5. **Set EOL dates** when deprecating versions
6. **Keep VERSION_ROADMAP.md in sync** with code

## Updating Current Version

When releasing a new version:

1. Update `productivity_tracker/versioning/version.py`:
   ```python
   __version__ = "1.1.0"
   __version_info__ = (1, 1, 0)
   RELEASE_DATE = date(2025, 2, 1)
   RELEASE_NAME = "Security & Validation Enhancement"
   ```

2. Update version status in `versioning.py`:
   ```python
   V1_1 = Version(
       major=1,
       minor=1,
       patch=0,
       status=VersionStatus.ACTIVE,  # Change from PLANNED
       release_date=date(2025, 2, 1),  # Add release date
   )

   CURRENT_VERSION = V1_1  # Update current
   LATEST_VERSION = V1_1   # Update latest
   ```

3. Update previous version to MAINTENANCE if needed:
   ```python
   V1_0 = Version(
       ...
       status=VersionStatus.MAINTENANCE,
   )
   ```

## Reference

- **Versioning Strategy**: `docs/VERSIONING_STRATEGY.md`
- **Version Roadmap**: `docs/VERSION_ROADMAP.md`
- **Semantic Versioning**: https://semver.org/

## Support

For questions or issues with the versioning system, see:
- Implementation: `productivity_tracker/versioning/`
- Tests: `tests/utils/test_versioning.py`
- CLI: `productivity_tracker/cli.py` (`roadmap` and `version` commands)
