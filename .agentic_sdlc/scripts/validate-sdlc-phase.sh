#!/bin/bash
#
# validate-sdlc-phase.sh
# Valida se uma fase do SDLC foi completada corretamente
#
# Uso:
#   ./\.agentic_sdlc/scripts/validate-sdlc-phase.sh [PROJECT_PATH] [PHASE_NUMBER]
#

set -e

PROJECT_PATH="${1:-/home/armando_jr/source/repos/arbgjr/smart_alarm}"
PHASE="${2:-0}"
SDLC_PATH="$PROJECT_PATH/.agentic_sdlc"

echo "=== Validação de Fase SDLC ==="
echo "Projeto: $PROJECT_PATH"
echo "Fase: $PHASE"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Função para verificar arquivo
check_file() {
    local file="$1"
    local required="$2"

    if [[ -f "$file" ]]; then
        local size=$(stat -c %s "$file" 2>/dev/null || stat -f %z "$file" 2>/dev/null)
        echo "  ✅ $(basename "$file") (${size} bytes)"
        return 0
    else
        if [[ "$required" == "required" ]]; then
            echo "  ❌ $(basename "$file") - MISSING (REQUIRED)"
            return 1
        else
            echo "  ⚠️  $(basename "$file") - missing (optional)"
            return 0
        fi
    fi
}

# Função para validar YAML
validate_yaml() {
    local file="$1"
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "  ✅ YAML válido: $(basename "$file")"
            return 0
        else
            echo "  ❌ YAML inválido: $(basename "$file")"
            return 1
        fi
    else
        echo "  ⚠️  Python3 não encontrado, pulando validação YAML"
        return 0
    fi
}

ERRORS=0

# Verificar estrutura base
echo "[1/4] Verificando estrutura SDLC..."
if [[ ! -d "$SDLC_PATH" ]]; then
    echo "  ❌ Diretório .agentic_sdlc não encontrado"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ Diretório .agentic_sdlc existe"
fi

# Verificar projeto
echo ""
echo "[2/4] Verificando projeto..."
PROJECT_DIR=$(find "$SDLC_PATH/projects" -maxdepth 1 -type d -name "*" ! -name "projects" 2>/dev/null | head -1)
if [[ -z "$PROJECT_DIR" ]]; then
    echo "  ❌ Nenhum projeto encontrado em $SDLC_PATH/projects/"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ Projeto encontrado: $(basename "$PROJECT_DIR")"

    # Verificar manifest
    if check_file "$PROJECT_DIR/manifest.yml" "required"; then
        validate_yaml "$PROJECT_DIR/manifest.yml" || ERRORS=$((ERRORS + 1))
    else
        ERRORS=$((ERRORS + 1))
    fi
fi

# Verificar artefatos da fase
echo ""
echo "[3/4] Verificando artefatos da Phase $PHASE..."
PHASE_DIR="$PROJECT_DIR/phase-$PHASE"

case $PHASE in
    0)
        echo "Phase 0 - Preparation:"
        check_file "$PHASE_DIR/intake-analysis.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/compliance-assessment.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/compliance-summary.md" "optional"
        check_file "$PHASE_DIR/compliance-checklist.md" "optional"

        # Validar YAMLs
        if [[ -f "$PHASE_DIR/intake-analysis.yml" ]]; then
            validate_yaml "$PHASE_DIR/intake-analysis.yml" || ERRORS=$((ERRORS + 1))
        fi
        if [[ -f "$PHASE_DIR/compliance-assessment.yml" ]]; then
            validate_yaml "$PHASE_DIR/compliance-assessment.yml" || ERRORS=$((ERRORS + 1))
        fi
        ;;
    1)
        echo "Phase 1 - Discovery:"
        check_file "$PHASE_DIR/research-brief.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/technology-recommendations.md" "optional"
        ;;
    2)
        echo "Phase 2 - Requirements:"
        check_file "$PHASE_DIR/spec.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/user-stories.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/nfr.yml" "optional"
        ;;
    3)
        echo "Phase 3 - Architecture:"
        check_file "$PHASE_DIR/architecture.yml" "required" || ERRORS=$((ERRORS + 1))
        check_file "$PHASE_DIR/threat-model.yml" "required" || ERRORS=$((ERRORS + 1))
        # ADRs podem estar em subdiretório
        ADR_COUNT=$(find "$PHASE_DIR" -name "adr-*.yml" 2>/dev/null | wc -l)
        if [[ $ADR_COUNT -gt 0 ]]; then
            echo "  ✅ $ADR_COUNT ADR(s) encontrado(s)"
        else
            echo "  ⚠️  Nenhum ADR encontrado (recomendado ter pelo menos 1)"
        fi
        ;;
    *)
        echo "Validação para Phase $PHASE não implementada ainda"
        ;;
esac

# Resultado final
echo ""
echo "[4/4] Resultado..."
echo "========================================"
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ Phase $PHASE VALIDADA com sucesso!"
    echo "   Pode avançar para Phase $((PHASE + 1))"
    exit 0
else
    echo "❌ Phase $PHASE com $ERRORS erro(s)"
    echo "   Corrija os erros antes de avançar"
    exit 1
fi
