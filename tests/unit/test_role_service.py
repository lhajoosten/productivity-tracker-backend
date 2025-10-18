"""Unit tests for RoleService."""

from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from productivity_tracker.database.entities import Role
from productivity_tracker.models.auth import RoleCreate, RoleUpdate
from productivity_tracker.services.role_service import RoleService

pytestmark = [pytest.mark.unit, pytest.mark.rbac]


class TestRoleService:
    """Test cases for RoleService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def role_service(self, mock_db):
        """Create a RoleService instance with mocked dependencies."""
        return RoleService(mock_db)

    @pytest.fixture
    def mock_role(self):
        """Create a mock role."""
        role = Mock(spec=Role)
        role.id = uuid4()
        role.name = "user"
        role.description = "Regular user role"
        role.permissions = []
        return role

    def test_create_role_success(self, role_service, mock_role):
        """Test successful role creation."""
        # Arrange
        role_data = RoleCreate(
            name="manager",
            description="Manager role",
        )
        role_service.repository.get_by_name = Mock(return_value=None)
        role_service.repository.create = Mock(return_value=mock_role)

        # Act
        result = role_service.create_role(role_data)

        # Assert
        assert result == mock_role
        role_service.repository.get_by_name.assert_called_once_with("manager")
        role_service.repository.create.assert_called_once()

    def test_create_role_duplicate_name(self, role_service, mock_role):
        """Test role creation fails with duplicate name."""
        # Arrange
        role_data = RoleCreate(
            name="user",
            description="Duplicate role",
        )
        role_service.repository.get_by_name = Mock(return_value=mock_role)

        # Act & Assert
        with pytest.raises(ResourceAlreadyExistsError) as exc_info:
            role_service.create_role(role_data)

        assert exc_info.value.status_code == 409
        assert "user" in str(exc_info.value.context.get("value", ""))

    def test_create_role_with_permissions(self, role_service, mock_role):
        """Test creating role with permissions."""
        # Arrange
        permission_ids = [uuid4(), uuid4()]
        role_data = RoleCreate(
            name="manager",
            description="Manager role",
            permission_ids=permission_ids,
        )
        role_service.repository.get_by_name = Mock(return_value=None)
        role_service.repository.create = Mock(return_value=mock_role)
        role_service.repository.assign_permissions = Mock(return_value=mock_role)

        # Act
        result = role_service.create_role(role_data)

        # Assert
        assert result == mock_role
        role_service.repository.assign_permissions.assert_called_once_with(
            mock_role, permission_ids
        )

    def test_get_role_success(self, role_service, mock_role):
        """Test successful role retrieval."""
        # Arrange
        role_id = mock_role.id
        role_service.repository.get_by_id = Mock(return_value=mock_role)

        # Act
        result = role_service.get_role(role_id)

        # Assert
        assert result == mock_role
        role_service.repository.get_by_id.assert_called_once_with(role_id)

    def test_get_role_not_found(self, role_service):
        """Test role retrieval fails when not found."""
        # Arrange
        role_id = uuid4()
        role_service.repository.get_by_id = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ResourceNotFoundError) as exc_info:
            role_service.get_role(role_id)

        assert exc_info.value.status_code == 404
        assert "role" in exc_info.value.user_message.lower()

    def test_get_role_by_name_success(self, role_service, mock_role):
        """Test successful role retrieval by name."""
        # Arrange
        role_service.repository.get_by_name = Mock(return_value=mock_role)

        # Act
        result = role_service.get_role_by_name("user")

        # Assert
        assert result == mock_role
        role_service.repository.get_by_name.assert_called_once_with("user")

    def test_get_role_by_name_not_found(self, role_service):
        """Test role retrieval by name fails when not found."""
        # Arrange
        role_service.repository.get_by_name = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            role_service.get_role_by_name("nonexistent")

    def test_update_role_success(self, role_service, mock_role):
        """Test successful role update."""
        # Arrange
        role_id = mock_role.id
        update_data = RoleUpdate(name="updated_role")
        role_service.repository.get_by_id = Mock(return_value=mock_role)
        role_service.repository.get_by_name = Mock(return_value=None)
        role_service.repository.update = Mock(return_value=mock_role)

        # Act
        result = role_service.update_role(role_id, update_data)

        # Assert
        assert result == mock_role
        assert mock_role.name == "updated_role"

    def test_update_role_duplicate_name(self, role_service, mock_role):
        """Test role update fails with duplicate name."""
        # Arrange
        role_id = mock_role.id
        other_role = Mock(spec=Role)
        other_role.id = uuid4()
        update_data = RoleUpdate(name="admin")

        role_service.repository.get_by_id = Mock(return_value=mock_role)
        role_service.repository.get_by_name = Mock(return_value=other_role)

        # Act & Assert
        with pytest.raises(ResourceAlreadyExistsError):
            role_service.update_role(role_id, update_data)

    def test_delete_role(self, role_service):
        """Test role deletion."""
        # Arrange
        role_id = uuid4()
        role_service.repository.delete = Mock(return_value=True)

        # Act
        result = role_service.delete_role(role_id)

        # Assert
        assert result is True
        role_service.repository.delete.assert_called_once_with(role_id, soft=True)

    def test_assign_permissions(self, role_service, mock_role):
        """Test assigning permissions to role."""
        # Arrange
        role_id = mock_role.id
        permission_ids = [uuid4(), uuid4()]
        role_service.repository.get_by_id = Mock(return_value=mock_role)
        role_service.repository.assign_permissions = Mock(return_value=mock_role)

        # Act
        result = role_service.assign_permissions(role_id, permission_ids)

        # Assert
        assert result == mock_role
        role_service.repository.assign_permissions.assert_called_once_with(
            mock_role, permission_ids
        )
