#!/bin/bash
#
# Hook: Check Gate
# Verifica se o gate entre fases foi passado.
# Pode ser usado como pre-requisito antes de avancar.
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

GATE_NAME="${1:-auto}"
GATE_DIR=".claude/skills/gate-evaluator/gates"

# Auto-detectar gate baseado na fase atual
if [[ "$GATE_NAME" == "auto" ]]; then
    # Ler fase atual do arquivo de estado
    if [[ -f ".claude/memory/sdlc-state.yml" ]]; then
        CURRENT_PHASE=$(grep "current_phase:" .claude/memory/sdlc-state.yml | cut -d: -f2 | tr -d ' ')
        NEXT_PHASE=$((CURRENT_PHASE + 1))
        GATE_NAME="phase-${CURRENT_PHASE}-to-${NEXT_PHASE}"
    else
        echo -e "${YELLOW}[WARN]${NC} Estado do SDLC nao encontrado, use /sdlc-start"
        exit 0
    fi
fi

GATE_FILE="$GATE_DIR/${GATE_NAME}.yml"

if [[ ! -f "$GATE_FILE" ]]; then
    echo -e "${YELLOW}[WARN]${NC} Gate nao encontrado: $GATE_NAME"
    echo "Gates disponiveis:"
    ls -1 "$GATE_DIR" 2>/dev/null | sed 's/\.yml$//' || echo "  (nenhum)"
    exit 0
fi

echo "Verificando gate: $GATE_NAME"
echo "---"

ERRORS=0
WARNINGS=0

# Ler e verificar artefatos obrigatorios
while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name: ]]; then
        ARTIFACT_NAME=$(echo "$line" | sed 's/.*name:[[:space:]]*//' | tr -d '"')
    elif [[ "$line" =~ ^[[:space:]]*path: ]]; then
        ARTIFACT_PATH=$(echo "$line" | sed 's/.*path:[[:space:]]*//' | tr -d '"')

        # Verificar se arquivo existe
        if [[ -f "$ARTIFACT_PATH" ]] || [[ -d "$ARTIFACT_PATH" ]]; then
            echo -e "${GREEN}[OK]${NC} $ARTIFACT_NAME: $ARTIFACT_PATH"
        else
            # Verificar se e glob
            if compgen -G "$ARTIFACT_PATH" > /dev/null 2>&1; then
                echo -e "${GREEN}[OK]${NC} $ARTIFACT_NAME: $ARTIFACT_PATH (glob match)"
            else
                echo -e "${RED}[MISSING]${NC} $ARTIFACT_NAME: $ARTIFACT_PATH"
                ERRORS=$((ERRORS + 1))
            fi
        fi
    fi
done < "$GATE_FILE"

echo "---"

if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}Gate BLOQUEADO${NC}: $ERRORS artefato(s) faltando"
    exit 1
else
    echo -e "${GREEN}Gate PASSADO${NC}"
    exit 0
fi
