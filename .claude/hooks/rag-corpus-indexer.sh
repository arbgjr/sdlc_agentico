#!/bin/bash
#
# Hook: RAG Corpus Indexer
# Indexa automaticamente novos conteúdos no RAG corpus
# Triggers: Criação de ADRs, conclusão de fases, extração de learnings
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Carrega lib de logging se disponível
if [[ -f "$SCRIPT_DIR/../lib/logging.sh" ]]; then
    source "$SCRIPT_DIR/../lib/logging.sh"
fi

# Diretórios do corpus
CORPUS_DIR="$REPO_ROOT/.agentic_sdlc/corpus"
CORPUS_DECISIONS="$CORPUS_DIR/nodes/decisions"
CORPUS_LEARNINGS="$CORPUS_DIR/nodes/learnings"
CORPUS_INDEX="$CORPUS_DIR/index.yml"

# Garante estrutura
ensure_structure() {
    mkdir -p "$CORPUS_DECISIONS" 2>/dev/null || true
    mkdir -p "$CORPUS_LEARNINGS" 2>/dev/null || true
    mkdir -p "$CORPUS_DIR/nodes/patterns" 2>/dev/null || true
    mkdir -p "$CORPUS_DIR/nodes/docs" 2>/dev/null || true
}

# Indexa ADRs
index_adrs() {
    local count=0
    
    # Busca ADRs em vários locais
    for adr_file in \
        "$REPO_ROOT/.agentic_sdlc/projects"/*/decisions/adr-*.yml \
        "$REPO_ROOT/.claude/memory/decisions/"adr-*.yml \
        "$CORPUS_DECISIONS"/adr-*.yml; do
        
        if [[ -f "$adr_file" ]]; then
            ((count++))
        fi
    done
    
    echo "ADRs indexados: $count"
}

# Indexa learnings das sessões
index_learnings() {
    local count=0
    local sessions_dir="$REPO_ROOT/.agentic_sdlc/sessions"
    
    if [[ -d "$sessions_dir" ]]; then
        for session_file in "$sessions_dir"/*.yml; do
            if [[ -f "$session_file" ]]; then
                # Extrai learnings da sessão
                local learnings
                learnings=$(grep -A 100 "learnings:" "$session_file" 2>/dev/null | head -50 || true)
                
                if [[ -n "$learnings" ]]; then
                    ((count++))
                fi
            fi
        done
    fi
    
    echo "Sessões com learnings: $count"
}

# Atualiza índice do corpus
update_index() {
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    local adr_count
    adr_count=$(find "$CORPUS_DECISIONS" -name "adr-*.yml" 2>/dev/null | wc -l)
    
    local learning_count
    learning_count=$(find "$CORPUS_LEARNINGS" -name "*.yml" 2>/dev/null | wc -l)
    
    cat > "$CORPUS_INDEX" << EOF
# RAG Corpus Index
# Atualizado automaticamente pelo hook rag-corpus-indexer
#
index:
  updated_at: "$timestamp"
  
  stats:
    total_nodes: $((adr_count + learning_count))
    decisions: $adr_count
    learnings: $learning_count
    
  sources:
    decisions:
      - "$CORPUS_DECISIONS"
      - ".agentic_sdlc/projects/*/decisions"
      - ".claude/memory/decisions"
    learnings:
      - "$CORPUS_LEARNINGS"
      - ".agentic_sdlc/sessions"
    patterns:
      - "$CORPUS_DIR/nodes/patterns"
    docs:
      - "$CORPUS_DIR/nodes/docs"
      - ".agentic_sdlc/references"
      
  search_paths:
    - ".agentic_sdlc/corpus"
    - ".agentic_sdlc/projects"
    - ".agentic_sdlc/references"
    - ".claude/memory"
    - ".claude/knowledge"
EOF
    
    echo "Índice atualizado: $CORPUS_INDEX"
}

# Extrai learnings da sessão atual (se session-analyzer disponível)
extract_session_learnings() {
    local analyzer_script="$REPO_ROOT/.claude/skills/session-analyzer/scripts/extract_learnings.py"

    if [[ -f "$analyzer_script" ]]; then
        # Flag correta é --output-dir, não --output
        python3 "$analyzer_script" --persist --output-dir "$CORPUS_LEARNINGS" 2>/dev/null || true
    fi
}

# Main
main() {
    echo "🔄 Indexando RAG Corpus..."
    
    ensure_structure
    index_adrs
    index_learnings
    update_index
    
    # Tenta extrair learnings da sessão atual
    extract_session_learnings
    
    echo "✓ RAG Corpus indexado"
}

main "$@"
