from unittest.mock import Mock

from productivity_tracker.database.entities.user import User


def create_mock_user(
    user_id: str = "3cde7768-85e7-4cd4-a7f9-3474fb0105e2",
    email: str = "test@example.com",
    username: str = "testuser",
    is_active: bool = True,
    is_superuser: bool = True,
) -> User:
    """Create a mock user for testing."""
    mock_user = Mock(spec=User)
    mock_user.id = user_id
    mock_user.email = email
    mock_user.username = username
    mock_user.is_active = is_active
    mock_user.is_superuser = is_superuser
    return mock_user


def mock_current_user(user: User = None):
    """Return a mock current user for dependency override."""
    if user is None:
        user = create_mock_user()
    return lambda: user
