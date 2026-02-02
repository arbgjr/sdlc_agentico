#!/usr/bin/env python3
"""
Hook: Auto Migrate

Automatically migrates artifacts from .claude/memory to .agentic_sdlc structure.
Runs once per session on UserPromptSubmit hook.
"""

import sys
import os
import shutil
import json
import yaml
from typing import Optional, List, Tuple
from pathlib import Path
from datetime import datetime

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


class ArtifactMigrator:
    """Migrates artifacts from .claude/memory to .agentic_sdlc structure."""

    def __init__(self):
        self.logger = get_logger(__name__, skill="memory-manager")
        self.repo_root = Path.cwd()
        self.migrated_count = 0

        # Marker file to prevent repeated migrations
        today = datetime.now().strftime("%Y%m%d")
        self.marker_file = Path(f"/tmp/.sdlc-migrated-{today}")

    def should_skip_migration(self) -> Tuple[bool, str]:
        """
        Check if migration should be skipped.

        Returns:
            Tuple of (should_skip: bool, reason: str)
        """
        # Check if already migrated today
        if self.marker_file.exists():
            self.logger.debug("Migration already done today, skipping")
            return True, "Already migrated today"

        # Check if in SDLC Agêntico repository
        settings_file = self.repo_root / ".claude" / "settings.json"
        if not settings_file.exists():
            self.logger.debug("Not an SDLC Agêntico repository, skipping")
            return True, "Not an SDLC repository"

        # Check if .claude/memory exists
        memory_dir = self.repo_root / ".claude" / "memory"
        if not memory_dir.exists():
            self.logger.debug("No .claude/memory directory found")
            self.marker_file.touch()
            return True, "No memory directory"

        # Check if .claude/memory has files
        memory_files = list(memory_dir.rglob("*"))
        file_count = sum(1 for f in memory_files if f.is_file())

        if file_count == 0:
            self.logger.debug("No files in .claude/memory")
            self.marker_file.touch()
            return True, "No files to migrate"

        return False, ""

    def get_project_id(self) -> str:
        """
        Get current project ID from project.yml.

        Returns:
            Project ID or 'default' if not found
        """
        project_file = self.repo_root / ".claude" / "memory" / "project.yml"

        if not project_file.exists():
            return "default"

        try:
            with open(project_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                project_id = data.get("id", "default")
                return project_id if project_id else "default"
        except Exception as e:
            self.logger.warning(
                f"Could not read project.yml: {e}",
                extra={"error": str(e)}
            )
            return "default"

    def ensure_destination_structure(self, project_id: str) -> Path:
        """
        Ensure destination directory structure exists.

        Args:
            project_id: Project identifier

        Returns:
            Path to project destination
        """
        agentic_dir = self.repo_root / ".agentic_sdlc"

        if not agentic_dir.exists():
            self.logger.info("Creating .agentic_sdlc directory structure")
            agentic_dir.mkdir()

            # Create subdirectories
            for subdir in ["projects", "references", "templates", "corpus", "sessions"]:
                (agentic_dir / subdir).mkdir(exist_ok=True)

        # Create project-specific structure
        dest = agentic_dir / "projects" / project_id

        for subdir in ["phases", "decisions", "specs", "security", "docs"]:
            (dest / subdir).mkdir(parents=True, exist_ok=True)

        # Create corpus structure for learnings
        corpus_learnings = self.repo_root / ".project" / "corpus" / "learnings"
        corpus_learnings.mkdir(parents=True, exist_ok=True)

        return dest

    def migrate_directory(
        self,
        source_dir: Path,
        dest_dir: Path,
        pattern: str = "*"
    ) -> int:
        """
        Migrate files from source to destination.

        Args:
            source_dir: Source directory
            dest_dir: Destination directory
            pattern: File pattern to match

        Returns:
            Number of files migrated
        """
        if not source_dir.exists():
            return 0

        count = 0
        for source_file in source_dir.glob(pattern):
            if not source_file.is_file():
                continue

            dest_file = dest_dir / source_file.name

            # Only copy if destination doesn't exist
            if not dest_file.exists():
                shutil.copy2(source_file, dest_file)
                self.logger.debug(
                    f"Migrated {source_dir.name} file",
                    extra={"file": source_file.name}
                )
                count += 1

        return count

    def migrate_artifacts(self, dest: Path) -> int:
        """
        Migrate all artifacts to destination.

        Args:
            dest: Destination directory

        Returns:
            Total number of files migrated
        """
        total = 0
        memory_dir = self.repo_root / ".claude" / "memory"

        # Migrate decisions/
        decisions_src = memory_dir / "decisions"
        if decisions_src.exists():
            count = self.migrate_directory(
                decisions_src,
                dest / "decisions",
                "*.yml"
            )
            total += count

        # Migrate context/ -> phases/
        context_src = memory_dir / "context"
        if context_src.exists():
            count = self.migrate_directory(
                context_src,
                dest / "phases",
                "*"
            )
            total += count

        # Migrate learnings/ -> corpus/learnings/
        learnings_src = memory_dir / "learnings"
        learnings_dest = self.repo_root / ".project" / "corpus" / "learnings"
        if learnings_src.exists():
            count = self.migrate_directory(
                learnings_src,
                learnings_dest,
                "*"
            )
            total += count

        # Migrate project.yml -> manifest.yml
        project_src = memory_dir / "project.yml"
        manifest_dest = dest / "manifest.yml"

        if project_src.exists() and not manifest_dest.exists():
            shutil.copy2(project_src, manifest_dest)
            self.logger.debug("Migrated project manifest")
            total += 1

        return total

    def execute(self) -> int:
        """
        Execute migration.

        Returns:
            0 always (never block)
        """
        # Check if should skip
        should_skip, reason = self.should_skip_migration()
        if should_skip:
            return 0

        # Get project ID
        project_id = self.get_project_id()

        # Count files to migrate
        memory_dir = self.repo_root / ".claude" / "memory"
        memory_files = list(memory_dir.rglob("*"))
        file_count = sum(1 for f in memory_files if f.is_file())

        self.logger.info(
            "Starting migration",
            extra={"files_to_migrate": file_count}
        )

        # Ensure destination structure
        dest = self.ensure_destination_structure(project_id)

        self.logger.debug(
            "Migration destination",
            extra={"project_id": project_id, "dest": str(dest)}
        )

        # Migrate artifacts
        migrated = self.migrate_artifacts(dest)

        # Create marker
        self.marker_file.touch()

        # Report results
        if migrated > 0:
            self.logger.info(
                "Migration completed",
                extra={
                    "files_migrated": migrated,
                    "destination": str(dest)
                }
            )

            print()
            print("AUTO_MIGRATED=true")
            print(f"MIGRATED_FILES={migrated}")
            print(f"MIGRATION_DEST={dest}")
            print()
            print(f"INFO: {migrated} arquivo(s) migrado(s) de .claude/memory para {dest}")
            print("Considere remover .claude/memory quando estiver seguro.")
            print()
        else:
            self.logger.debug("No files needed migration")

        return 0


def main() -> int:
    """
    Main entry point for auto-migrate hook.

    Returns:
        Exit code (0 always)
    """
    migrator = ArtifactMigrator()

    try:
        return migrator.execute()
    except Exception as e:
        migrator.logger.warning(
            f"Migration failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Don't block on errors
        return 0


if __name__ == "__main__":
    sys.exit(main())
