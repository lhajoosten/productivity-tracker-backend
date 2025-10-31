"""Unit tests for base repository."""

from uuid import uuid4

import pytest

from productivity_tracker.core.security import hash_password
from productivity_tracker.database.entities.user import User
from productivity_tracker.repositories.user_repository import UserRepository

pytestmark = [pytest.mark.unit]


class TestBaseRepository:
    """Test base repository CRUD methods."""

    def test_restore_soft_deleted(self, db_session_unit):
        """Should restore a soft-deleted entity."""
        repo = UserRepository(db_session_unit)

        # Create and soft delete user
        user = User(
            username="deleteduser",
            email="deleted@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)
        repo.delete(created_user.id, soft=True)

        # Restore user
        restored = repo.restore(created_user.id)

        assert restored is not None
        assert restored.is_deleted is False
        assert restored.id == created_user.id

    def test_restore_nonexistent(self, db_session_unit):
        """Should return None when restoring non-existent entity."""
        repo = UserRepository(db_session_unit)

        result = repo.restore(uuid4())

        assert result is None

    def test_restore_not_deleted(self, db_session_unit):
        """Should return None when restoring entity that's not deleted."""
        repo = UserRepository(db_session_unit)

        # Create user (not deleted)
        user = User(
            username="activeuser",
            email="active@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Try to restore
        result = repo.restore(created_user.id)

        assert result is None

    def test_count_without_deleted(self, db_session_unit):
        """Should count entities excluding soft-deleted ones."""
        repo = UserRepository(db_session_unit)

        # Create users
        user1 = User(
            username="user1", email="user1@example.com", hashed_password=hash_password("password")
        )
        user2 = User(
            username="user2", email="user2@example.com", hashed_password=hash_password("password")
        )
        created_user1 = repo.create(user1)
        repo.create(user2)

        # Soft delete one
        repo.delete(created_user1.id, soft=True)

        # Count should exclude deleted
        count = repo.count(include_deleted=False)

        # There might be other users from fixtures, so we check relative count
        count_with_deleted = repo.count(include_deleted=True)
        assert count < count_with_deleted

    def test_count_with_deleted(self, db_session_unit):
        """Should count entities including soft-deleted ones."""
        repo = UserRepository(db_session_unit)

        # Create users
        user1 = User(
            username="countuser1",
            email="countuser1@example.com",
            hashed_password=hash_password("password"),
        )
        user2 = User(
            username="countuser2",
            email="countuser2@example.com",
            hashed_password=hash_password("password"),
        )
        created_user1 = repo.create(user1)
        repo.create(user2)

        # Count before delete
        count_before = repo.count(include_deleted=True)

        # Soft delete one
        repo.delete(created_user1.id, soft=True)

        # Count after delete should be the same when including deleted
        count_after = repo.count(include_deleted=True)
        assert count_before == count_after

    def test_get_by_id_exclude_deleted(self, db_session_unit):
        """Should not return soft-deleted entity by default."""
        repo = UserRepository(db_session_unit)

        # Create and soft delete user
        user = User(
            username="softdeleted",
            email="softdeleted@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)
        repo.delete(created_user.id, soft=True)

        # Try to get without including deleted
        result = repo.get_by_id(created_user.id, include_deleted=False)

        assert result is None

    def test_get_by_id_include_deleted(self, db_session_unit):
        """Should return soft-deleted entity when include_deleted=True."""
        repo = UserRepository(db_session_unit)

        # Create and soft delete user
        user = User(
            username="includedeleted",
            email="includedeleted@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)
        repo.delete(created_user.id, soft=True)

        # Get with include_deleted=True
        result = repo.get_by_id(created_user.id, include_deleted=True)

        assert result is not None
        assert result.id == created_user.id
        assert result.is_deleted is True

    def test_get_all_exclude_deleted(self, db_session_unit):
        """Should exclude soft-deleted entities from get_all by default."""
        repo = UserRepository(db_session_unit)

        # Create users
        user1 = User(
            username="getalluser1",
            email="getalluser1@example.com",
            hashed_password=hash_password("password"),
        )
        user2 = User(
            username="getalluser2",
            email="getalluser2@example.com",
            hashed_password=hash_password("password"),
        )
        created_user1 = repo.create(user1)
        repo.create(user2)

        # Soft delete one
        repo.delete(created_user1.id, soft=True)

        # Get all without deleted
        users = repo.get_all(include_deleted=False)

        usernames = [u.username for u in users]
        assert "getalluser2" in usernames
        assert "getalluser1" not in usernames

    def test_get_all_include_deleted(self, db_session_unit):
        """Should include soft-deleted entities when include_deleted=True."""
        repo = UserRepository(db_session_unit)

        # Create users
        user1 = User(
            username="includeuser1",
            email="includeuser1@example.com",
            hashed_password=hash_password("password"),
        )
        user2 = User(
            username="includeuser2",
            email="includeuser2@example.com",
            hashed_password=hash_password("password"),
        )
        created_user1 = repo.create(user1)
        repo.create(user2)

        # Soft delete one
        repo.delete(created_user1.id, soft=True)

        # Get all with deleted
        users = repo.get_all(include_deleted=True)

        usernames = [u.username for u in users]
        assert "includeuser1" in usernames
        assert "includeuser2" in usernames

    def test_hard_delete(self, db_session_unit):
        """Should permanently delete entity when soft=False."""
        repo = UserRepository(db_session_unit)

        # Create user
        user = User(
            username="harddelete",
            email="harddelete@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)
        user_id = created_user.id

        # Hard delete
        repo.delete(user_id, soft=False)

        # Should not be found even with include_deleted=True
        result = repo.get_by_id(user_id, include_deleted=True)
        assert result is None
