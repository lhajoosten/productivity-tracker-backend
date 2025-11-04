# Role-Based Access Control (RBAC) Guide

This document describes the Role-Based Access Control (RBAC) system implemented in the productivity tracker backend.

## Overview

The RBAC system provides fine-grained access control through a three-tier model:
- **Users** have **Roles**
- **Roles** have **Permissions**
- **Permissions** define what actions can be performed on resources

This separation allows flexible permission management without modifying user records directly.

## Architecture

### Database Schema

```
┌─────────┐       ┌────────────┐       ┌─────────┐       ┌──────────────┐       ┌──────────────┐
│  User   │───────│ user_roles │───────│  Role   │───────│ role_perms   │───────│  Permission  │
└─────────┘       └────────────┘       └─────────┘       └──────────────┘       └──────────────┘
    1:N                M:N                  1:N                 M:N                     N:1
```

**User** (users table)
- `id` - Unique identifier
- `username` - Unique username
- `email` - Unique email address
- `hashed_password` - Encrypted password
- `is_active` - Account status
- `is_superuser` - Bypass all permission checks

**Role** (roles table)
- `id` - Unique identifier
- `name` - Unique role name (e.g., "admin", "user")
- `description` - Role description

**Permission** (permissions table)
- `id` - Unique identifier
- `name` - Unique permission name (e.g., "users:read")
- `resource` - Resource type (e.g., "user", "task", "project")
- `action` - Action type (e.g., "create", "read", "update", "delete")
- `description` - Permission description

**user_roles** (junction table)
- `user_id` - Foreign key to users
- `role_id` - Foreign key to roles

**role_permissions** (junction table)
- `role_id` - Foreign key to roles
- `permission_id` - Foreign key to permissions

## Permission Naming Convention

Permissions follow the format: `resource:action`

Examples:
- `users:read` - Read user data
- `users:create` - Create new users
- `users:update` - Update user information
- `users:delete` - Delete users
- `tasks:create` - Create tasks
- `projects:read` - Read project data

## Default Roles

The system comes with three default roles:

### 1. Admin
**Description**: Administrator with full access to all resources

**Permissions**: All permissions (users:*, tasks:*, projects:*)

**Use Case**: System administrators who need complete control

### 2. User
**Description**: Regular user with limited access

**Permissions**:
- `tasks:create`, `tasks:read`, `tasks:update`
- `projects:create`, `projects:read`, `projects:update`

**Use Case**: Standard users who can manage their own tasks and projects

### 3. Viewer
**Description**: Read-only access to resources

**Permissions**:
- `users:read`
- `tasks:read`
- `projects:read`

**Use Case**: Observers, auditors, or reporting systems

## Superuser

The `is_superuser` flag bypasses all permission checks. Superusers:
- Have access to all endpoints
- Can perform any action
- Don't need roles or permissions assigned

**Important**: Use sparingly, only for system administrators.

## User Permission Checks

The `User` entity provides convenient methods for permission checking:

### has_permission(permission_name: str) -> bool
Check if user has a specific permission through any of their roles.

```python
if user.has_permission("users:delete"):
    # User can delete users
    pass
```

### has_any_permission(*permission_names: str) -> bool
Check if user has at least one of the specified permissions.

```python
if user.has_any_permission("users:update", "users:delete"):
    # User can update OR delete users
    pass
```

### has_all_permissions(*permission_names: str) -> bool
Check if user has all of the specified permissions.

```python
if user.has_all_permissions("tasks:create", "tasks:update", "tasks:delete"):
    # User has full task management permissions
    pass
```

### has_role(role_name: str) -> bool
Check if user has a specific role.

```python
if user.has_role("admin"):
    # User is an admin
    pass
```

## Using RBAC in Routes

### Method 1: Using Dependencies

The most common way to protect routes is using FastAPI dependencies.

#### Require Superuser

```python
from productivity_tracker.core.dependencies import get_current_superuser

@router.get("/admin/users")
def get_all_users(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Only superusers can access this endpoint."""
    # Implementation...
```

#### Require Specific Permission

```python
from productivity_tracker.core.dependencies import require_permission

@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_permission("users:delete")),
    db: Session = Depends(get_db),
):
    """Only users with 'users:delete' permission can access."""
    # Implementation...
```

#### Require Any Permission (OR logic)

```python
from productivity_tracker.core.dependencies import require_any_permission

@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(
        require_any_permission("tasks:read", "projects:read")
    ),
    db: Session = Depends(get_db),
):
    """Users with either tasks:read OR projects:read can access."""
    # Implementation...
```

### Method 2: Manual Permission Check

For more complex logic, check permissions manually in the route handler.

```python
from productivity_tracker.core.exceptions import PermissionDeniedError

@router.put("/tasks/{task_id}")
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    task = task_service.get_task(task_id)

    # Check if user owns the task OR has admin permission
    if task.owner_id != current_user.id and not current_user.has_permission("tasks:update:any"):
        raise PermissionDeniedError(
            permission="tasks:update",
            resource=f"task {task_id}"
        )

    # Update task...
```

## Role Management API

### Create Role

```http
POST /api/v1/roles
Authorization: Required (Superuser)

{
  "name": "manager",
  "description": "Project manager with elevated permissions",
  "permission_ids": [
    "uuid-of-permission-1",
    "uuid-of-permission-2"
  ]
}
```

### Get All Roles

```http
GET /api/v1/roles
Authorization: Required (Superuser)
```

### Get Role by ID

```http
GET /api/v1/roles/{role_id}
Authorization: Required (Superuser)
```

### Update Role

```http
PUT /api/v1/roles/{role_id}
Authorization: Required (Superuser)

{
  "name": "senior_manager",
  "description": "Updated description",
  "permission_ids": ["uuid1", "uuid2"]
}
```

### Delete Role

```http
DELETE /api/v1/roles/{role_id}
Authorization: Required (Superuser)
```

### Assign Permissions to Role

```http
POST /api/v1/roles/{role_id}/permissions
Authorization: Required (Superuser)

{
  "permission_ids": ["uuid1", "uuid2", "uuid3"]
}
```

## Permission Management API

### Create Permission

```http
POST /api/v1/permissions
Authorization: Required (Superuser)

{
  "name": "reports:generate",
  "resource": "report",
  "action": "generate",
  "description": "Generate system reports"
}
```

### Get All Permissions

```http
GET /api/v1/permissions
Authorization: Required (Superuser)
```

### Get Permission by ID

```http
GET /api/v1/permissions/{permission_id}
Authorization: Required (Superuser)
```

### Get Permissions by Resource

```http
GET /api/v1/permissions/resource/{resource_name}
Authorization: Required (Superuser)
```

## User Role Assignment

### Assign Roles to User

```http
POST /api/v1/auth/users/{user_id}/roles
Authorization: Required (Superuser)

{
  "role_ids": ["uuid1", "uuid2"]
}
```

This replaces all existing roles with the specified ones.

## Initial Setup

### 1. Seed RBAC Data

Run the seeding script to create default roles and permissions:

```bash
# Using the CLI
python -m productivity_tracker.cli seed-rbac

# Or directly
python productivity_tracker/scripts/seed_rbac.py
```

This creates:
- All default permissions (users:*, tasks:*, projects:*)
- Three default roles (admin, user, viewer)
- A default admin user (username: `admin`, password: `admin123`)

⚠️ **Important**: Change the default admin password immediately!

### 2. Create Superuser

Create a superuser account:

```bash
python -m productivity_tracker.cli create-superuser
```

Follow the prompts to enter username, email, and password.

## Common Patterns

### Resource Ownership

For resources owned by users, combine ownership checks with permissions:

```python
def can_access_task(user: User, task: Task) -> bool:
    """Check if user can access a task."""
    # Owner can always access
    if task.owner_id == user.id:
        return True

    # Admin can access any task
    if user.has_permission("tasks:read:any"):
        return True

    # Team members can access shared tasks
    if task.team_id and user.team_id == task.team_id:
        return user.has_permission("tasks:read:team")

    return False
```

### Hierarchical Permissions

Implement permission hierarchies:

```python
PERMISSION_HIERARCHY = {
    "tasks:admin": ["tasks:create", "tasks:read", "tasks:update", "tasks:delete"],
    "tasks:manage": ["tasks:create", "tasks:read", "tasks:update"],
    "tasks:write": ["tasks:create", "tasks:update"],
}

def has_hierarchical_permission(user: User, permission: str) -> bool:
    """Check permission with hierarchy."""
    if user.has_permission(permission):
        return True

    # Check if user has parent permission
    for parent, children in PERMISSION_HIERARCHY.items():
        if permission in children and user.has_permission(parent):
            return True

    return False
```

### Dynamic Role Assignment

Automatically assign roles based on conditions:

```python
def assign_role_on_signup(user: User, db: Session):
    """Assign default role to new user."""
    default_role = db.query(Role).filter(Role.name == "user").first()
    if default_role:
        user.roles.append(default_role)
        db.commit()
```

## Security Best Practices

### 1. Principle of Least Privilege
Grant users only the permissions they need to perform their job.

```python
# Good: Specific permission
if user.has_permission("tasks:read"):
    return tasks

# Bad: Too broad
if user.is_superuser:
    return tasks
```

### 2. Separate Admin and User Permissions
Don't mix administrative and user-level permissions in the same role.

```python
# Good: Separate roles
admin_role.permissions = [all_permissions]
user_role.permissions = [user_level_permissions]

# Bad: Mixed permissions
mixed_role.permissions = [user_permissions + some_admin_permissions]
```

### 3. Check Permissions, Not Roles
Check for specific permissions rather than roles when possible.

```python
# Good: Check permission
if user.has_permission("users:delete"):
    delete_user(user_id)

# Less flexible: Check role
if user.has_role("admin"):
    delete_user(user_id)
```

### 4. Validate Permission Changes
Prevent users from escalating their own privileges.

```python
def assign_roles(admin: User, target_user: User, role_ids: list[UUID]):
    """Only superusers can assign roles."""
    if not admin.is_superuser:
        raise PermissionDeniedError(
            permission="role assignment",
            resource="users"
        )

    # Prevent self-privilege escalation in production systems
    if admin.id == target_user.id:
        raise BusinessLogicError(
            message="Cannot modify own roles",
            user_message="You cannot modify your own role assignments."
        )
```

### 5. Audit Permission Changes
Log all permission and role changes for security auditing.

```python
import logging

logger = logging.getLogger(__name__)

def update_user_roles(user: User, role_ids: list[UUID], admin: User):
    old_roles = [r.name for r in user.roles]
    # Update roles...
    new_roles = [r.name for r in user.roles]

    logger.info(
        f"Role change for user {user.username}: "
        f"{old_roles} -> {new_roles} by {admin.username}"
    )
```

## Testing RBAC

### Unit Tests

```python
import pytest
from productivity_tracker.database.entities import User, Role, Permission

def test_user_has_permission():
    user = User(username="test_user")
    role = Role(name="user")
    permission = Permission(name="tasks:read", resource="task", action="read")

    role.permissions.append(permission)
    user.roles.append(role)

    assert user.has_permission("tasks:read")
    assert not user.has_permission("tasks:delete")

def test_superuser_has_all_permissions():
    user = User(username="admin", is_superuser=True)

    assert user.has_permission("any:permission")
    assert user.has_permission("users:delete")
```

### Integration Tests

```python
def test_protected_endpoint_requires_permission(client):
    # Login as user without permission
    response = client.post("/api/v1/auth/login", json={
        "username": "viewer",
        "password": "password"
    })

    # Try to access protected endpoint
    response = client.delete("/api/v1/users/some-uuid")

    assert response.status_code == 403
    assert response.json()["error"] == "PERMISSION_DENIED"
```

## Troubleshooting

### User Has Role But Can't Access Endpoint

1. **Check if role has the required permission**:
   ```sql
   SELECT p.name FROM permissions p
   JOIN role_permissions rp ON p.id = rp.permission_id
   JOIN roles r ON rp.role_id = r.id
   WHERE r.name = 'user';
   ```

2. **Verify user has the role**:
   ```sql
   SELECT r.name FROM roles r
   JOIN user_roles ur ON r.id = ur.role_id
   JOIN users u ON ur.user_id = u.id
   WHERE u.username = 'john_doe';
   ```

3. **Check endpoint dependency**:
   Ensure the route uses the correct dependency and permission name.

### Permission Denied Despite Having Permission

1. **User might be inactive**: Check `user.is_active`
2. **Token might be expired**: Try logging in again
3. **Permission name mismatch**: Verify exact permission name spelling
4. **Lazy loading issue**: Ensure relationships are loaded with `lazy="selectin"`

## Migration Guide

### Adding New Permissions

1. **Create migration**:
   ```bash
   alembic revision -m "add_new_permissions"
   ```

2. **Add permissions in migration**:
   ```python
   from alembic import op
   import sqlalchemy as sa

   def upgrade():
       # Create permissions
       op.execute("""
           INSERT INTO permissions (name, resource, action, description)
           VALUES
               ('reports:generate', 'report', 'generate', 'Generate reports'),
               ('reports:export', 'report', 'export', 'Export reports');
       """)
   ```

3. **Assign to roles**:
   ```python
   # In seed script or migration
   report_permissions = db.query(Permission).filter(
       Permission.resource == "report"
   ).all()

   admin_role = db.query(Role).filter(Role.name == "admin").first()
   admin_role.permissions.extend(report_permissions)
   db.commit()
   ```

## Performance Considerations

### Eager Loading

Use `lazy="selectin"` to avoid N+1 queries:

```python
# Already configured in entities
roles = relationship("Role", lazy="selectin")
permissions = relationship("Permission", lazy="selectin")
```

### Caching

For high-traffic applications, consider caching permission checks:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_permissions(user_id: str) -> set[str]:
    """Cache user permissions."""
    user = db.query(User).filter(User.id == user_id).first()
    permissions = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
    return permissions
```

### Minimize Database Queries

Load user with roles and permissions in one query:

```python
user = db.query(User).options(
    selectinload(User.roles).selectinload(Role.permissions)
).filter(User.id == user_id).first()
```

## Resources

- [OWASP Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html)
- [NIST RBAC Standard](https://csrc.nist.gov/projects/role-based-access-control)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
