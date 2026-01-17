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

# EXECUTAR AUTOMATICAMENTE o phase-commit (v1.7.15+)
sdlc_log_info "Executando phase-commit automaticamente" "phase=$CURRENT_PHASE"

echo ""
echo "============================================"
echo "  Auto-commit: Fase ${CURRENT_PHASE} (${PHASE_NAME})"
echo "============================================"
echo ""

# Obter PROJECT_ID
PROJECT_ID=""
if [ -f ".agentic_sdlc/.current-project" ]; then
    PROJECT_ID=$(cat .agentic_sdlc/.current-project)
fi

# Executar phase-commit.sh
PHASE_COMMIT_SCRIPT="${SCRIPT_DIR}/../skills/phase-commit/scripts/phase-commit.sh"

if [ -f "$PHASE_COMMIT_SCRIPT" ]; then
    sdlc_log_debug "Chamando phase-commit.sh" "script=$PHASE_COMMIT_SCRIPT"

    if bash "$PHASE_COMMIT_SCRIPT" "$PROJECT_ID" "$CURRENT_PHASE" "completar fase ${PHASE_NAME}"; then
        sdlc_log_info "Phase-commit executado com sucesso" "phase=$CURRENT_PHASE"
        echo ""
        echo "✓ Commit e push realizados automaticamente"
    else
        sdlc_log_error "Falha ao executar phase-commit" "phase=$CURRENT_PHASE"
        echo ""
        echo "✗ Erro ao executar phase-commit automatico"
        echo "Execute manualmente: bash $PHASE_COMMIT_SCRIPT"
    fi
else
    sdlc_log_warn "Script phase-commit.sh nao encontrado" "path=$PHASE_COMMIT_SCRIPT"
    echo ""
    echo "⚠ Script phase-commit.sh nao encontrado"
    echo "Faca commit manualmente: git add . && git commit && git push"
fi

echo ""
echo "============================================"
echo ""

# Exportar variavel para o Claude Code
echo "PHASE_COMMIT_EXECUTED=true"
echo "CURRENT_PHASE=${CURRENT_PHASE}"

exit 0
