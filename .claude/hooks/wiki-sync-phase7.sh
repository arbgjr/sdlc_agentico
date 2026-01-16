#!/bin/bash
#
# Hook: Wiki Sync on Phase 7
# Sincroniza automaticamente a Wiki ao passar o gate da Phase 7 (Release)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Carrega lib de fallback se disponível
if [[ -f "$SCRIPT_DIR/../lib/fallback.sh" ]]; then
    source "$SCRIPT_DIR/../lib/fallback.sh"
fi

# Detecta fase atual
get_current_phase() {
    local phase=0
    
    if [[ -f "$REPO_ROOT/.claude/memory/sdlc-state.yml" ]]; then
        phase=$(grep "current_phase:" "$REPO_ROOT/.claude/memory/sdlc-state.yml" 2>/dev/null | head -1 | cut -d: -f2 | tr -d ' ')
    elif [[ -f "$REPO_ROOT/.agentic_sdlc/state/current_phase" ]]; then
        phase=$(cat "$REPO_ROOT/.agentic_sdlc/state/current_phase" 2>/dev/null)
    fi
    
    echo "${phase:-0}"
}

# Main
main() {
    local phase
    phase=$(get_current_phase)
    
    # Só executa na Phase 7
    if [[ "$phase" != "7" ]]; then
        return 0
    fi
    
    echo "🔄 Phase 7 detectada - Sincronizando Wiki..."
    
    local wiki_script="$REPO_ROOT/.claude/skills/github-wiki/scripts/wiki_sync.sh"
    
    if [[ ! -x "$wiki_script" ]]; then
        chmod +x "$wiki_script" 2>/dev/null || true
    fi
    
    if [[ -x "$wiki_script" ]]; then
        # Executa com retry se biblioteca fallback disponível
        if command -v retry_with_backoff &>/dev/null; then
            retry_with_backoff "$wiki_script" 3 2 || echo "⚠️ Wiki sync falhou após retries (continuando workflow)"
        else
            "$wiki_script" || echo "⚠️ Wiki sync falhou (continuando workflow)"
        fi
    else
        echo "⚠️ Script wiki_sync.sh não encontrado"
    fi
}

main "$@"
