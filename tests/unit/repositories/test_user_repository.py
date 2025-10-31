"""Unit tests for user repository."""

from uuid import uuid4

import pytest

from productivity_tracker.core.security import hash_password
from productivity_tracker.database.entities.role import Role
from productivity_tracker.database.entities.user import User
from productivity_tracker.repositories.user_repository import UserRepository

pytestmark = [pytest.mark.unit]


class TestUserRepository:
    """Test user repository methods."""

    def test_get_by_username(self, db_session_unit):
        """Should get user by username."""
        repo = UserRepository(db_session_unit)

        # Create user
        user = User(
            username="testuser", email="test@example.com", hashed_password=hash_password("password")
        )
        created_user = repo.create(user)

        # Get by username
        retrieved = repo.get_by_username("testuser")

        assert retrieved is not None
        assert retrieved.id == created_user.id
        assert retrieved.username == "testuser"

    def test_get_by_username_not_found(self, db_session_unit):
        """Should return None for non-existent username."""
        repo = UserRepository(db_session_unit)

        result = repo.get_by_username("nonexistent")

        assert result is None

    def test_get_by_email(self, db_session_unit):
        """Should get user by email."""
        repo = UserRepository(db_session_unit)

        # Create user
        user = User(
            username="emailuser",
            email="email@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Get by email
        retrieved = repo.get_by_email("email@example.com")

        assert retrieved is not None
        assert retrieved.id == created_user.id
        assert retrieved.email == "email@example.com"

    def test_get_by_email_not_found(self, db_session_unit):
        """Should return None for non-existent email."""
        repo = UserRepository(db_session_unit)

        result = repo.get_by_email("nonexistent@example.com")

        assert result is None

    def test_get_by_email_or_username_by_email(self, db_session_unit):
        """Should get user by email when searching by email or username."""
        repo = UserRepository(db_session_unit)

        # Create user
        unique = uuid4().hex[:8]
        user = User(
            username=f"user1_{unique}",
            email=f"user1_{unique}@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Get by email
        retrieved = repo.get_by_email_or_username(f"user1_{unique}@example.com", "other_username")

        assert retrieved is not None
        assert retrieved.id == created_user.id

    def test_get_by_email_or_username_by_username(self, db_session_unit):
        """Should get user by username when searching by email or username."""
        repo = UserRepository(db_session_unit)

        # Create user
        unique = uuid4().hex[:8]
        user = User(
            username=f"user2_{unique}",
            email=f"user2_{unique}@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Get by username
        retrieved = repo.get_by_email_or_username("other@example.com", f"user2_{unique}")

        assert retrieved is not None
        assert retrieved.id == created_user.id

    def test_get_active_users(self, db_session_unit):
        """Should get all active users."""
        repo = UserRepository(db_session_unit)

        # Create active and inactive users
        unique = uuid4().hex[:8]
        active_user = User(
            username=f"active_{unique}",
            email=f"active_{unique}@example.com",
            hashed_password=hash_password("password"),
            is_active=True,
        )
        inactive_user = User(
            username=f"inactive_{unique}",
            email=f"inactive_{unique}@example.com",
            hashed_password=hash_password("password"),
            is_active=False,
        )
        repo.create(active_user)
        repo.create(inactive_user)

        # Get active users
        users = repo.get_active_users()

        usernames = [u.username for u in users]
        assert f"active_{unique}" in usernames
        assert f"inactive_{unique}" not in usernames

    def test_get_superusers(self, db_session_unit):
        """Should get all superusers."""
        repo = UserRepository(db_session_unit)

        # Create regular user and superuser
        regular_user = User(
            username="regular",
            email="regular@example.com",
            hashed_password=hash_password("password"),
            is_superuser=False,
        )
        super_user = User(
            username="superuser",
            email="super@example.com",
            hashed_password=hash_password("password"),
            is_superuser=True,
        )
        repo.create(regular_user)
        repo.create(super_user)

        # Get superusers
        superusers = repo.get_superusers()

        usernames = [u.username for u in superusers]
        assert "superuser" in usernames
        assert "regular" not in usernames

    def test_assign_roles(self, db_session_unit):
        """Should assign multiple roles to user."""
        repo = UserRepository(db_session_unit)

        # Create user
        user = User(
            username="roleuser", email="role@example.com", hashed_password=hash_password("password")
        )
        created_user = repo.create(user)

        # Create roles
        role1 = Role(name="role1", description="Role 1")
        role2 = Role(name="role2", description="Role 2")
        db_session_unit.add(role1)
        db_session_unit.add(role2)
        db_session_unit.commit()
        db_session_unit.refresh(role1)
        db_session_unit.refresh(role2)

        # Assign roles
        updated_user = repo.assign_roles(created_user, [role1.id, role2.id])

        assert len(updated_user.roles) == 2
        role_names = [r.name for r in updated_user.roles]
        assert "role1" in role_names
        assert "role2" in role_names

    def test_add_role(self, db_session_unit):
        """Should add single role to user."""
        repo = UserRepository(db_session_unit)

        # Create user
        user = User(
            username="addroleuser",
            email="addrole@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Create role
        role = Role(name="newrole", description="New Role")
        db_session_unit.add(role)
        db_session_unit.commit()
        db_session_unit.refresh(role)

        # Add role
        updated_user = repo.add_role(created_user, role.id)

        assert len(updated_user.roles) == 1
        assert updated_user.roles[0].name == "newrole"

    def test_add_role_already_exists(self, db_session_unit):
        """Should not duplicate role if already exists."""
        repo = UserRepository(db_session_unit)

        # Create user with role
        role = Role(name="existing", description="Existing Role")
        user = User(
            username="dupuser", email="dup@example.com", hashed_password=hash_password("password")
        )
        user.roles.append(role)
        created_user = repo.create(user)

        # Try to add same role again
        updated_user = repo.add_role(created_user, role.id)

        assert len(updated_user.roles) == 1

    def test_remove_role(self, db_session_unit):
        """Should remove role from user."""
        repo = UserRepository(db_session_unit)

        # Create user with roles
        role1 = Role(name="keep", description="Keep Role")
        role2 = Role(name="remove", description="Remove Role")
        user = User(
            username="removeuser",
            email="remove@example.com",
            hashed_password=hash_password("password"),
        )
        user.roles.extend([role1, role2])
        created_user = repo.create(user)

        # Remove one role
        updated_user = repo.remove_role(created_user, role2.id)

        assert len(updated_user.roles) == 1
        assert updated_user.roles[0].name == "keep"

    def test_remove_role_not_in_user(self, db_session_unit):
        """Should handle removing role not assigned to user."""
        repo = UserRepository(db_session_unit)

        # Create user without roles
        user = User(
            username="noroleuser",
            email="norole@example.com",
            hashed_password=hash_password("password"),
        )
        created_user = repo.create(user)

        # Create role not assigned to user
        role = Role(name="notassigned", description="Not Assigned")
        db_session_unit.add(role)
        db_session_unit.commit()
        db_session_unit.refresh(role)

        # Try to remove it
        updated_user = repo.remove_role(created_user, role.id)

        assert len(updated_user.roles) == 0

    def test_get_users_by_role(self, db_session_unit):
        """Should get users by role name."""
        repo = UserRepository(db_session_unit)

        # Create role
        unique = uuid4().hex[:8]
        admin_role = Role(name=f"admin_{unique}", description="Admin Role")
        db_session_unit.add(admin_role)
        db_session_unit.commit()
        db_session_unit.refresh(admin_role)

        # Create users with and without role
        admin_user = User(
            username=f"admin1_{unique}",
            email=f"admin1_{unique}@example.com",
            hashed_password=hash_password("password"),
        )
        admin_user.roles.append(admin_role)

        regular_user = User(
            username=f"regular1_{unique}",
            email=f"regular1_{unique}@example.com",
            hashed_password=hash_password("password"),
        )

        repo.create(admin_user)
        repo.create(regular_user)

        # Get users by role
        users = repo.get_users_by_role(f"admin_{unique}")

        assert len(users) >= 1
        usernames = [u.username for u in users]
        assert f"admin1_{unique}" in usernames
        assert f"regular1_{unique}" not in usernames

    def test_search_users_by_username(self, db_session_unit):
        """Should search users by username."""
        repo = UserRepository(db_session_unit)

        # Create users
        user1 = User(
            username="searchable_john",
            email="john@example.com",
            hashed_password=hash_password("password"),
        )
        user2 = User(
            username="searchable_jane",
            email="jane@example.com",
            hashed_password=hash_password("password"),
        )
        user3 = User(
            username="other", email="other@example.com", hashed_password=hash_password("password")
        )
        repo.create(user1)
        repo.create(user2)
        repo.create(user3)

        # Search
        results = repo.search_users("searchable")

        usernames = [u.username for u in results]
        assert "searchable_john" in usernames
        assert "searchable_jane" in usernames
        assert "other" not in usernames

    def test_search_users_by_email(self, db_session_unit):
        """Should search users by email."""
        repo = UserRepository(db_session_unit)

        # Create users
        unique = uuid4().hex[:8]
        user1 = User(
            username=f"searchuser1_{unique}",
            email=f"search{unique}@company.com",
            hashed_password=hash_password("password"),
        )
        user2 = User(
            username=f"otheruser2_{unique}",
            email=f"other{unique}@different.com",
            hashed_password=hash_password("password"),
        )
        repo.create(user1)
        repo.create(user2)

        # Search by email domain
        results = repo.search_users(f"search{unique}")

        emails = [u.email for u in results]
        assert f"search{unique}@company.com" in emails
        assert f"other{unique}@different.com" not in emails
