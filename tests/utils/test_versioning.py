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
    is_feature_enabled,
)

pytestmark = [pytest.mark.utils]


class TestVersionDefinitions:
    """Test that all versions are properly defined."""

    def test_all_versions_have_features(self):
        """All defined versions should have feature mappings."""
        versions = [V1_0, V1_1, V1_2, V2_0, V2_1, V2_2, V3_0, V3_1, V3_2, V3_3]
        for version in versions:
            assert version in VERSION_FEATURES
            assert isinstance(VERSION_FEATURES[version], dict)

    def test_current_version_is_valid(self):
        """Current version should be in VERSION_FEATURES."""
        assert CURRENT_VERSION in VERSION_FEATURES


class TestV1Features:
    """Test V1.x feature flags."""

    @pytest.mark.parametrize("version", [V1_0, V1_1, V1_2])
    def test_v1_base_features(self, version):
        """V1.x should have core features only."""
        features = VERSION_FEATURES[version]

        # Core features enabled
        assert features["auth"] is True
        assert features["rbac"] is True
        assert features["users"] is True
        assert features["roles"] is True
        assert features["permissions"] is True
        assert features["health"] is True
        assert features["organizations"] is True
        assert features["departments"] is True
        assert features["teams"] is True

        # Advanced features disabled
        assert features["time_tracking"] is False
        assert features["tasks"] is False
        assert features["projects"] is False
        assert features["analytics"] is False

        # AI features disabled
        assert features["ai_integration"] is False
        assert features["llm_features"] is False
        assert features["mcp_support"] is False


class TestV2Features:
    """Test V2.x feature flags."""

    @pytest.mark.parametrize("version", [V2_0, V2_1, V2_2])
    def test_v2_features(self, version):
        """V2.x should have core + advanced features."""
        features = VERSION_FEATURES[version]

        # Core features still enabled
        assert features["auth"] is True
        assert features["users"] is True

        # Advanced features enabled
        assert features["time_tracking"] is True
        assert features["tasks"] is True
        assert features["projects"] is True
        assert features["analytics"] is True

        # AI features still disabled
        assert features["ai_integration"] is False
        assert features["llm_features"] is False
        assert features["mcp_support"] is False


class TestV3Features:
    """Test V3.x feature flags."""

    @pytest.mark.parametrize("version", [V3_0, V3_1, V3_2, V3_3])
    def test_v3_features(self, version):
        """V3.x should have all features enabled."""
        features = VERSION_FEATURES[version]

        # Core features still enabled
        assert features["auth"] is True
        assert features["users"] is True

        # Advanced features still enabled
        assert features["time_tracking"] is True
        assert features["projects"] is True

        # AI features enabled
        assert features["ai_integration"] is True
        assert features["llm_features"] is True
        assert features["mcp_support"] is True


class TestFeatureInheritance:
    """Test that patch versions inherit features correctly."""

    def test_v1_patches_are_identical(self):
        """V1.1 and V1.2 should have same features as V1.0."""
        assert VERSION_FEATURES[V1_0] == VERSION_FEATURES[V1_1]
        assert VERSION_FEATURES[V1_1] == VERSION_FEATURES[V1_2]

    def test_v2_patches_are_identical(self):
        """V2.1 and V2.2 should have same features as V2.0."""
        assert VERSION_FEATURES[V2_0] == VERSION_FEATURES[V2_1]
        assert VERSION_FEATURES[V2_1] == VERSION_FEATURES[V2_2]

    def test_v3_patches_are_identical(self):
        """V3.1, V3.2, V3.3 should have same features as V3.0."""
        assert VERSION_FEATURES[V3_0] == VERSION_FEATURES[V3_1]
        assert VERSION_FEATURES[V3_1] == VERSION_FEATURES[V3_2]
        assert VERSION_FEATURES[V3_2] == VERSION_FEATURES[V3_3]


class TestIsFeatureEnabled:
    """Test the is_feature_enabled helper function."""

    def test_enabled_feature_returns_true(self):
        """Should return True for enabled features."""
        assert is_feature_enabled(V1_0, "auth") is True
        assert is_feature_enabled(V2_0, "time_tracking") is True
        assert is_feature_enabled(V3_0, "ai_integration") is True

    def test_disabled_feature_returns_false(self):
        """Should return False for disabled features."""
        assert is_feature_enabled(V1_0, "time_tracking") is False
        assert is_feature_enabled(V1_0, "ai_integration") is False
        assert is_feature_enabled(V2_0, "llm_features") is False

    def test_nonexistent_feature_returns_false(self):
        """Should return False for non-existent features."""
        assert is_feature_enabled(V1_0, "nonexistent") is False
        assert is_feature_enabled(V3_0, "invalid_feature") is False


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
