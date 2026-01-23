#!/usr/bin/env bash
# doc-search - Search for documents related to keywords

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/shell/logging_utils.sh"

sdlc_set_context skill="document-enricher" phase="0"

# Parse arguments
if [ $# -eq 0 ]; then
    sdlc_log_error "Usage: /doc-search <keywords>"
    echo "Example: /doc-search OAuth 2.1 migration"
    exit 1
fi

KEYWORDS="$*"

sdlc_log_info "Searching for documents related to: $KEYWORDS"

# Run find_related.py
python3 "$SCRIPT_DIR/../skills/document-enricher/scripts/find_related.py" \
    "$KEYWORDS" \
    --output text

exit $?
