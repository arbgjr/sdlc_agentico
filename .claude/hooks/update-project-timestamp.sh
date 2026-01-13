#!/bin/bash
# update-project-timestamp.sh
# Atualiza timestamp do projeto antes de commits

set -e

# Determinar arquivo do projeto
CURRENT_PROJECT_FILE=".agentic_sdlc/.current-project"
if [ -f "$CURRENT_PROJECT_FILE" ]; then
  PROJECT_ID=$(cat "$CURRENT_PROJECT_FILE")
else
  PROJECT_ID="default"
fi

PROJECT_FILE=".agentic_sdlc/projects/${PROJECT_ID}/manifest.yml"

# Verificar se arquivo existe
if [ ! -f "$PROJECT_FILE" ]; then
  # Tentar estrutura antiga
  PROJECT_FILE=".claude/memory/project.yml"
  if [ ! -f "$PROJECT_FILE" ]; then
    echo "Nenhum arquivo de projeto encontrado."
    exit 0
  fi
fi

# Verificar se Python esta disponivel
if ! command -v python3 &> /dev/null; then
  echo "Python3 nao encontrado. Pulando atualizacao de timestamp."
  exit 0
fi

# Atualizar timestamp
python3 << EOF
import yaml
from datetime import datetime, timezone
import sys

try:
    with open('${PROJECT_FILE}', 'r') as f:
        data = yaml.safe_load(f) or {}

    # Garantir estrutura
    if 'project' not in data:
        data['project'] = {}

    # Atualizar timestamp
    data['project']['updated_at'] = datetime.now(timezone.utc).isoformat()

    with open('${PROJECT_FILE}', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"Timestamp atualizado em ${PROJECT_FILE}")
except Exception as e:
    print(f"Aviso: Nao foi possivel atualizar timestamp: {e}")
    sys.exit(0)
EOF

# Adicionar ao staging se houver mudanca
if git diff --quiet "$PROJECT_FILE" 2>/dev/null; then
  : # Sem mudancas
else
  git add "$PROJECT_FILE"
  echo "Arquivo ${PROJECT_FILE} adicionado ao staging."
fi
