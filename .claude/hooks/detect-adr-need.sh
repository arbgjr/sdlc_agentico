#!/bin/bash
#
# Hook: Detect ADR Need
# Detecta se uma mudanca arquitetural requer ADR.
# Analisa arquivos modificados e sugere criacao de ADR.
#

set -e

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
    exit 0
fi

NEEDS_ADR=0
REASONS=()

# Verificar padroes de arquivos
for pattern in "${ARCHITECTURAL_PATTERNS[@]}"; do
    if echo "$MODIFIED_FILES" | grep -i "$pattern" > /dev/null; then
        NEEDS_ADR=1
        REASONS+=("Arquivo modificado: $pattern")
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
                    break
                fi
            fi
        done
    fi
done

# Output
if [[ $NEEDS_ADR -eq 1 ]]; then
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
fi

exit 0
