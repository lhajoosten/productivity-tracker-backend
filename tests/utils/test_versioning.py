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
