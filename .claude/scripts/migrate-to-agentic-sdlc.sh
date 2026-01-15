#!/bin/bash
# migrate-to-agentic-sdlc.sh
# Migra estrutura de .claude/memory para .agentic_sdlc

set -e

PROJECT_ID="${1:-default}"
SOURCE=".claude/memory"
DEST=".agentic_sdlc/projects/${PROJECT_ID}"

echo "============================================"
echo "  Migracao para .agentic_sdlc"
echo "============================================"
echo ""
echo "Projeto: ${PROJECT_ID}"
echo "Origem:  ${SOURCE}"
echo "Destino: ${DEST}"
echo ""

# Verificar se fonte existe
if [ ! -d "${SOURCE}" ]; then
  echo "AVISO: Diretorio ${SOURCE} nao encontrado."
  echo "Criando estrutura vazia..."
fi

# Criar estrutura de destino
echo "Criando estrutura de diretorios..."
mkdir -p "${DEST}"/{phases,decisions,specs,security,docs,iac/{terraform,kubernetes}}
mkdir -p .agentic_sdlc/{references/{legal,technical,business,internal},templates,corpus/{indexed,pending},sessions}

# Contar arquivos a migrar
MIGRATED=0

# Migrar project.yml -> manifest.yml
if [ -f "${SOURCE}/project.yml" ]; then
  cp "${SOURCE}/project.yml" "${DEST}/manifest.yml"
  echo "[OK] project.yml -> manifest.yml"
  ((MIGRATED++))
fi

# Migrar context/ -> phases/
if [ -d "${SOURCE}/context" ]; then
  count=$(find "${SOURCE}/context" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/context/"* "${DEST}/phases/" 2>/dev/null || true
    echo "[OK] context/ -> phases/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar decisions/ -> decisions/
if [ -d "${SOURCE}/decisions" ]; then
  count=$(find "${SOURCE}/decisions" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/decisions/"* "${DEST}/decisions/" 2>/dev/null || true
    echo "[OK] decisions/ -> decisions/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar security/ -> security/
if [ -d "${SOURCE}/security" ]; then
  count=$(find "${SOURCE}/security" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/security/"* "${DEST}/security/" 2>/dev/null || true
    echo "[OK] security/ -> security/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar learnings/ -> corpus/indexed/
if [ -d "${SOURCE}/learnings" ]; then
  count=$(find "${SOURCE}/learnings" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/learnings/"* ".agentic_sdlc/corpus/indexed/" 2>/dev/null || true
    echo "[OK] learnings/ -> corpus/indexed/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar intake/ -> phases/ (como fase 0)
if [ -d "${SOURCE}/intake" ]; then
  count=$(find "${SOURCE}/intake" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    mkdir -p "${DEST}/phases/intake"
    cp -r "${SOURCE}/intake/"* "${DEST}/phases/intake/" 2>/dev/null || true
    echo "[OK] intake/ -> phases/intake/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar product/ -> specs/
if [ -d "${SOURCE}/product" ]; then
  count=$(find "${SOURCE}/product" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/product/"* "${DEST}/specs/" 2>/dev/null || true
    echo "[OK] product/ -> specs/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar sessions/
if [ -d "${SOURCE}/sessions" ]; then
  count=$(find "${SOURCE}/sessions" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r "${SOURCE}/sessions/"* ".agentic_sdlc/sessions/" 2>/dev/null || true
    echo "[OK] sessions/ -> sessions/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Migrar .claude/rag -> .agentic_sdlc/corpus
if [ -d ".claude/rag" ]; then
  count=$(find ".claude/rag" -type f 2>/dev/null | wc -l)
  if [ "$count" -gt 0 ]; then
    cp -r ".claude/rag/"* ".agentic_sdlc/corpus/" 2>/dev/null || true
    echo "[OK] .claude/rag/ -> corpus/ (${count} arquivos)"
    MIGRATED=$((MIGRATED + count))
  fi
fi

# Salvar projeto atual
echo "${PROJECT_ID}" > .agentic_sdlc/.current-project

# Criar manifest.yml se nao existir
if [ ! -f "${DEST}/manifest.yml" ]; then
  cat > "${DEST}/manifest.yml" << EOF
project:
  id: "${PROJECT_ID}"
  name: "${PROJECT_ID}"
  created_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  updated_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  current_phase: 0
  complexity_level: 2
  status: active
  metrics:
    phase_durations: {}
    decisions_count: 0
    learnings_count: 0
  tags: []
EOF
  echo "[OK] Criado manifest.yml"
fi

# Criar index de decisions se nao existir
if [ ! -f "${DEST}/decisions/index.yml" ]; then
  cat > "${DEST}/decisions/index.yml" << EOF
decisions_index:
  last_id: 0
  decisions: []
EOF
  echo "[OK] Criado decisions/index.yml"
fi

echo ""
echo "============================================"
echo "  Migracao concluida!"
echo "============================================"
echo ""
echo "Arquivos migrados: ${MIGRATED}"
echo "Projeto ativo: ${PROJECT_ID}"
echo ""
echo "Proximos passos:"
echo "  1. Verifique a estrutura: ls -la ${DEST}"
echo "  2. Remova .claude/memory quando estiver seguro"
echo "  3. Use /phase-status para ver o estado do projeto"
echo ""
