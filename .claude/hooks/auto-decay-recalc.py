#!/usr/bin/env python3
"""
Hook: Auto Decay Recalc

Automatically recalculates decay scores when corpus is modified.
Runs on UserPromptSubmit and checks if decay index needs updating.
Recalculates if index is stale (> 24 hours old) or doesn't exist.
"""

import sys
import subprocess
import time
from typing import Optional
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


class DecayRecalculator:
    """Recalculates corpus decay scores periodically."""

    # Configuration
    CORPUS_PATH = ".project/corpus"
    DECAY_INDEX = "decay_index.json"
    SCRIPT_PATH = ".claude/skills/decay-scoring/scripts/decay_calculator.py"

    # Recalculate if index is older than 24 hours
    MAX_AGE_HOURS = 24

    def __init__(self):
        self.logger = get_logger(__name__, skill="decay-scoring")
        self.repo_root = Path.cwd()

    def should_recalculate(self) -> tuple[bool, str]:
        """
        Check if decay scores should be recalculated.

        Returns:
            Tuple of (should_recalc: bool, reason: str)
        """
        # Check if decay calculator script exists
        script_path = self.repo_root / self.SCRIPT_PATH
        if not script_path.exists():
            self.logger.debug("Decay calculator script not found, skipping")
            return False, "Script not found"

        # Check if corpus nodes directory exists
        nodes_dir = self.repo_root / self.CORPUS_PATH / "nodes"
        if not nodes_dir.exists():
            self.logger.debug("Nodes directory not found")
            return False, "Nodes directory not found"

        # Count YAML files in nodes directory
        node_files = list(nodes_dir.rglob("*.yml"))
        if not node_files:
            self.logger.debug("No nodes to process")
            return False, "No nodes found"

        # Check decay index age
        decay_index = self.repo_root / self.CORPUS_PATH / self.DECAY_INDEX

        if decay_index.exists():
            # Get file modification time
            mtime = decay_index.stat().st_mtime
            age_seconds = time.time() - mtime
            age_hours = age_seconds / 3600

            self.logger.debug(
                "Decay index age",
                extra={"hours": int(age_hours)}
            )

            # Skip if index is recent
            if age_hours < self.MAX_AGE_HOURS:
                self.logger.debug("Index is recent, skipping recalculation")
                return False, "Index is recent"

        # Should recalculate
        return True, f"{len(node_files)} nodes to process"

    def recalculate(self) -> bool:
        """
        Recalculate decay scores.

        Returns:
            True if successful
        """
        script_path = self.repo_root / self.SCRIPT_PATH
        corpus_path = self.repo_root / self.CORPUS_PATH

        # Count nodes for logging
        nodes_dir = corpus_path / "nodes"
        node_count = len(list(nodes_dir.rglob("*.yml")))

        self.logger.info(
            "Recalculating decay scores",
            extra={"node_count": node_count}
        )

        # Run decay calculator
        cmd = [
            "python3",
            str(script_path),
            "--corpus",
            str(corpus_path),
            "--update-nodes"
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.debug("Decay scores updated successfully")
                return True
            else:
                self.logger.warning("Failed to update decay scores")
                return False

        except Exception as e:
            self.logger.warning(
                f"Failed to update decay scores: {str(e)}",
                extra={"error": str(e)}
            )
            return False

    def execute(self) -> int:
        """
        Execute decay recalculation check.

        Returns:
            0 always (never block)
        """
        # Check if should recalculate
        should_recalc, reason = self.should_recalculate()

        if should_recalc:
            self.recalculate()

        return 0


def main() -> int:
    """
    Main entry point for auto-decay-recalc hook.

    Returns:
        Exit code (0 always)
    """
    recalculator = DecayRecalculator()

    try:
        return recalculator.execute()
    except Exception as e:
        recalculator.logger.debug(
            f"Decay recalc failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Don't block on errors
        return 0


if __name__ == "__main__":
    sys.exit(main())
