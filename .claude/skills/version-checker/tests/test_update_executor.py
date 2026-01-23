#!/usr/bin/env python3
"""
Unit tests for update_executor module.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from update_executor import (
    execute_update,
    get_current_commit,
    find_migration_script,
    verify_installation,
    rollback
)


class TestGetCurrentCommit:
    """Tests for get_current_commit function."""

    @patch("subprocess.run")
    def test_get_current_commit(self, mock_run):
        """Test getting current commit SHA."""
        mock_run.return_value = MagicMock(
            stdout="abc123def456\n",
            returncode=0
        )

        commit = get_current_commit()

        assert commit == "abc123def456"
        mock_run.assert_called_once()


class TestFindMigrationScript:
    """Tests for find_migration_script function."""

    def test_no_scripts_directory(self):
        """Test when .scripts directory doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            script = find_migration_script("2.1.0")
            assert script is None

    def test_no_migration_script_found(self):
        """Test when no matching migration script exists."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.glob", return_value=[]):
                script = find_migration_script("2.1.0")
                assert script is None

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists")
    def test_migration_script_found(self, mock_exists, mock_glob):
        """Test finding migration script."""
        mock_exists.return_value = True

        mock_script = MagicMock(spec=Path)
        mock_script.is_file.return_value = True
        mock_script.stat.return_value.st_mode = 0o755  # Executable

        mock_glob.return_value = [mock_script]

        script = find_migration_script("2.1.0")
        assert script is not None


class TestVerifyInstallation:
    """Tests for verify_installation function."""

    @patch("subprocess.run")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_verification_success(self, mock_exists, mock_is_dir, mock_run):
        """Test successful verification."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        result = verify_installation()
        assert result is True

    @patch("pathlib.Path.exists")
    def test_verification_fails_no_version_file(self, mock_exists):
        """Test verification fails when VERSION file missing."""
        mock_exists.return_value = False

        result = verify_installation()
        assert result is False

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_verification_fails_missing_directory(self, mock_exists, mock_is_dir):
        """Test verification fails when required directory missing."""
        mock_exists.return_value = True

        # First call for VERSION file check (True)
        # Subsequent calls for directory checks (False)
        mock_is_dir.side_effect = [False, True, True]

        result = verify_installation()
        assert result is False


class TestRollback:
    """Tests for rollback function."""

    @patch("subprocess.run")
    def test_rollback_success(self, mock_run):
        """Test successful rollback."""
        mock_run.return_value = MagicMock(returncode=0)

        result = rollback("abc123")

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_rollback_failure(self, mock_run):
        """Test failed rollback."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git"])

        result = rollback("abc123")

        assert result is False


class TestExecuteUpdate:
    """Tests for execute_update function."""

    @patch("update_executor.verify_installation")
    @patch("update_executor.run_command")
    @patch("update_executor.get_current_commit")
    def test_update_success_no_migrations(
        self,
        mock_get_commit,
        mock_run_cmd,
        mock_verify
    ):
        """Test successful update without migrations."""
        mock_get_commit.return_value = "abc123"
        mock_verify.return_value = True

        with patch("update_executor.find_migration_script", return_value=None):
            result = execute_update("v2.1.0")

        assert result["success"] is True
        assert result["new_version"] == "2.1.0"
        assert len(result["migrations_run"]) == 0

    @patch("update_executor.verify_installation")
    @patch("update_executor.run_command")
    @patch("update_executor.get_current_commit")
    def test_update_verification_fails(
        self,
        mock_get_commit,
        mock_run_cmd,
        mock_verify
    ):
        """Test update fails when verification fails."""
        mock_get_commit.return_value = "abc123"
        mock_verify.return_value = False

        with patch("update_executor.rollback") as mock_rollback:
            result = execute_update("v2.1.0")

        assert result["success"] is False
        assert "verification failed" in " ".join(result["errors"]).lower()
        mock_rollback.assert_called_once_with("abc123")

    @patch("update_executor.get_current_commit")
    @patch("update_executor.run_command")
    def test_update_git_fetch_fails(self, mock_run_cmd, mock_get_commit):
        """Test update fails when git fetch fails."""
        mock_get_commit.return_value = "abc123"
        mock_run_cmd.side_effect = subprocess.CalledProcessError(1, ["git"])

        result = execute_update("v2.1.0")

        assert result["success"] is False
        assert "fetch failed" in " ".join(result["errors"]).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
