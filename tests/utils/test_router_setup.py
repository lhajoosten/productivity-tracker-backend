from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from productivity_tracker.api.setup import setup_versioned_routers
from productivity_tracker.core.dependencies import get_current_user, get_db
from productivity_tracker.versioning.versioning import CURRENT_VERSION
from tests.utils.mock_auth import create_mock_user, mock_current_user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
    return mock_session


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    app = FastAPI(
        title="Test API",
        version="1.0.0",
        docs_url=f"{CURRENT_VERSION.prefix}/docs",
        redoc_url=f"{CURRENT_VERSION.prefix}/redoc",
        openapi_url=f"{CURRENT_VERSION.prefix}/openapi.json",
    )
    setup_versioned_routers(app)
    return app


@pytest.fixture
def authenticated_app(app, mock_db_session):
    """Create an authenticated test app with mocked user and database."""
    mock_user = create_mock_user()
    app.dependency_overrides[get_current_user] = mock_current_user(mock_user)
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield app
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def authenticated_client(authenticated_app):
    """Create an authenticated test client."""
    return TestClient(authenticated_app)


pytestmark = [pytest.mark.utils]


class TestRouterRegistration:
    """Test that routers are registered correctly."""

    def test_health_endpoint_exists(self, client):
        """Health endpoint should be registered."""
        response = client.get(f"{CURRENT_VERSION.prefix}/health")
        assert response.status_code == 200

    def test_auth_endpoints_exist(self, client):
        """Auth endpoints should be registered."""
        # This will fail validation (missing body) but endpoint exists
        response = client.post(f"{CURRENT_VERSION.prefix}/auth/login")
        assert response.status_code == 422  # Validation error, not 404

    def test_roles_endpoints_exist(self, authenticated_client):
        """Roles endpoints should be registered."""
        response = authenticated_client.get(f"{CURRENT_VERSION.prefix}/roles")
        # Should return 200 (success) not 404 (not found)
        assert response.status_code == 200
        # Empty list since we're mocking
        assert response.json() == []

    def test_permissions_endpoints_exist(self, authenticated_client):
        """Permissions endpoints should be registered."""
        response = authenticated_client.get(f"{CURRENT_VERSION.prefix}/permissions")
        # Should return 200 (success) not 404 (not found)
        assert response.status_code == 200
        # Empty list since we're mocking
        assert response.json() == []


class TestOpenAPIGeneration:
    """Test that OpenAPI docs are generated correctly."""

    def test_openapi_schema_generated(self, client):
        """OpenAPI schema should be generated."""
        response = client.get(f"{CURRENT_VERSION.prefix}/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_no_duplicate_paths(self, client):
        """OpenAPI schema should not have duplicate paths."""
        response = client.get(f"{CURRENT_VERSION.prefix}/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        paths = schema["paths"]

        # Check for duplicates
        path_list = list(paths.keys())
        unique_paths = set(path_list)

        if len(path_list) != len(unique_paths):
            duplicates = [p for p in path_list if path_list.count(p) > 1]
            pytest.fail(f"Duplicate paths found: {set(duplicates)}")

    def test_correct_tags(self, client):
        """Endpoints should have correct tags."""
        response = client.get(f"{CURRENT_VERSION.prefix}/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Collect all tags used
        used_tags = set()
        for path_data in schema["paths"].values():
            for operation_data in path_data.values():
                if isinstance(operation_data, dict) and "tags" in operation_data:
                    used_tags.update(operation_data["tags"])

        # Should have feature tags only
        expected_tags = {
            "Health",
            "Authentication",
            "Roles",
            "Permissions",
            "Teams",
            "Organizations",
            "Departments",
        }

        # All used tags should be in expected tags
        unexpected = used_tags - expected_tags
        if unexpected:
            pytest.fail(f"Unexpected tags found: {unexpected}")

        # At least some expected tags should be present
        assert len(used_tags) > 0, "No tags found in OpenAPI schema"
        assert used_tags.issubset(expected_tags), (
            f"Found unexpected tags: {used_tags - expected_tags}"
        )
