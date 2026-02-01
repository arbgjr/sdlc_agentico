"""
Tests for validate-commit.py hook.

Tests conventional commits validation, forbidden words detection,
and anti-mock policy enforcement.
"""

import sys
import os
from pathlib import Path
import pytest

# Add hooks directory to path
HOOKS_DIR = Path(__file__).parent.parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from validate_commit import CommitValidator


class TestConventionalCommits:
    """Test conventional commits validation."""

    def test_valid_commit_with_scope(self, sample_commit_message):
        """Valid commit message with scope should pass."""
        validator = CommitValidator()
        message = sample_commit_message["valid_with_scope"]

        assert validator.validate_conventional_commits(message)
        assert validator.errors == 0

    def test_valid_commit_without_scope(self, sample_commit_message):
        """Valid commit message without scope should pass."""
        validator = CommitValidator()
        message = sample_commit_message["valid_no_scope"]

        assert validator.validate_conventional_commits(message)
        assert validator.errors == 0

    def test_invalid_commit_no_type(self, sample_commit_message):
        """Invalid commit without type should fail."""
        validator = CommitValidator()
        message = sample_commit_message["invalid_no_type"]

        assert not validator.validate_conventional_commits(message)
        assert validator.errors == 1

    def test_invalid_commit_too_long(self, sample_commit_message):
        """Commit message too long should fail."""
        validator = CommitValidator()
        message = sample_commit_message["invalid_too_long"]

        validator.validate_conventional_commits(message)  # Type is valid
        assert not validator.validate_message_length(message)
        assert validator.errors >= 1


class TestForbiddenWords:
    """Test forbidden words detection."""

    def test_forbidden_word_todo(self, sample_commit_message):
        """Commit with TODO should be detected."""
        validator = CommitValidator()
        message = sample_commit_message["forbidden_word"]

        assert not validator.validate_forbidden_words(message)
        assert validator.errors == 1

    def test_forbidden_word_fixme(self):
        """Commit with FIXME should be detected."""
        validator = CommitValidator()
        message = "feat(test): add FIXME for later"

        assert not validator.validate_forbidden_words(message)
        assert validator.errors == 1

    def test_no_forbidden_words(self, sample_commit_message):
        """Commit without forbidden words should pass."""
        validator = CommitValidator()
        message = sample_commit_message["valid"]

        assert validator.validate_forbidden_words(message)
        assert validator.errors == 0


class TestAntiMockPolicy:
    """Test anti-mock policy enforcement."""

    def test_mock_in_test_file_allowed(self, temp_git_repo):
        """Mocks in test files should not trigger warnings."""
        validator = CommitValidator()
        validator.repo_root = temp_git_repo

        # Create test file with mock
        test_file = temp_git_repo / "tests" / "test_service.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("from unittest.mock import Mock\n\nmock_service = Mock()\n")

        # This should pass without incrementing errors
        result = validator.check_anti_mock_policy()
        assert result is True
        assert validator.errors == 0

    def test_mock_in_production_code_warning(self, temp_git_repo, capsys):
        """Mocks in production code should trigger warning (not error)."""
        validator = CommitValidator()
        validator.repo_root = temp_git_repo

        # Create source file with mock
        src_file = temp_git_repo / "src" / "service.py"
        src_file.parent.mkdir(exist_ok=True)
        src_file.write_text("class MockService:\n    pass\n")

        # Stage the file
        import subprocess
        subprocess.run(["git", "add", str(src_file)], cwd=temp_git_repo, check=True)

        # This should warn but not increment errors
        result = validator.check_anti_mock_policy()
        assert result is True
        # Errors should still be 0 (warnings don't block)
        assert validator.errors == 0


class TestIntegration:
    """Integration tests for full validation flow."""

    def test_valid_commit_full_validation(self, temp_git_repo, monkeypatch):
        """Valid commit should pass all validations."""
        validator = CommitValidator()
        validator.repo_root = temp_git_repo

        # Mock commit message
        message = "feat(auth): add user authentication"
        monkeypatch.setenv("COMMIT_MSG", message)

        # Run full validation
        result = validator.validate()
        assert result is True
        assert validator.errors == 0

    def test_invalid_commit_full_validation(self, temp_git_repo, monkeypatch):
        """Invalid commit should fail validation."""
        validator = CommitValidator()
        validator.repo_root = temp_git_repo

        # Mock invalid commit message
        message = "add new feature with TODO"
        monkeypatch.setenv("COMMIT_MSG", message)

        # Run full validation
        result = validator.validate()
        assert result is False
        assert validator.errors >= 2  # Missing type + forbidden word
