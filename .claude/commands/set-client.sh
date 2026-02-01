#!/usr/bin/env bash
# set-client.sh - Shell wrapper for set_client.py
# Version: 3.0.0 (Cross-platform via Python)
# Part of: Phase 1 - Foundation (Multi-Client Architecture)

# This is a shell wrapper that calls the Python implementation
# Works on Linux, macOS, Windows (via Python)

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call Python implementation
if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/set_client.py" "$@"
elif command -v python &>/dev/null; then
    python "$SCRIPT_DIR/set_client.py" "$@"
else
    echo "[ERROR] Python not found - required for set-client command" >&2
    echo "Install Python 3.7+ to use this command" >&2
    exit 1
fi
