#!/usr/bin/env python3
"""
Version comparison utilities for SDLC Agêntico auto-update system.

Handles semantic versioning comparison and current version detection.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
import yaml

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="version-checker", phase=0)


def get_current_version() -> str:
    """
    Get current version from .claude/VERSION file.

    Returns:
        str: Current version (e.g., "2.0.0")

    Raises:
        FileNotFoundError: If VERSION file doesn't exist
        ValueError: If VERSION file is invalid
    """
    version_file = Path(".claude/VERSION")

    if not version_file.exists():
        logger.error("VERSION file not found", extra={"path": str(version_file)})
        raise FileNotFoundError(f"VERSION file not found: {version_file}")

    try:
        with open(version_file) as f:
            data = yaml.safe_load(f)

        version = data.get("version")
        if not version:
            raise ValueError("Missing 'version' field in VERSION file")

        logger.debug("Current version loaded", extra={"version": version})
        return version

    except Exception as e:
        logger.error(f"Failed to parse VERSION file: {e}")
        raise ValueError(f"Invalid VERSION file: {e}")


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse semantic version string into tuple.

    Args:
        version_str: Version string (e.g., "2.1.0", "v2.1.0")

    Returns:
        Tuple[int, int, int]: (major, minor, patch)

    Raises:
        ValueError: If version string is invalid

    Examples:
        >>> parse_version("2.1.0")
        (2, 1, 0)
        >>> parse_version("v3.0.1")
        (3, 0, 1)
    """
    # Strip 'v' prefix if present
    clean_version = version_str.lstrip("v")

    # Match semantic version pattern
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"
    match = re.match(pattern, clean_version)

    if not match:
        raise ValueError(f"Invalid semantic version: {version_str}")

    major, minor, patch = match.groups()[:3]
    return (int(major), int(minor), int(patch))


def compare_versions(current: str, latest: str) -> Dict:
    """
    Compare two semantic versions.

    Args:
        current: Current version string
        latest: Latest version string

    Returns:
        dict: {
            "is_newer": bool,
            "current": str,
            "latest": str,
            "diff": {
                "major": int,  # Difference in major version
                "minor": int,  # Difference in minor version
                "patch": int   # Difference in patch version
            }
        }

    Examples:
        >>> compare_versions("2.0.0", "2.1.0")
        {'is_newer': True, 'current': '2.0.0', 'latest': '2.1.0', 'diff': {'major': 0, 'minor': 1, 'patch': 0}}
    """
    try:
        current_tuple = parse_version(current)
        latest_tuple = parse_version(latest)

        # Calculate differences
        diff = {
            "major": latest_tuple[0] - current_tuple[0],
            "minor": latest_tuple[1] - current_tuple[1],
            "patch": latest_tuple[2] - current_tuple[2]
        }

        # Determine if latest is newer
        is_newer = latest_tuple > current_tuple

        result = {
            "is_newer": is_newer,
            "current": current,
            "latest": latest,
            "diff": diff
        }

        logger.debug("Version comparison completed", extra={
            "current": current,
            "latest": latest,
            "is_newer": is_newer
        })

        return result

    except ValueError as e:
        logger.error(f"Version comparison failed: {e}")
        raise


def get_upgrade_type(diff: Dict) -> str:
    """
    Determine upgrade type from version diff.

    Args:
        diff: Version difference dict from compare_versions()

    Returns:
        str: "major", "minor", or "patch"

    Examples:
        >>> get_upgrade_type({"major": 1, "minor": 0, "patch": 0})
        'major'
        >>> get_upgrade_type({"major": 0, "minor": 2, "patch": 0})
        'minor'
    """
    if diff["major"] > 0:
        return "major"
    elif diff["minor"] > 0:
        return "minor"
    elif diff["patch"] > 0:
        return "patch"
    else:
        return "none"


if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Compare semantic versions")
    parser.add_argument("--current", help="Current version (default: from .claude/VERSION)")
    parser.add_argument("--latest", required=True, help="Latest version to compare")

    args = parser.parse_args()

    current = args.current or get_current_version()
    result = compare_versions(current, args.latest)

    print(f"Current: {result['current']}")
    print(f"Latest: {result['latest']}")
    print(f"Newer: {result['is_newer']}")
    print(f"Upgrade type: {get_upgrade_type(result['diff'])}")
