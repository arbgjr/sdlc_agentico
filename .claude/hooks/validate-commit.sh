#!/bin/bash
#
# Hook: Validate Commit
# Valida commit messages seguem Conventional Commits
# e nao contem secrets ou codigo proibido.
#

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="git-hooks" phase="5"
else
    # Fallback to simple logging
    log_error() { echo -e "\033[0;31m[BLOCKED]\033[0m $1"; }
    log_warn() { echo -e "\033[1;33m[WARNING]\033[0m $1"; }
    log_ok() { echo -e "\033[0;32m[OK]\033[0m $1"; }
fi

sdlc_log_debug "Starting commit validation"

# Obter mensagem do commit
COMMIT_MSG="${COMMIT_MSG:-$(cat .git/COMMIT_EDITMSG 2>/dev/null || echo '')}"

# Se nao tem mensagem, e dry run
if [[ -z "$COMMIT_MSG" ]]; then
    sdlc_log_warn "Nenhuma mensagem de commit para validar (dry run)"
    exit 0
fi

sdlc_log_debug "Validating commit message" "length=${#COMMIT_MSG}"

ERRORS=0

# 1. Validar Conventional Commits
CONVENTIONAL_PATTERN="^(feat|fix|refactor|docs|test|chore|ci|perf|style)(\(.+\))?: .+"

if [[ ! "$COMMIT_MSG" =~ $CONVENTIONAL_PATTERN ]]; then
    sdlc_log_error "Commit message nao segue Conventional Commits"
    echo "  Formato esperado: type(scope): description"
    echo "  Tipos validos: feat, fix, refactor, docs, test, chore, ci, perf, style"
    echo "  Exemplo: feat(orders): add order history endpoint"
    ERRORS=$((ERRORS + 1))
else
    sdlc_log_info "Conventional Commits: OK"
fi

# 2. Verificar tamanho da primeira linha
FIRST_LINE=$(echo "$COMMIT_MSG" | head -n1)
if [[ ${#FIRST_LINE} -gt 72 ]]; then
    sdlc_log_warn "Primeira linha do commit muito longa" "length=${#FIRST_LINE}" "max=72"
    ERRORS=$((ERRORS + 1))
fi

# 3. Verificar palavras proibidas na mensagem
FORBIDDEN_WORDS="TODO|FIXME|WIP|DO NOT COMMIT|secret|password|api.key"

if echo "$COMMIT_MSG" | grep -iE "$FORBIDDEN_WORDS" > /dev/null; then
    DETECTED=$(echo "$COMMIT_MSG" | grep -ioE "$FORBIDDEN_WORDS" | tr '\n' ', ')
    sdlc_log_error "Commit message contem palavras proibidas" "detected=${DETECTED}"
    ERRORS=$((ERRORS + 1))
else
    sdlc_log_info "Sem palavras proibidas: OK"
fi

# 4. Verificar arquivos staged por secrets
if command -v gitleaks &> /dev/null; then
    sdlc_log_debug "Running gitleaks scan"
    if ! gitleaks protect --staged --no-banner 2>/dev/null; then
        sdlc_log_error "Secrets detectados nos arquivos staged"
        ERRORS=$((ERRORS + 1))
    else
        sdlc_log_info "Secrets scan: OK"
    fi
else
    sdlc_log_debug "gitleaks not installed, skipping secrets scan"
fi

# 5. Verificar se ha mocks em codigo de producao
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

for file in $STAGED_FILES; do
    # Ignorar diretorio de testes
    if [[ "$file" =~ ^tests?/ ]] || [[ "$file" =~ /tests?/ ]]; then
        continue
    fi

    # Verificar por mock patterns
    if [[ -f "$file" ]]; then
        if grep -iE "(mock|stub|fake|dummy)" "$file" > /dev/null 2>&1; then
            sdlc_log_warn "Possivel mock em codigo de producao" "file=$file"
            # Nao bloqueia, apenas avisa
        fi
    fi
done

# Resultado
echo ""
if [[ $ERRORS -gt 0 ]]; then
    sdlc_log_error "Commit bloqueado" "errors=$ERRORS"
    exit 1
else
    sdlc_log_info "Commit validado com sucesso"
    exit 0
fi
