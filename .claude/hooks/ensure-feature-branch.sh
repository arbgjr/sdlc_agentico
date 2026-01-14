#!/bin/bash
# ensure-feature-branch.sh
# Verifica se estamos em uma branch apropriada antes de criar arquivos
# Se nao, avisa o usuario para criar branch primeiro

set -e

# Obter branch atual
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

if [ -z "$CURRENT_BRANCH" ]; then
  echo "AVISO: Nao foi possivel detectar a branch atual"
  exit 0
fi

# Branches protegidas que nao devem ter commits diretos
PROTECTED_BRANCHES="main master develop production release"

# Verificar se estamos em branch protegida
for PROTECTED in $PROTECTED_BRANCHES; do
  if [ "$CURRENT_BRANCH" = "$PROTECTED" ]; then
    echo ""
    echo "============================================"
    echo "  AVISO: Branch Protegida Detectada"
    echo "============================================"
    echo ""
    echo "Voce esta na branch '${CURRENT_BRANCH}'"
    echo "Esta branch e protegida e nao deve receber commits diretos."
    echo ""
    echo "Antes de criar arquivos, crie uma branch apropriada:"
    echo ""
    echo "  Para features:"
    echo "    .claude/hooks/auto-branch.sh feature \"nome-da-feature\""
    echo ""
    echo "  Para bug fixes:"
    echo "    .claude/hooks/auto-branch.sh fix \"descricao-do-bug\""
    echo ""
    echo "  Para hotfixes:"
    echo "    .claude/hooks/auto-branch.sh hotfix \"descricao-urgente\""
    echo ""
    echo "Ou use os comandos do SDLC:"
    echo "  /sdlc-start \"Descricao do projeto\""
    echo "  /new-feature \"Nome da feature\""
    echo "  /quick-fix \"Descricao do bug\""
    echo ""
    echo "============================================"
    echo ""

    # Exportar variavel para o Claude Code saber que precisa criar branch
    echo "BRANCH_REQUIRED=true"
    echo "SUGGESTED_BRANCH_TYPE=feature"
    exit 0
  fi
done

# Verificar se a branch segue padrao valido
VALID_PREFIXES="feature/ fix/ hotfix/ release/ chore/ refactor/ docs/"
VALID=false

for PREFIX in $VALID_PREFIXES; do
  if [[ "$CURRENT_BRANCH" == ${PREFIX}* ]]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = false ]; then
  echo ""
  echo "AVISO: Branch '${CURRENT_BRANCH}' nao segue padrao recomendado."
  echo "Prefixos validos: feature/, fix/, hotfix/, release/, chore/, refactor/, docs/"
  echo ""
  echo "Considere usar .claude/hooks/auto-branch.sh para criar branch corretamente."
  echo ""
fi

# Tudo ok, continuar
exit 0
