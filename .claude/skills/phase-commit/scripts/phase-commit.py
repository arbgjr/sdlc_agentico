#!/usr/bin/env python3
"""
Script: Phase Commit

Commits and pushes artifacts at the end of each SDLC phase.

Usage:
    python3 phase-commit.py [project_id] [phase] [message]
"""

import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Optional

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
            self.logger.info(f"{msg} {kwargs}")

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def error(self, msg, **kwargs):
            self.logger.error(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class PhaseCommitter:
    """Commits SDLC phase artifacts."""

    # Phase names
    PHASE_NAMES = [
        "Preparation",
        "Discovery",
        "Requirements",
        "Architecture",
        "Planning",
        "Implementation",
        "Quality",
        "Release",
        "Operations",
    ]

    # Commit type mapping
    COMMIT_TYPES = {
        0: "docs",
        1: "docs",
        2: "feat",
        3: "feat",
        4: "docs",
        5: "feat",
        6: "test",
        7: "chore",
        8: "docs",
    }

    def __init__(
        self,
        project_id: Optional[str] = None,
        phase: Optional[int] = None,
        message: Optional[str] = None,
    ):
        self.project_id = project_id
        self.phase = phase
        self.message = message
        self.logger = get_logger(__name__, skill="phase-commit", phase=phase)
        self.repo_root = Path.cwd()

    def run_command(
        self, cmd: list[str], capture_output: bool = True, check: bool = False
    ) -> Tuple[int, str, str]:
        """
        Run command and return (returncode, stdout, stderr).

        Args:
            cmd: Command to run
            capture_output: Whether to capture output
            check: Whether to raise on error

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""
        except Exception as e:
            self.logger.error(f"Command failed: {' '.join(cmd)}", extra={"error": str(e)})
            return 1, "", str(e)

    def detect_phase(self) -> Optional[int]:
        """
        Detect current phase from manifest files.

        Returns:
            Phase number or None if not found
        """
        # Try legacy location first
        legacy_file = self.repo_root / ".claude" / "memory" / "project.yml"
        if legacy_file.exists():
            try:
                with open(legacy_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("current_phase:"):
                            phase_str = line.split(":")[1].strip()
                            return int(phase_str)
            except Exception as e:
                self.logger.debug(f"Failed to read legacy project.yml: {e}")

        # Try new location
        current_project_file = self.repo_root / ".agentic_sdlc" / ".current-project"
        if current_project_file.exists():
            try:
                with open(current_project_file, "r", encoding="utf-8") as f:
                    current_project = f.read().strip()

                manifest_file = (
                    self.repo_root
                    / ".agentic_sdlc"
                    / "projects"
                    / current_project
                    / "manifest.yml"
                )
                if manifest_file.exists():
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("current_phase:"):
                                phase_str = line.split(":")[1].strip()
                                return int(phase_str)
            except Exception as e:
                self.logger.debug(f"Failed to read manifest: {e}")

        return None

    def has_changes(self) -> bool:
        """
        Check if there are changes to commit.

        Returns:
            True if there are changes
        """
        # Check unstaged changes
        code, _, _ = self.run_command(["git", "diff", "--quiet"])
        has_unstaged = code != 0

        # Check staged changes
        code, _, _ = self.run_command(["git", "diff", "--cached", "--quiet"])
        has_staged = code != 0

        return has_unstaged or has_staged

    def get_staged_files(self) -> Tuple[list[str], int]:
        """
        Get list of staged files.

        Returns:
            Tuple of (files list, total count)
        """
        code, stdout, _ = self.run_command(
            ["git", "diff", "--cached", "--name-only"]
        )
        if code != 0 or not stdout:
            return [], 0

        files = stdout.split("\n")
        return files[:20], len(files)  # First 20 files

    def create_commit(self, commit_type: str, phase_name: str, files: list[str], file_count: int) -> Optional[str]:
        """
        Create git commit.

        Args:
            commit_type: Type of commit (docs, feat, test, chore)
            phase_name: Name of the phase
            files: List of modified files
            file_count: Total file count

        Returns:
            Commit hash or None if failed
        """
        message = self.message or f"artefatos da fase {phase_name}"

        files_list = "\n".join(files)

        commit_msg = f"""{commit_type}(phase-{self.phase}): {message}

Fase: {phase_name}
Projeto: {self.project_id or 'unknown'}
Arquivos: {file_count}

Artefatos criados/modificados:
{files_list}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

        code, _, stderr = self.run_command(["git", "commit", "-m", commit_msg])
        if code != 0:
            self.logger.error(f"Failed to create commit: {stderr}")
            return None

        # Get commit hash
        code, stdout, _ = self.run_command(["git", "rev-parse", "--short", "HEAD"])
        if code == 0:
            return stdout
        return None

    def push_to_remote(self) -> bool:
        """
        Push commit to remote repository.

        Returns:
            True if successful
        """
        # Check if remote exists
        code, _, _ = self.run_command(["git", "remote", "get-url", "origin"])
        if code != 0:
            self.logger.warning("No remote configured", extra={"skip_push": True})
            print("⚠ Nenhum remote configurado. Commit local criado apenas.")
            return True  # Not an error

        # Get current branch
        code, branch, _ = self.run_command(["git", "branch", "--show-current"])
        if code != 0:
            self.logger.error("Failed to get current branch")
            return False

        self.logger.info(f"Pushing to remote", extra={"branch": branch})

        # Check if branch has upstream
        code, _, _ = self.run_command(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
        )

        if code == 0:
            # Branch has upstream, just push
            code, _, stderr = self.run_command(["git", "push"])
            if code == 0:
                self.logger.info("Push successful", extra={"branch": branch})
                print(f"✓ Push realizado para origin/{branch}")
                return True
            else:
                self.logger.error(f"Push failed: {stderr}", extra={"branch": branch})
                print(f"✗ Erro ao fazer push. Execute manualmente: git push")
                return False
        else:
            # Branch doesn't have upstream, create it
            code, _, stderr = self.run_command(["git", "push", "-u", "origin", branch])
            if code == 0:
                self.logger.info("Push with upstream created", extra={"branch": branch})
                print(f"✓ Push realizado e upstream configurado: origin/{branch}")
                return True
            else:
                self.logger.error(f"Push with upstream failed: {stderr}", extra={"branch": branch})
                print(f"✗ Erro ao fazer push. Execute manualmente: git push -u origin {branch}")
                return False

    def update_manifest(self, commit_hash: str) -> bool:
        """
        Update manifest.yml with commit hash.

        Args:
            commit_hash: Commit hash to add

        Returns:
            True if successful
        """
        if not self.project_id:
            return True  # No project ID, skip

        manifest_file = (
            self.repo_root
            / ".agentic_sdlc"
            / "projects"
            / self.project_id
            / "manifest.yml"
        )

        if not manifest_file.exists():
            return True  # Manifest doesn't exist, skip

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Find phases_completed section
            phases_completed_idx = None
            for i, line in enumerate(lines):
                if "phases_completed:" in line:
                    phases_completed_idx = i
                    break

            if phases_completed_idx is None:
                return True  # No phases_completed section

            # Check if phase already in list
            for line in lines[phases_completed_idx + 1 :]:
                if f"  - phase: {self.phase}" in line:
                    return True  # Already recorded

            # Add phase entry
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            new_entry = f"""  - phase: {self.phase}
    commit: {commit_hash}
    completed_at: {timestamp}
"""
            lines.insert(phases_completed_idx + 1, new_entry)

            # Write back
            with open(manifest_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

            self.logger.info(
                "Manifest updated",
                extra={"phase": self.phase, "commit": commit_hash}
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to update manifest: {e}")
            return False

    def execute(self) -> int:
        """
        Execute phase commit.

        Returns:
            0 on success, 1 on failure
        """
        self.logger.info(
            "Starting phase-commit",
            extra={
                "project_id": self.project_id or "unknown",
                "phase": self.phase or "unknown"
            }
        )

        # Detect phase if not specified
        if self.phase is None:
            self.phase = self.detect_phase()
            if self.phase is None:
                self.logger.error("Could not determine current phase")
                print("✗ Não foi possível determinar a fase atual")
                return 1

        self.logger.debug(f"Phase detected: {self.phase}")

        # Validate phase
        if self.phase < 0 or self.phase >= len(self.PHASE_NAMES):
            self.logger.error(f"Invalid phase: {self.phase}")
            return 1

        phase_name = self.PHASE_NAMES[self.phase]
        commit_type = self.COMMIT_TYPES.get(self.phase, "chore")

        self.logger.info(
            f"Processing phase",
            extra={"phase_name": phase_name, "type": commit_type}
        )

        # Check for changes
        if not self.has_changes():
            self.logger.warning("No changes to commit", extra={"phase": self.phase})
            print(f"Nenhuma mudança para commitar na fase {self.phase} ({phase_name})")
            return 0

        # Stage all changes
        self.logger.debug("Adding files to staging")
        code, _, _ = self.run_command(["git", "add", "-A"])
        if code != 0:
            self.logger.error("Failed to stage changes")
            return 1

        # Check staged changes
        code, _, _ = self.run_command(["git", "diff", "--cached", "--quiet"])
        if code == 0:
            self.logger.warning("No changes staged", extra={"phase": self.phase})
            print("Nenhuma mudança staged para commitar")
            return 0

        # Get file list
        files, file_count = self.get_staged_files()
        self.logger.info("Files modified", extra={"count": file_count})

        # Create commit
        commit_hash = self.create_commit(commit_type, phase_name, files, file_count)
        if not commit_hash:
            return 1

        self.logger.info(
            "Commit created",
            extra={"hash": commit_hash, "files": file_count}
        )

        print()
        print("============================================")
        print(f"  ✓ Commit da Fase {self.phase} Criado")
        print("============================================")
        print(f"Fase: {phase_name}")
        print(f"Hash: {commit_hash}")
        print(f"Arquivos: {file_count}")
        print()

        # Push to remote
        if not self.push_to_remote():
            return 1

        # Update manifest
        self.update_manifest(commit_hash)

        print()
        print("============================================")
        print(f"  ✓ Fase {self.phase} ({phase_name}) Completa")
        print("============================================")
        print()

        self.logger.info(
            "Phase commit complete",
            extra={"phase": self.phase, "commit": commit_hash, "pushed": True}
        )

        return 0


def main() -> int:
    """
    Main entry point for phase-commit script.

    Usage:
        python3 phase-commit.py [project_id] [phase] [message]

    Returns:
        Exit code (0 on success, 1 on failure)
    """
    project_id = sys.argv[1] if len(sys.argv) > 1 else None
    phase_str = sys.argv[2] if len(sys.argv) > 2 else None
    message = sys.argv[3] if len(sys.argv) > 3 else None

    phase = int(phase_str) if phase_str else None

    committer = PhaseCommitter(project_id, phase, message)

    try:
        return committer.execute()
    except Exception as e:
        committer.logger.error(
            f"Phase commit failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
