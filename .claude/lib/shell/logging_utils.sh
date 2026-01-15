#!/usr/bin/env bash
# =============================================================================
# SDLC Agentico Shell Logging Utilities
#
# Source this file in shell scripts for consistent, structured logging.
#
# Usage:
#   source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
#
#   sdlc_log_info "Processing started"
#   sdlc_log_debug "Detailed info" "key1=value1" "key2=value2"
#   sdlc_log_error "Something failed"
# =============================================================================

# -----------------------------------------------------------------------------
# Configuration (can be overridden by environment)
# -----------------------------------------------------------------------------
export SDLC_LOG_LEVEL="${SDLC_LOG_LEVEL:-DEBUG}"
export SDLC_LOKI_URL="${SDLC_LOKI_URL:-http://localhost:3100}"
export SDLC_LOKI_ENABLED="${SDLC_LOKI_ENABLED:-true}"
export SDLC_JSON_LOGS="${SDLC_JSON_LOGS:-true}"
export SDLC_CORRELATION_ID="${SDLC_CORRELATION_ID:-}"
export SDLC_SKILL="${SDLC_SKILL:-}"
export SDLC_PHASE="${SDLC_PHASE:-}"
export SDLC_SCRIPT_NAME="${SDLC_SCRIPT_NAME:-$(basename "$0")}"
export SDLC_ENV="${SDLC_ENV:-development}"

# Log level values (lower = more verbose)
declare -A SDLC_LOG_LEVELS=(
    ["VERBOSE"]=10
    ["DEBUG"]=10
    ["INFO"]=20
    ["WARNING"]=30
    ["WARN"]=30
    ["ERROR"]=40
    ["CRITICAL"]=50
)

# Colors for console output
declare -A SDLC_LOG_COLORS=(
    ["DEBUG"]="\033[36m"     # Cyan
    ["INFO"]="\033[32m"      # Green
    ["WARNING"]="\033[33m"   # Yellow
    ["ERROR"]="\033[31m"     # Red
    ["CRITICAL"]="\033[35m"  # Magenta
)
SDLC_COLOR_RESET="\033[0m"

# -----------------------------------------------------------------------------
# Internal Functions
# -----------------------------------------------------------------------------

# Generate correlation ID if not set
_sdlc_ensure_correlation_id() {
    if [[ -z "${SDLC_CORRELATION_ID}" ]]; then
        if command -v uuidgen &> /dev/null; then
            SDLC_CORRELATION_ID=$(uuidgen | cut -c1-8)
        elif [[ -r /dev/urandom ]]; then
            SDLC_CORRELATION_ID=$(head -c 4 /dev/urandom | xxd -p 2>/dev/null || od -An -tx1 /dev/urandom | head -1 | tr -d ' ' | cut -c1-8)
        else
            SDLC_CORRELATION_ID="$(date +%s | tail -c 8)"
        fi
        export SDLC_CORRELATION_ID
    fi
    echo "${SDLC_CORRELATION_ID}"
}

# Get numeric log level
_sdlc_get_level_value() {
    local level="${1^^}"
    echo "${SDLC_LOG_LEVELS[$level]:-20}"
}

# Check if level should be logged
_sdlc_should_log() {
    local msg_level="$1"
    local configured_level="${SDLC_LOG_LEVEL^^}"

    local msg_value=$(_sdlc_get_level_value "$msg_level")
    local cfg_value=$(_sdlc_get_level_value "$configured_level")

    [[ $msg_value -ge $cfg_value ]]
}

# Get ISO 8601 timestamp
_sdlc_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%S.%3NZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Escape string for JSON
_sdlc_json_escape() {
    local str="$1"
    str="${str//\\/\\\\}"
    str="${str//\"/\\\"}"
    str="${str//$'\n'/\\n}"
    str="${str//$'\r'/\\r}"
    str="${str//$'\t'/\\t}"
    echo "$str"
}

# Build JSON log entry
_sdlc_build_json() {
    local level="$1"
    local message="$2"
    shift 2

    local correlation_id=$(_sdlc_ensure_correlation_id)
    local timestamp=$(_sdlc_timestamp)
    local escaped_message=$(_sdlc_json_escape "$message")

    # Start JSON object
    local json="{"
    json+="\"timestamp\":\"${timestamp}\","
    json+="\"level\":\"${level}\","
    json+="\"message\":\"${escaped_message}\","
    json+="\"correlation_id\":\"${correlation_id}\","
    json+="\"script\":\"${SDLC_SCRIPT_NAME}\""

    # Add skill if set
    if [[ -n "${SDLC_SKILL}" ]]; then
        json+=",\"skill\":\"${SDLC_SKILL}\""
    fi

    # Add phase if set
    if [[ -n "${SDLC_PHASE}" ]]; then
        json+=",\"phase\":${SDLC_PHASE}"
    fi

    # Add extra fields (key=value pairs)
    if [[ $# -gt 0 ]]; then
        json+=",\"extra\":{"
        local first=true
        for kv in "$@"; do
            local key="${kv%%=*}"
            local value="${kv#*=}"

            if [[ "$first" == "true" ]]; then
                first=false
            else
                json+=","
            fi

            # Try to detect if value is numeric or boolean
            if [[ "$value" =~ ^-?[0-9]+$ ]]; then
                json+="\"${key}\":${value}"
            elif [[ "$value" =~ ^-?[0-9]+\.[0-9]+$ ]]; then
                json+="\"${key}\":${value}"
            elif [[ "$value" == "true" || "$value" == "false" ]]; then
                json+="\"${key}\":${value}"
            elif [[ "$value" == "null" ]]; then
                json+="\"${key}\":null"
            else
                # Escape quotes in string value
                local escaped_value=$(_sdlc_json_escape "$value")
                json+="\"${key}\":\"${escaped_value}\""
            fi
        done
        json+="}"
    fi

    json+="}"
    echo "$json"
}

# Build console log entry
_sdlc_build_console() {
    local level="$1"
    local message="$2"
    shift 2

    local correlation_id=$(_sdlc_ensure_correlation_id)
    local color="${SDLC_LOG_COLORS[$level]:-}"

    # Format: [LEVEL   ] [corr_id ] script: message (key=value, ...)
    local output="${color}[${level}]${SDLC_COLOR_RESET}"
    output+=" [${correlation_id:0:8}]"
    output+=" ${SDLC_SCRIPT_NAME}:"
    output+=" ${message}"

    # Add extra fields
    if [[ $# -gt 0 ]]; then
        output+=" ($*)"
    fi

    echo -e "$output"
}

# Send log to Loki
_sdlc_push_to_loki() {
    local level="$1"
    local json_log="$2"

    if [[ "${SDLC_LOKI_ENABLED}" != "true" ]]; then
        return 0
    fi

    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        return 0
    fi

    local correlation_id=$(_sdlc_ensure_correlation_id)
    local labels="\"app\":\"sdlc-agentico\",\"level\":\"${level,,}\",\"script\":\"${SDLC_SCRIPT_NAME}\",\"env\":\"${SDLC_ENV}\""

    if [[ -n "${SDLC_SKILL}" ]]; then
        labels+=",\"skill\":\"${SDLC_SKILL}\""
    fi

    if [[ -n "${SDLC_PHASE}" ]]; then
        labels+=",\"phase\":\"${SDLC_PHASE}\""
    fi

    # Get timestamp in nanoseconds
    local timestamp_ns
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS doesn't have nanoseconds, use microseconds * 1000
        timestamp_ns="$(date +%s)000000000"
    else
        timestamp_ns=$(date +%s%N)
    fi

    # Build Loki push payload
    local payload="{\"streams\":[{\"stream\":{${labels}},\"values\":[[\"${timestamp_ns}\",${json_log}]]}]}"

    # Send to Loki (async, ignore errors)
    (curl -s -X POST \
        -H "Content-Type: application/json" \
        --data "${payload}" \
        "${SDLC_LOKI_URL}/loki/api/v1/push" \
        >/dev/null 2>&1 &) 2>/dev/null
}

# Core logging function
_sdlc_log() {
    local level="$1"
    local message="$2"
    shift 2

    # Check if we should log this level
    if ! _sdlc_should_log "$level"; then
        return 0
    fi

    # Build log entry
    local json_log=$(_sdlc_build_json "$level" "$message" "$@")

    # Output to console
    if [[ "${SDLC_JSON_LOGS}" == "true" ]]; then
        echo "$json_log" >&2
    else
        _sdlc_build_console "$level" "$message" "$@" >&2
    fi

    # Push to Loki
    _sdlc_push_to_loki "$level" "$json_log"
}

# -----------------------------------------------------------------------------
# Public Logging Functions
# -----------------------------------------------------------------------------

sdlc_log_debug() {
    _sdlc_log "DEBUG" "$@"
}

sdlc_log_info() {
    _sdlc_log "INFO" "$@"
}

sdlc_log_warning() {
    _sdlc_log "WARNING" "$@"
}

sdlc_log_warn() {
    _sdlc_log "WARNING" "$@"
}

sdlc_log_error() {
    _sdlc_log "ERROR" "$@"
}

sdlc_log_critical() {
    _sdlc_log "CRITICAL" "$@"
}

# -----------------------------------------------------------------------------
# Context Management
# -----------------------------------------------------------------------------

# Set logging context
sdlc_set_context() {
    for kv in "$@"; do
        local key="${kv%%=*}"
        local value="${kv#*=}"

        case "$key" in
            skill)
                export SDLC_SKILL="$value"
                ;;
            phase)
                export SDLC_PHASE="$value"
                ;;
            correlation_id)
                export SDLC_CORRELATION_ID="$value"
                ;;
            script)
                export SDLC_SCRIPT_NAME="$value"
                ;;
            env)
                export SDLC_ENV="$value"
                ;;
        esac
    done
}

# Generate and set correlation ID
sdlc_new_correlation_id() {
    SDLC_CORRELATION_ID=""
    _sdlc_ensure_correlation_id
}

# Get current correlation ID
sdlc_get_correlation_id() {
    _sdlc_ensure_correlation_id
}

# -----------------------------------------------------------------------------
# Operation Timing
# -----------------------------------------------------------------------------

# Declare associative array for operation start times
declare -A _SDLC_OP_STARTS

# Start a timed operation
sdlc_operation_start() {
    local operation_name="$1"
    shift

    sdlc_log_info "Starting: ${operation_name}" "$@"

    # Store start time
    if [[ "$OSTYPE" == "darwin"* ]]; then
        _SDLC_OP_STARTS["$operation_name"]=$(date +%s)000
    else
        _SDLC_OP_STARTS["$operation_name"]=$(date +%s%3N)
    fi
}

# End a timed operation
sdlc_operation_end() {
    local operation_name="$1"
    local status="${2:-success}"
    shift 2

    local start_time="${_SDLC_OP_STARTS[$operation_name]:-0}"
    local end_time
    if [[ "$OSTYPE" == "darwin"* ]]; then
        end_time=$(date +%s)000
    else
        end_time=$(date +%s%3N)
    fi

    local duration_ms=$((end_time - start_time))

    if [[ "$status" == "success" ]]; then
        sdlc_log_info "Completed: ${operation_name}" "duration_ms=${duration_ms}" "status=success" "$@"
    else
        sdlc_log_error "Failed: ${operation_name}" "duration_ms=${duration_ms}" "status=error" "$@"
    fi

    unset "_SDLC_OP_STARTS[$operation_name]"
}

# -----------------------------------------------------------------------------
# Legacy Compatibility Layer
# -----------------------------------------------------------------------------
# These functions match the existing patterns in shell scripts

log_info() {
    sdlc_log_info "$@"
}

log_error() {
    sdlc_log_error "$@"
}

log_warning() {
    sdlc_log_warning "$@"
}

log_warn() {
    sdlc_log_warning "$@"
}

log_debug() {
    sdlc_log_debug "$@"
}

log_ok() {
    sdlc_log_info "$@"
}

log_success() {
    sdlc_log_info "$@"
}

# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

# Auto-initialize correlation ID on source
_sdlc_ensure_correlation_id > /dev/null
