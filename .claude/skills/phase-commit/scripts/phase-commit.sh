#!/bin/bash
# phase-commit.sh
# Commita e faz PUSH de artefatos ao final de cada fase do SDLC

set -e

# Carregar logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../../../lib/shell/logging_utils.sh" 2>/dev/null || true

PROJECT_ID="${1:-}"
PHASE="${2:-}"
MESSAGE="${3:-}"

sdlc_set_context skill="phase-commit" phase="${PHASE:-unknown}"
sdlc_log_info "Iniciando phase-commit" "project_id=$PROJECT_ID phase=$PHASE"

# Obter fase atual se nao especificada
if [ -z "$PHASE" ]; then
  if [ -f ".claude/memory/project.yml" ]; then
    PHASE=$(grep "current_phase:" .claude/memory/project.yml | awk '{print $2}')
  elif [ -f ".agentic_sdlc/.current-project" ]; then
    CURRENT_PROJECT=$(cat .agentic_sdlc/.current-project)
    if [ -f ".agentic_sdlc/projects/${CURRENT_PROJECT}/manifest.yml" ]; then
      PHASE=$(grep "current_phase:" ".agentic_sdlc/projects/${CURRENT_PROJECT}/manifest.yml" | awk '{print $2}')
    fi
  fi
fi

if [ -z "$PHASE" ]; then
  sdlc_log_error "Nao foi possivel determinar a fase atual"
  exit 1
fi

sdlc_log_debug "Fase detectada: $PHASE"

# Mapear tipo de commit
case $PHASE in
  0|1|4|8) TYPE="docs" ;;
  2|3|5)   TYPE="feat" ;;
  6)       TYPE="test" ;;
  7)       TYPE="chore" ;;
  *)       TYPE="chore" ;;
esac

# Nomes das fases
PHASE_NAMES=(
  "Preparation"
  "Discovery"
  "Requirements"
  "Architecture"
  "Planning"
  "Implementation"
  "Quality"
  "Release"
  "Operations"
)

PHASE_NAME="${PHASE_NAMES[$PHASE]}"
sdlc_log_info "Processando fase" "phase_name=$PHASE_NAME type=$TYPE"

# Verificar se ha mudancas
if git diff --quiet && git diff --cached --quiet; then
  sdlc_log_warn "Nenhuma mudanca para commitar" "phase=$PHASE"
  echo "Nenhuma mudanca para commitar na fase ${PHASE} (${PHASE_NAME})"
  exit 0
fi

# Adicionar arquivos nao rastreados
sdlc_log_debug "Adicionando arquivos ao staging"
git add -A

# Verificar novamente apos adicionar
if git diff --cached --quiet; then
  sdlc_log_warn "Nenhuma mudanca staged" "phase=$PHASE"
  echo "Nenhuma mudanca staged para commitar"
  exit 0
fi

# Gerar lista de arquivos
FILES=$(git diff --cached --name-only | head -20)
FILE_COUNT=$(git diff --cached --name-only | wc -l)

sdlc_log_info "Arquivos modificados" "count=$FILE_COUNT"

# Mensagem de commit
if [ -z "$MESSAGE" ]; then
  MESSAGE="artefatos da fase ${PHASE_NAME}"
fi

# Criar commit
COMMIT_MSG=$(cat <<EOF
${TYPE}(phase-${PHASE}): ${MESSAGE}

Fase: ${PHASE_NAME}
Projeto: ${PROJECT_ID}
Arquivos: ${FILE_COUNT}

Artefatos criados/modificados:
${FILES}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)

git commit -m "$COMMIT_MSG"
COMMIT_HASH=$(git rev-parse --short HEAD)

sdlc_log_info "Commit criado" "hash=$COMMIT_HASH files=$FILE_COUNT"

echo ""
echo "============================================"
echo "  ✓ Commit da Fase ${PHASE} Criado"
echo "============================================"
echo "Fase: ${PHASE_NAME}"
echo "Hash: ${COMMIT_HASH}"
echo "Arquivos: ${FILE_COUNT}"
echo ""

# PUSH AUTOMATICO para remote
if git remote get-url origin >/dev/null 2>&1; then
  CURRENT_BRANCH=$(git branch --show-current)

  sdlc_log_info "Fazendo push para remote" "branch=$CURRENT_BRANCH"

  # Verificar se branch tem remote
  if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    # Branch ja tem upstream, apenas push
    if git push; then
      sdlc_log_info "Push realizado com sucesso" "branch=$CURRENT_BRANCH"
      echo "✓ Push realizado para origin/${CURRENT_BRANCH}"
    else
      sdlc_log_error "Falha ao fazer push" "branch=$CURRENT_BRANCH"
      echo "✗ Erro ao fazer push. Execute manualmente: git push"
      exit 1
    fi
  else
    # Branch nao tem upstream, criar
    if git push -u origin "$CURRENT_BRANCH"; then
      sdlc_log_info "Push com upstream criado" "branch=$CURRENT_BRANCH"
      echo "✓ Push realizado e upstream configurado: origin/${CURRENT_BRANCH}"
    else
      sdlc_log_error "Falha ao fazer push com upstream" "branch=$CURRENT_BRANCH"
      echo "✗ Erro ao fazer push. Execute manualmente: git push -u origin ${CURRENT_BRANCH}"
      exit 1
    fi
  fi
else
  sdlc_log_warn "Sem remote configurado" "skip_push=true"
  echo "⚠ Nenhum remote configurado. Commit local criado apenas."
fi

# Atualizar manifest com commit hash (se existir)
if [ -n "$PROJECT_ID" ] && [ -f ".agentic_sdlc/projects/${PROJECT_ID}/manifest.yml" ]; then
  MANIFEST=".agentic_sdlc/projects/${PROJECT_ID}/manifest.yml"

  # Adicionar hash do commit ao manifest
  if grep -q "phases_completed:" "$MANIFEST"; then
    # Verificar se fase ja esta na lista
    if ! grep -q "  - phase: ${PHASE}" "$MANIFEST"; then
      # Adicionar fase com hash
      sed -i "/phases_completed:/a\\  - phase: ${PHASE}\n    commit: ${COMMIT_HASH}\n    completed_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$MANIFEST"
      sdlc_log_info "Manifest atualizado" "phase=$PHASE commit=$COMMIT_HASH"
    fi
  fi
fi

echo ""
echo "============================================"
echo "  ✓ Fase ${PHASE} (${PHASE_NAME}) Completa"
echo "============================================"
echo ""

sdlc_log_info "Phase commit completo" "phase=$PHASE commit=$COMMIT_HASH pushed=true"
