#!/usr/bin/env python3
"""
Impact analyzer for SDLC Agêntico auto-update system.

Analyzes changelog content to detect breaking changes, required migrations,
and dependency updates.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="version-checker", phase=0)


def analyze_impact(changelog: str, version_diff: Dict) -> Dict:
    """
    Analyze impact of upgrade based on changelog and version difference.

    Args:
        changelog: Release changelog/body text
        version_diff: Version difference dict from compare_versions()

    Returns:
        dict: {
            "severity": str,  # "major", "minor", or "patch"
            "breaking_changes": list[str],
            "migrations": list[str],
            "dependencies": dict,  # {package: {old: ver, new: ver}}
            "security_fixes": list[str]
        }

    Examples:
        >>> diff = {"major": 0, "minor": 1, "patch": 0}
        >>> result = analyze_impact("BREAKING: API changed", diff)
        >>> result["severity"]
        'minor'
        >>> len(result["breaking_changes"]) > 0
        True
    """
    logger.debug("Analyzing upgrade impact", extra={
        "changelog_length": len(changelog),
        "version_diff": version_diff
    })

    # Determine base severity from version diff
    severity = get_severity_from_diff(version_diff)

    # Detect breaking changes
    breaking_changes = detect_breaking_changes(changelog)

    # If breaking changes found, upgrade severity to major
    if breaking_changes and severity != "major":
        logger.warning(
            "Breaking changes detected in non-major version",
            extra={"severity": severity, "breaking_count": len(breaking_changes)}
        )

    # Detect migrations
    migrations = detect_migrations(changelog)

    # Detect dependency updates
    dependencies = detect_dependency_updates(changelog)

    # Detect security fixes
    security_fixes = detect_security_fixes(changelog)

    result = {
        "severity": severity,
        "breaking_changes": breaking_changes,
        "migrations": migrations,
        "dependencies": dependencies,
        "security_fixes": security_fixes
    }

    logger.info("Impact analysis completed", extra={
        "severity": severity,
        "breaking_changes_count": len(breaking_changes),
        "migrations_count": len(migrations),
        "security_fixes_count": len(security_fixes)
    })

    return result


def get_severity_from_diff(diff: Dict) -> str:
    """
    Determine severity level from version difference.

    Args:
        diff: Version difference dict

    Returns:
        str: "major", "minor", or "patch"
    """
    if diff["major"] > 0:
        return "major"
    elif diff["minor"] > 0:
        return "minor"
    elif diff["patch"] > 0:
        return "patch"
    else:
        return "none"


def detect_breaking_changes(changelog: str) -> List[str]:
    """
    Detect breaking changes in changelog.

    Looks for markers:
    - BREAKING:
    - BREAKING CHANGE:
    - [BREAKING]
    - ⚠️ (warning emoji)

    Args:
        changelog: Changelog text

    Returns:
        list[str]: List of breaking change descriptions
    """
    breaking_changes = []

    # Patterns to match breaking changes
    patterns = [
        r"BREAKING:\s*(.+?)(?:\n|$)",
        r"BREAKING CHANGE:\s*(.+?)(?:\n|$)",
        r"\[BREAKING\]\s*(.+?)(?:\n|$)",
        r"⚠️\s*(.+?)(?:\n|$)"
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, changelog, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            change = match.group(1).strip()
            if change and change not in breaking_changes:
                breaking_changes.append(change)

    logger.debug(f"Found {len(breaking_changes)} breaking changes")
    return breaking_changes


def detect_migrations(changelog: str) -> List[str]:
    """
    Detect required migration steps in changelog.

    Looks for markers:
    - Migration:
    - Run:
    - Required:
    - Action required:
    - [MIGRATION]

    Args:
        changelog: Changelog text

    Returns:
        list[str]: List of migration instructions
    """
    migrations = []

    # Patterns to match migration instructions
    patterns = [
        r"Migration:\s*(.+?)(?:\n|$)",
        r"Run:\s*(.+?)(?:\n|$)",
        r"Required:\s*(.+?)(?:\n|$)",
        r"Action required:\s*(.+?)(?:\n|$)",
        r"\[MIGRATION\]\s*(.+?)(?:\n|$)"
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, changelog, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            migration = match.group(1).strip()
            if migration and migration not in migrations:
                migrations.append(migration)

    logger.debug(f"Found {len(migrations)} migration steps")
    return migrations


def detect_dependency_updates(changelog: str) -> Dict:
    """
    Detect dependency version updates in changelog.

    Looks for patterns like:
    - Python: 3.9 → 3.11
    - Node.js: 18 → 20
    - package_name: 1.0.0 → 2.0.0

    Args:
        changelog: Changelog text

    Returns:
        dict: {package_name: {"old": version, "new": version}}
    """
    dependencies = {}

    # Pattern to match version updates
    # Format: "Package: old → new" or "Package: old -> new"
    pattern = r"(\w+(?:\.js)?(?::\s*|\s+))(\d+(?:\.\d+)*)\s*(?:→|->|to)\s*(\d+(?:\.\d+)*)"

    matches = re.finditer(pattern, changelog, re.IGNORECASE)
    for match in matches:
        package = match.group(1).strip().rstrip(":")
        old_version = match.group(2)
        new_version = match.group(3)

        dependencies[package] = {
            "old": old_version,
            "new": new_version
        }

    logger.debug(f"Found {len(dependencies)} dependency updates")
    return dependencies


def detect_security_fixes(changelog: str) -> List[str]:
    """
    Detect security fixes in changelog.

    Looks for markers:
    - Security:
    - CVE-
    - [SECURITY]
    - 🔒 (lock emoji)
    - Vulnerability

    Args:
        changelog: Changelog text

    Returns:
        list[str]: List of security fix descriptions
    """
    security_fixes = []

    # Patterns to match security fixes
    patterns = [
        r"Security:\s*(.+?)(?:\n|$)",
        r"(CVE-\d{4}-\d{4,})",
        r"\[SECURITY\]\s*(.+?)(?:\n|$)",
        r"🔒\s*(.+?)(?:\n|$)",
        r"Vulnerability:\s*(.+?)(?:\n|$)",
        r"Security fix:\s*(.+?)(?:\n|$)"
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, changelog, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            fix = match.group(1).strip() if match.lastindex else match.group(0)
            if fix and fix not in security_fixes:
                security_fixes.append(fix)

    logger.debug(f"Found {len(security_fixes)} security fixes")
    return security_fixes


def format_impact_summary(impact: Dict) -> str:
    """
    Format impact analysis into human-readable summary.

    Args:
        impact: Impact analysis result from analyze_impact()

    Returns:
        str: Formatted markdown summary
    """
    severity_emoji = {
        "major": "🔴",
        "minor": "🟡",
        "patch": "🟢",
        "none": "⚪"
    }

    emoji = severity_emoji.get(impact["severity"], "ℹ️")
    lines = [f"{emoji} **Severity:** {impact['severity'].upper()}"]

    if impact["breaking_changes"]:
        lines.append("\n### ⚠️ Breaking Changes")
        for change in impact["breaking_changes"]:
            lines.append(f"- {change}")

    if impact["migrations"]:
        lines.append("\n### 📋 Required Migrations")
        for migration in impact["migrations"]:
            lines.append(f"- {migration}")

    if impact["dependencies"]:
        lines.append("\n### 📦 Dependency Updates")
        for pkg, versions in impact["dependencies"].items():
            lines.append(f"- **{pkg}:** {versions['old']} → {versions['new']}")

    if impact["security_fixes"]:
        lines.append("\n### 🔒 Security Fixes")
        for fix in impact["security_fixes"]:
            lines.append(f"- {fix}")

    return "\n".join(lines)


if __name__ == "__main__":
    # CLI interface for testing
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analyze changelog impact")
    parser.add_argument("changelog_file", help="Path to changelog file")
    parser.add_argument("--major", type=int, default=0, help="Major version diff")
    parser.add_argument("--minor", type=int, default=1, help="Minor version diff")
    parser.add_argument("--patch", type=int, default=0, help="Patch version diff")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")

    args = parser.parse_args()

    with open(args.changelog_file) as f:
        changelog = f.read()

    diff = {
        "major": args.major,
        "minor": args.minor,
        "patch": args.patch
    }

    impact = analyze_impact(changelog, diff)

    if args.format == "json":
        print(json.dumps(impact, indent=2))
    else:
        print(format_impact_summary(impact))
