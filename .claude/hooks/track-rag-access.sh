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

CORPUS_PATH=".agentic_sdlc/corpus"
TRACKER_SCRIPT=".claude/skills/decay-scoring/scripts/decay_tracker.py"

# Skip if tracker script doesn't exist
if [ ! -f "$TRACKER_SCRIPT" ]; then
    exit 0
fi

# Skip if no tool output
if [ -z "$TOOL_OUTPUT" ]; then
    exit 0
fi

# Extract node IDs from JSON output (looking for "id" fields)
# This is a simple extraction - may need adjustment based on actual output format
NODE_IDS=$(echo "$TOOL_OUTPUT" | grep -oP '"id"\s*:\s*"\K[^"]+' 2>/dev/null || true)

if [ -z "$NODE_IDS" ]; then
    exit 0
fi

# Track access for each returned node (limit to first 10 to avoid slowdown)
COUNT=0
while IFS= read -r node_id; do
    if [ -n "$node_id" ] && [ "$COUNT" -lt 10 ]; then
        python "$TRACKER_SCRIPT" --corpus "$CORPUS_PATH" access "$node_id" --type query > /dev/null 2>&1 || true
        COUNT=$((COUNT + 1))
    fi
done <<< "$NODE_IDS"

exit 0
