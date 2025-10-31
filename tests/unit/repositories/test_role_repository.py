"""Unit tests for role repository."""

import pytest

from productivity_tracker.database.entities.role import Permission, Role
from productivity_tracker.repositories.role_repository import RoleRepository

pytestmark = [pytest.mark.unit]


class TestRoleRepository:
    """Test role repository methods."""

    def test_get_by_name(self, db_session_unit):
        """Should get role by name."""
        repo = RoleRepository(db_session_unit)

        # Create role
        role = Role(name="admin", description="Admin role")
        created_role = repo.create(role)

        # Get by name
        retrieved = repo.get_by_name("admin")
        assert retrieved is not None
        assert retrieved.id == created_role.id
        assert retrieved.name == "admin"

    def test_get_by_name_not_found(self, db_session_unit):
        """Should return None for non-existent role."""
        repo = RoleRepository(db_session_unit)

        result = repo.get_by_name("nonexistent")
        assert result is None

    def test_assign_permissions(self, db_session_unit):
        """Should assign multiple permissions to a role."""
        repo = RoleRepository(db_session_unit)

        # Create role
        role = Role(name="editor", description="Editor role")
        created_role = repo.create(role)

        # Create permissions
        perm1 = Permission(name="read:articles", resource="article", action="read")
        perm2 = Permission(name="write:articles", resource="article", action="write")
        db_session_unit.add(perm1)
        db_session_unit.add(perm2)
        db_session_unit.commit()
        db_session_unit.refresh(perm1)
        db_session_unit.refresh(perm2)

        # Assign permissions
        updated_role = repo.assign_permissions(created_role, [perm1.id, perm2.id])

        assert len(updated_role.permissions) == 2
        assert any(p.id == perm1.id for p in updated_role.permissions)
        assert any(p.id == perm2.id for p in updated_role.permissions)

    def test_add_permission(self, db_session_unit):
        """Should add a single permission to a role."""
        repo = RoleRepository(db_session_unit)

        # Create role
        role = Role(name="viewer", description="Viewer role")
        created_role = repo.create(role)

        # Create permission
        perm = Permission(name="read:posts", resource="post", action="read")
        db_session_unit.add(perm)
        db_session_unit.commit()
        db_session_unit.refresh(perm)

        # Add permission
        updated_role = repo.add_permission(created_role, perm.id)

        assert len(updated_role.permissions) == 1
        assert updated_role.permissions[0].id == perm.id

    def test_add_permission_already_exists(self, db_session_unit):
        """Should not duplicate permission if already exists."""
        repo = RoleRepository(db_session_unit)

        # Create role with permission
        role = Role(name="manager", description="Manager role")
        perm = Permission(name="manage:teams", resource="team", action="manage")
        role.permissions.append(perm)
        created_role = repo.create(role)

        # Try to add same permission again
        updated_role = repo.add_permission(created_role, perm.id)

        assert len(updated_role.permissions) == 1

    def test_remove_permission(self, db_session_unit):
        """Should remove a permission from a role."""
        repo = RoleRepository(db_session_unit)

        # Create role with permissions
        role = Role(name="contributor", description="Contributor role")
        perm1 = Permission(name="read:data", resource="data", action="read")
        perm2 = Permission(name="write:data", resource="data", action="write")
        role.permissions.extend([perm1, perm2])
        created_role = repo.create(role)

        # Remove one permission
        updated_role = repo.remove_permission(created_role, perm1.id)

        assert len(updated_role.permissions) == 1
        assert updated_role.permissions[0].id == perm2.id

    def test_remove_permission_not_in_role(self, db_session_unit):
        """Should handle removing permission not in role."""
        repo = RoleRepository(db_session_unit)

        # Create role
        role = Role(name="guest", description="Guest role")
        created_role = repo.create(role)

        # Create permission not assigned to role
        perm = Permission(name="delete:all", resource="all", action="delete")
        db_session_unit.add(perm)
        db_session_unit.commit()
        db_session_unit.refresh(perm)

        # Try to remove it
        updated_role = repo.remove_permission(created_role, perm.id)

        assert len(updated_role.permissions) == 0

    def test_get_roles_with_permission(self, db_session_unit):
        """Should get all roles with a specific permission."""
        repo = RoleRepository(db_session_unit)

        # Create permission
        perm = Permission(name="admin:access", resource="admin", action="access")
        db_session_unit.add(perm)
        db_session_unit.commit()
        db_session_unit.refresh(perm)

        # Create roles with this permission
        role1 = Role(name="superadmin", description="Super Admin")
        role1.permissions.append(perm)
        role2 = Role(name="siteadmin", description="Site Admin")
        role2.permissions.append(perm)
        role3 = Role(name="user", description="Regular User")

        repo.create(role1)
        repo.create(role2)
        repo.create(role3)

        # Get roles with permission
        roles = repo.get_roles_with_permission("admin:access")

        assert len(roles) == 2
        role_names = [r.name for r in roles]
        assert "superadmin" in role_names
        assert "siteadmin" in role_names
        assert "user" not in role_names
