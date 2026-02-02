#!/usr/bin/env python3
"""
Command: Enable Multi-Client Architecture

Enables multi-client architecture feature by:
1. Creating .sdlc_clients directory structure
2. Updating settings.json feature flags
3. Providing next steps guidance
"""

import sys
import json
from pathlib import Path
from typing import Tuple

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)

        def info(self, msg, **kwargs):
            self.logger.info(f"{msg} {kwargs}")

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def error(self, msg, **kwargs):
            self.logger.error(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class MultiClientEnabler:
    """Enables multi-client architecture feature."""

    # Directories to create
    DIRECTORIES = [
        ".sdlc_clients/_base",
        ".sdlc_clients/generic",
        ".sdlc_clients/demo-client",
    ]

    def __init__(self):
        self.logger = get_logger(__name__, skill="multi-client")
        self.repo_root = Path.cwd()

    def create_directories(self) -> bool:
        """
        Create .sdlc_clients directory structure.

        Returns:
            True if successful
        """
        for dir_path in self.DIRECTORIES:
            full_path = self.repo_root / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(
                    f"Created directory: {dir_path}",
                    extra={"path": str(full_path)}
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to create directory: {dir_path}",
                    extra={"error": str(e)}
                )
                return False

        return True

    def update_settings(self) -> bool:
        """
        Update settings.json to enable multi-client architecture.

        Returns:
            True if successful
        """
        settings_file = self.repo_root / ".claude" / "settings.json"

        if not settings_file.exists():
            self.logger.error(
                "settings.json not found",
                extra={"path": str(settings_file)}
            )
            return False

        try:
            # Read current settings
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Update feature flags
            if "sdlc" not in settings:
                settings["sdlc"] = {}
            if "feature_flags" not in settings["sdlc"]:
                settings["sdlc"]["feature_flags"] = {}
            if "clients" not in settings["sdlc"]:
                settings["sdlc"]["clients"] = {}

            settings["sdlc"]["feature_flags"]["multi_client_architecture"] = True
            settings["sdlc"]["clients"]["enabled"] = True

            # Write updated settings
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                f.write("\n")  # Add trailing newline

            self.logger.info("Updated settings.json successfully")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to update settings.json: {str(e)}",
                extra={"error": str(e)}
            )
            return False

    def print_next_steps(self):
        """Print next steps guidance."""
        print("\n✅ Multi-Client Architecture enabled!")
        print("")
        print("Next steps:")
        print("  1. Check .sdlc_clients/ directory")
        print("  2. Use /create-client to create new profiles")
        print("  3. Use /set-client to switch between profiles")
        print("")

    def execute(self) -> int:
        """
        Execute multi-client enablement.

        Returns:
            0 on success, 1 on failure
        """
        print("🔧 Enabling Multi-Client Architecture...")
        print("")

        # Create directories
        print("📁 Creating directory structure...")
        if not self.create_directories():
            print("❌ Failed to create directories")
            return 1

        # Update settings
        print("⚙️  Updating settings.json...")
        if not self.update_settings():
            print("❌ Failed to update settings.json")
            return 1

        # Show next steps
        self.print_next_steps()

        return 0


def main() -> int:
    """
    Main entry point for enable-multi-client command.

    Returns:
        Exit code (0 on success, 1 on failure)
    """
    enabler = MultiClientEnabler()

    try:
        return enabler.execute()
    except Exception as e:
        enabler.logger.error(
            f"Multi-client enablement failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
