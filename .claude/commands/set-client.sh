#!/usr/bin/env bash
# set-client.sh - Set active SDLC Agêntico client profile
# Version: 3.0.0
# Part of: Phase 1 - Foundation (Multi-Client Architecture)

set -euo pipefail

# Configuration
CLIENTS_DIR="${SDLC_CLIENTS_DIR:-clients}"
PROJECT_DIR="${SDLC_PROJECT_ARTIFACTS_DIR:-.project}"
CLIENT_MARKER="$PROJECT_DIR/.client"

# Logging (if available)
if [[ -f .claude/lib/shell/logging_utils.sh ]]; then
    source .claude/lib/shell/logging_utils.sh
    sdlc_set_context skill="set-client" phase="N/A"
else
    sdlc_log_info() { echo "[INFO] $*"; }
    sdlc_log_error() { echo "[ERROR] $*" >&2; }
    sdlc_log_warning() { echo "[WARN] $*" >&2; }
fi

# Usage
usage() {
    cat << EOF
Usage: $0 <client-id>

Set active SDLC Agêntico client profile.

Arguments:
  client-id    Client ID (must exist in clients/ directory)

Examples:
  $0 generic        # Use base framework (default)
  $0 demo-client    # Use demo client profile
  $0 yourco         # Use custom client profile

Available clients:
EOF
    if [[ -d "$CLIENTS_DIR" ]]; then
        find "$CLIENTS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sed 's/^/  - /'
    else
        echo "  (no clients directory found)"
    fi
    exit 1
}

# Validate arguments
if [[ $# -ne 1 ]]; then
    sdlc_log_error "Missing client-id argument"
    usage
fi

CLIENT_ID="$1"

# Validate client exists
CLIENT_PROFILE="$CLIENTS_DIR/$CLIENT_ID/profile.yml"

if [[ ! -f "$CLIENT_PROFILE" ]]; then
    sdlc_log_error "Client profile not found: $CLIENT_PROFILE"
    echo ""
    echo "Available clients:"
    if [[ -d "$CLIENTS_DIR" ]]; then
        find "$CLIENTS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sed 's/^/  - /'
    fi
    exit 1
fi

# Validate profile syntax (if yq available)
if command -v yq &>/dev/null; then
    if ! yq eval '.' "$CLIENT_PROFILE" &>/dev/null; then
        sdlc_log_error "Invalid YAML in profile: $CLIENT_PROFILE"
        exit 1
    fi
fi

# Create .project directory if needed
mkdir -p "$PROJECT_DIR"

# Write client marker
echo "$CLIENT_ID" > "$CLIENT_MARKER"
sdlc_log_info "Active client set to: $CLIENT_ID"

# Export environment variable (for current session)
export SDLC_CLIENT="$CLIENT_ID"
sdlc_log_info "Environment variable exported: SDLC_CLIENT=$CLIENT_ID"

# Show client info
if command -v yq &>/dev/null; then
    CLIENT_NAME=$(yq eval '.client.name' "$CLIENT_PROFILE" 2>/dev/null || echo "$CLIENT_ID")
    CLIENT_VERSION=$(yq eval '.client.version' "$CLIENT_PROFILE" 2>/dev/null || echo "unknown")
    CLIENT_DOMAIN=$(yq eval '.client.domain' "$CLIENT_PROFILE" 2>/dev/null || echo "unknown")

    echo ""
    echo "Client Profile:"
    echo "  ID:      $CLIENT_ID"
    echo "  Name:    $CLIENT_NAME"
    echo "  Domain:  $CLIENT_DOMAIN"
    echo "  Version: $CLIENT_VERSION"
fi

# Persist marker file location
sdlc_log_info "Client persisted to: $CLIENT_MARKER"
echo ""
echo "Next steps:"
echo "  - Run /sdlc-start to use this client profile"
echo "  - Run /new-feature to create feature with this client"
echo "  - All workflows will use client: $CLIENT_ID"
