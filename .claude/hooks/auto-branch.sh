#!/bin/bash
# auto-branch.sh
# Cria branches automaticamente baseado no tipo de trabalho

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="git-hooks" phase="5"
fi

TYPE="${1:-feature}"  # fix, hotfix, feature, release
NAME="$2"

if [ -z "$NAME" ]; then
    sdlc_log_error "Nome da branch nao fornecido"
    echo "Uso: auto-branch.sh <tipo> <nome>"
    echo "Tipos: fix, hotfix, feature, release, chore, refactor, docs"
    exit 1
fi

sdlc_log_debug "Creating branch" "type=$TYPE" "name=$NAME"

# Normalizar nome: lowercase, espacos para hifens, remover caracteres especiais
BRANCH_NAME=$(echo "$NAME" | \
    tr '[:upper:]' '[:lower:]' | \
    tr ' ' '-' | \
    tr -cd '[:alnum:]-' | \
    sed 's/--*/-/g' | \
    sed 's/^-//' | \
    sed 's/-$//')

# Limitar tamanho do nome
if [ ${#BRANCH_NAME} -gt 50 ]; then
    BRANCH_NAME="${BRANCH_NAME:0:50}"
    sdlc_log_debug "Branch name truncated" "original_length=${#NAME}" "truncated_to=50"
fi

# Criar branch baseado no tipo
case $TYPE in
    fix)
        BRANCH="fix/${BRANCH_NAME}"
        ;;
    hotfix)
        BRANCH="hotfix/${BRANCH_NAME}"
        ;;
    feature)
        BRANCH="feature/${BRANCH_NAME}"
        ;;
    release)
        BRANCH="release/v${BRANCH_NAME}"
        ;;
    chore)
        BRANCH="chore/${BRANCH_NAME}"
        ;;
    refactor)
        BRANCH="refactor/${BRANCH_NAME}"
        ;;
    docs)
        BRANCH="docs/${BRANCH_NAME}"
        ;;
    *)
        sdlc_log_error "Tipo desconhecido" "type=$TYPE"
        echo "Tipos validos: fix, hotfix, feature, release, chore, refactor, docs"
        exit 1
        ;;
esac

sdlc_log_debug "Branch name resolved" "branch=$BRANCH"

# Verificar se estamos em um repositorio git
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    sdlc_log_error "Nao estamos em um repositorio git"
    exit 1
fi

# Verificar se ha mudancas nao commitadas
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    sdlc_log_warn "Existem mudancas nao commitadas"
    echo "Considere fazer stash ou commit antes de trocar de branch."
fi

# Verificar se branch existe localmente
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    sdlc_log_info "Branch ja existe localmente, fazendo checkout" "branch=$BRANCH"
    git checkout "${BRANCH}"
else
    # Verificar se existe remotamente
    if git ls-remote --exit-code --heads origin "${BRANCH}" > /dev/null 2>&1; then
        sdlc_log_info "Branch existe no remoto, fazendo checkout com tracking" "branch=$BRANCH"
        git checkout -b "${BRANCH}" "origin/${BRANCH}"
    else
        sdlc_log_info "Criando nova branch" "branch=$BRANCH"
        git checkout -b "${BRANCH}"
    fi
fi

# Verificar branch atual
CURRENT=$(git branch --show-current)
if [ "$CURRENT" = "$BRANCH" ]; then
    sdlc_log_info "Branch ativa com sucesso" "branch=$BRANCH" "type=$TYPE"
    echo ""
    echo "Branch ativa: ${BRANCH}"
    echo "Tipo: ${TYPE}"
else
    sdlc_log_error "Nao foi possivel ativar a branch" "branch=$BRANCH" "current=$CURRENT"
    exit 1
fi
