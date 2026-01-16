#!/bin/bash
#
# auto-graph-sync.sh
#
# Automatically updates the semantic graph when corpus node files are modified.
# Triggered by PostToolUse hook on Write operations.
#
# Usage:
#   This hook is called automatically by Claude Code after Write operations.
#   Manual invocation:
#     .claude/hooks/auto-graph-sync.sh /path/to/modified/file.yml
#
# Environment:
#   GRAPH_SYNC_ENABLED - Set to "false" to disable sync (default: true)
#   GRAPH_SYNC_VERBOSE - Set to "true" for verbose output (default: false)

set -euo pipefail

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="graph-navigator"
fi

# Configuration
CORPUS_NODES_PATH=".agentic_sdlc/corpus/nodes"
LEGACY_DECISIONS_PATH=".agentic_sdlc/decisions"
LEGACY_PROJECTS_PATH=".agentic_sdlc/projects"
GRAPH_BUILDER=".claude/skills/graph-navigator/scripts/graph_builder.py"

# Check if sync is enabled
if [[ "${GRAPH_SYNC_ENABLED:-true}" == "false" ]]; then
    sdlc_log_debug "Graph sync disabled via environment"
    exit 0
fi

# Get the modified file path
MODIFIED_FILE="${1:-}"

if [[ -z "$MODIFIED_FILE" ]]; then
    sdlc_log_debug "No file specified"
    exit 0
fi

sdlc_log_debug "Checking file for graph sync" "file=$MODIFIED_FILE"

# Check if the modified file is a corpus node
is_corpus_node() {
    local file="$1"

    # Check if file is in corpus nodes directory
    if [[ "$file" == *"$CORPUS_NODES_PATH"* ]]; then
        return 0
    fi

    # Check legacy paths
    if [[ "$file" == *"$LEGACY_DECISIONS_PATH"* ]]; then
        return 0
    fi

    if [[ "$file" == *"$LEGACY_PROJECTS_PATH"*"/decisions/"* ]]; then
        return 0
    fi

    if [[ "$file" == *"$LEGACY_PROJECTS_PATH"*"/learnings/"* ]]; then
        return 0
    fi

    return 1
}

# Check if it's a YAML file
is_yaml_file() {
    local file="$1"
    [[ "$file" == *.yml ]] || [[ "$file" == *.yaml ]]
}

# Main logic
if is_corpus_node "$MODIFIED_FILE" && is_yaml_file "$MODIFIED_FILE"; then
    # Check if graph builder exists
    if [[ ! -f "$GRAPH_BUILDER" ]]; then
        sdlc_log_debug "Graph builder not found" "path=$GRAPH_BUILDER"
        exit 0
    fi

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        sdlc_log_warn "Python3 not found, cannot sync graph"
        exit 0
    fi

    sdlc_log_info "Updating graph for modified file" "file=$MODIFIED_FILE"

    # Run incremental update
    if [[ "${GRAPH_SYNC_VERBOSE:-false}" == "true" ]]; then
        python3 "$GRAPH_BUILDER" --incremental "$MODIFIED_FILE"
    else
        if python3 "$GRAPH_BUILDER" --incremental "$MODIFIED_FILE" 2>/dev/null; then
            sdlc_log_debug "Graph sync completed"
        else
            sdlc_log_warn "Graph sync failed"
        fi
    fi
else
    sdlc_log_debug "File is not a corpus node" "file=$MODIFIED_FILE"
fi

exit 0
