#!/usr/bin/env python3
"""
Agent Session Isolation

Creates isolated working directories for agents to prevent context corruption
in parallel execution scenarios.

Based on OpenClaw pattern: Each agent operates with "its own session"

Usage:
    from agent_isolation import AgentSession

    session = AgentSession("code-author")
    session.create()
    corpus_dir = session.get_corpus_dir()
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import yaml


class AgentSession:
    """Manages isolated session for an agent"""

    def __init__(self, agent_id: str, base_dir: Optional[str] = None):
        """
        Initialize agent session.

        Args:
            agent_id: Unique identifier for the agent (e.g., "code-author-task-123")
            base_dir: Base directory for sessions (default: ~/.claude/agents)
        """
        self.agent_id = agent_id
        self.base_dir = Path(base_dir or Path.home() / ".claude" / "agents")
        self.session_dir = self.base_dir / agent_id

    def create(self, copy_corpus: bool = True, corpus_filter: Optional[str] = None) -> Path:
        """
        Create isolated session directory.

        Args:
            copy_corpus: Whether to copy relevant corpus nodes
            corpus_filter: Filter for corpus nodes (e.g., "phase:3", "type:decision")

        Returns:
            Path to session directory
        """
        # Create session directory structure
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.session_dir / "corpus").mkdir(exist_ok=True)
        (self.session_dir / "learnings").mkdir(exist_ok=True)
        (self.session_dir / "workspace").mkdir(exist_ok=True)

        # Copy filtered corpus if requested
        if copy_corpus:
            self._copy_filtered_corpus(corpus_filter)

        # Create session metadata
        self._create_metadata()

        return self.session_dir

    def _copy_filtered_corpus(self, corpus_filter: Optional[str] = None):
        """
        Copy relevant corpus nodes to session directory.

        Args:
            corpus_filter: Filter pattern (e.g., "phase:3" copies Phase 3 related nodes)
        """
        source_corpus = Path(".agentic_sdlc/corpus/nodes")
        target_corpus = self.session_dir / "corpus"

        if not source_corpus.exists():
            return

        # If no filter, copy recent decisions only (last 5)
        if not corpus_filter:
            decisions_dir = source_corpus / "decisions"
            if decisions_dir.exists():
                decision_files = sorted(
                    decisions_dir.glob("*.yml"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )[:5]

                target_decisions = target_corpus / "decisions"
                target_decisions.mkdir(parents=True, exist_ok=True)

                for file_path in decision_files:
                    shutil.copy2(file_path, target_decisions / file_path.name)
            return

        # TODO: Implement filter-based corpus copying
        # For now, copy all nodes matching filter criteria
        pass

    def _create_metadata(self):
        """Create session metadata file"""
        metadata = {
            "agent_id": self.agent_id,
            "session_dir": str(self.session_dir),
            "created_at": self._get_utc_timestamp(),
            "status": "active",
        }

        metadata_file = self.session_dir / "session.yml"
        with open(metadata_file, "w") as f:
            yaml.dump(metadata, f, default_flow_style=False)

    def _get_utc_timestamp(self) -> str:
        """Get current UTC timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_corpus_dir(self) -> Path:
        """Get path to session corpus directory"""
        return self.session_dir / "corpus"

    def get_workspace_dir(self) -> Path:
        """Get path to session workspace directory"""
        return self.session_dir / "workspace"

    def get_learnings_dir(self) -> Path:
        """Get path to session learnings directory"""
        return self.session_dir / "learnings"

    def merge_learnings(self, target_dir: str = ".agentic_sdlc/corpus/nodes/learnings"):
        """
        Merge session learnings back to main corpus.

        Args:
            target_dir: Target directory for merged learnings
        """
        learnings_dir = self.get_learnings_dir()
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        if not learnings_dir.exists():
            return []

        merged_files = []
        for learning_file in learnings_dir.glob("*.yml"):
            target_file = target_path / learning_file.name

            # If file exists, append unique ID to avoid collision
            if target_file.exists():
                stem = learning_file.stem
                suffix = learning_file.suffix
                target_file = target_path / f"{stem}-{self.agent_id}{suffix}"

            shutil.copy2(learning_file, target_file)
            merged_files.append(str(target_file))

        return merged_files

    def cleanup(self, merge_learnings: bool = True):
        """
        Clean up session directory.

        Args:
            merge_learnings: Whether to merge learnings before cleanup
        """
        if merge_learnings:
            self.merge_learnings()

        # Mark as completed
        metadata_file = self.session_dir / "session.yml"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = yaml.safe_load(f) or {}

            metadata["status"] = "completed"
            metadata["completed_at"] = self._get_utc_timestamp()

            with open(metadata_file, "w") as f:
                yaml.dump(metadata, f, default_flow_style=False)

        # Don't delete - keep for audit trail
        # Can be cleaned up manually later

    @staticmethod
    def list_active_sessions(base_dir: Optional[str] = None) -> List[str]:
        """
        List all active agent sessions.

        Returns:
            List of active session IDs
        """
        base_path = Path(base_dir or Path.home() / ".claude" / "agents")

        if not base_path.exists():
            return []

        active_sessions = []
        for session_dir in base_path.iterdir():
            if not session_dir.is_dir():
                continue

            metadata_file = session_dir / "session.yml"
            if not metadata_file.exists():
                continue

            with open(metadata_file, "r") as f:
                metadata = yaml.safe_load(f) or {}

            if metadata.get("status") == "active":
                active_sessions.append(str(session_dir.name))

        return active_sessions


def main():
    """CLI entrypoint for agent session management"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Agent Session Isolation Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create session
    create_parser = subparsers.add_parser("create", help="Create agent session")
    create_parser.add_argument("agent_id", help="Agent identifier")
    create_parser.add_argument("--no-corpus", action="store_true", help="Don't copy corpus")

    # List sessions
    list_parser = subparsers.add_parser("list", help="List active sessions")

    # Cleanup session
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup session")
    cleanup_parser.add_argument("agent_id", help="Agent identifier")
    cleanup_parser.add_argument("--no-merge", action="store_true", help="Don't merge learnings")

    args = parser.parse_args()

    if args.command == "create":
        session = AgentSession(args.agent_id)
        session_dir = session.create(copy_corpus=not args.no_corpus)
        print(f"✅ Created session: {session_dir}")
        print(f"   Corpus: {session.get_corpus_dir()}")
        print(f"   Workspace: {session.get_workspace_dir()}")

    elif args.command == "list":
        sessions = AgentSession.list_active_sessions()
        if sessions:
            print(f"📊 Active sessions ({len(sessions)}):")
            for session_id in sessions:
                print(f"   - {session_id}")
        else:
            print("No active sessions")

    elif args.command == "cleanup":
        session = AgentSession(args.agent_id)
        merged = session.cleanup(merge_learnings=not args.no_merge)
        print(f"✅ Cleaned up session: {args.agent_id}")
        if merged:
            print(f"   Merged learnings: {len(merged)} files")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
