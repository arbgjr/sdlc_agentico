#!/bin/bash
# =============================================================================
# Report SDLC Bug - Reporta bugs do SDLC Agêntico ao owner (arbgjr).
# =============================================================================
# Cria GitHub issue no repositório arbgjr/sdlc_agentico para reportar bugs.
#
# Usage: report_sdlc_bug.sh classified_errors.json
# =============================================================================

set -euo pipefail

CLASSIFIED_JSON="${1:-}"

if [[ -z "$CLASSIFIED_JSON" ]] || [[ ! -f "$CLASSIFIED_JSON" ]]; then
    echo "✗ Arquivo de erros não encontrado: $CLASSIFIED_JSON" >&2
    exit 1
fi

# Extrair bugs do SDLC
SDLC_BUGS_COUNT=$(jq -r '.summary.sdlc_bugs' "$CLASSIFIED_JSON" 2>/dev/null || echo "0")

if [[ "$SDLC_BUGS_COUNT" -eq 0 ]]; then
    echo "✓ Nenhum bug do SDLC para reportar"
    exit 0
fi

echo "📤 Reportando $SDLC_BUGS_COUNT bugs do SDLC Agêntico ao owner..."

# Gerar título do issue
ISSUE_TITLE="[Auto-Report] $SDLC_BUGS_COUNT bugs detectados na execução"

# Gerar body do issue
ISSUE_BODY=$(cat <<EOF
## 🐛 Bugs Detectados Automaticamente

**Total de bugs**: $SDLC_BUGS_COUNT
**Reportado em**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Projeto**: $(git remote get-url origin 2>/dev/null || echo "unknown")
**Branch**: $(git branch --show-current 2>/dev/null || echo "unknown")
**Commit**: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

---

### Detalhes dos Bugs

$(jq -r '.sdlc_bugs[] | "#### Bug #\((.timestamp | tostring)[-6:])

**Classificação**: \(.classification.classification) (confidence: \(.classification.confidence * 100 | floor)%)
**Skill**: \(.skill)
**Script**: \(.script // "N/A")
**Timestamp**: \(.timestamp | todate)

**Mensagem**:
\`\`\`
\(.message)
\`\`\`

**Razão**:
\(.classification.reason)

---
"' "$CLASSIFIED_JSON")

### Contexto Adicional

Esses bugs foram detectados automaticamente durante a execução do SDLC Agêntico.
A análise de erros do Loki identificou esses problemas como bugs do framework.

**Ação Recomendada**:
1. Investigar os erros listados acima
2. Corrigir os bugs no framework
3. Criar hotfix se necessário
4. Atualizar testes para prevenir regressão

EOF
)

# Criar issue no repositório do SDLC Agêntico
REPO_OWNER="arbgjr"
REPO_NAME="sdlc_agentico"

echo "Criando GitHub issue em ${REPO_OWNER}/${REPO_NAME}..."

# Tentar criar issue
if gh issue create \
    --repo "${REPO_OWNER}/${REPO_NAME}" \
    --title "$ISSUE_TITLE" \
    --body "$ISSUE_BODY" \
    --label "bug,auto-report" 2>/dev/null; then
    echo "✓ Issue criado com sucesso no repositório ${REPO_OWNER}/${REPO_NAME}"
else
    echo "⚠ Falha ao criar issue. Salvando report local..."

    # Salvar localmente se falhar
    REPORT_FILE=".agentic_sdlc/bug-reports/report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$REPORT_FILE")"

    cat > "$REPORT_FILE" <<EOF
# Bug Report

$ISSUE_BODY

---

**NOTA**: Este report foi salvo localmente porque não foi possível criar GitHub issue.
Para reportar manualmente, acesse: https://github.com/${REPO_OWNER}/${REPO_NAME}/issues/new
EOF

    echo "   Report salvo em: $REPORT_FILE"
    echo "   Por favor, reporte manualmente: https://github.com/${REPO_OWNER}/${REPO_NAME}/issues/new"
fi

exit 0
