"""Integration tests for RBAC (Role and Permission) endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from productivity_tracker.database.entities import Permission, Role, User

pytestmark = [pytest.mark.integration, pytest.mark.rbac]


class TestRoleEndpoints:
    """Integration tests for /api/v1/roles endpoints."""

    def test_create_role_as_superuser(
        self, client_integration: TestClient, sample_superuser_integration: User
    ):
        """Test superuser can create a role."""
        # Arrange - Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Use unique name to avoid conflicts
        import time

        unique_suffix = str(int(time.time() * 1000000))

        # Act
        response = client_integration.post(
            "/api/v1/roles",
            json={
                "name": f"manager_{unique_suffix}",
                "description": "Manager role with elevated permissions",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == f"manager_{unique_suffix}"
        assert data["description"] == "Manager role with elevated permissions"
        assert "id" in data

    def test_create_role_as_regular_user(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test regular user cannot create a role."""
        # Arrange - Login as regular user
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        import time

        unique_suffix = str(int(time.time() * 1000000))

        # Act
        response = client_integration.post(
            "/api/v1/roles",
            json={
                "name": f"manager_{unique_suffix}",
                "description": "Manager role",
            },
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "PERMISSION_DENIED"

    def test_create_role_duplicate_name(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test creating role with duplicate name fails."""
        # Arrange - Create a role first
        from uuid import uuid4

        existing_role = Role(
            id=uuid4(),
            name="duplicate_test_role",
            description="Existing role",
        )
        db_session_integration.add(existing_role)
        db_session_integration.flush()

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            "/api/v1/roles",
            json={
                "name": existing_role.name,  # Duplicate name
                "description": "Duplicate role",
            },
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "RESOURCE_ALREADY_EXISTS"

    def test_get_all_roles(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test getting all roles."""
        # Arrange - Create a test role
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name="get_all_test_role",
            description="Test role",
        )
        db_session_integration.add(test_role)
        db_session_integration.flush()

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get("/api/v1/roles")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_role_by_id(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test getting role by ID."""
        # Arrange - Create a test role
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name="get_by_id_test_role",
            description="Test role",
        )
        db_session_integration.add(test_role)
        db_session_integration.flush()
        db_session_integration.refresh(test_role)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get(f"/api/v1/roles/{test_role.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_role.id)
        assert data["name"] == test_role.name

    def test_get_role_not_found(
        self, client_integration: TestClient, sample_superuser_integration: User
    ):
        """Test getting non-existent role returns 404."""
        # Arrange - Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get(
            "/api/v1/roles/00000000-0000-0000-0000-000000000000"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "RESOURCE_NOT_FOUND"

    def test_update_role(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test updating a role."""
        # Arrange - Create a test role
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name="update_test_role",
            description="Original description",
        )
        db_session_integration.add(test_role)
        db_session_integration.flush()
        db_session_integration.refresh(test_role)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.put(
            f"/api/v1/roles/{test_role.id}",
            json={
                "name": "updated_role",
                "description": "Updated description",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated_role"
        assert data["description"] == "Updated description"

    def test_delete_role(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test deleting a role."""
        # Arrange - Create a test role
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name="delete_test_role",
            description="To be deleted",
        )
        db_session_integration.add(test_role)
        db_session_integration.flush()
        db_session_integration.refresh(test_role)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.delete(f"/api/v1/roles/{test_role.id}")

        # Assert
        assert response.status_code == 204

    def test_assign_permissions_to_role(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test assigning permissions to a role."""
        # Arrange - Create test role and permissions
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name="assign_perm_test_role",
            description="Test role",
        )
        db_session_integration.add(test_role)

        test_permissions = []
        for i in range(2):
            perm = Permission(
                id=uuid4(),
                name=f"test:perm_{i}_{uuid4().hex[:8]}",
                resource="test",
                action=f"action_{i}",
                description=f"Test permission {i}",
            )
            db_session_integration.add(perm)
            test_permissions.append(perm)

        db_session_integration.flush()
        for perm in test_permissions:
            db_session_integration.refresh(perm)
        db_session_integration.refresh(test_role)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            f"/api/v1/roles/{test_role.id}/permissions",
            json={
                "permission_ids": [str(p.id) for p in test_permissions],
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["permissions"]) == len(test_permissions)


class TestPermissionEndpoints:
    """Integration tests for /api/v1/permissions endpoints."""

    def test_create_permission_as_superuser(
        self, client_integration: TestClient, sample_superuser_integration: User
    ):
        """Test superuser can create a permission."""
        # Arrange - Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        import time

        unique_suffix = str(int(time.time() * 1000000))

        # Act
        response = client_integration.post(
            "/api/v1/permissions",
            json={
                "name": f"projects:create_{unique_suffix}",
                "resource": "project",
                "action": "create",
                "description": "Create projects",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == f"projects:create_{unique_suffix}"
        assert data["resource"] == "project"
        assert data["action"] == "create"

    def test_create_permission_as_regular_user(
        self, client_integration: TestClient, sample_user_integration: User
    ):
        """Test regular user cannot create a permission."""
        # Arrange - Login as regular user
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_user_integration.username,
                "password": "TestPassword123!",
            },
        )

        import time

        unique_suffix = str(int(time.time() * 1000000))

        # Act
        response = client_integration.post(
            "/api/v1/permissions",
            json={
                "name": f"projects:create_{unique_suffix}",
                "resource": "project",
                "action": "create",
                "description": "Create projects",
            },
        )

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "PERMISSION_DENIED"

    def test_create_permission_duplicate_name(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test creating permission with duplicate name fails."""
        # Arrange - Create a permission first
        from uuid import uuid4

        existing_perm = Permission(
            id=uuid4(),
            name="duplicate_test_perm",
            resource="test",
            action="read",
            description="Existing permission",
        )
        db_session_integration.add(existing_perm)
        db_session_integration.flush()

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            "/api/v1/permissions",
            json={
                "name": existing_perm.name,  # Duplicate name
                "resource": "task",
                "action": "write",
                "description": "Duplicate permission",
            },
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "RESOURCE_ALREADY_EXISTS"

    def test_get_all_permissions(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test getting all permissions."""
        # Arrange - Create test permissions
        from uuid import uuid4

        test_perms = []
        for i in range(2):
            perm = Permission(
                id=uuid4(),
                name=f"get_all_test:perm_{uuid4().hex[:8]}",
                resource="test",
                action=f"action_{i}",
                description=f"Test permission {i}",
            )
            db_session_integration.add(perm)
            test_perms.append(perm)

        db_session_integration.flush()

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get("/api/v1/permissions")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(test_perms)

    def test_get_permission_by_id(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test getting permission by ID."""
        # Arrange - Create a test permission
        from uuid import uuid4

        test_perm = Permission(
            id=uuid4(),
            name=f"get_by_id_test:perm_{uuid4().hex[:8]}",
            resource="test",
            action="read",
            description="Test permission",
        )
        db_session_integration.add(test_perm)
        db_session_integration.flush()
        db_session_integration.refresh(test_perm)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get(f"/api/v1/permissions/{test_perm.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_perm.id)
        assert data["name"] == test_perm.name

    def test_get_permissions_by_resource(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test getting permissions by resource."""
        # Arrange - Create test permissions with specific resource
        from uuid import uuid4

        unique_resource = f"task_{uuid4().hex[:8]}"
        test_perms = []
        for i in range(2):
            perm = Permission(
                id=uuid4(),
                name=f"{unique_resource}:action_{i}_{uuid4().hex[:8]}",
                resource=unique_resource,
                action=f"action_{i}",
                description=f"Test permission {i}",
            )
            db_session_integration.add(perm)
            test_perms.append(perm)

        db_session_integration.flush()

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.get(
            f"/api/v1/permissions/resource/{unique_resource}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All permissions should be for our unique resource
        for perm in data:
            assert perm["resource"] == unique_resource

    def test_update_permission(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test updating a permission."""
        # Arrange - Create a test permission
        from uuid import uuid4

        test_perm = Permission(
            id=uuid4(),
            name=f"update_test:perm_{uuid4().hex[:8]}",
            resource="test",
            action="read",
            description="Original description",
        )
        db_session_integration.add(test_perm)
        db_session_integration.flush()
        db_session_integration.refresh(test_perm)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.put(
            f"/api/v1/permissions/{test_perm.id}",
            json={
                "name": f"tasks:read_updated_{uuid4().hex[:8]}",
                "description": "Updated description",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "tasks:read_updated" in data["name"]
        assert data["description"] == "Updated description"

    def test_delete_permission(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        db_session_integration: Session,
    ):
        """Test deleting a permission."""
        # Arrange - Create a test permission
        from uuid import uuid4

        test_perm = Permission(
            id=uuid4(),
            name=f"delete_test:perm_{uuid4().hex[:8]}",
            resource="test",
            action="delete",
            description="To be deleted",
        )
        db_session_integration.add(test_perm)
        db_session_integration.flush()
        db_session_integration.refresh(test_perm)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.delete(f"/api/v1/permissions/{test_perm.id}")

        # Assert
        assert response.status_code == 204


class TestRBACIntegration:
    """Integration tests for complete RBAC flow."""

    def test_assign_role_to_user(
        self,
        client_integration: TestClient,
        sample_superuser_integration: User,
        sample_user_integration: User,
        db_session_integration: Session,
    ):
        """Test assigning a role to a user."""
        # Arrange - Create a test role
        from uuid import uuid4

        test_role = Role(
            id=uuid4(),
            name=f"assign_role_test_{uuid4().hex[:8]}",
            description="Test role",
        )
        db_session_integration.add(test_role)
        db_session_integration.flush()
        db_session_integration.refresh(test_role)

        # Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act
        response = client_integration.post(
            f"/api/v1/auth/users/{sample_user_integration.id}/roles",
            json={
                "role_ids": [str(test_role.id)],
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) >= 1
        role_names = [role["name"] for role in data["roles"]]
        assert test_role.name in role_names

    def test_superuser_bypasses_permission_checks(
        self, client_integration: TestClient, sample_superuser_integration: User
    ):
        """Test superuser can access all endpoints."""
        # Arrange - Login as superuser
        client_integration.post(
            "/api/v1/auth/login",
            json={
                "username": sample_superuser_integration.username,
                "password": "AdminPassword123!",
            },
        )

        # Act - Access admin endpoints
        users_response = client_integration.get("/api/v1/auth/users")
        roles_response = client_integration.get("/api/v1/roles")
        permissions_response = client_integration.get("/api/v1/permissions")

        # Assert
        assert users_response.status_code == 200
        assert roles_response.status_code == 200
        assert permissions_response.status_code == 200
