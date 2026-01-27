#!/usr/bin/env python3
"""
Integration tests for check_updates module.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_updates import (
    check_for_updates,
    build_notification,
    execute_update
)
from dismissal_tracker import clear_dismissal


class TestCheckForUpdates:
    """Tests for check_for_updates function."""

    def setup_method(self):
        """Clear dismissals before each test."""
        clear_dismissal()

    def teardown_method(self):
        """Clear dismissals after each test."""
        clear_dismissal()

    @patch("check_updates.get_current_version")
    @patch("check_updates.fetch_latest_release")
    def test_no_update_available(self, mock_fetch, mock_current):
        """Test when already on latest version."""
        mock_current.return_value = "2.1.0"
        mock_fetch.return_value = {
            "tag": "v2.1.0",
            "date": "2026-01-22T10:00:00Z",
            "changelog": "Current version",
            "assets": []
        }

        result = check_for_updates()

        assert result["update_available"] is False
        assert result["current"] == "2.1.0"
        assert result["latest"] == "2.1.0"

    @patch("check_updates.get_current_version")
    @patch("check_updates.fetch_latest_release")
    def test_update_available(self, mock_fetch, mock_current):
        """Test when update is available."""
        mock_current.return_value = "2.0.0"
        mock_fetch.return_value = {
            "tag": "v2.1.0",
            "date": "2026-01-22T10:00:00Z",
            "changelog": "# v2.1.0\n\n- New feature",
            "assets": []
        }

        result = check_for_updates()

        assert result["update_available"] is True
        assert result["current"] == "2.0.0"
        assert result["latest"] == "2.1.0"
        assert "changelog" in result
        assert "impact" in result
        assert "notification" in result
        assert result.get("dismissed") is False

    @patch("check_updates.get_current_version")
    @patch("check_updates.fetch_latest_release")
    def test_dismissed_update(self, mock_fetch, mock_current):
        """Test when update was dismissed."""
        from dismissal_tracker import dismiss_update

        mock_current.return_value = "2.0.0"
        mock_fetch.return_value = {
            "tag": "v2.1.0",
            "date": "2026-01-22T10:00:00Z",
            "changelog": "New version",
            "assets": []
        }

        # Dismiss the update
        dismiss_update("2.1.0")

        result = check_for_updates()

        assert result["update_available"] is True
        assert result["dismissed"] is True
        assert result["latest"] == "2.1.0"

    @patch("check_updates.get_current_version")
    @patch("check_updates.fetch_latest_release")
    def test_error_fetching_release(self, mock_fetch, mock_current):
        """Test error handling when GitHub fetch fails."""
        mock_current.return_value = "2.0.0"
        mock_fetch.side_effect = RuntimeError("GitHub API error")

        result = check_for_updates()

        assert result["update_available"] is False
        assert "error" in result
        assert "GitHub API error" in result["error"]


class TestBuildNotification:
    """Tests for build_notification function."""

    def test_notification_format(self):
        """Test notification markdown format."""
        release = {
            "date": "2026-01-22T10:00:00Z",
            "changelog": "# v2.1.0\n\n- New feature"
        }
        impact = {
            "severity": "minor",
            "breaking_changes": [],
            "migrations": [],
            "dependencies": {},
            "security_fixes": []
        }

        notification = build_notification(
            current="2.0.0",
            latest="2.1.0",
            release=release,
            impact=impact,
            upgrade_type="minor"
        )

        assert "v2.0.0" in notification
        assert "v2.1.0" in notification
        assert "2026-01-22" in notification
        assert "MINOR" in notification
        assert "What's New" in notification

    def test_notification_with_breaking_changes(self):
        """Test notification includes breaking changes."""
        release = {
            "date": "2026-01-22T10:00:00Z",
            "changelog": "BREAKING: API changed"
        }
        impact = {
            "severity": "major",
            "breaking_changes": ["API v1 removed"],
            "migrations": ["Run migration script"],
            "dependencies": {"Python": {"old": "3.9", "new": "3.11"}},
            "security_fixes": ["CVE-2024-1234"]
        }

        notification = build_notification(
            current="2.0.0",
            latest="3.0.0",
            release=release,
            impact=impact,
            upgrade_type="major"
        )

        assert "Breaking Changes" in notification
        assert "Migrations" in notification
        assert "Dependency Updates" in notification
        assert "Security Fixes" in notification


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
