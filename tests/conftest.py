"""Pytest configuration and fixtures for testing."""

import os
import threading
from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from productivity_tracker.core.database import Base
from productivity_tracker.core.security import hash_password
from productivity_tracker.database import get_db
from productivity_tracker.database.entities import Permission, Role, User
from productivity_tracker.main import app

# Use in-memory SQLite for unit tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Use PostgreSQL from environment for integration tests
SQLALCHEMY_INTEGRATION_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/test_productivity_tracker",
)

# Thread-safe counter for unique identifiers
_counter_lock = threading.Lock()
_counter = 0


def get_unique_id() -> str:
    """Generate a truly unique identifier combining UUID, thread ID, and counter."""
    global _counter
    with _counter_lock:
        _counter += 1
        thread_id = threading.get_ident()
        return f"{uuid4().hex[:8]}_{thread_id}_{_counter}"


@pytest.fixture(scope="session")
def engine_unit():
    """Create an in-memory SQLite engine for unit tests."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def engine_integration():
    """Create a PostgreSQL engine for integration tests."""
    engine = create_engine(
        SQLALCHEMY_INTEGRATION_DATABASE_URL,
        isolation_level="READ COMMITTED",  # Allow reading uncommitted data in same transaction
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session_unit(engine_unit) -> Generator[Session, None, None]:
    """Create a new database session for a unit test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine_unit
    )
    session = TestingSessionLocal()

    try:
        yield session
        session.flush()  # Ensure all changes are visible
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def db_session_integration(engine_integration) -> Generator[Session, None, None]:
    """Create a new database session for an integration test.

    This session uses a transaction that will be rolled back after the test,
    ensuring test isolation. All data created in fixtures and tests will be
    visible within the same transaction but rolled back at the end.
    """
    # Create a connection
    connection = engine_integration.connect()

    # Begin a transaction
    transaction = connection.begin()

    # Create session bound to the connection
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection, expire_on_commit=False
    )
    session = TestingSessionLocal()

    # Begin a nested transaction (savepoint)
    session.begin_nested()

    # When the application calls commit(), we want it to end the nested transaction
    # and start a new one, so the data stays in the outer transaction
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            # Re-establish a savepoint after each commit
            session.begin_nested()

    try:
        yield session
    finally:
        # Remove the event listener
        event.remove(session, "after_transaction_end", restart_savepoint)
        # Always rollback everything
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client_unit(db_session_unit: Session) -> Generator[TestClient, None, None]:
    """Create a test client with in-memory database for unit tests."""

    def override_get_db():
        try:
            yield db_session_unit
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_integration(
    db_session_integration: Session,
) -> Generator[TestClient, None, None]:
    """Create a test client with PostgreSQL database for integration tests."""

    def override_get_db():
        try:
            # Return the same session that the test fixtures use
            yield db_session_integration
        finally:
            # Don't close the session here - let the fixture handle it
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Entity Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def sample_user(db_session_unit: Session) -> User:
    """Create a sample user for testing."""
    # Use unique identifier to avoid conflicts across tests
    unique_id = str(uuid4())[:8]
    user = User(
        username=f"testuser_{unique_id}",
        email=f"testuser_{unique_id}@example.com",
        hashed_password=hash_password("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session_unit.add(user)
    db_session_unit.commit()
    db_session_unit.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_superuser(db_session_unit: Session) -> User:
    """Create a sample superuser for testing."""
    # Use unique identifier to avoid conflicts across tests
    unique_id = str(uuid4())[:8]
    user = User(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        hashed_password=hash_password("AdminPassword123!"),
        is_active=True,
        is_superuser=True,
    )
    db_session_unit.add(user)
    db_session_unit.commit()
    db_session_unit.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_inactive_user(db_session_unit: Session) -> User:
    """Create an inactive user for testing."""
    unique_id = str(uuid4())[:8]
    user = User(
        username=f"inactiveuser_{unique_id}",
        email=f"inactive_{unique_id}@example.com",
        hashed_password=hash_password("InactivePassword123!"),
        is_active=False,
        is_superuser=False,
    )
    db_session_unit.add(user)
    db_session_unit.commit()
    db_session_unit.refresh(user)
    return user


# ============================================================================
# Integration Test Entity Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def sample_user_integration(db_session_integration: Session) -> User:
    """Create a sample user for integration testing."""
    # Use unique identifier to avoid conflicts across tests
    unique_id = get_unique_id()
    user = User(
        username=f"testuser_{unique_id}",
        email=f"testuser_{unique_id}@example.com",
        hashed_password=hash_password("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session_integration.add(user)
    db_session_integration.flush()
    db_session_integration.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_superuser_integration(db_session_integration: Session) -> User:
    """Create a sample superuser for integration testing."""
    # Use unique identifier to avoid conflicts across tests
    unique_id = get_unique_id()
    user = User(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        hashed_password=hash_password("AdminPassword123!"),
        is_active=True,
        is_superuser=True,
    )
    db_session_integration.add(user)
    db_session_integration.flush()
    db_session_integration.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_inactive_user_integration(db_session_integration: Session) -> User:
    """Create an inactive user for integration testing."""
    unique_id = get_unique_id()
    user = User(
        username=f"inactiveuser_{unique_id}",
        email=f"inactive_{unique_id}@example.com",
        hashed_password=hash_password("InactivePassword123!"),
        is_active=False,
        is_superuser=False,
    )
    db_session_integration.add(user)
    db_session_integration.flush()
    db_session_integration.refresh(user)
    return user


@pytest.fixture
def sample_permission(db_session_unit: Session) -> Permission:
    """Create a sample permission for testing."""
    # Check if permission already exists
    existing = (
        db_session_unit.query(Permission)
        .filter(Permission.name == "tasks:read", Permission.is_deleted.is_(False))
        .first()
    )

    if existing:
        return existing

    permission = Permission(
        name="tasks:read",
        resource="task",
        action="read",
        description="Read tasks",
    )
    db_session_unit.add(permission)
    db_session_unit.commit()
    db_session_unit.refresh(permission)
    return permission


@pytest.fixture
def sample_permissions(db_session_unit: Session) -> list[Permission]:
    """Create multiple permissions for testing."""
    permission_data = [
        ("tasks:create", "task", "create", "Create tasks"),
        ("tasks:read", "task", "read", "Read tasks"),
        ("tasks:update", "task", "update", "Update tasks"),
        ("tasks:delete", "task", "delete", "Delete tasks"),
    ]

    permissions = []
    for name, resource, action, description in permission_data:
        # Check if permission already exists
        existing = (
            db_session_unit.query(Permission)
            .filter(Permission.name == name, Permission.is_deleted.is_(False))
            .first()
        )

        if existing:
            permissions.append(existing)
        else:
            perm = Permission(
                name=name,
                resource=resource,
                action=action,
                description=description,
            )
            db_session_unit.add(perm)
            permissions.append(perm)

    db_session_unit.commit()
    for perm in permissions:
        db_session_unit.refresh(perm)
    return permissions


@pytest.fixture
def sample_role(db_session_unit: Session, sample_permissions: list[Permission]) -> Role:
    """Create a sample role with permissions for testing."""
    role = Role(
        name="user",
        description="Regular user role",
    )
    role.permissions = sample_permissions[:2]  # Assign first 2 permissions
    db_session_unit.add(role)
    db_session_unit.commit()
    db_session_unit.refresh(role)
    return role


@pytest.fixture
def sample_admin_role(
    db_session_unit: Session, sample_permissions: list[Permission]
) -> Role:
    """Create an admin role with all permissions for testing."""
    role = Role(
        name="admin",
        description="Administrator role",
    )
    role.permissions = sample_permissions  # Assign all permissions
    db_session_unit.add(role)
    db_session_unit.commit()
    db_session_unit.refresh(role)
    return role


@pytest.fixture
def user_with_role(db_session_unit: Session, sample_role: Role) -> User:
    """Create a user with an assigned role."""
    user = User(
        username="roleuser",
        email="roleuser@example.com",
        hashed_password=hash_password("RolePassword123!"),
        is_active=True,
        is_superuser=False,
    )
    user.roles.append(sample_role)
    db_session_unit.add(user)
    db_session_unit.commit()
    db_session_unit.refresh(user)
    return user


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def auth_headers(client_unit: TestClient, sample_user: User) -> dict[str, str]:
    """Get authentication headers for a regular user."""
    response = client_unit.post(
        "/api/v1/auth/login",
        json={
            "username": sample_user.username,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
def superuser_auth_headers(
    client_unit: TestClient, sample_superuser: User
) -> dict[str, str]:
    """Get authentication headers for a superuser."""
    response = client_unit.post(
        "/api/v1/auth/login",
        json={
            "username": sample_superuser.username,
            "password": "AdminPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_user_data():
    """Sample user data for testing."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPassword123!",
    }


@pytest.fixture
def mock_role_data():
    """Sample role data for testing."""
    return {
        "name": "manager",
        "description": "Manager role with elevated permissions",
    }


@pytest.fixture
def mock_permission_data():
    """Sample permission data for testing."""
    return {
        "name": "projects:create",
        "resource": "project",
        "action": "create",
        "description": "Create projects",
    }
