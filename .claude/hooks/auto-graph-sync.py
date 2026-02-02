#!/usr/bin/env python3
"""
Hook: Auto Graph Sync

Automatically updates semantic graph when corpus node files are modified.
Triggered by PostToolUse hook on Write operations.

Environment:
    GRAPH_SYNC_ENABLED - Set to "false" to disable (default: true)
    GRAPH_SYNC_VERBOSE - Set to "true" for verbose output (default: false)
"""

import sys
import os
import subprocess
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


class GraphSyncer:
    """Synchronizes semantic graph with corpus node changes."""

    # Corpus paths to monitor
    CORPUS_NODES_PATH = ".project/corpus/nodes"
    LEGACY_DECISIONS_PATH = ".agentic_sdlc/decisions"
    LEGACY_PROJECTS_PATH = ".agentic_sdlc/projects"

    # Graph builder script
    GRAPH_BUILDER = ".claude/skills/graph-navigator/scripts/graph_builder.py"

    def __init__(self, modified_file: Optional[str] = None):
        self.logger = get_logger(__name__, skill="graph-navigator")
        self.repo_root = Path.cwd()
        self.modified_file = modified_file
        self.verbose = os.getenv("GRAPH_SYNC_VERBOSE", "false").lower() == "true"

    def is_sync_enabled(self) -> bool:
        """Check if graph sync is enabled."""
        enabled = os.getenv("GRAPH_SYNC_ENABLED", "true").lower()
        if enabled == "false":
            self.logger.debug("Graph sync disabled via environment")
            return False
        return True

    def is_corpus_node(self, file_path: str) -> bool:
        """
        Check if file is a corpus node.

        Args:
            file_path: Path to file

        Returns:
            True if file is a corpus node
        """
        # Check if file is in corpus nodes directory
        if self.CORPUS_NODES_PATH in file_path:
            return True

        # Check legacy paths
        if self.LEGACY_DECISIONS_PATH in file_path:
            return True

        if self.LEGACY_PROJECTS_PATH in file_path:
            if "/decisions/" in file_path or "/learnings/" in file_path:
                return True

        return False

    def is_yaml_file(self, file_path: str) -> bool:
        """
        Check if file is a YAML file.

        Args:
            file_path: Path to file

        Returns:
            True if YAML file
        """
        return file_path.endswith(".yml") or file_path.endswith(".yaml")

    def sync_graph(self, file_path: str) -> bool:
        """
        Sync graph for modified file.

        Args:
            file_path: Path to modified file

        Returns:
            True if sync succeeded
        """
        # Check if graph builder exists
        graph_builder = self.repo_root / self.GRAPH_BUILDER
        if not graph_builder.exists():
            self.logger.debug(
                "Graph builder not found",
                extra={"path": str(graph_builder)}
            )
            return False

        self.logger.info(
            "Updating graph for modified file",
            extra={"file": file_path}
        )

        # Run incremental update
        cmd = ["python3", str(graph_builder), "--incremental", file_path]

        try:
            if self.verbose:
                # Show output
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_root,
                    check=False
                )
                success = result.returncode == 0
            else:
                # Suppress output
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_root,
                    capture_output=True,
                    check=False
                )
                success = result.returncode == 0

            if success:
                self.logger.debug("Graph sync completed")
            else:
                self.logger.warning("Graph sync failed")

            return success

        except Exception as e:
            self.logger.warning(
                f"Graph sync failed with exception: {str(e)}",
                extra={"error": str(e)}
            )
            return False

    def execute(self) -> int:
        """
        Execute graph sync.

        Returns:
            0 always (never block)
        """
        # Check if sync is enabled
        if not self.is_sync_enabled():
            return 0

        # Check if file specified
        if not self.modified_file:
            self.logger.debug("No file specified")
            return 0

        self.logger.debug(
            "Checking file for graph sync",
            extra={"file": self.modified_file}
        )

        # Check if it's a corpus node YAML file
        if self.is_corpus_node(self.modified_file) and self.is_yaml_file(self.modified_file):
            self.sync_graph(self.modified_file)
        else:
            self.logger.debug(
                "File is not a corpus node",
                extra={"file": self.modified_file}
            )

        return 0


def main() -> int:
    """
    Main entry point for auto-graph-sync hook.

    Args:
        sys.argv[1]: Modified file path (optional)

    Returns:
        Exit code (0 always)
    """
    modified_file = sys.argv[1] if len(sys.argv) > 1 else None
    syncer = GraphSyncer(modified_file)

    try:
        return syncer.execute()
    except Exception as e:
        syncer.logger.debug(
            f"Graph sync failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Don't block on errors
        return 0


if __name__ == "__main__":
    sys.exit(main())
