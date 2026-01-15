#!/bin/bash
# auto-decay-recalc.sh
# Automatically recalculate decay scores when corpus is modified
#
# This hook runs on UserPromptSubmit and checks if decay index needs updating.
# Recalculates if index is stale (> 24 hours old) or doesn't exist.

set -e

CORPUS_PATH=".agentic_sdlc/corpus"
DECAY_INDEX="$CORPUS_PATH/decay_index.json"
SCRIPT_PATH=".claude/skills/decay-scoring/scripts/decay_calculator.py"

# Skip if script doesn't exist (skill not installed)
if [ ! -f "$SCRIPT_PATH" ]; then
    exit 0
fi

# Check if decay index exists
if [ -f "$DECAY_INDEX" ]; then
    # Get file age in hours
    if [ "$(uname)" == "Darwin" ]; then
        # macOS
        FILE_AGE=$(( ($(date +%s) - $(stat -f %m "$DECAY_INDEX")) / 3600 ))
    else
        # Linux
        FILE_AGE=$(( ($(date +%s) - $(stat -c %Y "$DECAY_INDEX")) / 3600 ))
    fi

    # Skip if index is recent (less than 24 hours old)
    if [ "$FILE_AGE" -lt 24 ]; then
        exit 0
    fi
fi

# Check if corpus has nodes to process
NODES_DIR="$CORPUS_PATH/nodes"
if [ ! -d "$NODES_DIR" ]; then
    exit 0
fi

# Count YAML files in nodes directory
NODE_COUNT=$(find "$NODES_DIR" -name "*.yml" -type f 2>/dev/null | wc -l)
if [ "$NODE_COUNT" -eq 0 ]; then
    exit 0
fi

# Recalculate scores silently
python "$SCRIPT_PATH" --corpus "$CORPUS_PATH" --update-nodes > /dev/null 2>&1 || true

exit 0
