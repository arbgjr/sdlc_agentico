#!/usr/bin/env python3
"""
Hook: Auto Branch

Creates git branches automatically based on work type.

Supports branch types:
- fix/* - Bug fixes
- hotfix/* - Critical production fixes
- feature/* - New features
- release/v* - Release branches
- chore/* - Maintenance tasks
- refactor/* - Code refactoring
- docs/* - Documentation updates
"""

import sys
import re
import subprocess
from typing import Optional, Tuple
from pathlib import Path

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)

        def info(self, msg, **kwargs):
            self.logger.info(f"{msg} {kwargs}")

        def error(self, msg, **kwargs):
            self.logger.error(f"{msg} {kwargs}")

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class BranchManager:
    """Manages automatic git branch creation."""

    # Valid branch types
    VALID_TYPES = {
        "fix",
        "hotfix",
        "feature",
        "release",
        "chore",
        "refactor",
        "docs"
    }

    # Maximum branch name length
    MAX_NAME_LENGTH = 50

    def __init__(self, branch_type: str, name: str):
        self.logger = get_logger(__name__, skill="git-hooks", phase=5)
        self.repo_root = self._find_repo_root()
        self.branch_type = branch_type.lower()
        self.raw_name = name
        self.branch_name = self._normalize_name(name)

    def _find_repo_root(self) -> Path:
        """Find git repository root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            return Path.cwd()

    def _run_git_command(
        self,
        args: list,
        check: bool = True
    ) -> Tuple[int, str, str]:
        """
        Run git command.

        Args:
            args: Git command arguments
            check: Raise exception on non-zero exit code

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=check,
                cwd=self.repo_root
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.returncode, e.stdout or "", e.stderr or ""

    def _normalize_name(self, name: str) -> str:
        """
        Normalize branch name:
        - Convert to lowercase
        - Replace spaces with hyphens
        - Remove special characters
        - Remove consecutive hyphens
        - Trim leading/trailing hyphens
        - Limit length to MAX_NAME_LENGTH

        Args:
            name: Raw branch name

        Returns:
            Normalized branch name
        """
        # Convert to lowercase
        normalized = name.lower()

        # Replace spaces with hyphens
        normalized = normalized.replace(" ", "-")

        # Remove special characters (keep alphanumeric and hyphens)
        normalized = re.sub(r"[^a-z0-9-]", "", normalized)

        # Remove consecutive hyphens
        normalized = re.sub(r"-+", "-", normalized)

        # Trim leading/trailing hyphens
        normalized = normalized.strip("-")

        # Limit length
        if len(normalized) > self.MAX_NAME_LENGTH:
            original_length = len(normalized)
            normalized = normalized[:self.MAX_NAME_LENGTH]
            self.logger.debug(
                "Branch name truncated",
                extra={
                    "original_length": original_length,
                    "truncated_to": self.MAX_NAME_LENGTH
                }
            )

        return normalized

    def _build_branch_name(self) -> str:
        """
        Build full branch name with type prefix.

        Returns:
            Full branch name (e.g., "feature/user-authentication")
        """
        if self.branch_type == "release":
            # Add 'v' prefix for release branches
            return f"release/v{self.branch_name}"

        return f"{self.branch_type}/{self.branch_name}"

    def validate(self) -> bool:
        """
        Validate branch creation preconditions.

        Returns:
            True if validation passes, False otherwise
        """
        # Check if in git repository
        returncode, _, _ = self._run_git_command(
            ["rev-parse", "--is-inside-work-tree"],
            check=False
        )

        if returncode != 0:
            self.logger.error("Not in a git repository")
            return False

        # Check branch type is valid
        if self.branch_type not in self.VALID_TYPES:
            self.logger.error(
                "Unknown branch type",
                extra={"type": self.branch_type}
            )
            print(f"Valid types: {', '.join(sorted(self.VALID_TYPES))}")
            return False

        return True

    def check_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes.

        Returns:
            True if there are uncommitted changes, False otherwise
        """
        returncode, _, _ = self._run_git_command(
            ["diff-index", "--quiet", "HEAD", "--"],
            check=False
        )

        if returncode != 0:
            self.logger.warning("There are uncommitted changes")
            print("Consider stashing or committing before switching branches.")
            return True

        return False

    def branch_exists_locally(self, branch: str) -> bool:
        """
        Check if branch exists locally.

        Args:
            branch: Branch name to check

        Returns:
            True if branch exists locally, False otherwise
        """
        returncode, _, _ = self._run_git_command(
            ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            check=False
        )

        return returncode == 0

    def branch_exists_remotely(self, branch: str) -> bool:
        """
        Check if branch exists on remote.

        Args:
            branch: Branch name to check

        Returns:
            True if branch exists remotely, False otherwise
        """
        returncode, _, _ = self._run_git_command(
            ["ls-remote", "--exit-code", "--heads", "origin", branch],
            check=False
        )

        return returncode == 0

    def create_or_checkout_branch(self) -> bool:
        """
        Create or checkout branch.

        Returns:
            True if successful, False otherwise
        """
        branch = self._build_branch_name()

        self.logger.debug(
            "Branch name resolved",
            extra={"branch": branch, "type": self.branch_type}
        )

        # Check for uncommitted changes (warning only)
        self.check_uncommitted_changes()

        # Check if branch exists locally
        if self.branch_exists_locally(branch):
            self.logger.info(
                "Branch exists locally, checking out",
                extra={"branch": branch}
            )
            returncode, _, _ = self._run_git_command(["checkout", branch])

            if returncode != 0:
                self.logger.error(
                    "Failed to checkout branch",
                    extra={"branch": branch}
                )
                return False

        # Check if branch exists remotely
        elif self.branch_exists_remotely(branch):
            self.logger.info(
                "Branch exists remotely, checking out with tracking",
                extra={"branch": branch}
            )
            returncode, _, _ = self._run_git_command(
                ["checkout", "-b", branch, f"origin/{branch}"]
            )

            if returncode != 0:
                self.logger.error(
                    "Failed to checkout remote branch",
                    extra={"branch": branch}
                )
                return False

        # Create new branch
        else:
            self.logger.info(
                "Creating new branch",
                extra={"branch": branch}
            )
            returncode, _, _ = self._run_git_command(["checkout", "-b", branch])

            if returncode != 0:
                self.logger.error(
                    "Failed to create branch",
                    extra={"branch": branch}
                )
                return False

        # Verify current branch
        returncode, current_branch, _ = self._run_git_command(
            ["branch", "--show-current"]
        )

        if returncode != 0 or current_branch != branch:
            self.logger.error(
                "Failed to activate branch",
                extra={"expected": branch, "current": current_branch}
            )
            return False

        self.logger.info(
            "Branch activated successfully",
            extra={"branch": branch, "type": self.branch_type}
        )
        print()
        print(f"Branch active: {branch}")
        print(f"Type: {self.branch_type}")

        return True

    def execute(self) -> int:
        """
        Execute branch creation/checkout.

        Returns:
            0 if successful, 1 otherwise
        """
        self.logger.debug(
            "Creating branch",
            extra={"type": self.branch_type, "name": self.raw_name}
        )

        if not self.validate():
            return 1

        if not self.create_or_checkout_branch():
            return 1

        return 0


def main() -> int:
    """
    Main entry point for auto-branch hook.

    Args:
        sys.argv[1]: Branch type (fix, hotfix, feature, release, chore, refactor, docs)
        sys.argv[2]: Branch name

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if len(sys.argv) < 3:
        print("Usage: auto-branch.py <type> <name>")
        print("Types: fix, hotfix, feature, release, chore, refactor, docs")
        return 1

    branch_type = sys.argv[1]
    name = sys.argv[2]

    manager = BranchManager(branch_type, name)

    try:
        return manager.execute()
    except Exception as e:
        manager.logger.error(
            f"Branch creation failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
