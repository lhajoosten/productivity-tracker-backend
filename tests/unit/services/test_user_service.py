"""Unit tests for UserService."""

from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from productivity_tracker.core.exceptions import (
    EmailAlreadyExistsError,
    PasswordMismatchError,
    ResourceNotFoundError,
    UsernameAlreadyExistsError,
)
from productivity_tracker.database.entities import User
from productivity_tracker.models.auth import UserCreate, UserPasswordUpdate, UserUpdate
from productivity_tracker.services.user_service import UserService

pytestmark = [pytest.mark.unit]


class TestUserService:
    """Test cases for UserService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def user_service(self, mock_db):
        """Create a UserService instance with mocked dependencies."""
        return UserService(mock_db)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid4()
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active = True
        user.is_superuser = False
        user.hashed_password = "hashed_password"
        return user

    # ============================================================================
    # create_user tests
    # ============================================================================

    def test_create_user_success(self, user_service, mock_user):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="Password123!",
        )
        user_service.repository.get_by_email = Mock(return_value=None)
        user_service.repository.get_by_username = Mock(return_value=None)
        user_service.repository.create = Mock(return_value=mock_user)

        # Act
        result = user_service.create_user(user_data)

        # Assert
        assert result == mock_user
        user_service.repository.get_by_email.assert_called_once_with("newuser@example.com")
        user_service.repository.get_by_username.assert_called_once_with("newuser")
        user_service.repository.create.assert_called_once()

    def test_create_user_duplicate_email(self, user_service, mock_user):
        """Test user creation fails with duplicate email."""
        # Arrange
        user_data = UserCreate(
            username="newuser",
            email="test@example.com",  # Existing email
            password="Password123!",
        )
        user_service.repository.get_by_email_or_username = Mock(return_value=mock_user)

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            user_service.create_user(user_data)

        assert "email" in str(exc_info.value.user_message).lower()

    def test_create_user_duplicate_username(self, user_service, mock_user):
        """Test user creation fails with duplicate username."""
        # Arrange
        mock_user.email = "different@example.com"
        user_data = UserCreate(
            username="testuser",  # Existing username
            email="new@example.com",
            password="Password123!",
        )
        user_service.repository.get_by_email = Mock(return_value=None)
        user_service.repository.get_by_username = Mock(return_value=mock_user)

        # Act & Assert
        with pytest.raises(UsernameAlreadyExistsError) as exc_info:
            user_service.create_user(user_data)

        assert "testuser" in str(exc_info.value.context.get("value", ""))

    def test_create_superuser(self, user_service, mock_user):
        """Test creating a superuser."""
        # Arrange
        user_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
        )
        user_service.repository.get_by_email = Mock(return_value=None)
        user_service.repository.get_by_username = Mock(return_value=None)
        user_service.repository.create = Mock(return_value=mock_user)

        # Act
        result = user_service.create_user(user_data, is_superuser=True)

        # Assert
        assert result == mock_user
        create_call = user_service.repository.create.call_args[0][0]
        assert create_call.is_superuser is True

    # ============================================================================
    # get_user tests
    # ============================================================================

    def test_get_user_success(self, user_service, mock_user):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = mock_user.id
        user_service.repository.get_by_id = Mock(return_value=mock_user)

        # Act
        result = user_service.get_user(user_id)

        # Assert
        assert result == mock_user
        user_service.repository.get_by_id.assert_called_once_with(user_id)

    def test_get_user_not_found(self, user_service):
        """Test user retrieval fails when user doesn't exist."""
        # Arrange
        user_id = uuid4()
        user_service.repository.get_by_id = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ResourceNotFoundError) as exc_info:
            user_service.get_user(user_id)

        assert exc_info.value.status_code == 404
        assert "user" in exc_info.value.user_message.lower()

    # ============================================================================
    # update_user tests
    # ============================================================================

    def test_update_user_success(self, user_service, mock_user):
        """Test successful user update."""
        # Arrange
        user_id = mock_user.id
        update_data = UserUpdate(username="updateduser")
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.get_by_username = Mock(return_value=None)
        user_service.repository.update = Mock(return_value=mock_user)

        # Act
        result = user_service.update_user(user_id, update_data)

        # Assert
        assert result == mock_user
        assert mock_user.username == "updateduser"
        user_service.repository.update.assert_called_once_with(mock_user)

    def test_update_user_duplicate_email(self, user_service, mock_user):
        """Test user update fails with duplicate email."""
        # Arrange
        user_id = mock_user.id
        other_user = Mock(spec=User)
        other_user.id = uuid4()
        update_data = UserUpdate(email="other@example.com")

        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.get_by_email = Mock(return_value=other_user)

        # Act & Assert
        with pytest.raises(EmailAlreadyExistsError):
            user_service.update_user(user_id, update_data)

    def test_update_user_duplicate_username(self, user_service, mock_user):
        """Test user update fails with duplicate username."""
        # Arrange
        user_id = mock_user.id
        other_user = Mock(spec=User)
        other_user.id = uuid4()
        update_data = UserUpdate(username="otheruser")

        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.get_by_username = Mock(return_value=other_user)

        # Act & Assert
        with pytest.raises(UsernameAlreadyExistsError):
            user_service.update_user(user_id, update_data)

    # ============================================================================
    # update_password tests
    # ============================================================================

    @patch("productivity_tracker.services.user_service.verify_password")
    @patch("productivity_tracker.services.user_service.hash_password")
    def test_update_password_success(self, mock_hash, mock_verify, user_service, mock_user):
        """Test successful password update."""
        # Arrange
        user_id = mock_user.id
        original_hashed_password = mock_user.hashed_password
        password_data = UserPasswordUpdate(
            current_password="OldPass123!",
            new_password="NewPass123!",
        )
        mock_verify.return_value = True
        mock_hash.return_value = "new_hashed_password"
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.update = Mock(return_value=mock_user)

        # Act
        result = user_service.update_password(user_id, password_data)

        # Assert
        assert result == mock_user
        mock_verify.assert_called_once_with("OldPass123!", original_hashed_password)
        mock_hash.assert_called_once_with("NewPass123!")
        assert mock_user.hashed_password == "new_hashed_password"
        user_service.repository.update.assert_called_once_with(mock_user)

    @patch("productivity_tracker.services.user_service.verify_password")
    def test_update_password_wrong_current(self, mock_verify, user_service, mock_user):
        """Test password update fails with incorrect current password."""
        # Arrange
        user_id = mock_user.id
        password_data = UserPasswordUpdate(
            current_password="WrongPass123!",
            new_password="NewPass123!",
        )
        mock_verify.return_value = False
        user_service.repository.get_by_id = Mock(return_value=mock_user)

        # Act & Assert
        with pytest.raises(PasswordMismatchError) as exc_info:
            user_service.update_password(user_id, password_data)

        assert exc_info.value.status_code == 422

    # ============================================================================
    # authenticate_user tests
    # ============================================================================

    @patch("productivity_tracker.services.user_service.verify_password")
    def test_authenticate_user_success(self, mock_verify, user_service, mock_user):
        """Test successful user authentication."""
        # Arrange
        mock_verify.return_value = True
        user_service.repository.get_by_username = Mock(return_value=mock_user)

        # Act
        result = user_service.authenticate_user("testuser", "Password123!")

        # Assert
        assert result == mock_user
        user_service.repository.get_by_username.assert_called_once_with("testuser")
        mock_verify.assert_called_once_with("Password123!", mock_user.hashed_password)

    def test_authenticate_user_not_found(self, user_service):
        """Test authentication fails when user doesn't exist."""
        # Arrange
        user_service.repository.get_by_username = Mock(return_value=None)

        # Act
        result = user_service.authenticate_user("nonexistent", "Password123!")

        # Assert
        assert result is None

    @patch("productivity_tracker.services.user_service.verify_password")
    def test_authenticate_user_wrong_password(self, mock_verify, user_service, mock_user):
        """Test authentication fails with wrong password."""
        # Arrange
        mock_verify.return_value = False
        user_service.repository.get_by_username = Mock(return_value=mock_user)

        # Act
        result = user_service.authenticate_user("testuser", "WrongPassword!")

        # Assert
        assert result is None

    # ============================================================================
    # delete_user tests
    # ============================================================================

    def test_delete_user_soft(self, user_service):
        """Test soft delete of user."""
        # Arrange
        user_id = uuid4()
        user_service.repository.delete = Mock(return_value=True)

        # Act
        result = user_service.delete_user(user_id, soft=True)

        # Assert
        assert result is True
        user_service.repository.delete.assert_called_once_with(user_id, soft=True)

    def test_delete_user_hard(self, user_service):
        """Test hard delete of user."""
        # Arrange
        user_id = uuid4()
        user_service.repository.delete = Mock(return_value=True)

        # Act
        result = user_service.delete_user(user_id, soft=False)

        # Assert
        assert result is True
        user_service.repository.delete.assert_called_once_with(user_id, soft=False)

    # ============================================================================
    # activate/deactivate tests
    # ============================================================================

    def test_activate_user(self, user_service, mock_user):
        """Test user activation."""
        # Arrange
        user_id = mock_user.id
        mock_user.is_active = False
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.update = Mock(return_value=mock_user)

        # Act
        result = user_service.activate_user(user_id)

        # Assert
        assert result == mock_user
        assert mock_user.is_active is True

    def test_deactivate_user(self, user_service, mock_user):
        """Test user deactivation."""
        # Arrange
        user_id = mock_user.id
        mock_user.is_active = True
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.update = Mock(return_value=mock_user)

        # Act
        result = user_service.deactivate_user(user_id)

        # Assert
        assert result == mock_user
        assert mock_user.is_active is False

    # ============================================================================
    # role management tests
    # ============================================================================

    def test_assign_roles(self, user_service, mock_user):
        """Test assigning roles to user."""
        # Arrange
        user_id = mock_user.id
        role_ids = [uuid4(), uuid4()]
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.assign_roles = Mock(return_value=mock_user)

        # Act
        result = user_service.assign_roles(user_id, role_ids)

        # Assert
        assert result == mock_user
        user_service.repository.assign_roles.assert_called_once_with(mock_user, role_ids)

    def test_add_role(self, user_service, mock_user):
        """Test adding a single role to user."""
        # Arrange
        user_id = mock_user.id
        role_id = uuid4()
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.add_role = Mock(return_value=mock_user)

        # Act
        result = user_service.add_role(user_id, role_id)

        # Assert
        assert result == mock_user
        user_service.repository.add_role.assert_called_once_with(mock_user, role_id)

    def test_remove_role(self, user_service, mock_user):
        """Test removing a role from user."""
        # Arrange
        user_id = mock_user.id
        role_id = uuid4()
        user_service.repository.get_by_id = Mock(return_value=mock_user)
        user_service.repository.remove_role = Mock(return_value=mock_user)

        # Act
        result = user_service.remove_role(user_id, role_id)

        # Assert
        assert result == mock_user
        user_service.repository.remove_role.assert_called_once_with(mock_user, role_id)
