#!/bin/bash
# validate-framework-structure.sh
# Validates that all required framework files exist
# Logs missing files to Loki for monitoring

set -euo pipefail

# Load logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/shell/logging_utils.sh"

sdlc_set_context skill="framework-validator" phase=0

# Required framework files (templates, schemas, docs)
REQUIRED_FILES=(
  # Templates
  ".agentic_sdlc/templates/adr-template.yml"
  ".agentic_sdlc/templates/odr-template.yml"
  ".agentic_sdlc/templates/spec-template.md"
  ".agentic_sdlc/templates/threat-model-template.yml"

  # Schemas
  ".agentic_sdlc/schemas/adr-schema.json"

  # Core documentation
  ".agentic_sdlc/docs/README.md"
  ".agentic_sdlc/docs/enrichment-guide.md"
  ".agentic_sdlc/docs/guides/quickstart.md"
  ".agentic_sdlc/docs/guides/infrastructure.md"
  ".agentic_sdlc/docs/guides/troubleshooting.md"
  ".agentic_sdlc/docs/guides/adr-vs-odr.md"
  ".agentic_sdlc/docs/sdlc/agents.md"
  ".agentic_sdlc/docs/sdlc/commands.md"
  ".agentic_sdlc/docs/sdlc/overview.md"

  # Engineering playbook
  ".agentic_sdlc/docs/engineering-playbook/README.md"
  ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/principios.md"
  ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/standards.md"
  ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/qualidade.md"
  ".agentic_sdlc/docs/engineering-playbook/manual-desenvolvimento/testes.md"
  ".agentic_sdlc/docs/engineering-playbook/stacks/devops/security.md"
  ".agentic_sdlc/docs/engineering-playbook/stacks/devops/ci-cd.md"
  ".agentic_sdlc/docs/engineering-playbook/stacks/devops/observability.md"

  # Scripts
  ".agentic_sdlc/scripts/setup-sdlc.sh"
  ".agentic_sdlc/scripts/validate-sdlc-phase.sh"
)

# Quality gates (critical for SDLC workflow)
REQUIRED_GATES=(
  ".claude/skills/gate-evaluator/gates/phase-0-to-1.yml"
  ".claude/skills/gate-evaluator/gates/phase-1-to-2.yml"
  ".claude/skills/gate-evaluator/gates/phase-2-to-3.yml"
  ".claude/skills/gate-evaluator/gates/phase-3-to-4.yml"
  ".claude/skills/gate-evaluator/gates/phase-4-to-5.yml"
  ".claude/skills/gate-evaluator/gates/phase-5-to-6.yml"
  ".claude/skills/gate-evaluator/gates/phase-6-to-7.yml"
  ".claude/skills/gate-evaluator/gates/phase-7-to-8.yml"
  ".claude/skills/gate-evaluator/gates/security-gate.yml"
)

# Counter for missing files
MISSING_COUNT=0
TOTAL_CHECKED=0

sdlc_log_info "Starting framework structure validation"

# Validate required files
for file in "${REQUIRED_FILES[@]}"; do
  TOTAL_CHECKED=$((TOTAL_CHECKED + 1))

  if [ ! -f "$file" ]; then
    MISSING_COUNT=$((MISSING_COUNT + 1))
    sdlc_log_error "Required framework file missing" "file=$file category=framework"
  else
    sdlc_log_debug "Framework file exists" "file=$file"
  fi
done

# Validate quality gates
for gate in "${REQUIRED_GATES[@]}"; do
  TOTAL_CHECKED=$((TOTAL_CHECKED + 1))

  if [ ! -f "$gate" ]; then
    MISSING_COUNT=$((MISSING_COUNT + 1))
    sdlc_log_error "Required quality gate missing" "file=$gate category=gate"
  else
    sdlc_log_debug "Quality gate exists" "gate=$gate"
  fi
done

# Log summary
if [ $MISSING_COUNT -eq 0 ]; then
  sdlc_log_info "Framework structure validation passed" \
    "checked=$TOTAL_CHECKED missing=0"
else
  sdlc_log_warn "Framework structure validation completed with missing files" \
    "checked=$TOTAL_CHECKED missing=$MISSING_COUNT"

  # Print summary to console (visible to user)
  echo "⚠️  Framework structure check: $MISSING_COUNT files missing (see Loki logs for details)"
fi

# Exit with success (don't block workflow)
exit 0
