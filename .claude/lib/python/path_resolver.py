#!/usr/bin/env python3
"""
Path Resolver - System Integration Connector

Resolves project output paths from settings.json configuration.
This is a SYSTEM-LEVEL INTEGRATION (permitted by Natural Language First policy).

Usage:
    # From agent markdown (natural language):
    "Use Bash to resolve project directory: python3 .claude/lib/python/path_resolver.py --project-dir"

    # From Python scripts:
    from path_resolver import get_project_dir, get_framework_dir

    project_dir = get_project_dir()  # Returns: /path/to/repo/.project
    framework_dir = get_framework_dir()  # Returns: /path/to/repo/.agentic_sdlc

Resolution Priority:
1. settings.json → sdlc.output.project_artifacts_dir (default: ".project")
2. settings.json → sdlc.output.framework_artifacts_dir (default: ".agentic_sdlc")
3. Fallback: ".project" and ".agentic_sdlc"

Author: SDLC Agêntico Framework
Version: 1.0.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional


def find_repo_root() -> Path:
    """
    Find repository root by looking for .claude directory.

    Returns:
        Path: Absolute path to repository root

    Raises:
        FileNotFoundError: If .claude directory not found
    """
    current = Path.cwd().resolve()

    # Walk up directory tree
    for parent in [current] + list(current.parents):
        claude_dir = parent / ".claude"
        if claude_dir.exists() and claude_dir.is_dir():
            return parent

    raise FileNotFoundError(
        "Repository root not found. "
        "Make sure you're running from within a repository with .claude/ directory."
    )


def load_settings() -> Dict:
    """
    Load settings.json from repository root.

    Returns:
        dict: Parsed settings.json

    Raises:
        FileNotFoundError: If settings.json not found
        json.JSONDecodeError: If settings.json is invalid
    """
    repo_root = find_repo_root()
    settings_path = repo_root / ".claude/settings.json"

    if not settings_path.exists():
        raise FileNotFoundError(
            f"settings.json not found at {settings_path}. "
            "Make sure the repository is properly initialized."
        )

    with settings_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_project_dir() -> Path:
    """
    Get project artifacts directory from settings.json.

    Priority:
    1. settings.json → sdlc.output.project_artifacts_dir
    2. Fallback: ".project"

    Returns:
        Path: Absolute path to project artifacts directory

    Example:
        >>> project_dir = get_project_dir()
        >>> print(project_dir)
        /home/user/repo/.project
    """
    try:
        repo_root = find_repo_root()
        settings = load_settings()

        # Extract from settings.json
        project_dir = (
            settings
            .get('sdlc', {})
            .get('output', {})
            .get('project_artifacts_dir', '.project')
        )

        # Convert to absolute path
        return (repo_root / project_dir).resolve()

    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to default
        print(f"Warning: {e}. Using fallback '.project'", file=sys.stderr)
        repo_root = find_repo_root()
        return (repo_root / ".project").resolve()


def get_framework_dir() -> Path:
    """
    Get framework artifacts directory from settings.json.

    Priority:
    1. settings.json → sdlc.output.framework_artifacts_dir
    2. Fallback: ".agentic_sdlc"

    Returns:
        Path: Absolute path to framework artifacts directory

    Example:
        >>> framework_dir = get_framework_dir()
        >>> print(framework_dir)
        /home/user/repo/.agentic_sdlc
    """
    try:
        repo_root = find_repo_root()
        settings = load_settings()

        # Extract from settings.json
        framework_dir = (
            settings
            .get('sdlc', {})
            .get('output', {})
            .get('framework_artifacts_dir', '.agentic_sdlc')
        )

        # Convert to absolute path
        return (repo_root / framework_dir).resolve()

    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to default
        print(f"Warning: {e}. Using fallback '.agentic_sdlc'", file=sys.stderr)
        repo_root = find_repo_root()
        return (repo_root / ".agentic_sdlc").resolve()


def ensure_directory_exists(path: Path) -> None:
    """
    Ensure directory exists, create if missing.

    Args:
        path: Directory path to create
    """
    path.mkdir(parents=True, exist_ok=True)


def main():
    """
    CLI interface for path resolution.

    Usage:
        python3 path_resolver.py --project-dir
        python3 path_resolver.py --framework-dir
        python3 path_resolver.py --repo-root
        python3 path_resolver.py --validate
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Resolve project and framework paths from settings.json"
    )
    parser.add_argument(
        '--project-dir',
        action='store_true',
        help='Print project artifacts directory'
    )
    parser.add_argument(
        '--framework-dir',
        action='store_true',
        help='Print framework artifacts directory'
    )
    parser.add_argument(
        '--repo-root',
        action='store_true',
        help='Print repository root'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate paths and settings.json'
    )
    parser.add_argument(
        '--ensure',
        action='store_true',
        help='Ensure directories exist (create if missing)'
    )

    args = parser.parse_args()

    try:
        if args.project_dir:
            project_dir = get_project_dir()
            if args.ensure:
                ensure_directory_exists(project_dir)
            print(project_dir)

        elif args.framework_dir:
            framework_dir = get_framework_dir()
            if args.ensure:
                ensure_directory_exists(framework_dir)
            print(framework_dir)

        elif args.repo_root:
            repo_root = find_repo_root()
            print(repo_root)

        elif args.validate:
            repo_root = find_repo_root()
            settings = load_settings()
            project_dir = get_project_dir()
            framework_dir = get_framework_dir()

            print(f"✓ Repository root: {repo_root}")
            print(f"✓ settings.json: {repo_root / '.claude/settings.json'}")
            print(f"✓ Project dir: {project_dir}")
            print(f"✓ Framework dir: {framework_dir}")

            if project_dir.exists():
                print(f"✓ Project dir exists")
            else:
                print(f"⚠ Project dir does not exist (will be created on first use)")

            if framework_dir.exists():
                print(f"✓ Framework dir exists")
            else:
                print(f"⚠ Framework dir does not exist")
        else:
            parser.print_help()

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
