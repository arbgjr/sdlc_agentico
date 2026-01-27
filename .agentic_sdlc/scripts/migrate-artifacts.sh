#!/usr/bin/env bash
#
# migrate-artifacts.sh - Migra artefatos de .agentic_sdlc/ para .project/
#
# Pode ser executado a qualquer momento, mesmo após instalação.
# Detecta automaticamente se há artefatos para migrar.
#

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se há artefatos para migrar
check_artifacts_to_migrate() {
    if [[ ! -d ".agentic_sdlc" ]]; then
        log_error ".agentic_sdlc/ não encontrado!"
        exit 1
    fi

    local HAS_ARTIFACTS=false
    local PROJECT_DIRS=(
        "corpus"
        "architecture"
        "security"
        "reports"
        "references"
        "sessions"
    )

    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          MIGRAÇÃO DE ARTEFATOS - SDLC AGÊNTICO            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Verificando artefatos em .agentic_sdlc/..."
    echo ""

    declare -g -A ARTIFACTS_COUNT

    for dir in "${PROJECT_DIRS[@]}"; do
        local source_dir=".agentic_sdlc/$dir"
        if [[ -d "$source_dir" ]]; then
            local COUNT=$(find "$source_dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
            if [[ $COUNT -gt 0 ]]; then
                ARTIFACTS_COUNT["$dir"]=$COUNT
                HAS_ARTIFACTS=true
                echo "  • $dir/ ($COUNT arquivos)"
            fi
        fi
    done

    if ! $HAS_ARTIFACTS; then
        echo ""
        log_success "Nenhum artefato encontrado em .agentic_sdlc/"
        log_info "Seus artefatos já estão em .project/ ou não há artefatos para migrar."
        exit 0
    fi

    echo ""
    local TOTAL_FILES=0
    for count in "${ARTIFACTS_COUNT[@]}"; do
        TOTAL_FILES=$((TOTAL_FILES + count))
    done

    echo "Total de arquivos para migrar: $TOTAL_FILES"
    echo ""
}

# Migra artefatos para .project/
migrate_artifacts() {
    log_info "Iniciando migração de artefatos..."
    echo ""

    # Criar .project/ se não existir
    mkdir -p .project

    local MIGRATED_COUNT=0
    local MIGRATED_FILES=0

    for dir in "${!ARTIFACTS_COUNT[@]}"; do
        local source_dir=".agentic_sdlc/$dir"
        local dest_dir=".project/$dir"
        local count=${ARTIFACTS_COUNT[$dir]}

        if [[ $count -gt 0 ]]; then
            log_info "Migrando $source_dir → $dest_dir ($count arquivos)"

            # Criar destino
            mkdir -p "$dest_dir"

            # Copiar arquivos (preservando estrutura)
            if cp -r "$source_dir"/* "$dest_dir/" 2>/dev/null; then
                # Remover .gitkeep do destino se existir
                rm -f "$dest_dir/.gitkeep"

                MIGRATED_COUNT=$((MIGRATED_COUNT + 1))
                MIGRATED_FILES=$((MIGRATED_FILES + count))
                log_success "  ✓ Migrado: $count arquivos"
            else
                log_warn "  ⚠ Falha ao migrar $dir"
            fi
        fi
    done

    echo ""
    log_success "Migração completa!"
    echo ""
    echo "  Diretórios migrados: $MIGRATED_COUNT"
    echo "  Arquivos migrados:   $MIGRATED_FILES"
    echo ""
}

# Limpa .agentic_sdlc/ após migração
clean_agentic_sdlc() {
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║          LIMPEZA DE .agentic_sdlc/                         ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    log_warn "Deseja remover os artefatos de .agentic_sdlc/ agora?"
    echo ""
    echo "Os arquivos já foram copiados para .project/"
    echo "Um backup será criado antes da remoção."
    echo ""
    read -p "Remover artefatos de .agentic_sdlc/? [y/N]: " remove_choice

    if [[ "$remove_choice" =~ ^[Yy]$ ]]; then
        # Criar backup
        local BACKUP_DIR=".agentic_sdlc.artifacts-backup-$(date +%Y%m%d-%H%M%S)"
        log_info "Criando backup em $BACKUP_DIR..."

        # Copiar apenas artefatos
        mkdir -p "$BACKUP_DIR"
        for dir in "${!ARTIFACTS_COUNT[@]}"; do
            if [[ -d ".agentic_sdlc/$dir" ]]; then
                cp -r ".agentic_sdlc/$dir" "$BACKUP_DIR/" 2>/dev/null || true
            fi
        done

        log_success "Backup criado: $BACKUP_DIR"

        # Remover artefatos de .agentic_sdlc/ (manter framework)
        echo ""
        log_info "Removendo artefatos de .agentic_sdlc/..."
        for dir in "${!ARTIFACTS_COUNT[@]}"; do
            if [[ -d ".agentic_sdlc/$dir" ]]; then
                rm -rf ".agentic_sdlc/$dir"
                mkdir -p ".agentic_sdlc/$dir"
                touch ".agentic_sdlc/$dir/.gitkeep"
            fi
        done

        log_success "Artefatos removidos de .agentic_sdlc/"
        log_info "Framework mantido em .agentic_sdlc/ (scripts/, templates/, etc.)"
    else
        log_info "Artefatos mantidos em .agentic_sdlc/"
        log_warn "ATENÇÃO: Você tem duplicação agora (.agentic_sdlc/ E .project/)"
        log_warn "Recomendamos remover os artefatos de .agentic_sdlc/ após validar a migração."
    fi
}

# Verificar estrutura de .project/
verify_migration() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          VERIFICAÇÃO PÓS-MIGRAÇÃO                          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    log_info "Verificando .project/..."
    echo ""

    for dir in "${!ARTIFACTS_COUNT[@]}"; do
        local dest_dir=".project/$dir"
        if [[ -d "$dest_dir" ]]; then
            local COUNT=$(find "$dest_dir" -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
            local expected=${ARTIFACTS_COUNT[$dir]}

            if [[ $COUNT -eq $expected ]]; then
                echo "  ✓ $dir/ - $COUNT arquivos (OK)"
            else
                echo "  ⚠ $dir/ - $COUNT arquivos (esperado: $expected)"
            fi
        fi
    done

    echo ""
    log_success "Verificação completa!"
    echo ""
    log_info "Próximos passos:"
    echo "  1. Verifique manualmente os arquivos em .project/"
    echo "  2. Se tudo estiver OK, remova artefatos de .agentic_sdlc/ (se ainda não removeu)"
    echo "  3. Commit as alterações: git add .project/ && git commit -m 'chore: migrate artifacts to .project/'"
    echo ""
}

# Main
main() {
    # Verificar se está no root do projeto
    if [[ ! -d ".claude" ]]; then
        log_error "Execute este script no diretório raiz do projeto (onde está .claude/)"
        exit 1
    fi

    # Verificar artefatos
    check_artifacts_to_migrate

    # Confirmar migração
    echo -e "${CYAN}Deseja migrar estes artefatos para .project/?${NC}"
    echo ""
    read -p "Migrar agora? [Y/n]: " confirm

    if [[ ! "$confirm" =~ ^[Nn]$ ]]; then
        # Migrar
        migrate_artifacts

        # Verificar
        verify_migration

        # Perguntar sobre limpeza
        clean_agentic_sdlc
    else
        log_info "Migração cancelada."
        exit 0
    fi
}

# Executar
main
