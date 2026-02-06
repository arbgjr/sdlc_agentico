#!/usr/bin/env python3
"""
detect-client.py - Auto-detect active SDLC Agêntico client profile
Version: 3.0.3
Hook: UserPromptSubmit
Part of: Phase 1 - Foundation (Multi-Client Architecture)

Cross-platform (Linux, macOS, Windows)
"""

import os
import sys
from pathlib import Path

# Add lib/python to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "python"))

try:
    from client_resolver import ClientResolver
except ImportError:
    # Fallback if client_resolver not available
    print("[WARN] client_resolver not available, skipping client detection", file=sys.stderr)
    sys.exit(0)


def main():
    """Auto-detect and export SDLC_CLIENT."""
    try:
        # Check if detection enabled
        settings_path = Path(".claude/settings.json")
        if settings_path.exists():
            import json
            with open(settings_path) as f:
                settings = json.load(f)
            enabled = settings.get("sdlc", {}).get("clients", {}).get("enabled", True)
            if not enabled:
                print("[DEBUG] Client detection disabled in settings.json", file=sys.stderr)
                sys.exit(0)

        # Initialize resolver
        resolver = ClientResolver()

        # Detect client
        client_id = resolver.detect_client()

        # Export environment variable (for current process tree)
        os.environ["SDLC_CLIENT"] = client_id

        # Print for parent shell to capture (if called from .sh wrapper)
        print(f"SDLC_CLIENT={client_id}")

        # Log detection
        marker_path = resolver.client_marker
        if marker_path.exists():
            print(f"[INFO] Client loaded from marker: {client_id}", file=sys.stderr)
        elif client_id != resolver.default_client:
            print(f"[INFO] Client auto-detected: {client_id}", file=sys.stderr)
        else:
            print(f"[DEBUG] No client detected, using default: {client_id}", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Client detection failed: {e}", file=sys.stderr)
        # Don't fail hook - set default
        print(f"SDLC_CLIENT=generic")
        sys.exit(0)


if __name__ == "__main__":
    main()
