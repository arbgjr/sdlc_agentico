#!/bin/bash
# phase-commit-reminder.sh
# Lembra o usuario de commitar apos passar um gate

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="phase-commit"
fi

# Verificar se o gate foi passado (variavel de ambiente do gate-evaluator)
GATE_RESULT="${GATE_RESULT:-}"
CURRENT_PHASE="${CURRENT_PHASE:-}"

if [ "$GATE_RESULT" != "passed" ]; then
    sdlc_log_debug "Gate not passed, skipping reminder"
    exit 0
fi

sdlc_set_context phase="$CURRENT_PHASE"

# Verificar se ha mudancas nao commitadas
CHANGES=$(git status --porcelain 2>/dev/null | wc -l)

if [ "$CHANGES" -eq 0 ]; then
    sdlc_log_debug "No uncommitted changes"
    exit 0
fi

sdlc_log_info "Uncommitted changes after gate pass" "changes=$CHANGES" "phase=$CURRENT_PHASE"

# Obter nome da fase
PHASE_NAMES=(
    "Preparation"
    "Discovery"
    "Requirements"
    "Architecture"
    "Planning"
    "Implementation"
    "Quality"
    "Release"
    "Operations"
)

if [ -n "$CURRENT_PHASE" ] && [ "$CURRENT_PHASE" -ge 0 ] && [ "$CURRENT_PHASE" -le 8 ]; then
    PHASE_NAME="${PHASE_NAMES[$CURRENT_PHASE]}"
else
    PHASE_NAME="atual"
fi

echo ""
echo "============================================"
echo "  LEMBRETE: Commit de Fase"
echo "============================================"
echo ""
echo "Voce passou o gate da fase ${CURRENT_PHASE} (${PHASE_NAME})."
echo "Existem ${CHANGES} arquivo(s) nao commitado(s)."
echo ""
echo "Recomendacao: Faca commit dos artefatos desta fase antes de prosseguir."
echo ""
echo "Voce pode usar:"
echo "  - Skill /phase-commit para commit automatico"
echo "  - git add . && git commit -m 'feat(phase-${CURRENT_PHASE}): ${PHASE_NAME}'"
echo ""
echo "============================================"
echo ""

# Exportar variavel para o Claude Code
echo "PHASE_COMMIT_SUGGESTED=true"
echo "UNCOMMITTED_CHANGES=${CHANGES}"

exit 0
