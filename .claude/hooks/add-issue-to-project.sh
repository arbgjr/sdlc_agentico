#!/bin/bash
#
# Hook: Add Issues to GitHub Project
# Adiciona issues automaticamente ao GitHub Project V2 após criação
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Carrega lib de fallback se disponível
if [[ -f "$SCRIPT_DIR/../lib/fallback.sh" ]]; then
    source "$SCRIPT_DIR/../lib/fallback.sh"
fi

# Obtém número do project do manifest ou ambiente
get_project_number() {
    local project_num=""
    
    # Tenta obter do manifest
    if [[ -f "$REPO_ROOT/.agentic_sdlc/projects/current/manifest.yml" ]]; then
        project_num=$(grep "github_project:" "$REPO_ROOT/.agentic_sdlc/projects/current/manifest.yml" 2>/dev/null | cut -d: -f2 | tr -d ' ')
    fi
    
    # Tenta obter do estado
    if [[ -z "$project_num" ]] && [[ -f "$REPO_ROOT/.claude/memory/sdlc-state.yml" ]]; then
        project_num=$(grep "project_number:" "$REPO_ROOT/.claude/memory/sdlc-state.yml" 2>/dev/null | cut -d: -f2 | tr -d ' ')
    fi
    
    # Tenta obter via gh projects
    if [[ -z "$project_num" ]]; then
        project_num=$(gh project list --owner @me --format json 2>/dev/null | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['projects'][0]['number'] if data.get('projects') else '')" 2>/dev/null || echo "")
    fi
    
    echo "$project_num"
}

# Adiciona issue ao project
add_issue_to_project() {
    local issue_url="$1"
    local project_number="$2"
    
    if [[ -z "$issue_url" ]] || [[ -z "$project_number" ]]; then
        return 1
    fi
    
    local script="$REPO_ROOT/.claude/skills/github-projects/scripts/project_manager.py"
    
    if [[ -f "$script" ]]; then
        python3 "$script" add-item \
            --project-number "$project_number" \
            --issue-url "$issue_url" 2>/dev/null || {
            # Fallback para gh CLI
            gh project item-add "$project_number" --owner @me --url "$issue_url" 2>/dev/null || true
        }
    else
        gh project item-add "$project_number" --owner @me --url "$issue_url" 2>/dev/null || true
    fi
}

# Main - recebe URL da issue como argumento
main() {
    local issue_url="$1"
    
    if [[ -z "$issue_url" ]]; then
        echo "Uso: $0 <issue_url>"
        return 1
    fi
    
    local project_number
    project_number=$(get_project_number)
    
    if [[ -z "$project_number" ]]; then
        echo "⚠️ Nenhum GitHub Project encontrado. Issue não adicionada ao project."
        return 0
    fi
    
    echo "📋 Adicionando issue ao Project #$project_number..."
    
    if add_issue_to_project "$issue_url" "$project_number"; then
        echo "✓ Issue adicionada ao project"
    else
        echo "⚠️ Falha ao adicionar issue ao project (continuando)"
    fi
}

main "$@"
