#!/bin/bash
#
# Hook: Auto Update Component Counts
# Detecta criação/exclusão de agents, skills, commands, hooks
# e atualiza automaticamente README.md e CLAUDE.md
#
# Executado em: PostToolUse
#

# Não usar set -e para evitar interrupção do fluxo
# set -e

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Carregar utilitários de log
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="auto-update-docs" phase="0"
fi

# Função de log compatível
log_info() {
    if command -v sdlc_log_info &> /dev/null; then
        sdlc_log_info "$1"
    else
        echo "[INFO] $1"
    fi
}

log_debug() {
    if command -v sdlc_log_debug &> /dev/null; then
        sdlc_log_debug "$1"
    else
        echo "[DEBUG] $1"
    fi
}

log_warning() {
    if command -v sdlc_log_warning &> /dev/null; then
        sdlc_log_warning "$1"
    else
        echo "[WARNING] $1"
    fi
}

# Verificar se há mudanças nos diretórios de componentes
cd "$PROJECT_ROOT" || exit 0

# Contar componentes ANTES (do git)
AGENTS_BEFORE=$(git ls-files .claude/agents/*.md 2>/dev/null | wc -l)
SKILLS_BEFORE=$(git ls-files .claude/skills/ 2>/dev/null | grep -c "^.claude/skills/[^/]*/$" || echo 0)
COMMANDS_BEFORE=$(git ls-files .claude/commands/*.md 2>/dev/null | wc -l)
HOOKS_BEFORE=$(git ls-files .claude/hooks/*.sh 2>/dev/null | wc -l)

# Contar componentes AGORA (filesystem)
AGENTS_NOW=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l)
SKILLS_NOW=$(find .claude/skills -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l)
COMMANDS_NOW=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)
HOOKS_NOW=$(find .claude/hooks -name "*.sh" 2>/dev/null | wc -l)

# Calcular diferenças
AGENTS_DIFF=$((AGENTS_NOW - AGENTS_BEFORE))
SKILLS_DIFF=$((SKILLS_NOW - SKILLS_BEFORE))
COMMANDS_DIFF=$((COMMANDS_NOW - COMMANDS_BEFORE))
HOOKS_DIFF=$((HOOKS_NOW - HOOKS_BEFORE))

# Se houver mudanças, atualizar documentos
if [[ $AGENTS_DIFF -ne 0 ]] || [[ $SKILLS_DIFF -ne 0 ]] || [[ $COMMANDS_DIFF -ne 0 ]] || [[ $HOOKS_DIFF -ne 0 ]]; then
    log_info "Componentes modificados detectados"

    if [[ $AGENTS_DIFF -ne 0 ]]; then
        log_info "  Agents: $AGENTS_BEFORE → $AGENTS_NOW ($AGENTS_DIFF)"
    fi

    if [[ $SKILLS_DIFF -ne 0 ]]; then
        log_info "  Skills: $SKILLS_BEFORE → $SKILLS_NOW ($SKILLS_DIFF)"
    fi

    if [[ $COMMANDS_DIFF -ne 0 ]]; then
        log_info "  Commands: $COMMANDS_BEFORE → $COMMANDS_NOW ($COMMANDS_DIFF)"
    fi

    if [[ $HOOKS_DIFF -ne 0 ]]; then
        log_info "  Hooks: $HOOKS_BEFORE → $HOOKS_NOW ($HOOKS_DIFF)"
    fi

    # Executar script de atualização
    if [[ -f "${SCRIPT_DIR}/../scripts/update-component-counts.sh" ]]; then
        log_info "Executando atualização automática de contadores..."

        # Capturar output e redirecionar stderr para stdout
        UPDATE_OUTPUT=$("${SCRIPT_DIR}/../scripts/update-component-counts.sh" 2>&1)
        UPDATE_STATUS=$?

        if [[ $UPDATE_STATUS -eq 0 ]]; then
            # Verificar se houve mudanças reais
            if git diff --quiet README.md CLAUDE.md 2>/dev/null; then
                log_debug "Contadores já estavam corretos"
            else
                log_info "📝 README.md e CLAUDE.md atualizados automaticamente"
                log_info "💡 Revisar mudanças: git diff README.md CLAUDE.md"
                log_info "💡 Commitar: git add README.md CLAUDE.md && git commit -m 'docs: update component counts'"

                # Mostrar diff resumido
                echo ""
                echo "COMPONENT_COUNTS_UPDATED=true"
                echo "AGENTS=$AGENTS_NOW"
                echo "SKILLS=$SKILLS_NOW"
                echo "COMMANDS=$COMMANDS_NOW"
                echo "HOOKS=$HOOKS_NOW"
            fi
        else
            log_warning "Falha ao atualizar contadores: $UPDATE_OUTPUT"
        fi
    else
        log_warning "Script de atualização não encontrado"
    fi
else
    log_debug "Nenhuma mudança em componentes detectada"
fi

exit 0
