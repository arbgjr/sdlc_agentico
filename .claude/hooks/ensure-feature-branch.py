#!/usr/bin/env python3
"""
Hook: Ensure Feature Branch

Verifies user is on appropriate branch before creating files.
Prevents direct commits to protected branches (main, master, develop, production).
"""

import sys
import subprocess
from typing import List, Optional
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

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class BranchEnforcer:
    """Enforces branch naming conventions and protects main branches."""

    # Protected branches that should not receive direct commits
    PROTECTED_BRANCHES = [
        "main",
        "master",
        "develop",
        "production",
        "release"
    ]

    # Valid branch prefixes
    VALID_PREFIXES = [
        "feature/",
        "fix/",
        "hotfix/",
        "release/",
        "chore/",
        "refactor/",
        "docs/"
    ]

    def __init__(self):
        self.logger = get_logger(__name__, skill="git-hooks", phase=5)
        self.current_branch: Optional[str] = None

    def get_current_branch(self) -> Optional[str]:
        """
        Get current git branch name.

        Returns:
            Branch name or None if not in git repo
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            self.current_branch = branch if branch else None
            return self.current_branch
        except subprocess.CalledProcessError:
            self.logger.warning("Could not detect current branch")
            return None

    def is_protected_branch(self, branch: str) -> bool:
        """
        Check if branch is protected.

        Args:
            branch: Branch name to check

        Returns:
            True if branch is protected
        """
        return branch in self.PROTECTED_BRANCHES

    def follows_valid_pattern(self, branch: str) -> bool:
        """
        Check if branch follows valid naming pattern.

        Args:
            branch: Branch name to check

        Returns:
            True if branch follows valid pattern
        """
        return any(branch.startswith(prefix) for prefix in self.VALID_PREFIXES)

    def show_protected_branch_warning(self, branch: str) -> None:
        """
        Display warning about protected branch.

        Args:
            branch: Protected branch name
        """
        self.logger.warning(
            "Protected branch detected",
            extra={"branch": branch}
        )

        print()
        print("=" * 60)
        print("  AVISO: Branch Protegida Detectada")
        print("=" * 60)
        print()
        print(f"Você está na branch '{branch}'")
        print("Esta branch é protegida e não deve receber commits diretos.")
        print()
        print("Antes de criar arquivos, crie uma branch apropriada:")
        print()
        print("  Para features:")
        print("    python3 .claude/hooks/auto-branch.py feature \"nome-da-feature\"")
        print()
        print("  Para bug fixes:")
        print("    python3 .claude/hooks/auto-branch.py fix \"descricao-do-bug\"")
        print()
        print("  Para hotfixes:")
        print("    python3 .claude/hooks/auto-branch.py hotfix \"descricao-urgente\"")
        print()
        print("Ou use os comandos do SDLC:")
        print("  /sdlc-start \"Descrição do projeto\"")
        print("  /new-feature \"Nome da feature\"")
        print("  /quick-fix \"Descrição do bug\"")
        print()
        print("=" * 60)
        print()

        # Export variables for Claude Code
        print("BRANCH_REQUIRED=true")
        print("SUGGESTED_BRANCH_TYPE=feature")

    def show_pattern_warning(self, branch: str) -> None:
        """
        Display warning about invalid branch pattern.

        Args:
            branch: Branch name
        """
        self.logger.warning(
            "Branch does not follow recommended pattern",
            extra={"branch": branch}
        )

        print()
        print(f"AVISO: Branch '{branch}' não segue padrão recomendado.")
        print(f"Prefixos válidos: {', '.join(self.VALID_PREFIXES)}")
        print()
        print("Considere usar auto-branch.py para criar branch corretamente.")
        print()

    def validate(self) -> bool:
        """
        Validate current branch.

        Returns:
            True if validation passes (can continue), False otherwise
        """
        branch = self.get_current_branch()

        if not branch:
            # Can't detect branch, allow operation
            return True

        self.logger.debug("Checking branch", extra={"branch": branch})

        # Check if protected branch
        if self.is_protected_branch(branch):
            self.show_protected_branch_warning(branch)
            # Return True to not block, just warn
            # Claude Code will see BRANCH_REQUIRED=true output
            return True

        # Check if follows valid pattern
        if not self.follows_valid_pattern(branch):
            self.show_pattern_warning(branch)
            # Warning only, don't block
            return True

        self.logger.debug(
            "Branch follows valid pattern",
            extra={"branch": branch}
        )

        return True

    def execute(self) -> int:
        """
        Execute branch enforcement check.

        Returns:
            0 always (warnings only, never block)
        """
        self.validate()
        return 0


def main() -> int:
    """
    Main entry point for branch enforcement hook.

    Returns:
        Exit code (0 for success)
    """
    enforcer = BranchEnforcer()

    try:
        return enforcer.execute()
    except Exception as e:
        enforcer.logger.warning(
            f"Branch check failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Don't block on errors
        return 0


if __name__ == "__main__":
    sys.exit(main())
