"""
Comprehensive tests for the versioning and feature flag system.

Tests cover:
- Version class and lifecycle management
- Feature flag functionality
- Version comparison and compatibility
- Feature dependencies
- Environment-specific toggles
- Helper functions
- Utility functions
"""

from datetime import date
from unittest.mock import Mock

import pytest

from productivity_tracker.versioning import (  # Version constants; Mappings; Classes; Functions
    ALL_VERSIONS,
    CURRENT_VERSION,
    FEATURE_DEPENDENCIES,
    LATEST_VERSION,
    V1_0,
    V1_1,
    V1_2,
    V2_0,
    VERSION_FEATURES,
    DeprecationInfo,
    Feature,
    Version,
    VersionStatus,
    check_feature_dependencies,
    get_all_features_up_to_version,
    get_enabled_features,
    get_migration_path,
    get_supported_versions,
    get_version_from_string,
    get_version_headers,
    get_version_info,
    is_feature_enabled,
)
from productivity_tracker.versioning.utils import (
    add_version_headers,
    get_active_versions,
    get_all_versions,
    get_api_version_from_request,
    get_deprecated_versions,
    get_version_by_prefix,
    is_version_accessible,
)

pytestmark = [pytest.mark.utils]

# ============================================================================
# Version Class Tests
# ============================================================================


class TestVersionClass:
    """Test the Version dataclass."""

    def test_version_initialization(self):
        """Test basic version initialization."""
        v = Version(major=1, minor=0, patch=0)
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0
        assert v.version_string == "1.0.0"
        assert v.api_prefix == "/api/v1.0"

    def test_version_with_prerelease(self):
        """Test version with prerelease tag."""
        v = Version(major=1, minor=0, patch=0, prerelease="beta")
        assert v.version_string == "1.0.0-beta"
        assert str(v) == "1.0.0-beta"

    def test_version_with_build_metadata(self):
        """Test version with build metadata."""
        v = Version(major=1, minor=0, patch=0, build_metadata="20250101")
        assert v.version_string == "1.0.0+20250101"

    def test_version_string_representation(self):
        """Test __str__ and __repr__."""
        v = Version(major=2, minor=3, patch=1, status=VersionStatus.ACTIVE)
        assert str(v) == "2.3.1"
        assert "2.3.1" in repr(v)
        assert "active" in repr(v)

    def test_version_equality(self):
        """Test version equality comparison."""
        v1 = Version(major=1, minor=0, patch=0)
        v2 = Version(major=1, minor=0, patch=0)
        v3 = Version(major=1, minor=0, patch=1)

        assert v1 == v2
        assert v1 != v3

    def test_version_comparison_major(self):
        """Test version comparison on major version."""
        v1 = Version(major=1, minor=0, patch=0)
        v2 = Version(major=2, minor=0, patch=0)

        assert v1 < v2
        assert v2 > v1
        assert v1 <= v2
        assert v2 >= v1

    def test_version_comparison_minor(self):
        """Test version comparison on minor version."""
        v1 = Version(major=1, minor=0, patch=0)
        v2 = Version(major=1, minor=1, patch=0)

        assert v1 < v2
        assert v2 > v1

    def test_version_comparison_patch(self):
        """Test version comparison on patch version."""
        v1 = Version(major=1, minor=0, patch=0)
        v2 = Version(major=1, minor=0, patch=1)

        assert v1 < v2
        assert v2 > v1

    def test_version_comparison_prerelease(self):
        """Test that stable version is greater than prerelease."""
        v1 = Version(major=1, minor=0, patch=0, prerelease="beta")
        v2 = Version(major=1, minor=0, patch=0)

        assert v1 < v2  # prerelease < stable
        assert v2 > v1

    def test_version_hash(self):
        """Test version hashing for use in dicts/sets."""
        v1 = Version(major=1, minor=0, patch=0)
        v2 = Version(major=1, minor=0, patch=0)
        v3 = Version(major=2, minor=0, patch=0)

        assert hash(v1) == hash(v2)
        assert hash(v1) != hash(v3)

        # Test usage in set
        version_set = {v1, v2, v3}
        assert len(version_set) == 2  # v1 and v2 are equal

    def test_version_compatibility(self):
        """Test version compatibility (same major version)."""
        v1_0 = Version(major=1, minor=0, patch=0)
        v1_1 = Version(major=1, minor=1, patch=0)
        v2_0 = Version(major=2, minor=0, patch=0)

        assert v1_0.is_compatible_with(v1_1)
        assert not v1_0.is_compatible_with(v2_0)

    def test_breaking_change_detection(self):
        """Test breaking change detection."""
        v1_0 = Version(major=1, minor=0, patch=0)
        v1_1 = Version(major=1, minor=1, patch=0)
        v2_0 = Version(major=2, minor=0, patch=0)

        assert not v1_1.is_breaking_change_from(v1_0)
        assert v2_0.is_breaking_change_from(v1_0)

    def test_version_lifecycle_states(self):
        """Test version lifecycle status checks."""
        v_planned = Version(major=1, minor=0, patch=0, status=VersionStatus.PLANNED)
        v_active = Version(major=1, minor=0, patch=0, status=VersionStatus.ACTIVE)
        v_deprecated = Version(major=1, minor=0, patch=0, status=VersionStatus.DEPRECATED)
        v_eol = Version(major=1, minor=0, patch=0, status=VersionStatus.EOL)

        # Supported versions
        assert not v_planned.is_supported()
        assert v_active.is_supported()
        assert not v_deprecated.is_supported()
        assert not v_eol.is_supported()

        # Deprecated check
        assert v_deprecated.is_deprecated()
        assert not v_active.is_deprecated()

        # EOL check
        assert v_eol.is_eol()
        assert not v_active.is_eol()

    def test_version_eol_date(self):
        """Test EOL date checking."""
        past_date = date(2024, 1, 1)
        future_date = date(2026, 1, 1)

        v_past = Version(major=1, minor=0, patch=0, eol_date=past_date)
        v_future = Version(major=1, minor=0, patch=0, eol_date=future_date)

        assert v_past.is_eol()  # EOL date has passed
        assert not v_future.is_eol()  # EOL date in future

    def test_version_to_dict(self):
        """Test version serialization to dict."""
        v = Version(
            major=1,
            minor=2,
            patch=3,
            prerelease="beta",
            status=VersionStatus.ACTIVE,
            release_date=date(2025, 1, 1),
            docs_url="/docs",
        )

        data = v.to_dict()

        assert data["version"] == "1.2.3-beta"
        assert data["major"] == 1
        assert data["minor"] == 2
        assert data["patch"] == 3
        assert data["prerelease"] == "beta"
        assert data["status"] == "active"
        assert data["release_date"] == "2025-01-01"
        assert data["api_prefix"] == "/api/v1.2"
        assert data["docs_url"] == "/docs"


# ============================================================================
# Feature Flag Tests
# ============================================================================


class TestFeatureFlags:
    """Test feature flag functionality."""

    def test_feature_enum_values(self):
        """Test that Feature enum has expected values."""
        assert Feature.JWT_AUTHENTICATION.value == "jwt_authentication"
        assert Feature.TASK_MANAGEMENT.value == "task_management"
        assert Feature.RBAC_SYSTEM.value == "rbac_system"

    def test_is_feature_enabled_current_version(self):
        """Test feature checking against current version."""
        # V1.0 features should be enabled
        assert is_feature_enabled(Feature.JWT_AUTHENTICATION)
        assert is_feature_enabled(Feature.ORGANIZATION_MANAGEMENT)

        # Future features should not be enabled
        assert not is_feature_enabled(Feature.TASK_MANAGEMENT)  # V1.2
        assert not is_feature_enabled(Feature.AI_PRODUCTIVITY_PATTERNS)  # V2.1

    def test_is_feature_enabled_specific_version(self):
        """Test feature checking against specific version."""
        # Check features against V1.2
        assert is_feature_enabled(Feature.TASK_MANAGEMENT, version=V1_2)
        assert is_feature_enabled(Feature.JWT_AUTHENTICATION, version=V1_2)  # Inherited

        # V1.3 features not enabled in V1.2
        assert not is_feature_enabled(Feature.ANALYTICS_DASHBOARD, version=V1_2)

    def test_is_feature_enabled_environment(self):
        """Test environment-specific feature toggles."""
        # In development, all features should be enabled
        assert is_feature_enabled(Feature.TASK_MANAGEMENT, environment="development")
        assert is_feature_enabled(Feature.AI_PRODUCTIVITY_PATTERNS, environment="development")

        # In production, only current version features
        assert not is_feature_enabled(Feature.TASK_MANAGEMENT, environment="production")

    def test_get_all_features_up_to_version(self):
        """Test cumulative feature retrieval."""
        v1_0_features = get_all_features_up_to_version(V1_0)
        v1_2_features = get_all_features_up_to_version(V1_2)

        # V1.2 should include V1.0, V1.1, and V1.2 features
        assert len(v1_2_features) > len(v1_0_features)

        # V1.0 features should be in V1.2
        assert Feature.JWT_AUTHENTICATION in v1_2_features

        # V1.2 specific features
        assert Feature.TASK_MANAGEMENT in v1_2_features

    def test_get_enabled_features(self):
        """Test getting all enabled features."""
        features = get_enabled_features()

        # Current version features should be enabled
        assert Feature.JWT_AUTHENTICATION in features
        assert Feature.ORGANIZATION_MANAGEMENT in features

        # Future features should not be
        assert Feature.TASK_MANAGEMENT not in features

    def test_feature_dependencies(self):
        """Test feature dependency system."""
        # Smart task suggestions requires task management + AI
        deps = FEATURE_DEPENDENCIES.get(Feature.SMART_TASK_SUGGESTIONS, set())

        assert Feature.TASK_MANAGEMENT in deps
        assert Feature.AI_PRODUCTIVITY_PATTERNS in deps

    def test_check_feature_dependencies_satisfied(self):
        """Test dependency checking when satisfied."""
        # JWT_AUTHENTICATION has no dependencies
        assert check_feature_dependencies(Feature.JWT_AUTHENTICATION)

    def test_check_feature_dependencies_not_satisfied(self):
        """Test dependency checking when not satisfied."""
        # SMART_TASK_SUGGESTIONS requires features not in V1.0
        assert not check_feature_dependencies(Feature.SMART_TASK_SUGGESTIONS, version=V1_0)


# ============================================================================
# Version Helper Function Tests
# ============================================================================


class TestVersionHelpers:
    """Test version helper functions."""

    def test_get_supported_versions(self):
        """Test getting supported versions."""
        supported = get_supported_versions()

        # V1.0 is ACTIVE (supported)
        assert V1_0 in supported
        assert V1_1 in supported

        # Planned versions are not supported
        assert V1_2 not in supported
        assert V2_0 not in supported

    def test_get_version_from_string_valid(self):
        """Test parsing valid version strings."""
        v = get_version_from_string("1.0")
        assert v == V1_0

        v = get_version_from_string("1.1")
        assert v == V1_1

        v = get_version_from_string("v2.0")  # with 'v' prefix
        assert v == V2_0

    def test_get_version_from_string_invalid(self):
        """Test parsing invalid version strings."""
        assert get_version_from_string("99.99") is None
        assert get_version_from_string("invalid") is None
        assert get_version_from_string("") is None

    def test_get_version_headers(self):
        """Test version header generation."""
        headers = get_version_headers(V1_0)

        assert "API-Version" in headers
        assert headers["API-Version"] == V1_0.version_string
        assert "API-Status" in headers
        assert headers["API-Status"] == V1_0.status.value
        assert "API-Deprecated" in headers
        assert headers["API-Deprecated"] == "false"

    def test_get_version_headers_deprecated(self):
        """Test headers for deprecated version."""
        v_deprecated = Version(
            major=0,
            minor=9,
            patch=0,
            status=VersionStatus.DEPRECATED,
            eol_date=date(2025, 12, 31),
        )

        headers = get_version_headers(v_deprecated)

        assert headers["API-Deprecated"] == "true"
        assert "Sunset" in headers  # RFC 8594 sunset header

    def test_get_version_info(self):
        """Test getting detailed version information."""
        info = get_version_info(V1_0)

        assert "version" in info
        assert "features" in info
        assert "compatibility" in info

        assert info["features"]["total"] > 0
        assert info["compatibility"]["supported"]
        assert not info["compatibility"]["deprecated"]

    def test_get_migration_path(self):
        """Test migration path calculation."""
        migration = get_migration_path(V1_0, V1_2)

        assert migration["from_version"] == str(V1_0)
        assert migration["to_version"] == str(V1_2)
        assert not migration["breaking_change"]  # Same major version
        assert migration["new_features_count"] > 0
        assert V1_1.version_string in migration["intermediate_versions"]

    def test_get_migration_path_breaking_change(self):
        """Test migration with breaking changes."""
        migration = get_migration_path(V1_0, V2_0)

        assert migration["breaking_change"]  # Major version change
        assert not migration["rollback_supported"]


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions from utils.py."""

    def test_get_all_versions(self):
        """Test getting all supported versions."""
        versions = get_all_versions()

        # Should include supported versions (ACTIVE, BETA, RC, MAINTENANCE)
        assert len(versions) >= 1
        assert V1_0 in versions  # ACTIVE

    def test_get_active_versions(self):
        """Test getting only active versions."""
        active = get_active_versions()

        assert V1_0 in active  # status=ACTIVE
        assert all(v.status == VersionStatus.ACTIVE for v in active)

    def test_get_deprecated_versions(self):
        """Test getting deprecated versions."""
        deprecated = get_deprecated_versions()

        # Currently no deprecated versions
        assert isinstance(deprecated, list)

    def test_get_version_by_prefix(self):
        """Test getting version by API prefix."""
        v = get_version_by_prefix("/api/v1.0")
        assert v == V1_0

        v = get_version_by_prefix("/api/v1.2")
        assert v == V1_2

        v = get_version_by_prefix("/api/v99.99")
        assert v is None

    def test_is_version_accessible(self):
        """Test version accessibility check."""
        # Active versions are accessible
        assert is_version_accessible(V1_1)

        # Planned versions are not accessible
        assert not is_version_accessible(V1_2)

    def test_add_version_headers_to_response(self):
        """Test adding version headers to response."""
        from fastapi import Response

        response = Response()
        response = add_version_headers(response, V1_0)

        assert "API-Version" in response.headers
        assert response.headers["API-Version"] == str(V1_0)
        assert "X-API-Version" in response.headers  # Legacy header

    def test_get_api_version_from_request(self):
        """Test extracting version from request path."""
        from fastapi import Request

        # Mock request with version in path
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/v1.0/health"

        version = get_api_version_from_request(mock_request)
        assert version == V1_0

    def test_get_api_version_from_request_no_version(self):
        """Test extracting version when no version in path."""
        from fastapi import Request

        mock_request = Mock(spec=Request)
        mock_request.url.path = "/admin/users"

        version = get_api_version_from_request(mock_request)
        assert version == CURRENT_VERSION  # Falls back to current


# ============================================================================
# Integration Tests
# ============================================================================


class TestVersioningIntegration:
    """Integration tests for versioning system."""

    def test_current_version_is_defined(self):
        """Test that CURRENT_VERSION is properly defined."""
        assert CURRENT_VERSION is not None
        assert isinstance(CURRENT_VERSION, Version)
        assert CURRENT_VERSION == V1_1

    def test_latest_version_is_defined(self):
        """Test that LATEST_VERSION is properly defined."""
        assert LATEST_VERSION is not None
        assert isinstance(LATEST_VERSION, Version)

    def test_all_versions_defined(self):
        """Test that all versions are in ALL_VERSIONS."""
        assert len(ALL_VERSIONS) == 11  # V1.0 through V2.3
        assert V1_0 in ALL_VERSIONS
        assert V1_1 in ALL_VERSIONS
        assert V2_0 in ALL_VERSIONS

    def test_version_features_mapping_complete(self):
        """Test that all versions have feature mappings."""
        for version in ALL_VERSIONS:
            assert version in VERSION_FEATURES
            features = VERSION_FEATURES[version]
            assert isinstance(features, set)

    def test_v1_0_features_correct(self):
        """Test that V1.0 has correct features."""
        v1_0_features = VERSION_FEATURES[V1_0]

        expected_features = {
            Feature.ORGANIZATION_MANAGEMENT,
            Feature.DEPARTMENT_MANAGEMENT,
            Feature.TEAM_MANAGEMENT,
            Feature.USER_MANAGEMENT,
            Feature.RBAC_SYSTEM,
            Feature.PERMISSION_SYSTEM,
            Feature.JWT_AUTHENTICATION,
            Feature.HEALTH_CHECKS,
            Feature.API_DOCUMENTATION,
            Feature.ERROR_HANDLING,
            Feature.DATABASE_MIGRATIONS,
        }

        assert v1_0_features == expected_features

    def test_feature_dependencies_are_valid(self):
        """Test that all feature dependencies reference valid features."""
        for feature, deps in FEATURE_DEPENDENCIES.items():
            assert isinstance(feature, Feature)
            for dep in deps:
                assert isinstance(dep, Feature)

    def test_version_sorting(self):
        """Test that versions can be sorted correctly."""
        versions = [V2_0, V1_0, V1_2, V1_1]
        sorted_versions = sorted(versions)

        assert sorted_versions == [V1_0, V1_1, V1_2, V2_0]

    def test_version_prefix_format(self):
        """Test that all versions have correct API prefix format."""
        for version in ALL_VERSIONS:
            assert version.api_prefix.startswith("/api/v")
            assert f"{version.major}.{version.minor}" in version.api_prefix


# ============================================================================
# Deprecation Tests
# ============================================================================


class TestDeprecation:
    """Test deprecation functionality."""

    def test_deprecation_info_structure(self):
        """Test DeprecationInfo dataclass."""
        info = DeprecationInfo(
            sunset_date=date(2026, 12, 31),
            replacement="JWT_AUTHENTICATION",
            migration_guide="/docs/migration",
            reason="Enhanced security",
        )

        assert info.sunset_date == date(2026, 12, 31)
        assert info.replacement == "JWT_AUTHENTICATION"
        assert info.migration_guide == "/docs/migration"
        assert info.reason == "Enhanced security"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_version_comparison_with_none(self):
        """Test that version comparison handles None gracefully."""
        v = Version(major=1, minor=0, patch=0)

        # Should return NotImplemented for invalid comparisons
        assert v.__eq__(None) == NotImplemented

    def test_empty_feature_set(self):
        """Test handling of versions with no features."""
        # This shouldn't happen in practice, but test the system handles it
        features = get_all_features_up_to_version(V1_0)
        assert len(features) > 0  # V1.0 has features

    def test_get_enabled_features_no_version(self):
        """Test get_enabled_features with no version defaults to CURRENT."""
        features_default = get_enabled_features()
        features_current = get_enabled_features(version=CURRENT_VERSION)

        assert features_default == features_current


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
