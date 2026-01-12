#!/bin/bash
#
# Hook: Detect Phase
# Detecta automaticamente a fase do SDLC baseado no contexto.
# Executado em UserPromptSubmit.
#

set -e

# Detectar fase baseado em arquivos e contexto
detect_phase() {
    # Verificar se ha incidente ativo
    if [[ -f ".claude/memory/active-incident.yml" ]]; then
        echo "phase:8 (incident-active)"
        return
    fi

    # Verificar arquivos de release
    if git tag --points-at HEAD 2>/dev/null | grep -q "^v"; then
        echo "phase:7 (release)"
        return
    fi

    # Verificar se ha codigo novo
    STAGED_CODE=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|js|ts|java|go)$' || echo "")
    if [[ -n "$STAGED_CODE" ]]; then
        echo "phase:5 (implementation)"
        return
    fi

    # Verificar se ha specs
    if [[ -d ".specify/specs" ]] && [[ "$(ls -A .specify/specs 2>/dev/null)" ]]; then
        if [[ -d ".specify/plans" ]] && [[ "$(ls -A .specify/plans 2>/dev/null)" ]]; then
            echo "phase:4 (planning)"
        else
            echo "phase:3 (architecture)"
        fi
        return
    fi

    # Verificar se ha intake
    if [[ -f ".claude/memory/current-intake.yml" ]]; then
        echo "phase:2 (requirements)"
        return
    fi

    # Default: discovery
    echo "phase:1 (discovery)"
}

# Output para SDLC
DETECTED=$(detect_phase)
echo "SDLC_PHASE=$DETECTED"

# Sugerir agente apropriado
case "$DETECTED" in
    phase:1*)
        echo "SUGGESTED_AGENT=domain-researcher"
        ;;
    phase:2*)
        echo "SUGGESTED_AGENT=requirements-analyst"
        ;;
    phase:3*)
        echo "SUGGESTED_AGENT=system-architect"
        ;;
    phase:4*)
        echo "SUGGESTED_AGENT=delivery-planner"
        ;;
    phase:5*)
        echo "SUGGESTED_AGENT=code-author"
        ;;
    phase:6*)
        echo "SUGGESTED_AGENT=security-scanner"
        ;;
    phase:7*)
        echo "SUGGESTED_AGENT=release-manager"
        ;;
    phase:8*)
        echo "SUGGESTED_AGENT=incident-commander"
        ;;
esac

exit 0
