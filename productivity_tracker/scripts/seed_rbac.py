"""Script to seed initial roles and permissions into the database."""

from sqlalchemy.orm import Session

from productivity_tracker.core.security import hash_password
from productivity_tracker.database import SessionLocal
from productivity_tracker.database.entities import Permission, Role, User


def create_permissions(db: Session):
    """Create default permissions."""
    permissions_data = [
        # User permissions
        {
            "name": "users:create",
            "resource": "user",
            "action": "create",
            "description": "Create users",
        },
        {
            "name": "users:read",
            "resource": "user",
            "action": "read",
            "description": "Read users",
        },
        {
            "name": "users:update",
            "resource": "user",
            "action": "update",
            "description": "Update users",
        },
        {
            "name": "users:delete",
            "resource": "user",
            "action": "delete",
            "description": "Delete users",
        },
        # Task permissions
        {
            "name": "tasks:create",
            "resource": "task",
            "action": "create",
            "description": "Create tasks",
        },
        {
            "name": "tasks:read",
            "resource": "task",
            "action": "read",
            "description": "Read tasks",
        },
        {
            "name": "tasks:update",
            "resource": "task",
            "action": "update",
            "description": "Update tasks",
        },
        {
            "name": "tasks:delete",
            "resource": "task",
            "action": "delete",
            "description": "Delete tasks",
        },
        # Project permissions
        {
            "name": "projects:create",
            "resource": "project",
            "action": "create",
            "description": "Create projects",
        },
        {
            "name": "projects:read",
            "resource": "project",
            "action": "read",
            "description": "Read projects",
        },
        {
            "name": "projects:update",
            "resource": "project",
            "action": "update",
            "description": "Update projects",
        },
        {
            "name": "projects:delete",
            "resource": "project",
            "action": "delete",
            "description": "Delete projects",
        },
        # Organization permissions
        {
            "name": "organizations:create",
            "resource": "organization",
            "action": "create",
            "description": "Create organizations",
        },
        {
            "name": "organizations:read",
            "resource": "organization",
            "action": "read",
            "description": "Read organizations",
        },
        {
            "name": "organizations:update",
            "resource": "organization",
            "action": "update",
            "description": "Update organizations",
        },
        {
            "name": "organizations:delete",
            "resource": "organization",
            "action": "delete",
            "description": "Delete organizations",
        },
        {
            "name": "organizations:manage_members",
            "resource": "organization",
            "action": "manage_members",
            "description": "Add or remove organization members",
        },
        # Department permissions
        {
            "name": "departments:create",
            "resource": "department",
            "action": "create",
            "description": "Create departments",
        },
        {
            "name": "departments:read",
            "resource": "department",
            "action": "read",
            "description": "Read departments",
        },
        {
            "name": "departments:update",
            "resource": "department",
            "action": "update",
            "description": "Update departments",
        },
        {
            "name": "departments:delete",
            "resource": "department",
            "action": "delete",
            "description": "Delete departments",
        },
        # Team permissions
        {
            "name": "teams:create",
            "resource": "team",
            "action": "create",
            "description": "Create teams",
        },
        {
            "name": "teams:read",
            "resource": "team",
            "action": "read",
            "description": "Read teams",
        },
        {
            "name": "teams:update",
            "resource": "team",
            "action": "update",
            "description": "Update teams",
        },
        {
            "name": "teams:delete",
            "resource": "team",
            "action": "delete",
            "description": "Delete teams",
        },
        {
            "name": "teams:manage_members",
            "resource": "team",
            "action": "manage_members",
            "description": "Add or remove team members",
        },
        {
            "name": "teams:manage_lead",
            "resource": "team",
            "action": "manage_lead",
            "description": "Set or update team lead",
        },
    ]

    permissions = []
    for perm_data in permissions_data:
        # Check if permission already exists
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            permissions.append(permission)
        else:
            permissions.append(existing)

    db.commit()
    return permissions


def create_roles(db: Session, permissions: list):
    """Create default roles and assign permissions."""
    # Create Admin role with all permissions
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator with full access")
        admin_role.permissions = permissions
        db.add(admin_role)

    # Create User role with limited permissions
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_permissions = [
            p
            for p in permissions
            if (p.resource in ["task", "project"] and p.action in ["create", "read", "update"])
            or (p.resource in ["organization", "department", "team"] and p.action == "read")
        ]
        user_role = Role(name="user", description="Regular user with limited access")
        user_role.permissions = user_permissions
        db.add(user_role)

    # Create Viewer role with read-only permissions
    viewer_role = db.query(Role).filter(Role.name == "viewer").first()
    if not viewer_role:
        viewer_permissions = [p for p in permissions if p.action == "read"]
        viewer_role = Role(name="viewer", description="Read-only access")
        viewer_role.permissions = viewer_permissions
        db.add(viewer_role)

    # Create Organization Manager role
    org_manager_role = db.query(Role).filter(Role.name == "organization_manager").first()
    if not org_manager_role:
        org_manager_permissions = [
            p
            for p in permissions
            if p.resource in ["organization", "department", "team"]
            or (p.resource in ["task", "project"] and p.action in ["create", "read", "update"])
        ]
        org_manager_role = Role(
            name="organization_manager",
            description="Manage organizations, departments, and teams",
        )
        org_manager_role.permissions = org_manager_permissions
        db.add(org_manager_role)

    # Create Team Lead role
    team_lead_role = db.query(Role).filter(Role.name == "team_lead").first()
    if not team_lead_role:
        team_lead_permissions = [
            p
            for p in permissions
            if (p.resource == "team" and p.action in ["read", "update", "manage_members"])
            or (p.resource in ["organization", "department"] and p.action == "read")
            or (p.resource in ["task", "project"])
        ]
        team_lead_role = Role(
            name="team_lead",
            description="Lead a team with task and member management",
        )
        team_lead_role.permissions = team_lead_permissions
        db.add(team_lead_role)

    # Create Department Manager role
    dept_manager_role = db.query(Role).filter(Role.name == "department_manager").first()
    if not dept_manager_role:
        dept_manager_permissions = [
            p
            for p in permissions
            if (p.resource in ["department", "team"])
            or (p.resource == "organization" and p.action == "read")
            or (p.resource in ["task", "project"] and p.action in ["create", "read", "update"])
        ]
        dept_manager_role = Role(
            name="department_manager",
            description="Manage departments and teams within an organization",
        )
        dept_manager_role.permissions = dept_manager_permissions
        db.add(dept_manager_role)

    db.commit()
    return {
        "admin": admin_role,
        "user": user_role,
        "viewer": viewer_role,
        "organization_manager": org_manager_role,
        "team_lead": team_lead_role,
        "department_manager": dept_manager_role,
    }


def create_default_admin(db: Session, admin_role: Role):
    """Create default admin user if not exists."""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),  # Change this password!
            is_active=True,
            is_superuser=True,
        )
        admin.roles.append(admin_role)
        db.add(admin)
        db.commit()
        print("✓ Created default admin user (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Change the admin password immediately!")
    else:
        print("✓ Admin user already exists")


def seed_rbac():
    """Main function to seed RBAC data."""
    db = SessionLocal()
    try:
        print("Seeding RBAC data...")

        # Create permissions
        print("Creating permissions...")
        permissions = create_permissions(db)
        print(f"✓ Created {len(permissions)} permissions")

        # Create roles
        print("Creating roles...")
        roles = create_roles(db, permissions)
        print(f"✓ Created {len(roles)} roles")

        # Create default admin
        print("Creating default admin user...")
        create_default_admin(db, roles["admin"])

        print("\n✓ RBAC seeding completed successfully!")

    except Exception as e:
        print(f"✗ Error seeding RBAC data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_rbac()
