#!/bin/bash
#
# Hook: Detect Phase
# Detecta automaticamente a fase do SDLC baseado no contexto.
# Executado em UserPromptSubmit.
#

# Nao usar set -e para permitir fallback gracioso
# set -e

# Diretorio do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Carregar biblioteca de fallback (se existir)
if [[ -f "${PROJECT_ROOT}/.claude/lib/fallback.sh" ]]; then
    source "${PROJECT_ROOT}/.claude/lib/fallback.sh"
else
    # Fallback minimo se biblioteca nao existe
    log_with_fallback() { echo "[${1:-INFO}] $2"; }
fi

# Carregar utilitarios antigos (compatibilidade)
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="orchestrator"
fi

# Funcao de log compativel
sdlc_log_debug() {
    log_with_fallback "DEBUG" "$*" "detect-phase" 2>/dev/null || echo "[DEBUG] $*"
}

sdlc_log_info() {
    log_with_fallback "INFO" "$*" "detect-phase" 2>/dev/null || echo "[INFO] $*"
}

sdlc_log_debug "Detecting SDLC phase"

# Detectar fase baseado em arquivos e contexto
detect_phase() {
    # Verificar se ha incidente ativo
    if [[ -f ".claude/memory/active-incident.yml" ]] || ls .agentic_sdlc/projects/*/active-incident.yml 2>/dev/null | head -1 | grep -q .; then
        sdlc_log_debug "Incident detected"
        echo "phase:8 (incident-active)"
        return
    fi

    # Verificar arquivos de release (com fallback se git nao disponivel)
    if command -v git >/dev/null 2>&1; then
        if git tag --points-at HEAD 2>/dev/null | grep -q "^v"; then
            sdlc_log_debug "Release tag detected"
            echo "phase:7 (release)"
            return
        fi

        # Verificar se ha codigo novo
        STAGED_CODE=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|js|ts|java|go|cs|rb)$' || echo "")
        if [[ -n "$STAGED_CODE" ]]; then
            local file_count=$(echo "$STAGED_CODE" | wc -l)
            sdlc_log_debug "Staged code detected: $file_count files"
            echo "phase:5 (implementation)"
            return
        fi
    fi

    # Verificar se ha specs
    if [[ -d ".specify/specs" ]] && [[ "$(ls -A .specify/specs 2>/dev/null)" ]]; then
        if [[ -d ".specify/plans" ]] && [[ "$(ls -A .specify/plans 2>/dev/null)" ]]; then
            sdlc_log_debug "Plans detected"
            echo "phase:4 (planning)"
        else
            sdlc_log_debug "Specs detected without plans"
            echo "phase:3 (architecture)"
        fi
        return
    fi

    # Verificar se ha intake
    if [[ -f ".claude/memory/current-intake.yml" ]] || ls .agentic_sdlc/projects/*/intake.yml 2>/dev/null | head -1 | grep -q .; then
        sdlc_log_debug "Intake detected"
        echo "phase:2 (requirements)"
        return
    fi

    # Verificar manifest de projeto existente
    if ls .agentic_sdlc/projects/*/manifest.yml 2>/dev/null | head -1 | grep -q .; then
        # Ler fase do manifest
        local manifest=$(ls .agentic_sdlc/projects/*/manifest.yml 2>/dev/null | head -1)
        if [[ -f "$manifest" ]]; then
            local phase=$(grep -E "^current_phase:" "$manifest" 2>/dev/null | cut -d: -f2 | tr -d ' ')
            if [[ -n "$phase" ]]; then
                sdlc_log_debug "Phase from manifest: $phase"
                echo "phase:$phase (from-manifest)"
                return
            fi
        fi
    fi

    # Default: discovery
    sdlc_log_debug "No specific phase indicators found, defaulting to discovery"
    echo "phase:1 (discovery)"
}

# Output para SDLC
DETECTED=$(detect_phase)
sdlc_log_info "Phase detected: $DETECTED"
echo "SDLC_PHASE=$DETECTED"

# Sugerir agente apropriado
case "$DETECTED" in
    phase:0*)
        AGENT="intake-analyst"
        ;;
    phase:1*)
        AGENT="domain-researcher"
        ;;
    phase:2*)
        AGENT="requirements-analyst"
        ;;
    phase:3*)
        AGENT="system-architect"
        ;;
    phase:4*)
        AGENT="delivery-planner"
        ;;
    phase:5*)
        AGENT="code-author"
        ;;
    phase:6*)
        AGENT="security-scanner"
        ;;
    phase:7*)
        AGENT="release-manager"
        ;;
    phase:8*)
        AGENT="incident-commander"
        ;;
    *)
        AGENT="orchestrator"
        ;;
esac

sdlc_log_debug "Suggested agent: $AGENT"
echo "SUGGESTED_AGENT=$AGENT"

exit 0
