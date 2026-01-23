#!/usr/bin/env python3
"""
Main auto-update checker for SDLC Agêntico.

Orchestrates version comparison, release fetching, impact analysis,
and user interaction for automated updates.

Usage:
    python3 check_updates.py                # Check and return JSON
    python3 check_updates.py --execute      # Execute update if available
    python3 check_updates.py --silent       # Check only, no output
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

# Import version-checker modules
from version_comparator import compare_versions, get_current_version, get_upgrade_type
from release_fetcher import fetch_latest_release, clear_cache as clear_release_cache
from impact_analyzer import analyze_impact, format_impact_summary
from dismissal_tracker import (
    is_update_dismissed,
    dismiss_update,
    clear_dismissal,
    update_check_count
)

logger = get_logger(__name__, skill="version-checker", phase=0)


def check_for_updates() -> Dict:
    """
    Check for available updates and return status.

    Returns:
        dict: {
            "update_available": bool,
            "current": str,
            "latest": str (if available),
            "dismissed": bool (if update was dismissed),
            "changelog": str (if update available),
            "impact": dict (if update available),
            "notification": str (formatted notification),
            "error": str (if error occurred)
        }
    """
    logger.info("Starting update check")

    try:
        # 1. Get current version
        with log_operation("get_current_version", logger):
            current = get_current_version()
            logger.debug(f"Current version: {current}")

        # 2. Fetch latest release
        with log_operation("fetch_latest_release", logger):
            try:
                release = fetch_latest_release()
            except Exception as e:
                logger.error(f"Failed to fetch release: {e}")
                return {
                    "update_available": False,
                    "error": str(e),
                    "current": current
                }

        latest = release["tag"].lstrip("v")
        logger.debug(f"Latest version: {latest}")

        # 3. Compare versions
        comparison = compare_versions(current, latest)

        if not comparison["is_newer"]:
            logger.info("Already on latest version")
            return {
                "update_available": False,
                "current": current,
                "latest": latest
            }

        logger.info(f"Update available: {current} → {latest}")

        # 4. Check if already dismissed
        if is_update_dismissed(latest):
            logger.info(f"Update to {latest} was dismissed by user")
            return {
                "update_available": True,
                "dismissed": True,
                "current": current,
                "latest": latest
            }

        # Update check count
        update_check_count()

        # 5. Analyze impact
        with log_operation("analyze_impact", logger):
            impact = analyze_impact(release["changelog"], comparison["diff"])

        # 6. Build notification
        notification = build_notification(
            current=current,
            latest=latest,
            release=release,
            impact=impact,
            upgrade_type=get_upgrade_type(comparison["diff"])
        )

        # 7. Return complete result
        return {
            "update_available": True,
            "current": current,
            "latest": latest,
            "dismissed": False,
            "changelog": release["changelog"],
            "impact": impact,
            "notification": notification,
            "release_date": release["date"]
        }

    except Exception as e:
        logger.error(f"Update check failed: {e}", exc_info=True)
        return {
            "update_available": False,
            "error": str(e)
        }


def build_notification(
    current: str,
    latest: str,
    release: Dict,
    impact: Dict,
    upgrade_type: str
) -> str:
    """
    Build markdown notification for user.

    Args:
        current: Current version
        latest: Latest version
        release: Release data from GitHub
        impact: Impact analysis result
        upgrade_type: "major", "minor", or "patch"

    Returns:
        str: Formatted markdown notification
    """
    severity_emoji = {
        "major": "🔴",
        "minor": "🟡",
        "patch": "🟢"
    }

    emoji = severity_emoji.get(impact["severity"], "ℹ️")

    # Extract release date (just the date part)
    release_date = release["date"][:10] if "date" in release else "Unknown"

    md = f"""# {emoji} Update Available: v{latest}

**Current version:** v{current}
**Latest version:** v{latest}
**Released:** {release_date}
**Upgrade type:** {upgrade_type.upper()}

## What's New

{release["changelog"]}

## Impact Analysis

{format_impact_summary(impact)}

---

**What would you like to do?**
"""

    return md


def execute_update(version: str) -> Dict:
    """
    Execute automated update to specified version.

    Args:
        version: Version to update to (e.g., "2.1.0")

    Returns:
        dict: {
            "success": bool,
            "new_version": str,
            "error": str (if failed)
        }
    """
    logger.info(f"Executing update to {version}")

    # Import update_executor only when needed
    try:
        from update_executor import execute_update as do_update
    except ImportError:
        logger.error("update_executor module not found")
        return {
            "success": False,
            "error": "Update executor not available"
        }

    try:
        result = do_update(f"v{version}")

        if result["success"]:
            # Clear dismissal after successful update
            clear_dismissal()
            # Clear release cache to force fresh check
            clear_release_cache()

            logger.info(f"Update to {version} completed successfully")

        return result

    except Exception as e:
        logger.error(f"Update execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check for SDLC Agêntico updates"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute update if available"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Silent mode, no output"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cached release data"
    )
    parser.add_argument(
        "--dismiss",
        metavar="VERSION",
        help="Dismiss specific version"
    )

    args = parser.parse_args()

    # Handle special commands
    if args.clear_cache:
        clear_release_cache()
        clear_dismissal()
        if not args.silent:
            print("Cache cleared")
        return 0

    if args.dismiss:
        dismiss_update(args.dismiss)
        if not args.silent:
            print(f"Dismissed version {args.dismiss}")
        return 0

    # Perform update check
    result = check_for_updates()

    if not args.silent:
        print(json.dumps(result, indent=2))

    # Execute update if requested
    if args.execute and result.get("update_available") and not result.get("dismissed"):
        if not args.silent:
            print("\nExecuting update...")

        update_result = execute_update(result["latest"])

        if not args.silent:
            print(json.dumps(update_result, indent=2))

        return 0 if update_result["success"] else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
