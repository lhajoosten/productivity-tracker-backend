# Versioning Strategy

This document defines the versioning approach for the Productivity Tracker API.

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format: **MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]**

### Version Components

```
1.2.3-beta.1+20251101
│ │ │   │      │
│ │ │   │      └─ Build metadata (optional)
│ │ │   └──────── Pre-release identifier (optional)
│ │ └──────────── PATCH version
│ └────────────── MINOR version
└──────────────── MAJOR version
```

### Versioning Rules

#### MAJOR Version (X.0.0)
Incremented when making **incompatible API changes**:
- Breaking changes to existing endpoints
- Removal of deprecated features
- Major architectural changes
- Changes to authentication/authorization mechanisms
- Database schema changes requiring data migration

**Examples:**
- Changing response structure of existing endpoints
- Removing endpoints or fields
- Changing authentication flow
- Modifying error response format

#### MINOR Version (1.X.0)
Incremented when adding **functionality in a backward-compatible manner**:
- New API endpoints
- New optional fields in requests/responses
- New features that don't break existing functionality
- Performance improvements
- New integrations

**Examples:**
- Adding new `/api/v1/tasks` endpoint
- Adding optional `description` field to User model
- Implementing new search capabilities
- Adding export functionality

#### PATCH Version (1.1.X)
Incremented for **backward-compatible bug fixes**:
- Bug fixes
- Security patches
- Documentation updates
- Internal refactoring with no API changes
- Performance optimizations with no breaking changes

**Examples:**
- Fixing validation error
- Correcting authentication bug
- Updating dependencies for security
- Fixing incorrect status codes

### Pre-Release Versions

Format: `1.0.0-{stage}.{number}`

Stages (in order):
1. **alpha**: Internal development, unstable
2. **beta**: Feature complete, testing phase
3. **rc** (release candidate): Production-ready, final testing

Examples:
- `1.0.0-alpha.1`
- `1.0.0-beta.2`
- `1.0.0-rc.1`
- `1.0.0` (stable release)

---

## API Versioning Strategy

We use **URL path versioning** for clear, explicit version control.

### URL Structure

```
https://api.productivity-tracker.com/api/v{major}/resource
```

Examples:
- `/api/v1/users`
- `/api/v1/organizations`
- `/api/v2/users`

### Versioning Rules

1. **Major version in URL**: Only MAJOR version appears in the URL path
2. **Minor/Patch transparent**: MINOR and PATCH versions are backward-compatible and don't require URL changes
3. **Multiple versions supported**: Support N and N-1 major versions simultaneously
4. **Version header**: Optional `API-Version` header for fine-grained control

### Version Header (Optional)

Clients can specify exact version via header:

```http
GET /api/v1/users
API-Version: 1.2.3
```

Response includes:
```http
HTTP/1.1 200 OK
API-Version: 1.2.3
API-Deprecated: false
```

---

## Feature Flags

Feature flags enable gradual rollout and A/B testing without version proliferation.

### Feature Flag Structure

```python
from enum import Enum

class Feature(str, Enum):
    """Available feature flags"""
    ENHANCED_SECURITY = "enhanced_security"  # v1.1.0
    TIME_TRACKING = "time_tracking"          # v1.2.0
    ANALYTICS_DASHBOARD = "analytics"        # v1.3.0
    NOTIFICATIONS = "notifications"          # v1.4.0
    BULK_OPERATIONS = "bulk_operations"      # v1.5.0
```

### Feature Flag Management

Flags are managed in `versioning.py`:

```python
FEATURE_FLAGS = {
    "1.1": [Feature.ENHANCED_SECURITY],
    "1.2": [Feature.ENHANCED_SECURITY, Feature.TIME_TRACKING],
    "1.3": [Feature.ENHANCED_SECURITY, Feature.TIME_TRACKING, Feature.ANALYTICS_DASHBOARD],
}
```

### Feature Flag Usage

```python
from productivity_tracker.versioning.versioning import is_feature_enabled

if is_feature_enabled(Feature.TIME_TRACKING):
    # Enable time tracking endpoints
    pass
```

### Flag States

- **Development**: All upcoming features enabled for testing
- **Staging**: Selected features enabled for QA
- **Production**: Only stable, released features enabled
- **Beta Users**: Opt-in to experimental features

---

## Deprecation Strategy

### Deprecation Process

1. **Announce**: Document in release notes and API docs
2. **Mark**: Add deprecation warnings to responses
3. **Grace Period**: Minimum 2 minor versions or 6 months
4. **Remove**: Only in next major version

### Deprecation Headers

Deprecated endpoints return warning headers:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Dec 2026 23:59:59 GMT
Link: <https://docs.productivity-tracker.com/migration>; rel="deprecation"
```

### Deprecation Documentation

```python
@router.get(
    "/old-endpoint",
    deprecated=True,
    description="⚠️ DEPRECATED: Use /api/v1/new-endpoint instead. Will be removed in v2.0.0"
)
```

---

## Version Lifecycle

### Support Tiers

| Tier | Duration | Support Type |
|------|----------|--------------|
| **Active** | Current major version | Full support: features, bugs, security |
| **Maintenance** | Previous major version | Limited support: bugs, security |
| **End of Life** | After maintenance | No support |

### Timeline Example

```
v1.0.0 released: Jan 2025
├─ v1.1.0 - Apr 2025
├─ v1.2.0 - Jul 2025
├─ v1.3.0 - Oct 2025
└─ v2.0.0 - Jan 2026
   ├─ v1.x enters maintenance mode
   └─ v1.x EOL: Jan 2027 (12 months after v2.0.0)
```

---

## Database Versioning

### Migration Strategy

We use **Alembic** for database migrations:

```bash
alembic revision --autogenerate -m "Add time_entries table for v1.2"
alembic upgrade head
```

### Migration Principles

1. **Backward Compatible Migrations**: Always for MINOR versions
   - Add new tables/columns only
   - Don't remove or rename existing structures
   - Use default values for new required fields

2. **Breaking Migrations**: Only for MAJOR versions
   - Can remove/rename tables/columns
   - Provide migration scripts
   - Support rollback procedures

3. **Data Migrations**: Separate from schema changes
   ```bash
   alembic revision -m "Migrate user roles data for v2.0"
   ```

### Migration Naming Convention

```
{version}_{description}
```

Examples:
- `v1_2_add_time_entries_table`
- `v2_0_restructure_permissions`

---

## Dependency Versioning

### Python Dependencies

Use **Poetry** for dependency management with version constraints:

```toml
[tool.poetry.dependencies]
fastapi = "^0.119.0"  # Compatible minor/patch updates
sqlalchemy = "~2.0.25" # Compatible patch updates only
```

### Version Pinning Strategy

- **Production**: Pin exact versions in `poetry.lock`
- **Development**: Allow minor version updates for testing
- **Security**: Regular dependency audits with `safety`

```bash
poetry update
safety check
```

---

## Release Process

### 1. Planning Phase
- Define features for version
- Update VERSION_ROADMAP.md
- Create feature branches

### 2. Development Phase
- Implement features behind feature flags
- Write tests (maintain 80%+ coverage)
- Update documentation

### 3. Pre-Release Phase

```bash
# Update version
poetry version 1.2.0-beta.1

# Run quality checks
pytest --cov
ruff check .
mypy productivity_tracker
bandit -r productivity_tracker

# Create release branch
git checkout -b release/v1.2.0
```

### 4. Release Phase

```bash
# Final version bump
poetry version 1.2.0

# Tag release
git tag -a v1.2.0 -m "Release v1.2.0: Time Tracking Core"
git push origin v1.2.0

# Deploy to production
docker build -t productivity-tracker:1.2.0 .
```

### 5. Post-Release Phase
- Monitor error rates and performance
- Gather user feedback
- Plan hotfixes if needed
- Update changelog

---

## Version Configuration

### Single Source of Truth

All version information is defined in `productivity_tracker/versioning/version.py`:

```python
# productivity_tracker/versioning/version.py
__version__ = "1.2.0"
__version_info__ = (1, 2, 0)
__version_tuple__ = (1, 2, 0, "final", 0)

# Release metadata
RELEASE_DATE = "2025-07-01"
RELEASE_NAME = "Productivity Core"
```

### Version Usage

```python
# In application
from productivity_tracker.versioning.version import __version__

app = FastAPI(version=__version__)
```

### Environment-Specific Versions

```python
# versioning.py
from productivity_tracker.core.settings import settings

def get_active_version():
    """Get version based on environment"""
    if settings.is_development:
        return "1.2.0-dev"
    elif settings.is_staging:
        return "1.2.0-rc.1"
    return __version__
```

---

## Client SDK Versioning

When providing client SDKs, follow the same versioning:

- **SDK version matches API version**: SDK v1.2.0 supports API v1.x
- **Breaking SDK changes**: Increment major version
- **New SDK features**: Increment minor version
- **SDK bug fixes**: Increment patch version

---

## Changelog Management

Maintain `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [1.2.0] - 2025-07-01

### Added
- Time tracking endpoints
- Task management system
- Project CRUD operations

### Changed
- Improved authentication performance

### Deprecated
- `/api/v1/legacy-tasks` endpoint (use `/api/v1/tasks`)

### Fixed
- User role assignment bug

### Security
- Updated JWT library to patch CVE-2025-XXXX
```

---

## Monitoring & Metrics

### Version Metrics

Track per version:
- Request count by version
- Error rate by version
- Response time by version
- Feature flag usage

### Version Analytics

```python
# Log version usage
logger.info(
    "API request",
    extra={
        "api_version": request.headers.get("API-Version"),
        "endpoint": request.url.path,
        "method": request.method,
    }
)
```

---

## Best Practices

### DO ✅
- ✅ Follow semantic versioning strictly
- ✅ Document all changes in CHANGELOG.md
- ✅ Use feature flags for gradual rollout
- ✅ Maintain backward compatibility within major versions
- ✅ Provide migration guides for breaking changes
- ✅ Version APIs in URL path
- ✅ Support N and N-1 major versions

### DON'T ❌
- ❌ Make breaking changes in minor/patch versions
- ❌ Remove features without deprecation period
- ❌ Change API behavior without version bump
- ❌ Use inconsistent versioning across components
- ❌ Skip version numbers
- ❌ Forget to update documentation

---

## Troubleshooting

### Version Mismatch Issues

**Problem**: Client using deprecated version
**Solution**: Return deprecation headers, provide migration guide

**Problem**: Feature not available in client's version
**Solution**: Check feature flags, return appropriate error with upgrade suggestion

**Problem**: Database migration conflicts
**Solution**: Use Alembic downgrade, document rollback procedures

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)
- [VERSION_ROADMAP.md](VERSION_ROADMAP.md) - Version feature planning

---

**Document Version**: 1.0
**Last Updated**: 2025-11-01
**Maintained By**: Luc Joosten
