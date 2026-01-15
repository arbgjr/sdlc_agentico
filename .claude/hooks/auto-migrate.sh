#!/bin/bash
# auto-migrate.sh
# Migra automaticamente artefatos de .claude/memory para .agentic_sdlc
# Executado uma vez por sessao no UserPromptSubmit

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="memory-manager"
fi

# Arquivo de controle para evitar migracao repetida na mesma sessao
MIGRATE_MARKER="/tmp/.sdlc-migrated-$(date +%Y%m%d)"

# Se ja migrou hoje, nao migrar novamente
if [ -f "$MIGRATE_MARKER" ]; then
    sdlc_log_debug "Migration already done today, skipping"
    exit 0
fi

# Verificar se estamos em um repositorio com SDLC Agentico
if [ ! -f ".claude/settings.json" ]; then
    sdlc_log_debug "Not an SDLC Agentico repository, skipping"
    exit 0
fi

# Verificar se ha algo para migrar
if [ ! -d ".claude/memory" ]; then
    sdlc_log_debug "No .claude/memory directory found"
    touch "$MIGRATE_MARKER"
    exit 0
fi

# Verificar se .claude/memory tem arquivos
MEMORY_FILES=$(find .claude/memory -type f 2>/dev/null | wc -l)
if [ "$MEMORY_FILES" -eq 0 ]; then
    sdlc_log_debug "No files in .claude/memory"
    touch "$MIGRATE_MARKER"
    exit 0
fi

sdlc_log_info "Starting migration" "files_to_migrate=$MEMORY_FILES"

# Verificar se .agentic_sdlc existe
if [ ! -d ".agentic_sdlc" ]; then
    sdlc_log_info "Creating .agentic_sdlc directory structure"
    mkdir -p .agentic_sdlc/{projects,references,templates,corpus,sessions}
fi

# Obter ID do projeto atual
PROJECT_ID=""
if [ -f ".claude/memory/project.yml" ]; then
    PROJECT_ID=$(grep "id:" .claude/memory/project.yml | head -1 | awk '{print $2}' | tr -d '"')
fi

if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="default"
fi

DEST=".agentic_sdlc/projects/${PROJECT_ID}"
sdlc_log_debug "Migration destination" "project_id=$PROJECT_ID" "dest=$DEST"

# Migrar silenciosamente
MIGRATED=0

# Criar diretorio de destino se nao existir
mkdir -p "${DEST}"/{phases,decisions,specs,security,docs}

# Migrar decisions/
if [ -d ".claude/memory/decisions" ]; then
    count=$(find .claude/memory/decisions -type f -name "*.yml" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        for file in .claude/memory/decisions/*.yml; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                if [ ! -f "${DEST}/decisions/${filename}" ]; then
                    cp "$file" "${DEST}/decisions/"
                    sdlc_log_debug "Migrated decision" "file=$filename"
                    MIGRATED=$((MIGRATED + 1))
                fi
            fi
        done
    fi
fi

# Migrar context/ -> phases/
if [ -d ".claude/memory/context" ]; then
    count=$(find .claude/memory/context -type f 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        for file in .claude/memory/context/*; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                if [ ! -f "${DEST}/phases/${filename}" ]; then
                    cp "$file" "${DEST}/phases/"
                    sdlc_log_debug "Migrated context" "file=$filename"
                    MIGRATED=$((MIGRATED + 1))
                fi
            fi
        done
    fi
fi

# Migrar learnings/ -> corpus/learnings/
if [ -d ".claude/memory/learnings" ]; then
    mkdir -p .agentic_sdlc/corpus/learnings
    count=$(find .claude/memory/learnings -type f 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        for file in .claude/memory/learnings/*; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                if [ ! -f ".agentic_sdlc/corpus/learnings/${filename}" ]; then
                    cp "$file" .agentic_sdlc/corpus/learnings/
                    sdlc_log_debug "Migrated learning" "file=$filename"
                    MIGRATED=$((MIGRATED + 1))
                fi
            fi
        done
    fi
fi

# Migrar project.yml -> manifest.yml (se nao existir)
if [ -f ".claude/memory/project.yml" ] && [ ! -f "${DEST}/manifest.yml" ]; then
    cp .claude/memory/project.yml "${DEST}/manifest.yml"
    sdlc_log_debug "Migrated project manifest"
    MIGRATED=$((MIGRATED + 1))
fi

# Criar marcador de migracao
touch "$MIGRATE_MARKER"

# Notificar se houve migracao
if [ "$MIGRATED" -gt 0 ]; then
    sdlc_log_info "Migration completed" "files_migrated=$MIGRATED" "destination=$DEST"
    echo ""
    echo "AUTO_MIGRATED=true"
    echo "MIGRATED_FILES=${MIGRATED}"
    echo "MIGRATION_DEST=${DEST}"
    echo ""
    echo "INFO: ${MIGRATED} arquivo(s) migrado(s) de .claude/memory para ${DEST}"
    echo "Considere remover .claude/memory quando estiver seguro."
    echo ""
else
    sdlc_log_debug "No files needed migration"
fi

exit 0
