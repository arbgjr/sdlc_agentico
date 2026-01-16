#!/usr/bin/env python3
"""
RAG Curator - Index ADRs
Indexes ADRs from project decisions to corpus RAG.
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone


def index_adrs(project_id: str = None, all_projects: bool = False) -> int:
    """
    Index ADRs from projects to corpus.

    Args:
        project_id: Specific project ID to index
        all_projects: Index all projects

    Returns:
        Number of ADRs indexed
    """
    project_root = Path.cwd()
    corpus_decisions = project_root / ".agentic_sdlc" / "corpus" / "nodes" / "decisions"
    projects_dir = project_root / ".agentic_sdlc" / "projects"

    # Ensure corpus directory exists
    corpus_decisions.mkdir(parents=True, exist_ok=True)

    indexed_count = 0

    # Find projects to process
    if all_projects:
        project_dirs = [p for p in projects_dir.iterdir() if p.is_dir() and not p.name.startswith('.')]
    elif project_id:
        project_dirs = [projects_dir / project_id]
    else:
        # Try to find current project from current.json symlink
        current_json = projects_dir / "current.json"
        if current_json.exists():
            import json
            current_data = json.loads(current_json.read_text())
            project_id = current_data.get("project_id")
            if project_id:
                project_dirs = [projects_dir / project_id]
            else:
                print("Error: Could not determine current project", file=sys.stderr)
                return 0
        else:
            print("Error: No project specified and current.json not found", file=sys.stderr)
            return 0

    # Process each project
    for project_dir in project_dirs:
        if not project_dir.exists():
            print(f"Warning: Project directory not found: {project_dir}", file=sys.stderr)
            continue

        decisions_dir = project_dir / "decisions"
        if not decisions_dir.exists():
            continue

        # Copy each ADR
        for adr_file in decisions_dir.glob("adr-*.yml"):
            dest_file = corpus_decisions / adr_file.name

            # Skip if already exists and is newer
            if dest_file.exists():
                if dest_file.stat().st_mtime >= adr_file.stat().st_mtime:
                    continue

            # Copy ADR to corpus
            shutil.copy2(adr_file, dest_file)
            indexed_count += 1
            print(f"✅ Indexed: {adr_file.name}")

    if indexed_count > 0:
        print(f"\n✅ Indexed {indexed_count} ADR(s) to corpus")
    else:
        print("ℹ️  No new ADRs to index")

    return indexed_count


def main():
    parser = argparse.ArgumentParser(description="Index ADRs to corpus RAG")
    parser.add_argument("--project-id", help="Specific project ID to index")
    parser.add_argument("--all", action="store_true", help="Index all projects")

    args = parser.parse_args()

    try:
        count = index_adrs(project_id=args.project_id, all_projects=args.all)
        sys.exit(0 if count >= 0 else 1)
    except Exception as e:
        print(f"❌ Error indexing ADRs: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
