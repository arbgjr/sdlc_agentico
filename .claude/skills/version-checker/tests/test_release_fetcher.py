#!/usr/bin/env python3
"""
Unit tests for release_fetcher module.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import subprocess

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from release_fetcher import (
    get_current_repo,
    fetch_latest_release_from_github,
    is_cache_valid,
    load_cached_release,
    save_cached_release,
    clear_cache,
    CACHE_FILE
)


class TestGetCurrentRepo:
    """Tests for get_current_repo function."""

    @patch("subprocess.run")
    def test_get_repo_success(self, mock_run):
        """Test successful repository detection."""
        mock_run.return_value = MagicMock(
            stdout='{"nameWithOwner": "owner/repo"}',
            returncode=0
        )

        repo = get_current_repo()
        assert repo == "owner/repo"

        mock_run.assert_called_once_with(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )

    @patch("subprocess.run")
    def test_get_repo_not_in_git(self, mock_run):
        """Test error when not in git repository."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["gh"], stderr="not a git repository"
        )

        with pytest.raises(RuntimeError, match="gh CLI error"):
            get_current_repo()

    @patch("subprocess.run")
    def test_get_repo_timeout(self, mock_run):
        """Test timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired(["gh"], 5)

        with pytest.raises(RuntimeError, match="timeout"):
            get_current_repo()


class TestFetchLatestReleaseFromGitHub:
    """Tests for fetch_latest_release_from_github function."""

    @patch("subprocess.run")
    def test_fetch_release_success(self, mock_run):
        """Test successful release fetch."""
        mock_response = {
            "tag_name": "v2.1.0",
            "published_at": "2026-01-22T10:00:00Z",
            "body": "# Changelog\n\n- New feature",
            "assets": [
                {"name": "asset1.tar.gz"},
                {"name": "asset2.zip"}
            ]
        }

        mock_run.return_value = MagicMock(
            stdout=json.dumps(mock_response),
            returncode=0
        )

        release = fetch_latest_release_from_github("owner/repo")

        assert release["tag"] == "v2.1.0"
        assert release["date"] == "2026-01-22T10:00:00Z"
        assert "New feature" in release["changelog"]
        assert release["assets"] == ["asset1.tar.gz", "asset2.zip"]

    @patch("subprocess.run")
    def test_fetch_release_no_releases(self, mock_run):
        """Test error when no releases exist."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["gh"], stderr="404 Not Found"
        )

        with pytest.raises(RuntimeError, match="No releases found"):
            fetch_latest_release_from_github("owner/repo")

    @patch("subprocess.run")
    def test_fetch_release_timeout(self, mock_run):
        """Test GitHub API timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["gh"], 10)

        with pytest.raises(RuntimeError, match="timeout"):
            fetch_latest_release_from_github("owner/repo")

    @patch("subprocess.run")
    def test_fetch_release_invalid_json(self, mock_run):
        """Test handling of invalid JSON response."""
        mock_run.return_value = MagicMock(
            stdout="invalid json",
            returncode=0
        )

        with pytest.raises(RuntimeError, match="Invalid GitHub response"):
            fetch_latest_release_from_github("owner/repo")


class TestCacheManagement:
    """Tests for cache management functions."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_cache()

    def test_cache_not_valid_when_missing(self):
        """Test cache validity when file doesn't exist."""
        assert is_cache_valid() is False

    def test_cache_valid_when_fresh(self):
        """Test cache validity when recently saved."""
        release = {
            "tag": "v2.1.0",
            "date": "2026-01-22T10:00:00Z",
            "changelog": "Test",
            "assets": []
        }

        save_cached_release(release)
        assert is_cache_valid() is True

    def test_cache_invalid_when_expired(self):
        """Test cache invalidity when TTL exceeded."""
        # Create cache with old timestamp
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)

        cache_data = {
            "cached_at": old_time.isoformat(),
            "release": {
                "tag": "v2.0.0",
                "date": "2026-01-20T10:00:00Z",
                "changelog": "Old",
                "assets": []
            }
        }

        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f)

        assert is_cache_valid() is False

    def test_load_cached_release(self):
        """Test loading release from cache."""
        release = {
            "tag": "v2.1.0",
            "date": "2026-01-22T10:00:00Z",
            "changelog": "Test changelog",
            "assets": ["file.tar.gz"]
        }

        save_cached_release(release)
        loaded = load_cached_release()

        assert loaded is not None
        assert loaded["tag"] == "v2.1.0"
        assert loaded["changelog"] == "Test changelog"

    def test_load_cached_release_when_expired(self):
        """Test loading returns None when cache expired."""
        # Create expired cache
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)

        cache_data = {
            "cached_at": old_time.isoformat(),
            "release": {"tag": "v2.0.0"}
        }

        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f)

        assert load_cached_release() is None

    def test_clear_cache(self):
        """Test cache clearing."""
        release = {"tag": "v2.1.0", "date": "2026-01-22", "changelog": "", "assets": []}
        save_cached_release(release)

        assert CACHE_FILE.exists()
        clear_cache()
        assert not CACHE_FILE.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
