#!/bin/bash
# ensure-feature-branch.sh
# Verifica se estamos em uma branch apropriada antes de criar arquivos
# Se nao, avisa o usuario para criar branch primeiro

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="git-hooks" phase="5"
fi

# Obter branch atual
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

if [ -z "$CURRENT_BRANCH" ]; then
    sdlc_log_warn "Could not detect current branch"
    exit 0
fi

sdlc_log_debug "Checking branch" "branch=$CURRENT_BRANCH"

# Branches protegidas que nao devem ter commits diretos
PROTECTED_BRANCHES="main master develop production release"

# Verificar se estamos em branch protegida
for PROTECTED in $PROTECTED_BRANCHES; do
    if [ "$CURRENT_BRANCH" = "$PROTECTED" ]; then
        sdlc_log_warn "Protected branch detected" "branch=$CURRENT_BRANCH"
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
    sdlc_log_warn "Branch does not follow recommended pattern" "branch=$CURRENT_BRANCH"
    echo ""
    echo "AVISO: Branch '${CURRENT_BRANCH}' nao segue padrao recomendado."
    echo "Prefixos validos: feature/, fix/, hotfix/, release/, chore/, refactor/, docs/"
    echo ""
    echo "Considere usar .claude/hooks/auto-branch.sh para criar branch corretamente."
    echo ""
else
    sdlc_log_debug "Branch follows valid pattern" "branch=$CURRENT_BRANCH"
fi

# Tudo ok, continuar
exit 0
