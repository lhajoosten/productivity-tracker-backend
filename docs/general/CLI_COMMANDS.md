# CLI Commands Reference - Versioning System

## 🎯 Quick Reference

All commands are run with: `poetry run pt <command>`

## Version Commands

### Show Current Version
```bash
poetry run pt version
```

**Output:**
- Application version (e.g., 1.0.0-beta)
- Release date
- Release name
- Current API version

**Example:**
```
┌─────────────────────────────────────┐
│      Version Information            │
├─────────────────────────────────────┤
│ Productivity Tracker Backend        │
│ Version: 1.0.0-beta                 │
│ Release Date: 2025-01-01            │
│ Release Name: Foundation            │
│ API Version: 1.0.0-beta             │
└─────────────────────────────────────┘
```

---

## Roadmap Commands

### Show Full Roadmap
```bash
poetry run pt roadmap
```

**Shows:**
- Current version status
- All planned versions (v1.0 - v2.3)
- Version focus areas
- Feature counts per version
- Active/deprecated version lists

**Aligned with:** `docs/VERSION_ROADMAP.md`

---

### Show Specific Version Details
```bash
poetry run pt roadmap --version 1.0
poetry run pt roadmap -v 1.1
```

**Shows:**
- Version status and lifecycle state
- New features introduced in that version
- Total cumulative features available
- API prefix
- Release/EOL dates
- Documentation URL

**Examples:**
```bash
poetry run pt roadmap -v 1.0  # Show v1.0 details
poetry run pt roadmap -v 1.2  # Show v1.2 details
poetry run pt roadmap -v 2.0  # Show v2.0 details
```

---

### Show All Features
```bash
poetry run pt roadmap --features
```

**Shows:**
- Complete feature matrix
- Which version each feature was introduced in
- Current availability status (Available vs Planned)
- Feature summary (total, available, planned)

**Combines with version filter:**
```bash
poetry run pt roadmap -v 1.2 --features  # Not implemented yet, shows v1.2 features
```

---

## Database Migration Commands

### Run Migrations
```bash
poetry run pt migrate
```

Applies all pending migrations to HEAD.

---

### Create New Migration
```bash
poetry run pt new_migration "migration_name"
poetry run pt new_migration "migration_name" --rev-id custom_id
poetry run pt new_migration "migration_name" --no-autogenerate
```

Creates a new Alembic migration file.

---

### Downgrade Migration
```bash
poetry run pt downgrade <revision>
poetry run pt downgrade <filename>
```

Reverts to a specific migration revision.

**Examples:**
```bash
poetry run pt downgrade abc123
poetry run pt downgrade abc123_create_users_table
```

---

## Development Commands

### Start Development Server
```bash
poetry run pt start
```

Starts FastAPI with hot reload enabled.

---

### Seed RBAC Data
```bash
poetry run pt seed_rbac
```

Seeds initial roles and permissions into the database.

---

### Create Superuser
```bash
poetry run pt create_superuser
```

Interactive command to create a superuser account.

---

## Command Summary Table

| Command | Purpose | Example |
|---------|---------|---------|
| `pt version` | Show version info | `poetry run pt version` |
| `pt roadmap` | Show full roadmap | `poetry run pt roadmap` |
| `pt roadmap -v X.X` | Show version details | `poetry run pt roadmap -v 1.0` |
| `pt roadmap --features` | Show feature matrix | `poetry run pt roadmap --features` |
| `pt migrate` | Run migrations | `poetry run pt migrate` |
| `pt new_migration` | Create migration | `poetry run pt new_migration "name"` |
| `pt downgrade` | Downgrade migration | `poetry run pt downgrade abc123` |
| `pt start` | Start dev server | `poetry run pt start` |
| `pt seed_rbac` | Seed RBAC data | `poetry run pt seed_rbac` |
| `pt create_superuser` | Create superuser | `poetry run pt create_superuser` |

---

## Versioning Commands - Detailed Examples

### Example 1: Check Current Version
```bash
$ poetry run pt version
```

### Example 2: View Roadmap
```bash
$ poetry run pt roadmap

# Output shows:
# - Current status panel
# - Version roadmap table with all versions
# - Active/deprecated version lists
# - Links to documentation
```

### Example 3: Inspect v1.2 (Productivity Tracking Core)
```bash
$ poetry run pt roadmap -v 1.2

# Output shows:
# - Status: PLANNED
# - New features: 7 (time_tracking, task_management, etc.)
# - Total features: 27 (cumulative from v1.0 + v1.1 + v1.2)
# - API prefix: /api/v1.2
# - Feature table with status
```

### Example 4: View All Features
```bash
$ poetry run pt roadmap --features

# Output shows:
# - Complete feature matrix
# - 88 total features across all versions
# - Which version each was introduced
# - Current availability (11 available, 77 planned)
```

---

## Tips

1. **Check version before deploying:**
   ```bash
   poetry run pt version
   ```

2. **Review features for next version:**
   ```bash
   poetry run pt roadmap -v 1.1
   ```

3. **See what's planned long-term:**
   ```bash
   poetry run pt roadmap
   ```

4. **Find when a feature was introduced:**
   ```bash
   poetry run pt roadmap --features | grep "Task Management"
   ```

5. **Verify migrations are up to date:**
   ```bash
   poetry run pt migrate
   ```

---

## Related Documentation

- **Usage Guide:** `docs/VERSIONING_USAGE.md`
- **Implementation Summary:** `docs/VERSIONING_SYSTEM_SUMMARY.md`
- **Version Roadmap:** `docs/VERSION_ROADMAP.md`
- **Versioning Strategy:** `docs/VERSIONING_STRATEGY.md`

---

## Environment Variables

The CLI respects these environment variables (if implemented):

- `PT_ENVIRONMENT` - Sets environment for feature toggles (development, staging, production)
- `DATABASE_URL` - Database connection string

---

## Notes

- All CLI commands use Rich library for beautiful formatted output
- Tables and panels are color-coded for easy reading
- Version strings can be specified with or without 'v' prefix (1.0 or v1.0)
- Feature flags are environment-aware (all features enabled in development)

---

**For more information, see the full documentation in `docs/`**
