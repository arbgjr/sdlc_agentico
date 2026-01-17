#!/bin/bash
#
# Wiki Sync - Sincroniza documentacao com GitHub Wiki
#
# Usage:
#   ./wiki_sync.sh              # Sincronizacao completa
#   ./wiki_sync.sh --verbose    # Com output detalhado
#   ./wiki_sync.sh --dry-run    # Mostra o que seria feito
#

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuracoes
VERBOSE=false
DRY_RUN=false
WIKI_DIR=""
CLEANUP=true

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Output detalhado"
            echo "  --dry-run, -n    Mostra o que seria feito"
            echo "  --no-cleanup     Nao remove diretorio temporario"
            echo "  --help, -h       Mostra esta mensagem"
            exit 0
            ;;
        *)
            echo "Opcao desconhecida: $1"
            exit 1
            ;;
    esac
done

# Funcoes de log
log_info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Verificar se estamos em um repositorio git
check_repo() {
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        log_error "Nao estamos em um repositorio git"
        exit 1
    fi
}

# Obter informacoes do repositorio
get_repo_info() {
    # Verificar se estamos em repositorio GitHub
    if ! git remote get-url origin >/dev/null 2>&1; then
        log_error "Nao estamos em repositorio GitHub (sem remote 'origin')"
        echo "Configure primeiro: git remote add origin <url>" >&2
        exit 1
    fi

    REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)
    if [[ -z "$REPO" ]]; then
        log_error "Nao foi possivel detectar repositorio GitHub via gh CLI"
        echo "Verifique:" >&2
        echo "  - gh auth status" >&2
        echo "  - git remote -v" >&2
        exit 1
    fi
    log_info "Repositorio: $REPO"
}

# Clonar wiki
clone_wiki() {
    WIKI_DIR=$(mktemp -d)
    log_info "Clonando wiki para $WIKI_DIR"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] git clone https://github.com/${REPO}.wiki.git $WIKI_DIR"
        return 0
    fi

    if ! git clone "https://github.com/${REPO}.wiki.git" "$WIKI_DIR" 2>/dev/null; then
        log_error "Falha ao clonar wiki. Verifique se a wiki esta habilitada e inicializada."
        log_info "Para inicializar: Acesse https://github.com/${REPO}/wiki e crie a pagina Home"
        rm -rf "$WIKI_DIR"
        exit 1
    fi

    log_success "Wiki clonada"
}

# Criar diretorio de ADRs
setup_wiki_structure() {
    log_info "Configurando estrutura da wiki"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] mkdir -p $WIKI_DIR/ADRs"
        return 0
    fi

    mkdir -p "$WIKI_DIR/ADRs"
}

# Copiar documentos do projeto
copy_project_docs() {
    log_info "Copiando documentos do projeto"

    # Encontrar diretorio do projeto atual
    PROJECT_DOCS=""
    for dir in .agentic_sdlc/projects/*/docs; do
        if [[ -d "$dir" ]]; then
            PROJECT_DOCS="$dir"
            break
        fi
    done

    if [[ -n "$PROJECT_DOCS" ]]; then
        log_info "Docs encontrados em: $PROJECT_DOCS"

        # Copiar README como Getting-Started
        if [[ -f "$PROJECT_DOCS/README.md" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "[DRY-RUN] cp $PROJECT_DOCS/README.md $WIKI_DIR/Getting-Started.md"
            else
                cp "$PROJECT_DOCS/README.md" "$WIKI_DIR/Getting-Started.md"
                log_success "README -> Getting-Started.md"
            fi
        fi

        # Copiar ARCHITECTURE
        if [[ -f "$PROJECT_DOCS/ARCHITECTURE.md" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "[DRY-RUN] cp $PROJECT_DOCS/ARCHITECTURE.md $WIKI_DIR/Architecture.md"
            else
                cp "$PROJECT_DOCS/ARCHITECTURE.md" "$WIKI_DIR/Architecture.md"
                log_success "ARCHITECTURE.md -> Architecture.md"
            fi
        fi

        # Copiar API docs
        if [[ -f "$PROJECT_DOCS/API.md" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                echo "[DRY-RUN] cp $PROJECT_DOCS/API.md $WIKI_DIR/API-Reference.md"
            else
                cp "$PROJECT_DOCS/API.md" "$WIKI_DIR/API-Reference.md"
                log_success "API.md -> API-Reference.md"
            fi
        fi
    else
        log_warn "Nenhum diretorio de docs encontrado em .agentic_sdlc/projects/*/docs"
    fi
}

# Copiar e converter ADRs
copy_adrs() {
    log_info "Processando ADRs"

    ADR_COUNT=0

    # ADRs no corpus
    for adr in .agentic_sdlc/corpus/nodes/decisions/*.yml .agentic_sdlc/corpus/nodes/decisions/*.yaml 2>/dev/null; do
        if [[ -f "$adr" ]]; then
            convert_adr_to_md "$adr"
            ((ADR_COUNT++))
        fi
    done

    # ADRs em projetos
    for adr in .agentic_sdlc/projects/*/decisions/*.yml .agentic_sdlc/projects/*/decisions/*.yaml 2>/dev/null; do
        if [[ -f "$adr" ]]; then
            convert_adr_to_md "$adr"
            ((ADR_COUNT++))
        fi
    done

    log_info "ADRs processados: $ADR_COUNT"
}

# Converter ADR YAML para Markdown
convert_adr_to_md() {
    local adr_file="$1"
    local basename=$(basename "$adr_file" | sed 's/\.[^.]*$//')
    local output_file="$WIKI_DIR/ADRs/${basename}.md"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] Convert $adr_file -> $output_file"
        return 0
    fi

    # Extrair dados do YAML e converter para Markdown
    # Usando python para processar YAML de forma robusta
    python3 - "$adr_file" "$output_file" << 'EOF'
import sys
import yaml
from pathlib import Path

adr_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(adr_file) as f:
        data = yaml.safe_load(f)

    # Extrair campos
    adr_id = data.get('id', Path(adr_file).stem)
    title = data.get('title', 'Untitled')
    status = data.get('status', 'Proposed')
    context = data.get('context', '')
    decision = data.get('decision', '')
    consequences = data.get('consequences', {})
    alternatives = data.get('alternatives', [])
    created_at = data.get('created_at', '')
    author = data.get('author', '')

    # Gerar Markdown
    md = []
    md.append(f"# {adr_id}: {title}")
    md.append("")
    md.append(f"**Status:** {status}")
    if created_at:
        md.append(f"**Date:** {created_at}")
    if author:
        md.append(f"**Author:** {author}")
    md.append("")

    md.append("## Context")
    md.append("")
    md.append(context)
    md.append("")

    md.append("## Decision")
    md.append("")
    md.append(decision)
    md.append("")

    if alternatives:
        md.append("## Alternatives Considered")
        md.append("")
        for alt in alternatives:
            if isinstance(alt, dict):
                md.append(f"### {alt.get('name', 'Option')}")
                if alt.get('pros'):
                    md.append("**Pros:**")
                    for pro in alt.get('pros', []):
                        md.append(f"- {pro}")
                if alt.get('cons'):
                    md.append("**Cons:**")
                    for con in alt.get('cons', []):
                        md.append(f"- {con}")
            else:
                md.append(f"- {alt}")
        md.append("")

    md.append("## Consequences")
    md.append("")
    if isinstance(consequences, dict):
        if consequences.get('positive'):
            md.append("### Positive")
            for item in consequences.get('positive', []):
                md.append(f"- {item}")
        if consequences.get('negative'):
            md.append("### Negative")
            for item in consequences.get('negative', []):
                md.append(f"- {item}")
        if consequences.get('neutral'):
            md.append("### Neutral")
            for item in consequences.get('neutral', []):
                md.append(f"- {item}")
    else:
        md.append(str(consequences))
    md.append("")

    md.append("---")
    md.append("*Generated by SDLC Agentico*")

    with open(output_file, 'w') as f:
        f.write('\n'.join(md))

except Exception as e:
    print(f"Error converting {adr_file}: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [[ $? -eq 0 ]]; then
        log_success "ADR: $basename"
    fi
}

# Gerar pagina Home
generate_home() {
    log_info "Gerando Home.md"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] Generate Home.md"
        return 0
    fi

    # Obter informacoes do projeto
    PROJECT_NAME=$(basename "$(git rev-parse --show-toplevel)")
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

    cat > "$WIKI_DIR/Home.md" << EOF
# ${PROJECT_NAME}

Welcome to the ${PROJECT_NAME} documentation.

## Navigation

- [Getting Started](Getting-Started) - Quick start guide
- [Architecture](Architecture) - System architecture overview
- [API Reference](API-Reference) - API documentation
- [ADRs](ADRs) - Architecture Decision Records

## ADRs

EOF

    # Listar ADRs
    if ls "$WIKI_DIR/ADRs"/*.md &>/dev/null; then
        for adr in "$WIKI_DIR/ADRs"/*.md; do
            adr_name=$(basename "$adr" .md)
            echo "- [${adr_name}](ADRs/${adr_name})" >> "$WIKI_DIR/Home.md"
        done
    else
        echo "_No ADRs yet_" >> "$WIKI_DIR/Home.md"
    fi

    cat >> "$WIKI_DIR/Home.md" << EOF

---

_Last updated: ${TIMESTAMP}_

_Synchronized automatically by SDLC Agentico_
EOF

    log_success "Home.md gerado"
}

# Gerar sidebar
generate_sidebar() {
    log_info "Gerando _Sidebar.md"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] Generate _Sidebar.md"
        return 0
    fi

    cat > "$WIKI_DIR/_Sidebar.md" << 'EOF'
## Navigation

- [Home](Home)
- [Getting Started](Getting-Started)
- [Architecture](Architecture)
- [API Reference](API-Reference)

## ADRs

EOF

    # Listar ADRs no sidebar
    if ls "$WIKI_DIR/ADRs"/*.md &>/dev/null; then
        for adr in "$WIKI_DIR/ADRs"/*.md; do
            adr_name=$(basename "$adr" .md)
            echo "- [${adr_name}](ADRs/${adr_name})" >> "$WIKI_DIR/_Sidebar.md"
        done
    fi

    log_success "_Sidebar.md gerado"
}

# Commit e push
commit_and_push() {
    log_info "Fazendo commit e push"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] git add . && git commit && git push"
        return 0
    fi

    cd "$WIKI_DIR"

    # Verificar se ha mudancas
    if git diff --quiet && git diff --staged --quiet; then
        log_info "Nenhuma mudanca para commitar"
        return 0
    fi

    git add .

    # Commit
    git commit -m "docs: sync from SDLC $(date +%Y-%m-%d)"

    # Push
    if git push; then
        log_success "Wiki atualizada com sucesso"
    else
        log_error "Falha ao fazer push"
        return 1
    fi
}

# Cleanup
cleanup() {
    if [[ "$CLEANUP" == "true" && -n "$WIKI_DIR" && -d "$WIKI_DIR" ]]; then
        log_info "Removendo diretorio temporario"
        rm -rf "$WIKI_DIR"
    fi
}

# Trap para cleanup
trap cleanup EXIT

# Main
main() {
    echo "=== GitHub Wiki Sync ==="
    echo ""

    check_repo
    get_repo_info
    clone_wiki
    setup_wiki_structure
    copy_project_docs
    copy_adrs
    generate_home
    generate_sidebar
    commit_and_push

    echo ""
    echo "Wiki URL: https://github.com/${REPO}/wiki"
}

main
