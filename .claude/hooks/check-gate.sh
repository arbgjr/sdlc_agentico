#!/bin/bash
#
# Hook: Check Gate
# Verifica se o gate entre fases foi passado.
# Pode ser usado como pre-requisito antes de avancar.
#

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="gate-evaluator"
fi

GATE_NAME="${1:-auto}"
GATE_DIR=".claude/skills/gate-evaluator/gates"

sdlc_log_debug "Starting gate check" "gate=$GATE_NAME"

# Auto-detectar gate baseado na fase atual
if [[ "$GATE_NAME" == "auto" ]]; then
    # Ler fase atual do arquivo de estado
    if [[ -f ".claude/memory/sdlc-state.yml" ]]; then
        CURRENT_PHASE=$(grep "current_phase:" .claude/memory/sdlc-state.yml | cut -d: -f2 | tr -d ' ')
        NEXT_PHASE=$((CURRENT_PHASE + 1))
        GATE_NAME="phase-${CURRENT_PHASE}-to-${NEXT_PHASE}"
        sdlc_log_debug "Auto-detected gate" "from_phase=$CURRENT_PHASE" "to_phase=$NEXT_PHASE" "gate=$GATE_NAME"
    elif [[ -f ".agentic_sdlc/projects/current/state.yml" ]]; then
        CURRENT_PHASE=$(grep "current_phase:" .agentic_sdlc/projects/current/state.yml | cut -d: -f2 | tr -d ' ')
        NEXT_PHASE=$((CURRENT_PHASE + 1))
        GATE_NAME="phase-${CURRENT_PHASE}-to-${NEXT_PHASE}"
        sdlc_log_debug "Auto-detected gate from agentic_sdlc" "from_phase=$CURRENT_PHASE" "to_phase=$NEXT_PHASE"
    else
        sdlc_log_warn "Estado do SDLC nao encontrado, use /sdlc-start"
        exit 0
    fi
fi

sdlc_set_context phase="$CURRENT_PHASE"

GATE_FILE="$GATE_DIR/${GATE_NAME}.yml"

if [[ ! -f "$GATE_FILE" ]]; then
    sdlc_log_warn "Gate nao encontrado" "gate=$GATE_NAME" "path=$GATE_FILE"
    echo "Gates disponiveis:"
    ls -1 "$GATE_DIR" 2>/dev/null | sed 's/\.yml$//' || echo "  (nenhum)"
    exit 0
fi

sdlc_log_info "Verificando gate" "gate=$GATE_NAME"
echo "Verificando gate: $GATE_NAME"
echo "---"

ERRORS=0
WARNINGS=0
CHECKS=0

# Ler e verificar artefatos obrigatorios
while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name: ]]; then
        ARTIFACT_NAME=$(echo "$line" | sed 's/.*name:[[:space:]]*//' | tr -d '"')
    elif [[ "$line" =~ ^[[:space:]]*path: ]]; then
        ARTIFACT_PATH=$(echo "$line" | sed 's/.*path:[[:space:]]*//' | tr -d '"')
        CHECKS=$((CHECKS + 1))

        # Verificar se arquivo existe
        if [[ -f "$ARTIFACT_PATH" ]] || [[ -d "$ARTIFACT_PATH" ]]; then
            sdlc_log_debug "Artifact found" "name=$ARTIFACT_NAME" "path=$ARTIFACT_PATH"
            echo -e "\033[0;32m[OK]\033[0m $ARTIFACT_NAME: $ARTIFACT_PATH"
        else
            # Verificar se e glob
            if compgen -G "$ARTIFACT_PATH" > /dev/null 2>&1; then
                sdlc_log_debug "Artifact found (glob)" "name=$ARTIFACT_NAME" "pattern=$ARTIFACT_PATH"
                echo -e "\033[0;32m[OK]\033[0m $ARTIFACT_NAME: $ARTIFACT_PATH (glob match)"
            else
                sdlc_log_error "Artifact missing" "name=$ARTIFACT_NAME" "path=$ARTIFACT_PATH"
                echo -e "\033[0;31m[MISSING]\033[0m $ARTIFACT_NAME: $ARTIFACT_PATH"
                ERRORS=$((ERRORS + 1))
            fi
        fi
    fi
done < "$GATE_FILE"

echo "---"

if [[ $ERRORS -gt 0 ]]; then
    sdlc_log_error "Gate BLOQUEADO" "gate=$GATE_NAME" "errors=$ERRORS" "checks=$CHECKS"
    echo -e "\033[0;31mGate BLOQUEADO\033[0m: $ERRORS artefato(s) faltando"
    exit 1
else
    sdlc_log_info "Gate PASSADO" "gate=$GATE_NAME" "checks=$CHECKS"
    echo -e "\033[0;32mGate PASSADO\033[0m"
    exit 0
fi
