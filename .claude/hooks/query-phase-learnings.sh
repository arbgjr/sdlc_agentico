#!/bin/bash
# =============================================================================
# Query Phase Learnings Hook
# =============================================================================
# Consulta corpus RAG por learnings relevantes da fase atual no INÍCIO da sessão.
# Exibe warnings/dicas ao usuário antes de iniciar trabalho.
#
# Triggered: UserPromptSubmit (início da sessão)
# =============================================================================

set -euo pipefail

# Carregar libs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
source "${SCRIPT_DIR}/../lib/fallback.sh"

sdlc_set_context skill="query-phase-learnings" phase="${SDLC_PHASE:-0}"

# Detectar fase atual
CURRENT_PHASE="${SDLC_PHASE:-0}"

if [[ "$CURRENT_PHASE" == "phase:"* ]]; then
    CURRENT_PHASE="${CURRENT_PHASE#phase:}"
fi

# Se não detectou fase, tentar do manifest
if [[ -z "$CURRENT_PHASE" ]] || [[ "$CURRENT_PHASE" == "0" ]]; then
    MANIFEST_PATH=".agentic_sdlc/projects/current.json"
    if [[ -f "$MANIFEST_PATH" ]]; then
        CURRENT_PHASE=$(jq -r '.current_phase // 0' "$MANIFEST_PATH" 2>/dev/null || echo "0")
    fi
fi

sdlc_log_debug "Consultando learnings para Phase $CURRENT_PHASE" "phase=$CURRENT_PHASE"

# Consultar corpus RAG por learnings da fase
CORPUS_LEARNINGS_DIR=".agentic_sdlc/corpus/nodes/learnings"

if [[ ! -d "$CORPUS_LEARNINGS_DIR" ]]; then
    sdlc_log_debug "Corpus learnings não encontrado, pulando" ""
    exit 0
fi

# Buscar learnings relevantes para a fase atual
RELEVANT_LEARNINGS=$(find "$CORPUS_LEARNINGS_DIR" -name "*.yml" -o -name "*.yaml" | \
    xargs grep -l "phase.*$CURRENT_PHASE" 2>/dev/null || true)

if [[ -z "$RELEVANT_LEARNINGS" ]]; then
    sdlc_log_info "Nenhum learning anterior encontrado para Phase $CURRENT_PHASE" ""
    exit 0
fi

# Exibir learnings ao usuário
LEARNINGS_COUNT=$(echo "$RELEVANT_LEARNINGS" | wc -l)
sdlc_log_info "Encontrados $LEARNINGS_COUNT learnings anteriores para Phase $CURRENT_PHASE" ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📚 LEARNINGS DA FASE $CURRENT_PHASE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Parsear e exibir cada learning
COUNTER=1
while IFS= read -r learning_file; do
    TITLE=$(grep -m1 "^title:" "$learning_file" | cut -d':' -f2- | xargs 2>/dev/null || echo "Sem título")
    TYPE=$(grep -m1 "^type:" "$learning_file" | cut -d':' -f2- | xargs 2>/dev/null || echo "learning")
    DESCRIPTION=$(grep -A3 "^description:" "$learning_file" | tail -n +2 | sed 's/^  - /• /' 2>/dev/null || echo "")

    echo ""
    echo "[$COUNTER] $TYPE: $TITLE"
    if [[ -n "$DESCRIPTION" ]]; then
        echo "$DESCRIPTION"
    fi

    COUNTER=$((COUNTER + 1))
done <<< "$RELEVANT_LEARNINGS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sdlc_log_info "Learnings exibidos ao usuário" "count=$LEARNINGS_COUNT"

exit 0
