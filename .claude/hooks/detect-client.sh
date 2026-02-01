#!/usr/bin/env bash
# detect-client.sh - Shell wrapper for detect-client.py
# Version: 3.0.0 (Cross-platform via Python)
# Hook: UserPromptSubmit
# Part of: Phase 1 - Foundation (Multi-Client Architecture)

# This is a shell wrapper that calls the Python implementation
# Works on Linux, macOS, Windows (via Python)

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call Python implementation
if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/detect-client.py"
elif command -v python &>/dev/null; then
    python "$SCRIPT_DIR/detect-client.py"
else
    echo "[ERROR] Python not found - required for client detection" >&2
    export SDLC_CLIENT="generic"
    exit 0
fi
