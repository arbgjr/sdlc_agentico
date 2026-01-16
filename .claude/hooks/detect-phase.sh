#!/bin/bash
#
# Hook: Detect Phase
# Detecta automaticamente a fase do SDLC baseado no contexto.
# Executado em UserPromptSubmit.
#

set -e

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/../lib/shell/logging_utils.sh" ]]; then
    source "${SCRIPT_DIR}/../lib/shell/logging_utils.sh"
    sdlc_set_context skill="orchestrator"
fi

sdlc_log_debug "Detecting SDLC phase"

# Detectar fase baseado em arquivos e contexto
detect_phase() {
    # Verificar se ha incidente ativo
    if [[ -f ".claude/memory/active-incident.yml" ]] || [[ -f ".agentic_sdlc/projects/*/active-incident.yml" ]]; then
        sdlc_log_debug "Incident detected"
        echo "phase:8 (incident-active)"
        return
    fi

    # Verificar arquivos de release
    if git tag --points-at HEAD 2>/dev/null | grep -q "^v"; then
        sdlc_log_debug "Release tag detected"
        echo "phase:7 (release)"
        return
    fi

    # Verificar se ha codigo novo
    STAGED_CODE=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|js|ts|java|go|cs|rb)$' || echo "")
    if [[ -n "$STAGED_CODE" ]]; then
        sdlc_log_debug "Staged code detected" "files_count=$(echo "$STAGED_CODE" | wc -l)"
        echo "phase:5 (implementation)"
        return
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
    if [[ -f ".claude/memory/current-intake.yml" ]] || [[ -f ".agentic_sdlc/projects/*/intake.yml" ]]; then
        sdlc_log_debug "Intake detected"
        echo "phase:2 (requirements)"
        return
    fi

    # Default: discovery
    sdlc_log_debug "No specific phase indicators found, defaulting to discovery"
    echo "phase:1 (discovery)"
}

# Output para SDLC
DETECTED=$(detect_phase)
sdlc_log_info "Phase detected" "phase=$DETECTED"
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

sdlc_log_debug "Suggested agent" "agent=$AGENT"
echo "SUGGESTED_AGENT=$AGENT"

exit 0
