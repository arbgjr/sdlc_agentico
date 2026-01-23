#!/usr/bin/env bash
# doc-enrich - Manually enrich a document with research findings

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/shell/logging_utils.sh"

sdlc_set_context skill="document-enricher" phase="0"

# Parse arguments
if [ $# -lt 2 ]; then
    sdlc_log_error "Usage: /doc-enrich <doc-id> <research-json>"
    echo "Example: /doc-enrich DOC-001 research_results.json"
    exit 1
fi

DOC_ID="$1"
RESEARCH_JSON="$2"

sdlc_log_info "Enriching document: $DOC_ID"

# Run enrich.py
METADATA_JSON=$(mktemp)

if python3 "$SCRIPT_DIR/../skills/document-enricher/scripts/enrich.py" \
    "$DOC_ID" \
    "$RESEARCH_JSON" > "$METADATA_JSON"; then

    sdlc_log_info "Enrichment created successfully"

    # Update index and graph
    python3 "$SCRIPT_DIR/../skills/document-enricher/scripts/update_index.py" \
        "$METADATA_JSON" \
        --validate

    if [ $? -eq 0 ]; then
        sdlc_log_info "✅ Document enriched successfully"

        # Display enrichment details
        ENRICHMENT_ID=$(jq -r '.enrichment_id' "$METADATA_JSON")
        VERSION=$(jq -r '.version' "$METADATA_JSON")
        ENRICHED_FILE=$(jq -r '.enriched_file' "$METADATA_JSON")

        echo ""
        echo "Enrichment Details:"
        echo "  ID: $ENRICHMENT_ID"
        echo "  Version: v$VERSION"
        echo "  File: .agentic_sdlc/references/$ENRICHED_FILE"
        echo "  Corpus: .agentic_sdlc/corpus/nodes/learnings/$ENRICHMENT_ID.yml"
        echo ""
    else
        sdlc_log_error "Failed to update index/graph"
        exit 1
    fi
else
    sdlc_log_error "Failed to create enrichment"
    exit 1
fi

rm -f "$METADATA_JSON"
exit 0
