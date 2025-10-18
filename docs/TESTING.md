# Testing Guide

This guide explains how to write and run tests for the Productivity Tracker Backend.

## Overview

The testing suite includes:
- **Unit Tests** - Fast tests with mocked dependencies
- **Integration Tests** - Tests with real database using Docker
- **Test Fixtures** - Reusable test data and configurations
- **Test Utilities** - Helper functions and factories

## Project Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── utils.py                       # Test utilities and factories
├── pytest.ini                     # Pytest configuration
├── unit/                          # Unit tests (mocked)
│   ├── test_user_service.py      # UserService tests
│   ├── test_role_service.py      # RoleService tests
│   ├── test_user_repository.py   # UserRepository tests
│   └── test_exceptions.py        # Exception tests
└── integration/                   # Integration tests (real DB)
    ├── test_auth_endpoints.py    # Authentication API tests
    └── test_rbac_endpoints.py    # RBAC API tests
```

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run unit tests only (fast)
make test-unit

# Run integration tests only
make test-integration

# Run with coverage report
make test-cov
```

### Using Pytest Directly

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_user_service.py

# Run specific test class
poetry run pytest tests/unit/test_user_service.py::TestUserService

# Run specific test method
poetry run pytest tests/unit/test_user_service.py::TestUserService::test_create_user_success

# Run tests matching a pattern
poetry run pytest -k "test_create"

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=productivity_tracker --cov-report=html
```

### Using Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run only authentication tests
poetry run pytest -m auth

# Run only RBAC tests
poetry run pytest -m rbac

# Combine markers (OR)
poetry run pytest -m "unit or integration"

# Combine markers (AND)
poetry run pytest -m "integration and auth"

# Exclude markers
poetry run pytest -m "not slow"
```

## Integration Tests with Docker

Integration tests use a PostgreSQL test database running in Docker.

### Starting the Test Database

```bash
# Start test database
make test-db-up

# Run integration tests
make test-integration

# Stop test database
make test-db-down

# Clean up (remove volumes)
make test-db-clean
```

### Running Full Integration Test Suite

```bash
# This command will:
# 1. Start the test database
# 2. Run integration tests
# 3. Stop the test database
make test-integration-full
```

### Test Database Configuration

The test database runs on:
- **Host**: localhost
- **Port**: 5433 (different from dev DB to avoid conflicts)
- **Database**: test_productivity_tracker
- **User**: test_user
- **Password**: test_password

Configuration is in `docker-compose.test.yml`.

## Writing Tests

### Unit Tests

Unit tests use mocked dependencies for fast, isolated testing.

**Example: Testing a Service**

```python
import pytest
from unittest.mock import MagicMock, Mock
from uuid import uuid4

pytestmark = pytest.mark.unit

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

    def test_create_user_success(self, user_service):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123!",
        )
        user_service.repository.get_by_email_or_username = Mock(return_value=None)
        user_service.repository.create = Mock(return_value=mock_user)

        # Act
        result = user_service.create_user(user_data)

        # Assert
        assert result == mock_user
        user_service.repository.create.assert_called_once()
```

### Integration Tests

Integration tests use a real database (SQLite for unit fixtures, PostgreSQL for full integration).

**Example: Testing an API Endpoint**

```python
import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.integration, pytest.mark.auth]

class TestAuthenticationEndpoints:
    """Integration tests for authentication endpoints."""

    def test_register_user_success(self, client_unit: TestClient):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }

        # Act
        response = client_unit.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
```

## Test Fixtures

### Available Fixtures

**Database Fixtures:**
- `db_session_unit` - In-memory SQLite session for unit tests
- `db_session_integration` - PostgreSQL session for integration tests
- `client_unit` - TestClient with unit test database
- `client_integration` - TestClient with integration test database

**Entity Fixtures:**
- `sample_user` - Regular active user
- `sample_superuser` - Superuser account
- `sample_inactive_user` - Inactive user
- `sample_permission` - Single permission
- `sample_permissions` - List of permissions
- `sample_role` - Role with permissions
- `sample_admin_role` - Admin role with all permissions
- `user_with_role` - User with assigned role

**Authentication Fixtures:**
- `auth_headers` - Authorization headers for regular user
- `superuser_auth_headers` - Authorization headers for superuser

**Mock Data Fixtures:**
- `mock_user_data` - Sample user data dictionary
- `mock_role_data` - Sample role data dictionary
- `mock_permission_data` - Sample permission data dictionary

### Using Fixtures

```python
def test_example(self, client_unit, sample_user, auth_headers):
    """Test using multiple fixtures."""
    # client_unit: TestClient instance
    # sample_user: User entity
    # auth_headers: Dict with Authorization header

    response = client_unit.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

## Test Utilities

### Factory Classes

Use factories to create test data easily:

```python
from tests.utils import UserFactory, RoleFactory, PermissionFactory

# Create a user
user = UserFactory.create(username="testuser", email="test@example.com")

# Create a superuser
admin = UserFactory.create_superuser()

# Create a role
role = RoleFactory.create(name="manager", description="Manager role")

# Create permissions
permissions = PermissionFactory.create_crud_permissions("task")
```

### Assertion Helpers

Use assertion helpers for consistent validation:

```python
from tests.utils import assert_user_response, assert_error_response

# Assert user response format
assert_user_response(response_data, expected_username="testuser")

# Assert error response format
assert_error_response(response_data, "EMAIL_ALREADY_EXISTS", 409)
```

## Best Practices

### 1. Test Organization

- **One test class per service/endpoint**
- **Group related tests together**
- **Use descriptive test names** that explain what is being tested

```python
# Good
def test_create_user_with_duplicate_email_fails(self):
    """Test that creating a user with an existing email fails."""
    pass

# Bad
def test_create_user_2(self):
    pass
```

### 2. Arrange-Act-Assert Pattern

Structure your tests clearly:

```python
def test_example(self):
    # Arrange - Set up test data and conditions
    user_data = UserCreate(...)

    # Act - Execute the code being tested
    result = user_service.create_user(user_data)

    # Assert - Verify the results
    assert result.username == user_data.username
```

### 3. Use Fixtures for Common Setup

Don't repeat setup code - use fixtures:

```python
# Bad - repeated setup
def test_one(self):
    user = User(username="test", email="test@example.com")
    # test code

def test_two(self):
    user = User(username="test", email="test@example.com")
    # test code

# Good - use fixture
@pytest.fixture
def sample_user(self):
    return User(username="test", email="test@example.com")

def test_one(self, sample_user):
    # test code

def test_two(self, sample_user):
    # test code
```

### 4. Mock External Dependencies

Mock everything except what you're testing:

```python
@patch("productivity_tracker.services.user_service.hash_password")
def test_create_user(self, mock_hash, user_service):
    mock_hash.return_value = "hashed_password"
    # Now hash_password is mocked and won't actually hash
```

### 5. Test Error Cases

Don't just test the happy path:

```python
def test_create_user_success(self):
    """Test successful user creation."""
    # Happy path

def test_create_user_duplicate_email(self):
    """Test failure with duplicate email."""
    # Error case

def test_create_user_invalid_email(self):
    """Test failure with invalid email."""
    # Validation error
```

### 6. Use Markers to Categorize Tests

```python
pytestmark = [pytest.mark.unit, pytest.mark.slow]

class TestExpensiveOperation:
    """Tests that take a long time."""
    pass
```

### 7. Keep Tests Independent

Each test should be able to run independently:

```python
# Bad - tests depend on each other
def test_create_user(self):
    self.user_id = service.create_user(data).id

def test_get_user(self):
    user = service.get_user(self.user_id)  # Depends on test_create_user

# Good - tests are independent
def test_create_user(self, user_service):
    result = user_service.create_user(data)
    assert result.id is not None

def test_get_user(self, user_service, sample_user):
    result = user_service.get_user(sample_user.id)
    assert result == sample_user
```

## Coverage Reports

### Viewing Coverage

After running tests with coverage:

```bash
# Generate HTML coverage report
make test-cov

# Open the report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Overall**: Aim for >80% coverage
- **Critical paths**: >90% coverage for auth, security, RBAC
- **New code**: All new code should have tests

### Checking Coverage

```bash
# Terminal report with missing lines
poetry run pytest --cov=productivity_tracker --cov-report=term-missing

# Generate XML for CI tools
poetry run pytest --cov=productivity_tracker --cov-report=xml
```

## Continuous Integration

The test suite integrates with CI/CD pipelines:

```bash
# Run all CI checks
make ci

# This runs:
# 1. Code formatting (black, isort)
# 2. Linting (ruff, mypy, bandit)
# 3. Tests with coverage
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Add print statements (they'll be captured)
poetry run pytest -s

# Drop into debugger on failure
poetry run pytest --pdb

# Drop into debugger on error
poetry run pytest -x --pdb
```

### Verbose Output

```bash
# Show all output
poetry run pytest -vv

# Show local variables on failure
poetry run pytest -l

# Show print statements
poetry run pytest -s
```

### Running Specific Tests During Development

```bash
# Run just one test repeatedly
poetry run pytest tests/unit/test_user_service.py::TestUserService::test_create_user_success -v

# Watch mode (requires pytest-watch)
make test-watch
```

## Common Issues

### Issue: Tests fail with "Database is locked"

**Solution**: This happens with SQLite when tests run in parallel. Disable parallelization for SQLite tests:

```bash
poetry run pytest tests/unit -n 0
```

### Issue: Integration tests fail with "Connection refused"

**Solution**: Make sure the test database is running:

```bash
make test-db-up
```

### Issue: Fixtures not found

**Solution**: Make sure `conftest.py` is in the correct location and fixtures are properly defined.

### Issue: Import errors in tests

**Solution**: Make sure you're running tests through poetry:

```bash
poetry run pytest  # Good
pytest  # May not work if not in venv
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## Next Steps

1. **Write tests for new features** before implementing them (TDD)
2. **Run tests before committing** - use `make check`
3. **Review coverage reports** to find untested code
4. **Add integration tests** for critical user flows
5. **Keep tests fast** - use unit tests when possible
