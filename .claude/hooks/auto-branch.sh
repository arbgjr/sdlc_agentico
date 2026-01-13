#!/bin/bash
# auto-branch.sh
# Cria branches automaticamente baseado no tipo de trabalho

set -e

TYPE="${1:-feature}"  # fix, hotfix, feature, release
NAME="$2"

if [ -z "$NAME" ]; then
  echo "Uso: auto-branch.sh <tipo> <nome>"
  echo "Tipos: fix, hotfix, feature, release"
  exit 1
fi

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
    echo "Tipo desconhecido: $TYPE"
    echo "Tipos validos: fix, hotfix, feature, release, chore, refactor, docs"
    exit 1
    ;;
esac

# Verificar se estamos em um repositorio git
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "ERRO: Nao estamos em um repositorio git"
  exit 1
fi

# Verificar se ha mudancas nao commitadas
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "AVISO: Existem mudancas nao commitadas."
  echo "Considere fazer stash ou commit antes de trocar de branch."
fi

# Verificar se branch existe localmente
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  echo "Branch '${BRANCH}' ja existe localmente."
  echo "Fazendo checkout..."
  git checkout "${BRANCH}"
else
  # Verificar se existe remotamente
  if git ls-remote --exit-code --heads origin "${BRANCH}" > /dev/null 2>&1; then
    echo "Branch '${BRANCH}' existe no remoto."
    echo "Fazendo checkout com tracking..."
    git checkout -b "${BRANCH}" "origin/${BRANCH}"
  else
    echo "Criando nova branch: ${BRANCH}"
    git checkout -b "${BRANCH}"
  fi
fi

# Verificar branch atual
CURRENT=$(git branch --show-current)
if [ "$CURRENT" = "$BRANCH" ]; then
  echo ""
  echo "Branch ativa: ${BRANCH}"
  echo "Tipo: ${TYPE}"
else
  echo "ERRO: Nao foi possivel ativar a branch ${BRANCH}"
  exit 1
fi
