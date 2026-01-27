#!/usr/bin/env python3
"""
Infrastructure Preserver - Preserves existing SDLC infrastructure during import
Ensures framework documentation, templates, and existing artifacts are not deleted.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set
import shutil

# Add logging utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class InfrastructurePreserver:
    """Preserve existing SDLC infrastructure during import"""

    # Files/directories that are part of framework infrastructure
    FRAMEWORK_PATTERNS = [
        # Templates
        "templates/adr-template.yml",
        "templates/odr-template.yml",
        "templates/spec-template.md",
        "templates/threat-model-template.yml",

        # Directory markers
        "**/.gitkeep",

        # Framework assets
        "logo.png",

        # Framework ADRs (not project-specific)
        "corpus/nodes/decisions/ADR-0[0-9][0-9]-*.yml",  # ADR-001 to ADR-099
        "corpus/nodes/learnings/LEARN-*.yml",
        "corpus/learnings/session-*.yml",

        # Project artifacts (preserve unless explicitly replaced)
        "projects/**/*.md",
        "sessions/**/*.md",
        "sessions/**/*.yml",
    ]

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.backup_dir = output_dir.parent / f".backup-{output_dir.name}"
        self.preserved_files: Set[Path] = set()

    def backup_existing_infrastructure(self) -> Dict[str, int]:
        """
        Backup existing infrastructure before import.

        Returns:
            Dict with backup statistics
        """
        if not self.output_dir.exists():
            logger.info("No existing infrastructure to preserve")
            return {"backed_up": 0, "skipped": 0}

        # Remove old backup if exists
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        self.backup_dir.mkdir(parents=True)
        backed_up = 0
        skipped = 0

        # Backup all existing files
        for item in self.output_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.output_dir)
                backup_path = self.backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, backup_path)
                backed_up += 1

                # Mark infrastructure files for restoration
                if self._is_infrastructure_file(relative_path):
                    self.preserved_files.add(relative_path)

        logger.info(
            f"Backed up {backed_up} files, {len(self.preserved_files)} marked for preservation",
            extra={"backed_up": backed_up, "preserved": len(self.preserved_files)}
        )

        return {
            "backed_up": backed_up,
            "preserved": len(self.preserved_files),
            "skipped": skipped
        }

    def restore_infrastructure(self) -> Dict[str, int]:
        """
        Restore preserved infrastructure files after import.

        Returns:
            Dict with restoration statistics
        """
        if not self.backup_dir.exists():
            logger.warning("No backup found to restore from")
            return {"restored": 0, "skipped": 0}

        restored = 0
        skipped = 0

        for relative_path in self.preserved_files:
            backup_path = self.backup_dir / relative_path
            target_path = self.output_dir / relative_path

            if not backup_path.exists():
                logger.warning(f"Backup file not found: {backup_path}")
                skipped += 1
                continue

            # Only restore if not already exists (import didn't create it)
            if not target_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, target_path)
                restored += 1
                logger.debug(f"Restored: {relative_path}")
            else:
                logger.debug(f"Skipped (exists): {relative_path}")
                skipped += 1

        # Cleanup backup
        shutil.rmtree(self.backup_dir)

        logger.info(
            f"Restored {restored} infrastructure files, skipped {skipped}",
            extra={"restored": restored, "skipped": skipped}
        )

        return {"restored": restored, "skipped": skipped}

    def _is_infrastructure_file(self, path: Path) -> bool:
        """Check if file is part of framework infrastructure"""
        path_str = str(path).replace('\\', '/')

        # Check exact matches
        for pattern in self.FRAMEWORK_PATTERNS:
            if pattern.endswith('/**/*') or '**' in pattern:
                # Glob pattern
                from fnmatch import fnmatch
                if fnmatch(path_str, pattern):
                    return True
            else:
                # Exact match
                if path_str == pattern or path_str.endswith(pattern):
                    return True

        # Additional checks
        # Preserve framework ADRs (ADR-001 to ADR-099)
        if path.parent.name == 'decisions' and path.name.startswith('ADR-'):
            adr_num = path.name.split('-')[1] if len(path.name.split('-')) > 1 else ''
            if adr_num.isdigit() and int(adr_num) < 100:
                return True

        # Preserve .gitkeep files
        if path.name == '.gitkeep':
            return True

        # Preserve logo
        if path.name == 'logo.png':
            return True

        return False


def main():
    """Test the infrastructure preserver"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="Output directory (.agentic_sdlc)")
    parser.add_argument("--backup", action="store_true", help="Backup infrastructure")
    parser.add_argument("--restore", action="store_true", help="Restore infrastructure")
    args = parser.parse_args()

    preserver = InfrastructurePreserver(Path(args.output_dir))

    if args.backup:
        result = preserver.backup_existing_infrastructure()
        print(f"Backed up: {result['backed_up']} files")
        print(f"Preserved: {result['preserved']} infrastructure files")

    if args.restore:
        result = preserver.restore_infrastructure()
        print(f"Restored: {result['restored']} files")


if __name__ == "__main__":
    main()
