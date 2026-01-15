#!/bin/bash
#
# Hook: Detect ADR Need
# Detecta se uma mudanca arquitetural requer ADR.
# Analisa arquivos modificados e sugere criacao de ADR.
#

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="adr-author" phase="3"
fi

sdlc_log_debug "Checking for architectural changes"

# Padroes que indicam mudanca arquitetural
ARCHITECTURAL_PATTERNS=(
    "docker-compose"
    "Dockerfile"
    "kubernetes"
    "k8s"
    "terraform"
    "infrastructure"
    "config/database"
    "config/cache"
    "config/queue"
    "migrations"
    "alembic"
    "requirements.txt"
    "package.json"
    "go.mod"
    "pom.xml"
    "build.gradle"
)

# Padroes de codigo que indicam decisao arquitetural
CODE_PATTERNS=(
    "class.*Service"
    "class.*Repository"
    "class.*Controller"
    "@router\|@api_router"
    "async def"
    "celery"
    "redis"
    "kafka"
    "rabbitmq"
)

# Obter arquivos modificados
MODIFIED_FILES=$(git diff --cached --name-only 2>/dev/null || git diff HEAD~1 --name-only 2>/dev/null || echo "")

if [[ -z "$MODIFIED_FILES" ]]; then
    sdlc_log_debug "No modified files found"
    exit 0
fi

FILE_COUNT=$(echo "$MODIFIED_FILES" | wc -l)
sdlc_log_debug "Analyzing modified files" "count=$FILE_COUNT"

NEEDS_ADR=0
REASONS=()

# Verificar padroes de arquivos
for pattern in "${ARCHITECTURAL_PATTERNS[@]}"; do
    if echo "$MODIFIED_FILES" | grep -i "$pattern" > /dev/null; then
        NEEDS_ADR=1
        REASONS+=("Arquivo modificado: $pattern")
        sdlc_log_debug "Architectural pattern matched" "pattern=$pattern"
    fi
done

# Verificar padroes de codigo
for file in $MODIFIED_FILES; do
    if [[ -f "$file" ]]; then
        for pattern in "${CODE_PATTERNS[@]}"; do
            if grep -E "$pattern" "$file" > /dev/null 2>&1; then
                # Verificar se e adicao nova (nao modificacao)
                if git diff --cached "$file" 2>/dev/null | grep "^+" | grep -E "$pattern" > /dev/null; then
                    NEEDS_ADR=1
                    REASONS+=("Novo padrao em $file: $pattern")
                    sdlc_log_debug "Code pattern matched" "file=$file" "pattern=$pattern"
                    break
                fi
            fi
        done
    fi
done

# Output
if [[ $NEEDS_ADR -eq 1 ]]; then
    sdlc_log_info "ADR recommended" "reasons_count=${#REASONS[@]}"
    echo "---"
    echo "ADR_RECOMMENDED=true"
    echo "REASONS:"
    for reason in "${REASONS[@]}"; do
        echo "  - $reason"
    done
    echo ""
    echo "Considere criar um ADR para documentar esta decisao:"
    echo "  /adr-create \"Titulo da Decisao\""
    echo "---"
else
    sdlc_log_debug "No ADR needed"
fi

exit 0
