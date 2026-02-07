#!/bin/bash
#
# Script: Update Component Counts
# Atualiza automaticamente contadores de agents, skills, commands e hooks
# em README.md e CLAUDE.md
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}🔄 Atualizando contadores de componentes...${NC}"

# Contar componentes
AGENTS=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l)
SKILLS=$(find .claude/skills -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
COMMANDS=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)
HOOKS=$(find .claude/hooks -name "*.py" 2>/dev/null | wc -l)

echo "📊 Contadores detectados:"
echo "   Agents:   $AGENTS"
echo "   Skills:   $SKILLS"
echo "   Commands: $COMMANDS"
echo "   Hooks:    $HOOKS"

# Função para atualizar contadores
update_counts() {
    local file=$1
    local temp_file="${file}.tmp"
    local updated=0

    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Arquivo não encontrado: $file${NC}"
        return 1
    fi

    cp "$file" "$temp_file"

    # README.md patterns
    if [[ "$file" == "README.md" ]]; then
        # Pattern 1: "**N agentes especializados**"
        if grep -q "\*\*[0-9]* agentes especializados\*\*" "$temp_file"; then
            sed -i "s/\*\*[0-9]* agentes especializados\*\*/\*\*$AGENTS agentes especializados\*\*/g" "$temp_file"
            updated=1
        fi

        # Pattern 2: "│  N Agentes |"
        if grep -q "│  [0-9]* Agentes |" "$temp_file"; then
            sed -i "s/│  [0-9]* Agentes |/│  $AGENTS Agentes |/g" "$temp_file"
            updated=1
        fi

        # Pattern 3: "# N agentes especializados"
        if grep -q "# [0-9]* agentes especializados" "$temp_file"; then
            sed -i "s/# [0-9]* agentes especializados/# $AGENTS agentes especializados/g" "$temp_file"
            updated=1
        fi

        # Pattern 4: "# N skills reutilizáveis"
        if grep -q "# [0-9]* skills reutilizáveis" "$temp_file"; then
            sed -i "s/# [0-9]* skills reutilizáveis/# $SKILLS skills reutilizáveis/g" "$temp_file"
            updated=1
        fi

        # Pattern 5: "# N comandos do usuário"
        if grep -q "# [0-9]* comandos do usuário" "$temp_file"; then
            sed -i "s/# [0-9]* comandos do usuário/# $COMMANDS comandos do usuário/g" "$temp_file"
            updated=1
        fi

        # Pattern 6: "# N hooks de automação"
        if grep -q "# [0-9]* hooks de automação" "$temp_file"; then
            sed -i "s/# [0-9]* hooks de automação/# $HOOKS hooks de automação/g" "$temp_file"
            updated=1
        fi
    fi

    # CLAUDE.md patterns
    if [[ "$file" == "CLAUDE.md" ]]; then
        # Pattern 1: "**N specialized agents"
        if grep -q "\*\*[0-9]* specialized agents" "$temp_file"; then
            sed -i "s/\*\*[0-9]* specialized agents/\*\*$AGENTS specialized agents/g" "$temp_file"
            updated=1
        fi

        # Pattern 2: "- N agents organized by SDLC phase"
        if grep -q "- [0-9]* agents organized by SDLC phase" "$temp_file"; then
            sed -i "s/- [0-9]* agents organized by SDLC phase/- $AGENTS agents organized by SDLC phase/g" "$temp_file"
            updated=1
        fi

        # Pattern 3: "# Agent specs (markdown) - N specialized roles"
        if grep -q "# Agent specs (markdown) - [0-9]* specialized roles" "$temp_file"; then
            sed -i "s/# Agent specs (markdown) - [0-9]* specialized roles/# Agent specs (markdown) - $AGENTS specialized roles/g" "$temp_file"
            updated=1
        fi
    fi

    # Comparar e mover se houve mudanças
    if ! cmp -s "$file" "$temp_file"; then
        mv "$temp_file" "$file"
        echo -e "${GREEN}✅ Atualizado: $file${NC}"
        return 0
    else
        rm "$temp_file"
        echo -e "${YELLOW}⏭️  Sem mudanças: $file${NC}"
        return 1
    fi
}

# Atualizar README.md
updated_files=0
if update_counts "README.md"; then
    ((updated_files++))
fi

# Atualizar CLAUDE.md
if update_counts "CLAUDE.md"; then
    ((updated_files++))
fi

echo ""
if [[ $updated_files -gt 0 ]]; then
    echo -e "${GREEN}✅ $updated_files arquivo(s) atualizado(s)${NC}"
    echo ""
    echo -e "${YELLOW}💡 Próximos passos:${NC}"
    echo "   1. Revisar as mudanças: git diff"
    echo "   2. Commitar: git add README.md CLAUDE.md && git commit -m 'docs: update component counts'"
    exit 0
else
    echo -e "${GREEN}✅ Todos os contadores já estão corretos!${NC}"
    exit 0
fi
