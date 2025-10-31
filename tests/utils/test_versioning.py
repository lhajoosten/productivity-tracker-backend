from unittest.mock import patch

import pytest

from productivity_tracker.versioning.versioning import (
    CURRENT_VERSION,
    V1_0,
    V1_1,
    V1_2,
    V2_0,
    V2_1,
    V2_2,
    V3_0,
    V3_1,
    V3_2,
    V3_3,
    VERSION_FEATURES,
    APIVersion,
    is_feature_enabled,
)

pytestmark = [pytest.mark.utils]


# Mock versions for testing the versioning system mechanics
MOCK_V1_0 = APIVersion(1, 0)
MOCK_V1_1 = APIVersion(1, 1)
MOCK_V2_0 = APIVersion(2, 0)
MOCK_V2_1 = APIVersion(2, 1)
MOCK_V3_0 = APIVersion(3, 0)
MOCK_V3_1 = APIVersion(3, 1)

# Mock feature configurations to test inheritance
MOCK_BASE_FEATURES = {
    "auth": False,
    "users": False,
    "advanced_feature": False,
    "ai_feature": False,
}

MOCK_VERSION_CHANGES = {
    MOCK_V1_0: {
        "auth": True,
        "users": True,
    },
    MOCK_V1_1: {},  # No new features - should inherit from V1.0
    MOCK_V2_0: {
        "advanced_feature": True,
    },
    MOCK_V2_1: {},  # No new features - should inherit from V2.0
    MOCK_V3_0: {
        "ai_feature": True,
    },
    MOCK_V3_1: {},  # No new features - should inherit from V3.0
}


def build_mock_features():
    """Build mock feature dictionary with inheritance."""
    result = {}
    versions = sorted(MOCK_VERSION_CHANGES.keys(), key=lambda v: (v.major, v.minor))

    for version in versions:
        features = MOCK_BASE_FEATURES.copy()

        for prev in versions:
            if prev.major < version.major or (
                prev.major == version.major and prev.minor < version.minor
            ):
                features.update(MOCK_VERSION_CHANGES[prev])

        features.update(MOCK_VERSION_CHANGES[version])
        result[version] = features

    return result


MOCK_VERSION_FEATURES = build_mock_features()


class TestVersionDefinitions:
    """Test that the current production version is properly defined."""

    def test_current_version_is_v1_0(self):
        """Current version should be V1.0."""
        assert CURRENT_VERSION == V1_0
        assert CURRENT_VERSION.major == 1
        assert CURRENT_VERSION.minor == 0

    def test_all_versions_have_features(self):
        """All defined versions should have feature mappings."""
        versions = [V1_0, V1_1, V1_2, V2_0, V2_1, V2_2, V3_0, V3_1, V3_2, V3_3]
        for version in versions:
            assert version in VERSION_FEATURES
            assert isinstance(VERSION_FEATURES[version], dict)

    def test_current_version_is_valid(self):
        """Current version should be in VERSION_FEATURES."""
        assert CURRENT_VERSION in VERSION_FEATURES


class TestV1ProductionFeatures:
    """Test V1.0 production features (currently implemented)."""

    def test_v1_0_has_core_features(self):
        """V1.0 should have all core features enabled."""
        features = VERSION_FEATURES[V1_0]

        # Core features enabled in production
        assert features["auth"] is True
        assert features["rbac"] is True
        assert features["users"] is True
        assert features["roles"] is True
        assert features["permissions"] is True
        assert features["health"] is True
        assert features["organizations"] is True
        assert features["departments"] is True
        assert features["teams"] is True

    def test_v1_0_future_features_disabled(self):
        """V1.0 should have all future features disabled."""
        features = VERSION_FEATURES[V1_0]

        # V1.1+ features not yet implemented
        assert features.get("audit_logging", False) is False
        assert features.get("bulk_operations", False) is False
        assert features.get("data_export", False) is False
        assert features.get("search", False) is False

        # V2.0+ features not yet implemented
        assert features.get("workspaces", False) is False
        assert features.get("projects", False) is False
        assert features.get("tasks", False) is False
        assert features.get("time_tracking", False) is False

        # V3.0+ features not yet implemented
        assert features.get("ai_integration", False) is False
        assert features.get("smart_insights", False) is False


class TestVersioningSystemMechanics:
    """Test the versioning system mechanics using mock data."""

    def test_feature_inheritance_mock(self):
        """Patch versions should inherit features from base version."""
        # V1.1 should have V1.0 features
        assert MOCK_VERSION_FEATURES[MOCK_V1_1]["auth"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V1_1]["users"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V1_1]["advanced_feature"] is False

        # V2.1 should have V1.0 + V2.0 features
        assert MOCK_VERSION_FEATURES[MOCK_V2_1]["auth"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V2_1]["users"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V2_1]["advanced_feature"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V2_1]["ai_feature"] is False

        # V3.1 should have all previous features
        assert MOCK_VERSION_FEATURES[MOCK_V3_1]["auth"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V3_1]["users"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V3_1]["advanced_feature"] is True
        assert MOCK_VERSION_FEATURES[MOCK_V3_1]["ai_feature"] is True

    def test_patch_versions_identical_to_base_mock(self):
        """Patch versions without changes should match their base version."""
        # V1.1 should equal V1.0 (no new features)
        assert MOCK_VERSION_FEATURES[MOCK_V1_0] == MOCK_VERSION_FEATURES[MOCK_V1_1]

        # V2.1 should equal V2.0 (no new features)
        assert MOCK_VERSION_FEATURES[MOCK_V2_0] == MOCK_VERSION_FEATURES[MOCK_V2_1]

        # V3.1 should equal V3.0 (no new features)
        assert MOCK_VERSION_FEATURES[MOCK_V3_0] == MOCK_VERSION_FEATURES[MOCK_V3_1]

    def test_major_versions_add_features_mock(self):
        """Major versions should add new features."""
        # V2.0 should have everything from V1.0 plus new features
        v1_features = MOCK_VERSION_FEATURES[MOCK_V1_0]
        v2_features = MOCK_VERSION_FEATURES[MOCK_V2_0]

        assert v2_features["auth"] == v1_features["auth"]
        assert v2_features["users"] == v1_features["users"]
        assert v2_features["advanced_feature"] is True  # New in V2

        # V3.0 should have everything from V2.0 plus new features
        v3_features = MOCK_VERSION_FEATURES[MOCK_V3_0]

        assert v3_features["auth"] == v2_features["auth"]
        assert v3_features["advanced_feature"] == v2_features["advanced_feature"]
        assert v3_features["ai_feature"] is True  # New in V3


class TestFeatureInheritance:
    """Test that patch versions inherit features correctly in production."""

    def test_v1_patches_have_same_core_features(self):
        """V1.1 and V1.2 should have same core features enabled as V1.0."""
        # Core features should be enabled in all V1.x versions
        core_features = [
            "auth",
            "rbac",
            "users",
            "roles",
            "permissions",
            "health",
            "organizations",
            "departments",
            "teams",
        ]

        for feature in core_features:
            assert VERSION_FEATURES[V1_0][feature] is True
            assert VERSION_FEATURES[V1_1][feature] is True
            assert VERSION_FEATURES[V1_2][feature] is True

    def test_v1_patches_no_new_enabled_features(self):
        """V1.1 and V1.2 should not have any new features enabled beyond V1.0."""
        # Count enabled features in each version
        v1_0_enabled = sum(1 for v in VERSION_FEATURES[V1_0].values() if v is True)
        v1_1_enabled = sum(1 for v in VERSION_FEATURES[V1_1].values() if v is True)
        v1_2_enabled = sum(1 for v in VERSION_FEATURES[V1_2].values() if v is True)

        # All V1.x should have same number of enabled features
        assert v1_0_enabled == v1_1_enabled
        assert v1_1_enabled == v1_2_enabled

    def test_future_versions_defined(self):
        """Future versions should be defined but not necessarily implemented."""
        # Just verify they exist in VERSION_FEATURES
        assert V2_0 in VERSION_FEATURES
        assert V2_1 in VERSION_FEATURES
        assert V2_2 in VERSION_FEATURES
        assert V3_0 in VERSION_FEATURES
        assert V3_1 in VERSION_FEATURES
        assert V3_2 in VERSION_FEATURES
        assert V3_3 in VERSION_FEATURES


class TestIsFeatureEnabled:
    """Test the is_feature_enabled helper function."""

    def test_enabled_feature_returns_true(self):
        """Should return True for enabled features in V1.0."""
        assert is_feature_enabled(V1_0, "auth") is True
        assert is_feature_enabled(V1_0, "rbac") is True
        assert is_feature_enabled(V1_0, "users") is True
        assert is_feature_enabled(V1_0, "organizations") is True

    def test_disabled_feature_returns_false(self):
        """Should return False for disabled/future features in V1.0."""
        assert is_feature_enabled(V1_0, "audit_logging") is False
        assert is_feature_enabled(V1_0, "time_tracking") is False
        assert is_feature_enabled(V1_0, "ai_integration") is False

    def test_nonexistent_feature_returns_false(self):
        """Should return False for non-existent features."""
        assert is_feature_enabled(V1_0, "nonexistent") is False
        assert is_feature_enabled(V1_0, "invalid_feature") is False

    @patch("productivity_tracker.versioning.versioning.VERSION_FEATURES", MOCK_VERSION_FEATURES)
    def test_feature_enabled_with_mocks(self):
        """Test feature enabling works correctly with mock data."""
        assert is_feature_enabled(MOCK_V1_0, "auth") is True
        assert is_feature_enabled(MOCK_V2_0, "advanced_feature") is True
        assert is_feature_enabled(MOCK_V3_0, "ai_feature") is True
        assert is_feature_enabled(MOCK_V1_0, "advanced_feature") is False


class TestAPIVersionDataclass:
    """Test the APIVersion dataclass."""

    def test_version_prefix(self):
        """Should generate correct API prefix."""
        v = APIVersion(1, 0)
        assert v.prefix == "/api/v1.0"

    def test_version_major_prefix(self):
        """Should generate correct major version prefix."""
        v = APIVersion(2, 5)
        assert v.major_prefix == "/api/v2"

    def test_version_string_representation(self):
        """Should have correct string representation."""
        v = APIVersion(3, 2)
        assert str(v) == "v3.2"
        assert repr(v) == "APIVersion(3.2)"

    def test_version_hashable(self):
        """Versions should be hashable for use in sets/dicts."""
        v1 = APIVersion(1, 0)
        v2 = APIVersion(1, 0)
        v3 = APIVersion(2, 0)

        assert hash(v1) == hash(v2)
        assert hash(v1) != hash(v3)

        # Can be used in sets
        versions = {v1, v2, v3}
        assert len(versions) == 2  # v1 and v2 are identical


class TestVersioningUtils:
    """Test versioning utility functions."""

    def test_get_all_versions(self):
        """Should return all registered versions."""
        from productivity_tracker.versioning.utils import get_all_registered_versions

        versions = get_all_registered_versions()
        assert isinstance(versions, list)
        assert len(versions) == 10  # V1.0-V3.3
        assert all(v.prefix.startswith("/api/v") for v in versions)

    def test_get_version_by_prefix(self):
        """Should find version by its prefix."""
        from productivity_tracker.versioning.utils import get_version_by_prefix

        v1 = get_version_by_prefix("/api/v1.0")
        assert v1 == V1_0

        v2 = get_version_by_prefix("/api/v2.1")
        assert v2 == V2_1

        v3 = get_version_by_prefix("/api/v3.2")
        assert v3 == V3_2

    def test_get_version_by_invalid_prefix(self):
        """Should return None for invalid prefix."""
        from productivity_tracker.versioning.utils import get_version_by_prefix

        result = get_version_by_prefix("/api/v99.0")
        assert result is None

    def test_iter_versions(self):
        """Should iterate over all versions."""
        from productivity_tracker.versioning.utils import iter_versions

        versions = list(iter_versions())
        assert len(versions) == 10
        assert V1_0 in versions
        assert V3_3 in versions

    def test_add_version_headers(self):
        """Should add version headers to response."""
        from fastapi import Response

        from productivity_tracker.versioning.utils import add_version_headers

        response = Response()
        result = add_version_headers(response, V2_0)

        assert "X-API-Version" in result.headers
        assert result.headers["X-API-Version"] == "v2.0"

    def test_add_version_headers_deprecated(self):
        """Should add deprecation warning for deprecated versions."""
        from fastapi import Response

        from productivity_tracker.versioning.utils import add_version_headers
        from productivity_tracker.versioning.versioning import DEPRECATED_VERSIONS

        # Use first deprecated version
        if DEPRECATED_VERSIONS:
            deprecated_version = list(DEPRECATED_VERSIONS)[0]
            response = Response()
            result = add_version_headers(response, deprecated_version)

            assert "Warning" in result.headers
            assert "deprecated" in result.headers["Warning"].lower()

    def test_get_api_version_from_request(self):
        """Should extract version from request path."""
        from fastapi import Request

        from productivity_tracker.versioning.utils import get_api_version_from_request

        # Create mock request
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v1.0/auth/login",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)

        version = get_api_version_from_request(request)
        assert version == V1_0

    def test_get_api_version_from_request_defaults_to_current(self):
        """Should default to current version if no match."""
        from fastapi import Request

        from productivity_tracker.versioning.utils import get_api_version_from_request

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/unknown/path",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)

        version = get_api_version_from_request(request)
        assert version == CURRENT_VERSION

    def test_is_version_accessible(self):
        from productivity_tracker.versioning.utils import is_version_accessible
        from productivity_tracker.versioning.versioning import (
            ACTIVE_VERSIONS,
            DEPRECATED_VERSIONS,
        )

        for version in ACTIVE_VERSIONS:
            assert is_version_accessible(version) is True
        for version in DEPRECATED_VERSIONS:
            assert is_version_accessible(version) is True

    def test_is_version_deprecated(self):
        from productivity_tracker.versioning.versioning import (
            DEPRECATED_VERSIONS,
            is_version_deprecated,
        )

        for version in DEPRECATED_VERSIONS:
            assert is_version_deprecated(version) is True
