#!/usr/bin/env python3
"""
Framework Path Resolution

Centralizes framework path resolution for sdlc-import.
Supports multiple installation modes:
- Development (relative path from script)
- User installation (~/.local/share/sdlc-agentico)
- System installation (/usr/local/share/sdlc-agentico)
- Custom via SDLC_FRAMEWORK_PATH env var

Usage:
    from framework_paths import get_template_dir, get_schema_dir

    template_path = get_template_dir() / "adr_template.yml"
    schema_path = get_schema_dir() / "adr_schema.json"
"""

import os
from pathlib import Path
from typing import Optional

# Global cache for framework root
_FRAMEWORK_ROOT: Optional[Path] = None


def get_framework_root() -> Path:
    """
    Get SDLC framework root directory (cached).

    Resolution order:
    1. SDLC_FRAMEWORK_PATH environment variable
    2. ~/.local/share/sdlc-agentico (user install)
    3. /usr/local/share/sdlc-agentico (system install)
    4. Relative to current script (development mode)

    Returns:
        Path: Absolute path to framework root

    Raises:
        FileNotFoundError: If framework cannot be located
    """
    global _FRAMEWORK_ROOT

    if _FRAMEWORK_ROOT is None:
        _FRAMEWORK_ROOT = _resolve_framework_root()

    return _FRAMEWORK_ROOT


def _resolve_framework_root() -> Path:
    """
    Resolve framework root with fallback chain.

    Returns:
        Path: Validated framework root path

    Raises:
        FileNotFoundError: If no valid framework found
    """
    # 1. Environment variable (highest priority)
    if env_path := os.getenv("SDLC_FRAMEWORK_PATH"):
        path = Path(env_path).resolve()
        if _validate_framework(path):
            return path
        raise FileNotFoundError(
            f"SDLC_FRAMEWORK_PATH set but invalid: {env_path}\n"
            f"Expected .agentic_sdlc/templates and .agentic_sdlc/schemas"
        )

    # 2. Standard user installation
    user_install = Path.home() / ".local/share/sdlc-agentico"
    if _validate_framework(user_install):
        return user_install

    # 3. Standard system installation
    system_install = Path("/usr/local/share/sdlc-agentico")
    if _validate_framework(system_install):
        return system_install

    # 4. Development mode (relative to current script)
    # This file is at: .claude/skills/sdlc-import/scripts/framework_paths.py
    # Framework root is 5 levels up (scripts → sdlc-import → skills → .claude → root)
    dev_path = Path(__file__).resolve().parent.parent.parent.parent.parent
    if _validate_framework(dev_path):
        return dev_path

    # No valid framework found
    raise FileNotFoundError(
        "SDLC framework not found in any standard location.\n"
        "Tried:\n"
        f"  - SDLC_FRAMEWORK_PATH env var: {os.getenv('SDLC_FRAMEWORK_PATH', 'not set')}\n"
        f"  - User install: {user_install}\n"
        f"  - System install: {system_install}\n"
        f"  - Development: {dev_path}\n"
        "\n"
        "To fix:\n"
        "  1. Set SDLC_FRAMEWORK_PATH to framework root, or\n"
        "  2. Run setup-sdlc.sh to install framework"
    )


def _validate_framework(path: Path) -> bool:
    """
    Check if path contains valid SDLC framework.

    Args:
        path: Path to validate

    Returns:
        bool: True if valid framework structure found
    """
    if not path.exists():
        return False

    required_paths = [
        path / ".agentic_sdlc/templates",
        path / ".agentic_sdlc/schemas",
    ]

    return all(p.exists() for p in required_paths)


def get_template_dir() -> Path:
    """
    Get framework templates directory.

    Returns:
        Path: Absolute path to templates directory

    Example:
        >>> template_dir = get_template_dir()
        >>> adr_template = template_dir / "adr_template.yml"
    """
    return get_framework_root() / ".agentic_sdlc/templates"


def get_schema_dir() -> Path:
    """
    Get framework schemas directory.

    Returns:
        Path: Absolute path to schemas directory

    Example:
        >>> schema_dir = get_schema_dir()
        >>> adr_schema = schema_dir / "adr_schema.json"
    """
    return get_framework_root() / ".agentic_sdlc/schemas"


def get_config_dir() -> Path:
    """
    Get framework config directory.

    Returns:
        Path: Absolute path to config directory
    """
    return get_framework_root() / ".claude/skills/sdlc-import/config"


def get_gates_dir() -> Path:
    """
    Get framework quality gates directory.

    Returns:
        Path: Absolute path to gates directory
    """
    return get_framework_root() / ".claude/skills/sdlc-import/gates"


# Convenience function for testing
def reset_cache():
    """Reset cached framework root (for testing only)."""
    global _FRAMEWORK_ROOT
    _FRAMEWORK_ROOT = None


if __name__ == "__main__":
    """CLI for testing framework path resolution."""
    import sys

    try:
        root = get_framework_root()
        print(f"Framework root: {root}")
        print(f"Templates: {get_template_dir()}")
        print(f"Schemas: {get_schema_dir()}")
        print(f"Config: {get_config_dir()}")
        print(f"Gates: {get_gates_dir()}")

        # Validate all paths exist
        for name, path in [
            ("Templates", get_template_dir()),
            ("Schemas", get_schema_dir()),
            ("Config", get_config_dir()),
            ("Gates", get_gates_dir()),
        ]:
            if path.exists():
                print(f"✓ {name} exists")
            else:
                print(f"✗ {name} missing", file=sys.stderr)
                sys.exit(1)

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
