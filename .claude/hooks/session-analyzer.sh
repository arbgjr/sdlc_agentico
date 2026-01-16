#!/bin/bash
#
# Hook: Session Analyzer
# Extrai learnings automaticamente após transição de fase bem-sucedida.
# Executado em PostToolUse quando gate-check passa.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

# Carregar biblioteca de fallback
if [[ -f "${PROJECT_ROOT}/lib/fallback.sh" ]]; then
    source "${PROJECT_ROOT}/lib/fallback.sh"
fi

# Verificar se é uma transição de fase bem-sucedida
# Este hook é chamado pelo gate-check quando o gate passa

log_with_fallback "INFO" "Extraindo learnings da sessão" "session-analyzer-hook" 2>/dev/null || echo "[INFO] Extraindo learnings da sessão"

# Executar session-analyzer
ANALYZER_SCRIPT="${PROJECT_ROOT}/skills/session-analyzer/scripts/analyze.sh"

if [[ -f "$ANALYZER_SCRIPT" ]]; then
    bash "$ANALYZER_SCRIPT" --extract-learnings 2>/dev/null || {
        log_with_fallback "WARN" "Falha ao extrair learnings (não crítico)" "session-analyzer-hook" 2>/dev/null
    }
else
    log_with_fallback "WARN" "Script analyze.sh não encontrado" "session-analyzer-hook" 2>/dev/null
fi

exit 0
