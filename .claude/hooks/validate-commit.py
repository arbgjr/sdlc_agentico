#!/usr/bin/env python3
"""
Hook: Validate Commit

Validates commit messages follow Conventional Commits format and
do not contain secrets or forbidden code patterns.

Security Checks:
- Conventional Commits format
- Message length validation
- Forbidden words detection
- Secrets scanning (gitleaks integration)
- Anti-mock policy enforcement
"""

import sys
import re
import subprocess
from typing import List, Tuple, Optional
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


class CommitValidator:
    """Validates git commit messages and staged files."""

    # Conventional Commits pattern
    CONVENTIONAL_PATTERN = re.compile(
        r"^(feat|fix|refactor|docs|test|chore|ci|perf|style)(\(.+\))?: .+"
    )

    # Forbidden words pattern
    FORBIDDEN_WORDS = re.compile(
        r"TODO|FIXME|WIP|DO NOT COMMIT|secret|password|api.key",
        re.IGNORECASE
    )

    # Anti-mock policy patterns
    MOCK_PATTERNS = re.compile(
        r"(mock|stub|fake|dummy)",
        re.IGNORECASE
    )

    def __init__(self):
        self.logger = get_logger(__name__, skill="git-hooks", phase=5)
        self.repo_root = self._find_repo_root()
        self.errors = 0

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

    def _get_commit_message(self) -> Optional[str]:
        """
        Get commit message from environment or file.

        Returns:
            Commit message text or None if not available
        """
        import os

        # Try environment variable first
        msg = os.environ.get("COMMIT_MSG")
        if msg:
            return msg

        # Try reading from git's commit message file
        commit_msg_file = self.repo_root / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            return commit_msg_file.read_text(encoding="utf-8")

        return None

    def _run_command(
        self,
        cmd: List[str],
        check: bool = False
    ) -> Tuple[int, str, str]:
        """
        Run command and capture output.

        Args:
            cmd: Command and arguments as list
            check: Raise exception on non-zero exit code

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=self.repo_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.returncode, e.stdout or "", e.stderr or ""

    def validate_conventional_commits(self, message: str) -> bool:
        """
        Validate commit message follows Conventional Commits format.

        Args:
            message: Commit message text

        Returns:
            True if valid, False otherwise
        """
        first_line = message.split("\n")[0]

        if not self.CONVENTIONAL_PATTERN.match(first_line):
            self.logger.error("Commit message does not follow Conventional Commits")
            print("  Expected format: type(scope): description")
            print("  Valid types: feat, fix, refactor, docs, test, chore, ci, perf, style")
            print("  Example: feat(orders): add order history endpoint")
            self.errors += 1
            return False

        self.logger.info("Conventional Commits: OK")
        return True

    def validate_message_length(self, message: str) -> bool:
        """
        Validate first line is not too long.

        Args:
            message: Commit message text

        Returns:
            True if valid, False otherwise
        """
        first_line = message.split("\n")[0]
        max_length = 72

        if len(first_line) > max_length:
            self.logger.warning(
                "First line too long",
                extra={"length": len(first_line), "max": max_length}
            )
            self.errors += 1
            return False

        return True

    def validate_forbidden_words(self, message: str) -> bool:
        """
        Check for forbidden words in commit message.

        Args:
            message: Commit message text

        Returns:
            True if no forbidden words found, False otherwise
        """
        matches = self.FORBIDDEN_WORDS.findall(message)

        if matches:
            detected = ", ".join(set(matches))
            self.logger.error(
                "Commit message contains forbidden words",
                extra={"detected": detected}
            )
            self.errors += 1
            return False

        self.logger.info("No forbidden words: OK")
        return True

    def scan_secrets(self) -> bool:
        """
        Scan staged files for secrets using gitleaks.

        Returns:
            True if no secrets found or gitleaks not available, False otherwise
        """
        # Check if gitleaks is installed
        returncode, _, _ = self._run_command(["which", "gitleaks"])
        if returncode != 0:
            self.logger.debug("gitleaks not installed, skipping secrets scan")
            return True

        self.logger.debug("Running gitleaks scan")

        # Run gitleaks on staged files
        returncode, stdout, stderr = self._run_command(
            ["gitleaks", "protect", "--staged", "--no-banner"]
        )

        if returncode != 0:
            self.logger.error("Secrets detected in staged files")
            self.errors += 1
            return False

        self.logger.info("Secrets scan: OK")
        return True

    def check_anti_mock_policy(self) -> bool:
        """
        Check for mock patterns in production code (anti-mock policy).

        Returns:
            True always (warnings only, doesn't block)
        """
        # Get staged files
        returncode, stdout, _ = self._run_command(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
        )

        if returncode != 0:
            return True

        staged_files = [f.strip() for f in stdout.split("\n") if f.strip()]

        for file_path in staged_files:
            # Skip test directories
            if "/test" in file_path or file_path.startswith("test"):
                continue

            # Check if file exists and is a text file
            full_path = self.repo_root / file_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")

                # Search for mock patterns
                if self.MOCK_PATTERNS.search(content):
                    self.logger.warning(
                        "Possible mock in production code",
                        extra={"file": file_path}
                    )
                    # Don't increment errors - this is a warning only
            except Exception as e:
                self.logger.debug(
                    f"Could not read file: {file_path}",
                    extra={"error": str(e)}
                )

        return True

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if all checks pass, False otherwise
        """
        message = self._get_commit_message()

        if not message:
            self.logger.warning("No commit message to validate (dry run)")
            return True

        self.logger.debug(
            "Validating commit message",
            extra={"length": len(message)}
        )

        # Run all validations
        self.validate_conventional_commits(message)
        self.validate_message_length(message)
        self.validate_forbidden_words(message)
        self.scan_secrets()
        self.check_anti_mock_policy()

        return self.errors == 0

    def execute(self) -> int:
        """
        Execute commit validation.

        Returns:
            0 if validation passes, 1 otherwise
        """
        self.logger.debug("Starting commit validation")

        if not self.validate():
            print()
            self.logger.error("Commit blocked", extra={"errors": self.errors})
            return 1

        self.logger.info("Commit validated successfully")
        return 0


def main() -> int:
    """
    Main entry point for commit validation hook.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    validator = CommitValidator()

    try:
        return validator.execute()
    except Exception as e:
        validator.logger.error(
            f"Validation failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
