#!/bin/bash
# track-rag-access.sh
# Track access when RAG queries return results
#
# This hook is called after rag-query returns results.
# It records which nodes were accessed for decay scoring.
#
# Arguments via environment:
#   TOOL_OUTPUT - The output from the tool (contains node IDs)

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="rag-query"
fi

CORPUS_PATH=".agentic_sdlc/corpus"
TRACKER_SCRIPT=".claude/skills/decay-scoring/scripts/decay_tracker.py"

# Skip if tracker script doesn't exist
if [ ! -f "$TRACKER_SCRIPT" ]; then
    sdlc_log_debug "Tracker script not found, skipping"
    exit 0
fi

# Skip if no tool output
if [ -z "$TOOL_OUTPUT" ]; then
    sdlc_log_debug "No tool output, skipping"
    exit 0
fi

sdlc_log_debug "Tracking RAG access"

# Extract node IDs from JSON output (looking for "id" fields)
# This is a simple extraction - may need adjustment based on actual output format
NODE_IDS=$(echo "$TOOL_OUTPUT" | grep -oP '"id"\s*:\s*"\K[^"]+' 2>/dev/null || true)

if [ -z "$NODE_IDS" ]; then
    sdlc_log_debug "No node IDs found in output"
    exit 0
fi

# Track access for each returned node (limit to first 10 to avoid slowdown)
COUNT=0
TRACKED=0
while IFS= read -r node_id; do
    if [ -n "$node_id" ] && [ "$COUNT" -lt 10 ]; then
        if python "$TRACKER_SCRIPT" --corpus "$CORPUS_PATH" access "$node_id" --type query > /dev/null 2>&1; then
            TRACKED=$((TRACKED + 1))
            sdlc_log_debug "Tracked access" "node_id=$node_id"
        fi
        COUNT=$((COUNT + 1))
    fi
done <<< "$NODE_IDS"

if [ "$TRACKED" -gt 0 ]; then
    sdlc_log_info "RAG access tracked" "nodes_tracked=$TRACKED"
fi

exit 0
