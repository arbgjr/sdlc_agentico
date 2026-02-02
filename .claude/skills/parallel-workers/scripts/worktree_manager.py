#!/usr/bin/env python3
"""
Script: Worktree Manager

Manages git worktrees for parallel workers.
Adapted from claude-orchestrator's wt.sh for cross-platform compatibility.

Usage:
    python3 worktree_manager.py create <project> <task-id> <base-branch>
    python3 worktree_manager.py list <project>
    python3 worktree_manager.py remove <project> <task-id>
    python3 worktree_manager.py prune
    python3 worktree_manager.py status <project> <task-id>
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Tuple, List, Optional

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent.parent.parent / "lib" / "python"
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
            print(f"[INFO] {msg}")

        def error(self, msg, **kwargs):
            print(f"[ERROR] {msg}", file=sys.stderr)

        def warning(self, msg, **kwargs):
            print(f"[WARN] {msg}")

        def debug(self, msg, **kwargs):
            pass

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class WorktreeManager:
    """Manages git worktrees for parallel workers."""

    def __init__(self):
        self.logger = get_logger(__name__, skill="parallel-workers", phase=5)
        self.worktree_base = Path.home() / ".worktrees"
        self.repo_root = Path.cwd()

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> Tuple[int, str, str]:
        """Run command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.repo_root,
                check=False,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return 1, "", str(e)

    def create(self, project: str, task_id: str, base_branch: str) -> Optional[str]:
        """
        Create new worktree.

        Args:
            project: Project name
            task_id: Task identifier
            base_branch: Base branch to create from

        Returns:
            Worktree path or None if failed
        """
        worktree_path = self.worktree_base / project / task_id
        branch_name = f"feature/{task_id}"

        self.logger.info(
            "Creating worktree",
            extra={
                "project": project,
                "task_id": task_id,
                "base_branch": base_branch,
                "worktree_path": str(worktree_path),
            }
        )

        # Create base directory
        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if worktree already exists
        if worktree_path.exists():
            self.logger.error(
                "Worktree already exists",
                extra={"path": str(worktree_path)}
            )
            return None

        # Create worktree and branch
        code, stdout, stderr = self.run_command([
            "git", "worktree", "add",
            "-b", branch_name,
            str(worktree_path),
            base_branch
        ])

        if code == 0:
            self.logger.info(
                "Worktree created successfully",
                extra={"branch": branch_name, "path": str(worktree_path)}
            )
            print(str(worktree_path))
            return str(worktree_path)
        else:
            self.logger.error(
                "Failed to create worktree",
                extra={"branch": branch_name, "base": base_branch, "error": stderr}
            )
            return None

    def list(self, project: str) -> List[str]:
        """
        List worktrees for project.

        Args:
            project: Project name

        Returns:
            List of worktree paths
        """
        project_path = self.worktree_base / project

        self.logger.debug("Listing worktrees", extra={"project": project})

        if not project_path.exists():
            self.logger.warning(
                "No worktrees found for project",
                extra={"project": project}
            )
            return []

        # Parse git worktree list
        code, stdout, _ = self.run_command(["git", "worktree", "list", "--porcelain"])
        if code != 0:
            return []

        worktrees = []
        for line in stdout.split("\n"):
            if line.startswith("worktree "):
                path = line[9:]  # Remove "worktree " prefix
                if path.startswith(str(project_path)):
                    worktrees.append(path)
                    print(path)

        return worktrees

    def remove(self, project: str, task_id: str, force: bool = False) -> bool:
        """
        Remove worktree.

        Args:
            project: Project name
            task_id: Task identifier
            force: Force removal even with uncommitted changes

        Returns:
            True if successful
        """
        worktree_path = self.worktree_base / project / task_id

        self.logger.info(
            "Removing worktree",
            extra={"project": project, "task_id": task_id, "path": str(worktree_path)}
        )

        if not worktree_path.exists():
            self.logger.warning("Worktree not found", extra={"path": str(worktree_path)})
            return True  # Already removed

        # Check for uncommitted changes (if not forcing)
        if not force:
            code, stdout, _ = self.run_command(
                ["git", "status", "--porcelain"],
                cwd=worktree_path
            )
            if stdout:
                self.logger.warning(
                    "Worktree has uncommitted changes",
                    extra={"path": str(worktree_path)}
                )
                response = input("Force remove? (y/N): ").strip().lower()
                if response != "y":
                    self.logger.info("Removal cancelled by user")
                    return False

        # Remove worktree
        code, stdout, stderr = self.run_command([
            "git", "worktree", "remove",
            str(worktree_path),
            "--force"
        ])

        if code == 0:
            self.logger.info(
                "Worktree removed successfully",
                extra={"path": str(worktree_path)}
            )
            return True
        else:
            self.logger.error(
                "Failed to remove worktree",
                extra={"path": str(worktree_path), "error": stderr}
            )
            return False

    def prune(self) -> bool:
        """
        Prune stale worktrees.

        Returns:
            True if successful
        """
        self.logger.info("Pruning stale worktrees")

        code, stdout, stderr = self.run_command(["git", "worktree", "prune", "--verbose"])

        if code == 0:
            self.logger.info("Worktrees pruned successfully")
            if stdout:
                print(stdout)
            return True
        else:
            self.logger.error("Failed to prune worktrees", extra={"error": stderr})
            return False

    def status(self, project: str, task_id: str) -> Optional[dict]:
        """
        Get worktree status.

        Args:
            project: Project name
            task_id: Task identifier

        Returns:
            Status dictionary or None if not found
        """
        worktree_path = self.worktree_base / project / task_id

        if not worktree_path.exists():
            self.logger.error("Worktree not found", extra={"path": str(worktree_path)})
            return None

        self.logger.debug("Checking worktree status", extra={"path": str(worktree_path)})

        # Get branch
        code, branch, _ = self.run_command(
            ["git", "branch", "--show-current"],
            cwd=worktree_path
        )
        if code != 0:
            branch = "unknown"

        # Get commit
        code, commit, _ = self.run_command(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=worktree_path
        )
        if code != 0:
            commit = "unknown"

        # Get uncommitted changes
        code, status_output, _ = self.run_command(
            ["git", "status", "--porcelain"],
            cwd=worktree_path
        )
        uncommitted_changes = len(status_output.split("\n")) if status_output else 0

        status_dict = {
            "path": str(worktree_path),
            "branch": branch,
            "commit": commit,
            "uncommitted_changes": uncommitted_changes,
            "exists": True
        }

        print(json.dumps(status_dict, indent=2))
        return status_dict


def usage():
    """Print usage information."""
    print("""Usage: worktree_manager.py <command> [args]

Commands:
  create <project> <task-id> <base-branch>  Create new worktree
  list <project>                             List active worktrees
  remove <project> <task-id>                 Remove worktree
  prune                                      Remove stale worktrees
  status <project> <task-id>                Check worktree status

Examples:
  worktree_manager.py create my-project task-001 main
  worktree_manager.py list my-project
  worktree_manager.py remove my-project task-001
  worktree_manager.py prune

Environment:
  WORKTREE_BASE    Base directory for worktrees (default: ~/.worktrees)
""", file=sys.stderr)


def main() -> int:
    """Main entry point for worktree_manager script."""
    if len(sys.argv) < 2:
        usage()
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    manager = WorktreeManager()

    try:
        if command == "create":
            if len(args) != 3:
                usage()
                return 1
            result = manager.create(args[0], args[1], args[2])
            return 0 if result else 1

        elif command == "list":
            if len(args) != 1:
                usage()
                return 1
            manager.list(args[0])
            return 0

        elif command == "remove":
            if len(args) != 2:
                usage()
                return 1
            result = manager.remove(args[0], args[1])
            return 0 if result else 1

        elif command == "prune":
            result = manager.prune()
            return 0 if result else 1

        elif command == "status":
            if len(args) != 2:
                usage()
                return 1
            result = manager.status(args[0], args[1])
            return 0 if result else 1

        else:
            manager.logger.error("Unknown command", extra={"command": command})
            usage()
            return 1

    except Exception as e:
        manager.logger.error(
            f"Operation failed: {e}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
