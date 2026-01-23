#!/usr/bin/env python3
"""
Unit tests for impact_analyzer module.
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from impact_analyzer import (
    analyze_impact,
    get_severity_from_diff,
    detect_breaking_changes,
    detect_migrations,
    detect_dependency_updates,
    detect_security_fixes,
    format_impact_summary
)


class TestGetSeverityFromDiff:
    """Tests for get_severity_from_diff function."""

    def test_major_severity(self):
        """Test major version change."""
        assert get_severity_from_diff({"major": 1, "minor": 0, "patch": 0}) == "major"
        assert get_severity_from_diff({"major": 2, "minor": 5, "patch": 3}) == "major"

    def test_minor_severity(self):
        """Test minor version change."""
        assert get_severity_from_diff({"major": 0, "minor": 1, "patch": 0}) == "minor"
        assert get_severity_from_diff({"major": 0, "minor": 3, "patch": 2}) == "minor"

    def test_patch_severity(self):
        """Test patch version change."""
        assert get_severity_from_diff({"major": 0, "minor": 0, "patch": 1}) == "patch"
        assert get_severity_from_diff({"major": 0, "minor": 0, "patch": 5}) == "patch"

    def test_none_severity(self):
        """Test no version change."""
        assert get_severity_from_diff({"major": 0, "minor": 0, "patch": 0}) == "none"


class TestDetectBreakingChanges:
    """Tests for detect_breaking_changes function."""

    def test_breaking_colon_marker(self):
        """Test detection of 'BREAKING:' marker."""
        changelog = """
        # v2.1.0

        BREAKING: Removed deprecated API endpoint
        - feat: Added new feature
        """
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 1
        assert "Removed deprecated API endpoint" in changes[0]

    def test_breaking_change_marker(self):
        """Test detection of 'BREAKING CHANGE:' marker."""
        changelog = """
        BREAKING CHANGE: Changed authentication method
        """
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 1
        assert "Changed authentication method" in changes[0]

    def test_breaking_bracket_marker(self):
        """Test detection of '[BREAKING]' marker."""
        changelog = """
        [BREAKING] Database schema updated
        """
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 1
        assert "Database schema updated" in changes[0]

    def test_multiple_breaking_changes(self):
        """Test detection of multiple breaking changes."""
        changelog = """
        BREAKING: API v1 removed
        BREAKING CHANGE: Config format changed
        [BREAKING] New Python version required
        """
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 3

    def test_no_breaking_changes(self):
        """Test changelog with no breaking changes."""
        changelog = """
        # v2.1.0

        - feat: Added new feature
        - fix: Fixed bug
        """
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 0

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        changelog = "breaking: lowercase marker"
        changes = detect_breaking_changes(changelog)
        assert len(changes) == 1


class TestDetectMigrations:
    """Tests for detect_migrations function."""

    def test_migration_marker(self):
        """Test detection of 'Migration:' marker."""
        changelog = """
        Migration: Run .scripts/migrate-v2-to-v3.sh
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 1
        assert "migrate-v2-to-v3.sh" in migrations[0]

    def test_run_marker(self):
        """Test detection of 'Run:' marker."""
        changelog = """
        Run: python manage.py migrate
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 1
        assert "python manage.py migrate" in migrations[0]

    def test_required_marker(self):
        """Test detection of 'Required:' marker."""
        changelog = """
        Required: Update configuration files
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 1

    def test_action_required_marker(self):
        """Test detection of 'Action required:' marker."""
        changelog = """
        Action required: Regenerate API keys
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 1

    def test_migration_bracket_marker(self):
        """Test detection of '[MIGRATION]' marker."""
        changelog = """
        [MIGRATION] Update database schema
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 1

    def test_multiple_migrations(self):
        """Test detection of multiple migrations."""
        changelog = """
        Migration: Run script A
        Run: Execute command B
        Required: Manual step C
        """
        migrations = detect_migrations(changelog)
        assert len(migrations) == 3

    def test_no_migrations(self):
        """Test changelog with no migrations."""
        changelog = "feat: Added new feature"
        migrations = detect_migrations(changelog)
        assert len(migrations) == 0


class TestDetectDependencyUpdates:
    """Tests for detect_dependency_updates function."""

    def test_arrow_separator(self):
        """Test detection with arrow separator."""
        changelog = """
        Python: 3.9 → 3.11
        """
        deps = detect_dependency_updates(changelog)
        assert "Python" in deps
        assert deps["Python"]["old"] == "3.9"
        assert deps["Python"]["new"] == "3.11"

    def test_ascii_arrow_separator(self):
        """Test detection with ASCII arrow separator."""
        changelog = """
        Node.js: 18 -> 20
        """
        deps = detect_dependency_updates(changelog)
        assert "Node.js" in deps or "Node" in deps
        assert any(d["old"] == "18" and d["new"] == "20" for d in deps.values())

    def test_to_separator(self):
        """Test detection with 'to' separator."""
        changelog = """
        package 1.0.0 to 2.0.0
        """
        deps = detect_dependency_updates(changelog)
        assert len(deps) >= 1

    def test_multiple_dependencies(self):
        """Test detection of multiple dependencies."""
        changelog = """
        Python: 3.9 → 3.11
        Node: 18 → 20
        Redis: 6.0 → 7.0
        """
        deps = detect_dependency_updates(changelog)
        assert len(deps) >= 2

    def test_no_dependencies(self):
        """Test changelog with no dependency updates."""
        changelog = "feat: Added new feature"
        deps = detect_dependency_updates(changelog)
        assert len(deps) == 0


class TestDetectSecurityFixes:
    """Tests for detect_security_fixes function."""

    def test_security_marker(self):
        """Test detection of 'Security:' marker."""
        changelog = """
        Security: Fixed XSS vulnerability
        """
        fixes = detect_security_fixes(changelog)
        assert len(fixes) == 1
        assert "XSS" in fixes[0]

    def test_cve_marker(self):
        """Test detection of CVE identifiers."""
        changelog = """
        Fixed CVE-2024-1234
        """
        fixes = detect_security_fixes(changelog)
        assert len(fixes) == 1
        assert "CVE-2024-1234" in fixes[0]

    def test_security_bracket_marker(self):
        """Test detection of '[SECURITY]' marker."""
        changelog = """
        [SECURITY] Patched SQL injection
        """
        fixes = detect_security_fixes(changelog)
        assert len(fixes) == 1

    def test_vulnerability_marker(self):
        """Test detection of 'Vulnerability:' marker."""
        changelog = """
        Vulnerability: Remote code execution fixed
        """
        fixes = detect_security_fixes(changelog)
        assert len(fixes) == 1

    def test_multiple_security_fixes(self):
        """Test detection of multiple security fixes."""
        changelog = """
        Security: Fixed auth bypass
        Fixed CVE-2024-5678
        [SECURITY] Patched CSRF
        """
        fixes = detect_security_fixes(changelog)
        assert len(fixes) >= 2

    def test_no_security_fixes(self):
        """Test changelog with no security fixes."""
        changelog = "feat: Added new feature"
        fixes = detect_security_fixes(changelog)
        assert len(fixes) == 0


class TestAnalyzeImpact:
    """Tests for analyze_impact function."""

    def test_complete_analysis(self):
        """Test full impact analysis with all types."""
        changelog = """
        # v2.1.0

        BREAKING: Removed deprecated API
        Migration: Run update script
        Python: 3.9 → 3.11
        Security: Fixed vulnerability
        """
        diff = {"major": 0, "minor": 1, "patch": 0}

        impact = analyze_impact(changelog, diff)

        assert impact["severity"] == "minor"
        assert len(impact["breaking_changes"]) == 1
        assert len(impact["migrations"]) == 1
        assert len(impact["dependencies"]) >= 1
        assert len(impact["security_fixes"]) >= 1

    def test_major_version_analysis(self):
        """Test analysis for major version."""
        changelog = "feat: New architecture"
        diff = {"major": 1, "minor": 0, "patch": 0}

        impact = analyze_impact(changelog, diff)

        assert impact["severity"] == "major"

    def test_patch_version_analysis(self):
        """Test analysis for patch version."""
        changelog = "fix: Minor bug fix"
        diff = {"major": 0, "minor": 0, "patch": 1}

        impact = analyze_impact(changelog, diff)

        assert impact["severity"] == "patch"

    def test_empty_changelog(self):
        """Test analysis with empty changelog."""
        impact = analyze_impact("", {"major": 0, "minor": 1, "patch": 0})

        assert impact["severity"] == "minor"
        assert len(impact["breaking_changes"]) == 0
        assert len(impact["migrations"]) == 0


class TestFormatImpactSummary:
    """Tests for format_impact_summary function."""

    def test_format_with_all_sections(self):
        """Test formatting with all impact types."""
        impact = {
            "severity": "major",
            "breaking_changes": ["API removed"],
            "migrations": ["Run script"],
            "dependencies": {"Python": {"old": "3.9", "new": "3.11"}},
            "security_fixes": ["CVE-2024-1234"]
        }

        summary = format_impact_summary(impact)

        assert "MAJOR" in summary
        assert "Breaking Changes" in summary
        assert "Migrations" in summary
        assert "Dependency Updates" in summary
        assert "Security Fixes" in summary

    def test_format_minimal_impact(self):
        """Test formatting with minimal impact."""
        impact = {
            "severity": "patch",
            "breaking_changes": [],
            "migrations": [],
            "dependencies": {},
            "security_fixes": []
        }

        summary = format_impact_summary(impact)

        assert "PATCH" in summary
        assert "Breaking Changes" not in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
