#!/usr/bin/env python3
"""
GitHub release fetcher for SDLC Agêntico auto-update system.

Fetches latest release information using gh CLI and implements caching.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="version-checker", phase=0)

# Cache settings
CACHE_DIR = Path.home() / ".claude/simple-memory"
CACHE_FILE = CACHE_DIR / "latest_release.json"
CACHE_TTL_HOURS = 1


def get_current_repo() -> str:
    """
    Get current repository name using gh CLI.

    Returns:
        str: Repository name in format "owner/repo"

    Raises:
        RuntimeError: If gh CLI fails or not in a git repo
    """
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        repo_data = json.loads(result.stdout)
        repo = repo_data["nameWithOwner"]

        logger.debug("Current repository detected", extra={"repo": repo})
        return repo

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repository: {e.stderr}")
        raise RuntimeError(f"gh CLI error: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("gh CLI command timed out")
        raise RuntimeError("GitHub API timeout")
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Invalid gh CLI response: {e}")
        raise RuntimeError(f"Invalid gh response: {e}")


def fetch_latest_release_from_github(repo: str) -> Dict:
    """
    Fetch latest release from GitHub API using gh CLI.

    Args:
        repo: Repository name in format "owner/repo"

    Returns:
        dict: {
            "tag": str,
            "date": str (ISO 8601),
            "changelog": str,
            "assets": list[str]
        }

    Raises:
        RuntimeError: If GitHub API fails
    """
    logger.info("Fetching latest release from GitHub", extra={"repo": repo})

    try:
        with log_operation("github_api_call", logger):
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}/releases/latest"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

        release_data = json.loads(result.stdout)

        release = {
            "tag": release_data["tag_name"],
            "date": release_data["published_at"],
            "changelog": release_data.get("body", ""),
            "assets": [asset["name"] for asset in release_data.get("assets", [])]
        }

        logger.info("Release fetched successfully", extra={
            "tag": release["tag"],
            "date": release["date"]
        })

        return release

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "Unknown error"
        logger.error(f"GitHub API error: {error_msg}")

        # Check if no releases exist
        if "404" in error_msg or "Not Found" in error_msg:
            raise RuntimeError("No releases found in repository")

        raise RuntimeError(f"GitHub API error: {error_msg}")

    except subprocess.TimeoutExpired:
        logger.error("GitHub API timeout")
        raise RuntimeError("GitHub API timeout after 10 seconds")

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Invalid GitHub API response: {e}")
        raise RuntimeError(f"Invalid GitHub response: {e}")


def is_cache_valid() -> bool:
    """
    Check if cache file exists and is within TTL.

    Returns:
        bool: True if cache is valid and fresh
    """
    if not CACHE_FILE.exists():
        return False

    try:
        with open(CACHE_FILE) as f:
            cache_data = json.load(f)

        cached_at = datetime.fromisoformat(cache_data["cached_at"])
        now = datetime.now(timezone.utc)
        age = now - cached_at

        is_valid = age < timedelta(hours=CACHE_TTL_HOURS)

        logger.debug("Cache validity check", extra={
            "valid": is_valid,
            "age_minutes": age.total_seconds() / 60
        })

        return is_valid

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(f"Cache file corrupted: {e}")
        return False


def load_cached_release() -> Optional[Dict]:
    """
    Load release data from cache.

    Returns:
        dict or None: Cached release data if valid, None otherwise
    """
    if not is_cache_valid():
        return None

    try:
        with open(CACHE_FILE) as f:
            cache_data = json.load(f)

        logger.info("Using cached release data", extra={
            "tag": cache_data["release"]["tag"]
        })

        return cache_data["release"]

    except Exception as e:
        logger.warning(f"Failed to load cache: {e}")
        return None


def save_cached_release(release: Dict):
    """
    Save release data to cache with timestamp.

    Args:
        release: Release data to cache
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_data = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "release": release
    }

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)

        logger.debug("Release cached successfully")

    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")
        # Non-critical error, continue without caching


def fetch_latest_release() -> Dict:
    """
    Fetch latest release with caching.

    Returns:
        dict: Release data (from cache or GitHub)

    Raises:
        RuntimeError: If fetch fails and no cache available
    """
    # Try cache first
    cached = load_cached_release()
    if cached:
        return cached

    # Fetch from GitHub
    try:
        repo = get_current_repo()
        release = fetch_latest_release_from_github(repo)

        # Cache for future use
        save_cached_release(release)

        return release

    except Exception as e:
        logger.error(f"Failed to fetch release: {e}")
        raise


def clear_cache():
    """Clear cached release data."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        logger.info("Release cache cleared")


if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Fetch latest GitHub release")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cached data")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, fetch fresh")

    args = parser.parse_args()

    if args.clear_cache:
        clear_cache()
        print("Cache cleared")
        sys.exit(0)

    if args.no_cache:
        clear_cache()

    try:
        release = fetch_latest_release()
        print(json.dumps(release, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
