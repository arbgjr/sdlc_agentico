#!/usr/bin/env bash
# detect-client.sh - Auto-detect active SDLC Agêntico client profile
# Version: 3.0.0
# Hook: UserPromptSubmit
# Part of: Phase 1 - Foundation (Multi-Client Architecture)

set -euo pipefail

# Configuration
CLIENTS_DIR="${SDLC_CLIENTS_DIR:-clients}"
PROJECT_DIR="${SDLC_PROJECT_ARTIFACTS_DIR:-.project}"
CLIENT_MARKER="$PROJECT_DIR/.client"
DEFAULT_CLIENT="${SDLC_DEFAULT_CLIENT:-generic}"

# Logging (if available)
if [[ -f .claude/lib/shell/logging_utils.sh ]]; then
    source .claude/lib/shell/logging_utils.sh
    sdlc_set_context skill="detect-client" phase="N/A"
else
    sdlc_log_info() { echo "[INFO] $*"; }
    sdlc_log_debug() { :; }  # Silent in non-logging mode
fi

# Function: Check if client detection enabled
is_detection_enabled() {
    # Check settings.json for enabled flag
    if command -v jq &>/dev/null && [[ -f .claude/settings.json ]]; then
        local enabled
        enabled=$(jq -r '.sdlc.clients.enabled // true' .claude/settings.json 2>/dev/null)
        [[ "$enabled" == "true" ]]
    else
        # Enabled by default
        return 0
    fi
}

# Function: Detect client from markers
detect_from_markers() {
    local client_id="$1"
    local profile="$CLIENTS_DIR/$client_id/profile.yml"

    [[ ! -f "$profile" ]] && return 1

    # Check for yq
    if ! command -v yq &>/dev/null; then
        return 1
    fi

    # Get detection markers
    local markers_count
    markers_count=$(yq eval '.client.detection.markers | length' "$profile" 2>/dev/null || echo 0)

    for ((i=0; i<markers_count; i++)); do
        local marker_type
        marker_type=$(yq eval ".client.detection.markers[$i].type" "$profile" 2>/dev/null)

        case "$marker_type" in
            file)
                local file_path
                file_path=$(yq eval ".client.detection.markers[$i].path" "$profile" 2>/dev/null)
                if [[ -f "$file_path" ]]; then
                    sdlc_log_debug "Client $client_id detected via file marker: $file_path"
                    return 0
                fi
                ;;
            env)
                local env_var env_value
                env_var=$(yq eval ".client.detection.markers[$i].env" "$profile" 2>/dev/null)
                env_value=$(yq eval ".client.detection.markers[$i].value" "$profile" 2>/dev/null)
                if [[ "${!env_var:-}" == "$env_value" ]]; then
                    sdlc_log_debug "Client $client_id detected via env var: $env_var=$env_value"
                    return 0
                fi
                ;;
            git_remote)
                if command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null; then
                    local remote_pattern
                    remote_pattern=$(yq eval ".client.detection.markers[$i].remote" "$profile" 2>/dev/null)
                    local remotes
                    remotes=$(git remote -v 2>/dev/null || true)
                    if echo "$remotes" | grep -q "$remote_pattern"; then
                        sdlc_log_debug "Client $client_id detected via git remote: $remote_pattern"
                        return 0
                    fi
                fi
                ;;
        esac
    done

    return 1
}

# Skip if detection disabled
if ! is_detection_enabled; then
    sdlc_log_debug "Client detection disabled in settings.json"
    exit 0
fi

# Skip if clients directory doesn't exist
if [[ ! -d "$CLIENTS_DIR" ]]; then
    sdlc_log_debug "Clients directory not found: $CLIENTS_DIR"
    export SDLC_CLIENT="$DEFAULT_CLIENT"
    exit 0
fi

# Resolution order:
# 1. Check if already set (environment variable)
if [[ -n "${SDLC_CLIENT:-}" ]]; then
    sdlc_log_debug "Client already set: $SDLC_CLIENT"
    exit 0
fi

# 2. Check persisted marker (.project/.client)
if [[ -f "$CLIENT_MARKER" ]]; then
    DETECTED_CLIENT=$(cat "$CLIENT_MARKER")
    sdlc_log_info "Client loaded from marker: $DETECTED_CLIENT"
    export SDLC_CLIENT="$DETECTED_CLIENT"
    exit 0
fi

# 3. Auto-detect from profiles
if command -v yq &>/dev/null; then
    for client_dir in "$CLIENTS_DIR"/*; do
        [[ ! -d "$client_dir" ]] && continue
        client_id=$(basename "$client_dir")

        if detect_from_markers "$client_id"; then
            sdlc_log_info "Client auto-detected: $client_id"
            export SDLC_CLIENT="$client_id"
            # Persist detection
            mkdir -p "$PROJECT_DIR"
            echo "$client_id" > "$CLIENT_MARKER"
            exit 0
        fi
    done
fi

# 4. Fallback to default (generic)
sdlc_log_debug "No client detected, using default: $DEFAULT_CLIENT"
export SDLC_CLIENT="$DEFAULT_CLIENT"
