"""Example unit tests for repositories."""

from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from productivity_tracker.database.entities import User
from productivity_tracker.repositories.user_repository import UserRepository

pytestmark = [pytest.mark.unit]


class TestUserRepository:
    """Test cases for UserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def repository(self, mock_session):
        """Create a UserRepository instance with a mocked session."""
        return UserRepository(mock_session)

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid4()
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_deleted = False
        return user

    def test_get_by_username(self, repository, mock_session, mock_user):
        """Test get user by username."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_user

        # Act
        result = repository.get_by_username("testuser")

        # Assert
        assert result == mock_user
        mock_session.query.assert_called_once_with(User)

    def test_get_by_username_not_found(self, repository, mock_session):
        """Test get user by username returns None when not found."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None

        # Act
        result = repository.get_by_username("nonexistent")

        # Assert
        assert result is None

    def test_get_by_email(self, repository, mock_session, mock_user):
        """Test get user by email."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_user

        # Act
        result = repository.get_by_email("test@example.com")

        # Assert
        assert result == mock_user

    def test_get_active_users(self, repository, mock_session, mock_user):
        """Test get active users with pagination."""
        # Arrange
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_user
        ]

        # Act
        result = repository.get_active_users(skip=0, limit=10)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_user

    def test_create_user(self, repository, mock_session, mock_user):
        """Test creating a user."""
        # Arrange
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Act
        result = repository.create(mock_user)

        # Assert
        assert result == mock_user
        mock_session.add.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_user)
