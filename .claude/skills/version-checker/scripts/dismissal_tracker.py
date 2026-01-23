#!/usr/bin/env python3
"""
Dismissal tracker for SDLC Agêntico auto-update system.

Tracks user decisions to dismiss specific update versions.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="version-checker", phase=0)

# Storage location
STORE_DIR = Path.home() / ".claude/simple-memory"
STORE_FILE = STORE_DIR / "dismissed_updates.json"


def is_update_dismissed(version: str) -> bool:
    """
    Check if user has dismissed update to specific version.

    Args:
        version: Version string (e.g., "2.1.0")

    Returns:
        bool: True if this version was dismissed
    """
    if not STORE_FILE.exists():
        logger.debug("No dismissal record found")
        return False

    try:
        with open(STORE_FILE) as f:
            data = json.load(f)

        dismissed_version = data.get("dismissed_version")
        is_dismissed = (dismissed_version == version)

        logger.debug("Dismissal check", extra={
            "version": version,
            "dismissed_version": dismissed_version,
            "is_dismissed": is_dismissed
        })

        return is_dismissed

    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read dismissal record: {e}")
        return False


def dismiss_update(version: str):
    """
    Record that user dismissed update to specific version.

    Args:
        version: Version string to dismiss
    """
    STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing data or create new
    if STORE_FILE.exists():
        try:
            with open(STORE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = {}
    else:
        data = {}

    # Update dismissal record
    data["dismissed_version"] = version
    data["dismissed_at"] = datetime.now(timezone.utc).isoformat()
    data["checks_count"] = data.get("checks_count", 0) + 1

    # Save
    try:
        with open(STORE_FILE, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Update dismissed", extra={"version": version})

    except IOError as e:
        logger.error(f"Failed to save dismissal record: {e}")
        raise


def clear_dismissal():
    """
    Clear all dismissal records.

    Used when user accepts an update or manually resets dismissals.
    """
    if STORE_FILE.exists():
        try:
            STORE_FILE.unlink()
            logger.info("Dismissal record cleared")
        except IOError as e:
            logger.error(f"Failed to clear dismissal record: {e}")
            raise
    else:
        logger.debug("No dismissal record to clear")


def get_dismissal_info() -> Optional[Dict]:
    """
    Get current dismissal information.

    Returns:
        dict or None: {
            "dismissed_version": str,
            "dismissed_at": str (ISO 8601),
            "checks_count": int
        }
    """
    if not STORE_FILE.exists():
        return None

    try:
        with open(STORE_FILE) as f:
            data = json.load(f)

        return {
            "dismissed_version": data.get("dismissed_version"),
            "dismissed_at": data.get("dismissed_at"),
            "checks_count": data.get("checks_count", 0)
        }

    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read dismissal info: {e}")
        return None


def update_check_count():
    """
    Increment the check count (called each time version check runs).
    """
    if not STORE_FILE.exists():
        return

    try:
        with open(STORE_FILE) as f:
            data = json.load(f)

        data["checks_count"] = data.get("checks_count", 0) + 1
        data["last_checked_at"] = datetime.now(timezone.utc).isoformat()

        with open(STORE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to update check count: {e}")


if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Manage update dismissals")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dismiss command
    dismiss_parser = subparsers.add_parser("dismiss", help="Dismiss an update version")
    dismiss_parser.add_argument("version", help="Version to dismiss")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check if version is dismissed")
    check_parser.add_argument("version", help="Version to check")

    # Info command
    subparsers.add_parser("info", help="Show dismissal info")

    # Clear command
    subparsers.add_parser("clear", help="Clear dismissal records")

    args = parser.parse_args()

    if args.command == "dismiss":
        dismiss_update(args.version)
        print(f"Dismissed version {args.version}")

    elif args.command == "check":
        is_dismissed = is_update_dismissed(args.version)
        print(f"Version {args.version} dismissed: {is_dismissed}")
        sys.exit(0 if is_dismissed else 1)

    elif args.command == "info":
        info = get_dismissal_info()
        if info:
            print(json.dumps(info, indent=2))
        else:
            print("No dismissal records found")

    elif args.command == "clear":
        clear_dismissal()
        print("Dismissal records cleared")
