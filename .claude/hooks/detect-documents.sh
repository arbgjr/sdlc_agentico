#!/bin/bash
# Hook: detect-documents.sh
# Purpose: Detect PDF/XLSX/DOCX files in the project and suggest document-processor skill
# Triggered: On UserPromptSubmit

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="document-processor" phase="0"
fi

sdlc_log_debug "Scanning for documents"

# Find document files in common locations
DOCS_FOUND=()

# Check for documents in typical locations
for pattern in "*.pdf" "*.xlsx" "*.xls" "*.docx" "*.doc"; do
    while IFS= read -r -d '' file; do
        DOCS_FOUND+=("$file")
    done < <(find . -maxdepth 3 -name "$pattern" -type f -print0 2>/dev/null || true)
done

# Check .agentic_sdlc/references for documents
if [ -d ".agentic_sdlc/references" ]; then
    for pattern in "*.pdf" "*.xlsx" "*.xls" "*.docx" "*.doc"; do
        while IFS= read -r -d '' file; do
            DOCS_FOUND+=("$file")
        done < <(find .agentic_sdlc/references -name "$pattern" -type f -print0 2>/dev/null || true)
    done
fi

# If documents found, output suggestion
if [ ${#DOCS_FOUND[@]} -gt 0 ]; then
    sdlc_log_info "Documents detected" "count=${#DOCS_FOUND[@]}"
    echo "DOCUMENTS_DETECTED=true"
    echo "DOCUMENT_COUNT=${#DOCS_FOUND[@]}"
    echo "DOCUMENTS_HINT=Use /doc-extract to process documents"

    # List first 5 documents
    count=0
    for doc in "${DOCS_FOUND[@]}"; do
        if [ $count -lt 5 ]; then
            sdlc_log_debug "Document found" "path=$doc"
            echo "DOCUMENT_$count=$doc"
            ((count++))
        fi
    done
else
    sdlc_log_debug "No documents found"
fi

exit 0
