#!/usr/bin/env python3
"""
validate-client-version.py - Validate client profile version compatibility
Version: 3.0.0
Hook: Can be called before workflow execution
Part of: Phase 2 - Orchestrator Refactoring (Multi-Client Architecture)

Cross-platform (Linux, macOS, Windows)
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add lib/python to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "python"))

try:
    from client_resolver import ClientResolver
except ImportError:
    print("[ERROR] client_resolver not available", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed (pip install pyyaml)", file=sys.stderr)
    sys.exit(1)


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse semantic version string to tuple.

    Args:
        version_str: Version string like "3.0.0"

    Returns:
        Tuple of (major, minor, patch)
    """
    parts = version_str.strip().lstrip("v").split(".")
    return (
        int(parts[0]) if len(parts) > 0 else 0,
        int(parts[1]) if len(parts) > 1 else 0,
        int(parts[2]) if len(parts) > 2 else 0,
    )


def is_version_compatible(
    framework_version: str,
    min_version: Optional[str],
    max_version: Optional[str],
) -> bool:
    """
    Check if framework version is compatible with client requirements.

    Args:
        framework_version: Current framework version
        min_version: Minimum required version (inclusive)
        max_version: Maximum supported version (inclusive)

    Returns:
        bool: True if compatible
    """
    fw_ver = parse_version(framework_version)

    if min_version:
        min_ver = parse_version(min_version)
        if fw_ver < min_ver:
            return False

    if max_version:
        max_ver = parse_version(max_version)
        if fw_ver > max_ver:
            return False

    return True


def get_framework_version() -> str:
    """Get current framework version from .claude/VERSION."""
    version_file = Path(".claude/VERSION")

    if not version_file.exists():
        # Fallback to settings.json or assume 3.0.0
        return "3.0.0"

    try:
        with open(version_file) as f:
            version_data = yaml.safe_load(f)
        return version_data.get("version", "3.0.0")
    except Exception:
        return "3.0.0"


def main():
    """Validate client version compatibility."""
    resolver = ClientResolver()

    # Detect active client
    client_id = resolver.detect_client()

    if client_id == "generic":
        # Generic profile is always compatible
        print(f"[INFO] Client: generic (base framework, always compatible)", file=sys.stderr)
        sys.exit(0)

    # Get framework version
    framework_version = get_framework_version()

    # Get client info
    client_info = resolver.get_client_info(client_id)

    if not client_info:
        print(f"[WARN] Could not load client info for: {client_id}", file=sys.stderr)
        sys.exit(0)  # Don't block workflow

    # Get version requirements
    framework_req = client_info.get("framework", {})
    min_version = framework_req.get("min_version")
    max_version = framework_req.get("max_version")

    # Check compatibility
    if not is_version_compatible(framework_version, min_version, max_version):
        print("", file=sys.stderr)
        print("❌ VERSION INCOMPATIBILITY DETECTED", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"Client Profile: {client_id}", file=sys.stderr)
        print(f"  Name: {client_info.get('name', 'N/A')}", file=sys.stderr)
        print(f"  Version: {client_info.get('version', 'N/A')}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Framework Requirements:", file=sys.stderr)
        if min_version:
            print(f"  Minimum: {min_version}", file=sys.stderr)
        if max_version:
            print(f"  Maximum: {max_version}", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"Current Framework: {framework_version}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Solutions:", file=sys.stderr)
        if parse_version(framework_version) < parse_version(min_version or "0.0.0"):
            print(f"  1. Update framework to v{min_version} or later", file=sys.stderr)
            print("     git pull origin main && git checkout <tag>", file=sys.stderr)
        elif parse_version(framework_version) > parse_version(max_version or "999.0.0"):
            print(f"  1. Update client profile to support v{framework_version}", file=sys.stderr)
            print(f"     Edit: clients/{client_id}/profile.yml", file=sys.stderr)
            print(f"     Set: max_version: \"{framework_version}\"", file=sys.stderr)
        print("  2. Switch to generic client: /set-client generic", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(1)

    # Compatible
    print(f"[INFO] Version check passed: {client_id} compatible with v{framework_version}", file=sys.stderr)
    print(f"  Client requirements: {min_version} <= v <= {max_version}", file=sys.stderr)


if __name__ == "__main__":
    main()
