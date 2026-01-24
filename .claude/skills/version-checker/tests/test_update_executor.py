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
    rollback,
    validate_migration_script,
    get_version_from_commit
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


class TestValidateMigrationScript:
    """Tests for validate_migration_script function."""

    def test_script_does_not_exist(self):
        """Test validation fails when script doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            mock_path = MagicMock(spec=Path)
            mock_path.exists.return_value = False

            result = validate_migration_script(mock_path)
            assert result is False

    def test_script_not_executable(self):
        """Test validation fails when script is not executable."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.stat.return_value.st_mode = 0o644  # Not executable

        result = validate_migration_script(mock_path)
        assert result is False

    def test_script_missing_shebang(self):
        """Test validation fails when script missing shebang."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.stat.return_value.st_mode = 0o755

        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=lambda s: s, __exit__=lambda s, *_: None, readline=lambda: "echo test\n"))):
            result = validate_migration_script(mock_path)
            assert result is False

    def test_script_dangerous_pattern(self):
        """Test validation fails when dangerous pattern detected."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.stat.return_value.st_mode = 0o755

        dangerous_content = "#!/bin/bash\nrm -rf /\necho done\n"

        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = lambda s, *_: None
        mock_file.readline.return_value = "#!/bin/bash\n"
        mock_file.read.return_value = dangerous_content

        with patch("builtins.open", return_value=mock_file):
            result = validate_migration_script(mock_path)
            assert result is False

    def test_script_valid(self):
        """Test validation passes for valid script."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = True
        mock_path.stat.return_value.st_mode = 0o755

        safe_content = "#!/bin/bash\necho 'Running migration'\npython3 migrate.py\necho 'Done'\n"

        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = lambda s, *_: None
        mock_file.readline.return_value = "#!/bin/bash\n"
        mock_file.read.return_value = safe_content

        with patch("builtins.open", return_value=mock_file):
            result = validate_migration_script(mock_path)
            assert result is True


class TestGetVersionFromCommit:
    """Tests for get_version_from_commit function."""

    @patch("subprocess.run")
    def test_get_version_success(self, mock_run):
        """Test getting version from commit."""
        version_content = """version: "2.0.2"
build_date: "2026-01-23"
"""
        mock_run.return_value = MagicMock(
            stdout=version_content,
            returncode=0
        )

        version = get_version_from_commit("abc123")

        assert version == "2.0.2"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_version_no_version_field(self, mock_run):
        """Test handling when version field not found."""
        version_content = """build_date: "2026-01-23"
"""
        mock_run.return_value = MagicMock(
            stdout=version_content,
            returncode=0
        )

        version = get_version_from_commit("abc123")

        assert version == "unknown"

    @patch("subprocess.run")
    def test_get_version_git_fails(self, mock_run):
        """Test handling when git command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git"])

        version = get_version_from_commit("abc123")

        assert version == "unknown"


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
            with patch("update_executor.get_version_from_commit", return_value="2.0.2"):
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

    @patch("update_executor.verify_installation")
    @patch("update_executor.run_command")
    @patch("update_executor.get_current_commit")
    @patch("update_executor.validate_migration_script")
    def test_update_migration_validation_fails(
        self,
        mock_validate,
        mock_get_commit,
        mock_run_cmd,
        mock_verify
    ):
        """Test update fails when migration validation fails."""
        mock_get_commit.return_value = "abc123"
        mock_validate.return_value = False

        mock_script = MagicMock(spec=Path)

        with patch("update_executor.find_migration_script", return_value=mock_script):
            with patch("update_executor.rollback") as mock_rollback:
                result = execute_update("v2.1.0")

        assert result["success"] is False
        assert "validation failed" in " ".join(result["errors"]).lower()
        mock_rollback.assert_called_once_with("abc123")

    @patch("update_executor.verify_installation")
    @patch("update_executor.run_command")
    @patch("update_executor.get_current_commit")
    @patch("update_executor.validate_migration_script")
    def test_update_migration_timeout(
        self,
        mock_validate,
        mock_get_commit,
        mock_run_cmd,
        mock_verify
    ):
        """Test update fails when migration times out."""
        mock_get_commit.return_value = "abc123"
        mock_validate.return_value = True

        # First call succeeds (git fetch), second succeeds (git checkout), third times out (migration)
        mock_run_cmd.side_effect = [
            None,  # git fetch
            None,  # git checkout
            subprocess.TimeoutExpired(["migrate.sh"], 300)  # migration timeout
        ]

        mock_script = MagicMock(spec=Path)
        mock_script.name = "migrate.sh"

        with patch("update_executor.find_migration_script", return_value=mock_script):
            with patch("update_executor.rollback") as mock_rollback:
                result = execute_update("v2.1.0")

        assert result["success"] is False
        assert "timeout" in " ".join(result["errors"]).lower()
        mock_rollback.assert_called_once_with("abc123")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
