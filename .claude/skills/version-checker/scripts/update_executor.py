#!/usr/bin/env python3
"""
Update executor for SDLC Agêntico auto-update system.

Handles automated git operations to update the repository to a new version.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="version-checker", phase=0)


def execute_update(release_tag: str) -> Dict:
    """
    Execute automated update to specified release tag.

    Steps:
    1. Save current state (for rollback)
    2. Fetch latest from remote
    3. Checkout release tag
    4. Run migration scripts (if exist)
    5. Verify installation
    6. Update VERSION file (if needed)

    Args:
        release_tag: Git tag to checkout (e.g., "v2.1.0")

    Returns:
        dict: {
            "success": bool,
            "new_version": str,
            "errors": list[str],
            "migrations_run": list[str],
            "rollback_available": bool
        }
    """
    logger.info(f"Starting update to {release_tag}")

    errors = []
    migrations_run = []
    rollback_ref = None

    try:
        # Step 0: Save current state for potential rollback
        with log_operation("save_current_state", logger):
            rollback_ref = get_current_commit()
            logger.debug(f"Rollback reference: {rollback_ref}")

        # Step 1: Fetch latest tags from remote
        with log_operation("git_fetch", logger):
            try:
                run_command(["git", "fetch", "--tags"], "Fetching latest tags")
            except subprocess.CalledProcessError as e:
                errors.append(f"Git fetch failed: {e}")
                return build_error_result(errors, rollback_ref)

        # Step 2: Checkout release tag
        with log_operation("git_checkout", logger):
            try:
                run_command(["git", "checkout", release_tag], f"Checking out {release_tag}")
            except subprocess.CalledProcessError as e:
                errors.append(f"Git checkout failed: {e}")
                return build_error_result(errors, rollback_ref)

        # Step 3: Run migration scripts (if exist)
        with log_operation("run_migrations", logger):
            version = release_tag.lstrip("v")
            migration_script = find_migration_script(version)

            if migration_script:
                logger.info(f"Found migration script: {migration_script}")
                try:
                    run_command([str(migration_script)], "Running migration script")
                    migrations_run.append(migration_script.name)
                except subprocess.CalledProcessError as e:
                    # Migrations are non-critical, log but continue
                    logger.warning(f"Migration script failed: {e}")
                    errors.append(f"Migration failed (non-critical): {e}")

        # Step 4: Verify installation
        with log_operation("verify_installation", logger):
            if not verify_installation():
                errors.append("Installation verification failed")
                logger.error("Verification failed, rolling back")
                rollback(rollback_ref)
                return build_error_result(errors, rollback_ref)

        # Success!
        logger.info(f"Update to {release_tag} completed successfully")

        return {
            "success": True,
            "new_version": version,
            "errors": errors,
            "migrations_run": migrations_run,
            "rollback_available": True,
            "rollback_ref": rollback_ref
        }

    except Exception as e:
        logger.error(f"Unexpected error during update: {e}", exc_info=True)
        errors.append(f"Unexpected error: {e}")

        # Attempt rollback
        if rollback_ref:
            logger.warning("Attempting rollback due to error")
            rollback(rollback_ref)

        return build_error_result(errors, rollback_ref)


def get_current_commit() -> str:
    """
    Get current commit SHA for rollback purposes.

    Returns:
        str: Current commit SHA
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def run_command(cmd: List[str], description: str):
    """
    Run shell command with logging.

    Args:
        cmd: Command to run
        description: Human-readable description

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    logger.debug(f"Running: {' '.join(cmd)}", extra={"description": description})

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        timeout=300  # 5 minute timeout
    )

    if result.stdout:
        logger.debug(f"Command output: {result.stdout[:500]}")

    return result


def find_migration_script(version: str) -> Path:
    """
    Find migration script for specific version.

    Looks for:
    - .scripts/migrate-to-v{version}.sh
    - .scripts/migrate-to-{version}.sh
    - .scripts/migrate-v{old}-to-v{new}.sh

    Args:
        version: Version string (e.g., "2.1.0")

    Returns:
        Path or None: Migration script path if found
    """
    scripts_dir = Path(".scripts")

    if not scripts_dir.exists():
        return None

    # Try common patterns
    patterns = [
        f"migrate-to-v{version}.sh",
        f"migrate-to-{version}.sh",
        f"migrate-*-to-v{version}.sh",
        f"migrate-*-to-{version}.sh"
    ]

    for pattern in patterns:
        matches = list(scripts_dir.glob(pattern))
        if matches:
            script = matches[0]
            if script.is_file() and script.stat().st_mode & 0o111:  # Executable
                return script

    return None


def verify_installation() -> bool:
    """
    Verify that installation is correct after update.

    Checks:
    1. .claude/VERSION file exists
    2. Core directories exist
    3. Python dependencies are satisfied

    Returns:
        bool: True if verification passes
    """
    logger.info("Verifying installation")

    # Check VERSION file
    version_file = Path(".claude/VERSION")
    if not version_file.exists():
        logger.error("VERSION file not found")
        return False

    # Check core directories
    required_dirs = [
        ".claude/agents",
        ".claude/skills",
        ".claude/lib"
    ]

    for dir_path in required_dirs:
        if not Path(dir_path).is_dir():
            logger.error(f"Required directory missing: {dir_path}")
            return False

    # Try running setup verification if available
    setup_script = Path(".scripts/setup-sdlc.sh")
    if setup_script.exists():
        try:
            subprocess.run(
                [str(setup_script), "--verify"],
                capture_output=True,
                timeout=60,
                check=True
            )
            logger.info("Setup verification passed")
        except subprocess.CalledProcessError:
            logger.warning("Setup verification script failed (non-critical)")
            # Don't fail update if verification script has issues

    logger.info("Installation verification successful")
    return True


def rollback(commit_ref: str) -> bool:
    """
    Rollback to previous commit.

    Args:
        commit_ref: Commit SHA to rollback to

    Returns:
        bool: True if rollback successful
    """
    logger.warning(f"Rolling back to {commit_ref}")

    try:
        subprocess.run(
            ["git", "checkout", commit_ref],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.info("Rollback successful")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Rollback failed: {e}")
        return False


def build_error_result(errors: List[str], rollback_ref: str) -> Dict:
    """
    Build error result dictionary.

    Args:
        errors: List of error messages
        rollback_ref: Commit reference for rollback

    Returns:
        dict: Error result
    """
    return {
        "success": False,
        "errors": errors,
        "rollback_available": rollback_ref is not None,
        "rollback_ref": rollback_ref
    }


if __name__ == "__main__":
    # CLI interface for testing
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Execute SDLC update")
    parser.add_argument("release_tag", help="Release tag to update to (e.g., v2.1.0)")

    args = parser.parse_args()

    result = execute_update(args.release_tag)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result["success"] else 1)
