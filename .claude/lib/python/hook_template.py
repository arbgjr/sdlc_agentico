#!/usr/bin/env python3
"""
Template for converting shell hooks to Python.

This template provides a standard structure for hooks with:
- Cross-platform subprocess management
- Structured logging with correlation IDs
- Type hints and comprehensive docstrings
- Error handling and validation
- Exit code management

Usage:
    1. Copy this file to .claude/hooks/your-hook.py
    2. Implement the HookImplementation class
    3. Update __main__ section with proper metadata
"""

import sys
import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger, log_operation
except ImportError:
    # Fallback logger if sdlc_logging not available
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

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class HookBase:
    """Base class for all hooks with common functionality."""

    def __init__(self, skill: str = "unknown", phase: Optional[int] = None):
        """
        Initialize hook.

        Args:
            skill: Name of the skill/hook (e.g., "validate-commit")
            phase: SDLC phase number (0-8) if applicable
        """
        self.skill = skill
        self.phase = phase
        self.logger = get_logger(__name__, skill=skill, phase=phase)
        self.repo_root = self._find_repo_root()

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
            # Fallback to current directory
            return Path.cwd()

    def run_command(
        self,
        cmd: List[str],
        check: bool = True,
        capture_output: bool = True,
        cwd: Optional[Path] = None
    ) -> Tuple[int, str, str]:
        """
        Run command with cross-platform subprocess management.

        Args:
            cmd: Command and arguments as list
            check: Raise exception on non-zero exit code
            capture_output: Capture stdout/stderr
            cwd: Working directory (defaults to repo root)

        Returns:
            Tuple of (exit_code, stdout, stderr)

        Raises:
            subprocess.CalledProcessError: If check=True and command fails
        """
        if cwd is None:
            cwd = self.repo_root

        self.logger.info(
            f"Running command: {' '.join(cmd)}",
            extra={"cwd": str(cwd)}
        )

        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check,
                cwd=cwd
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"Command failed: {e.cmd}",
                extra={
                    "exit_code": e.returncode,
                    "stdout": e.stdout,
                    "stderr": e.stderr
                }
            )
            if check:
                raise
            return e.returncode, e.stdout or "", e.stderr or ""

    def validate(self) -> bool:
        """
        Validate hook preconditions.

        Override this method to implement validation logic.

        Returns:
            True if validation passes, False otherwise
        """
        raise NotImplementedError("Subclass must implement validate()")

    def execute(self) -> int:
        """
        Execute hook logic.

        Override this method to implement hook logic.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        raise NotImplementedError("Subclass must implement execute()")


class HookImplementation(HookBase):
    """
    Template hook implementation.

    Replace this class with your actual hook logic.

    Example:
        class ValidateCommitHook(HookBase):
            def validate(self) -> bool:
                # Check if in git repo
                return (self.repo_root / ".git").exists()

            def execute(self) -> int:
                # Validate commit message format
                # Return 0 if valid, 1 if invalid
                pass
    """

    def validate(self) -> bool:
        """
        Validate hook preconditions.

        Example validations:
        - Check if in git repository
        - Verify required files exist
        - Check environment variables

        Returns:
            True if validation passes, False otherwise
        """
        # TODO: Implement validation logic
        return True

    def execute(self) -> int:
        """
        Execute hook logic.

        Example logic:
        - Validate commit messages
        - Check quality gates
        - Create branches
        - Update files

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # TODO: Implement hook logic
        self.logger.info("Hook executed successfully")
        return 0


def main() -> int:
    """
    Main entry point for hook.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Update these metadata for your hook
    SKILL_NAME = "template-hook"
    PHASE_NUMBER = None  # Set to 0-8 if phase-specific, None otherwise

    hook = HookImplementation(skill=SKILL_NAME, phase=PHASE_NUMBER)

    # Validate preconditions
    if not hook.validate():
        hook.logger.error("Hook validation failed")
        return 1

    # Execute hook logic
    try:
        return hook.execute()
    except Exception as e:
        hook.logger.error(
            f"Hook execution failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
