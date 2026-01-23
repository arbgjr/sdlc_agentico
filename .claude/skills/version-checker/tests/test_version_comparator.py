#!/usr/bin/env python3
"""
Unit tests for version_comparator module.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from version_comparator import (
    parse_version,
    compare_versions,
    get_upgrade_type
)


class TestParseVersion:
    """Tests for parse_version function."""

    def test_parse_simple_version(self):
        """Test parsing simple semantic version."""
        assert parse_version("2.1.0") == (2, 1, 0)
        assert parse_version("1.0.0") == (1, 0, 0)
        assert parse_version("10.20.30") == (10, 20, 30)

    def test_parse_version_with_v_prefix(self):
        """Test parsing version with 'v' prefix."""
        assert parse_version("v2.1.0") == (2, 1, 0)
        assert parse_version("v1.0.0") == (1, 0, 0)

    def test_parse_version_with_prerelease(self):
        """Test parsing version with pre-release tag."""
        assert parse_version("2.1.0-alpha") == (2, 1, 0)
        assert parse_version("2.1.0-beta.1") == (2, 1, 0)

    def test_parse_version_with_build_metadata(self):
        """Test parsing version with build metadata."""
        assert parse_version("2.1.0+20230101") == (2, 1, 0)

    def test_parse_invalid_version(self):
        """Test that invalid versions raise ValueError."""
        with pytest.raises(ValueError):
            parse_version("invalid")

        with pytest.raises(ValueError):
            parse_version("2.1")

        with pytest.raises(ValueError):
            parse_version("2.1.a")


class TestCompareVersions:
    """Tests for compare_versions function."""

    def test_compare_newer_patch(self):
        """Test detection of newer patch version."""
        result = compare_versions("2.0.0", "2.0.1")
        assert result["is_newer"] is True
        assert result["diff"]["major"] == 0
        assert result["diff"]["minor"] == 0
        assert result["diff"]["patch"] == 1

    def test_compare_newer_minor(self):
        """Test detection of newer minor version."""
        result = compare_versions("2.0.0", "2.1.0")
        assert result["is_newer"] is True
        assert result["diff"]["major"] == 0
        assert result["diff"]["minor"] == 1
        assert result["diff"]["patch"] == 0

    def test_compare_newer_major(self):
        """Test detection of newer major version."""
        result = compare_versions("2.0.0", "3.0.0")
        assert result["is_newer"] is True
        assert result["diff"]["major"] == 1
        assert result["diff"]["minor"] == 0
        assert result["diff"]["patch"] == 0

    def test_compare_same_version(self):
        """Test comparison of identical versions."""
        result = compare_versions("2.0.0", "2.0.0")
        assert result["is_newer"] is False
        assert result["diff"]["major"] == 0
        assert result["diff"]["minor"] == 0
        assert result["diff"]["patch"] == 0

    def test_compare_older_version(self):
        """Test comparison with older version (downgrade)."""
        result = compare_versions("2.1.0", "2.0.0")
        assert result["is_newer"] is False
        assert result["diff"]["major"] == 0
        assert result["diff"]["minor"] == -1
        assert result["diff"]["patch"] == 0

    def test_compare_with_v_prefix(self):
        """Test comparison with 'v' prefix."""
        result = compare_versions("v2.0.0", "v2.1.0")
        assert result["is_newer"] is True

    def test_compare_multiple_version_jumps(self):
        """Test comparison with multiple version component changes."""
        result = compare_versions("1.2.3", "2.3.4")
        assert result["is_newer"] is True
        assert result["diff"]["major"] == 1
        assert result["diff"]["minor"] == 1
        assert result["diff"]["patch"] == 1


class TestGetUpgradeType:
    """Tests for get_upgrade_type function."""

    def test_major_upgrade(self):
        """Test major upgrade detection."""
        diff = {"major": 1, "minor": 0, "patch": 0}
        assert get_upgrade_type(diff) == "major"

        diff = {"major": 2, "minor": 5, "patch": 3}
        assert get_upgrade_type(diff) == "major"

    def test_minor_upgrade(self):
        """Test minor upgrade detection."""
        diff = {"major": 0, "minor": 1, "patch": 0}
        assert get_upgrade_type(diff) == "minor"

        diff = {"major": 0, "minor": 2, "patch": 5}
        assert get_upgrade_type(diff) == "minor"

    def test_patch_upgrade(self):
        """Test patch upgrade detection."""
        diff = {"major": 0, "minor": 0, "patch": 1}
        assert get_upgrade_type(diff) == "patch"

        diff = {"major": 0, "minor": 0, "patch": 10}
        assert get_upgrade_type(diff) == "patch"

    def test_no_upgrade(self):
        """Test same version (no upgrade)."""
        diff = {"major": 0, "minor": 0, "patch": 0}
        assert get_upgrade_type(diff) == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
