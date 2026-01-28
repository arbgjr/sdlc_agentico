#!/usr/bin/env bash
# Post-Gate Audit Hook
# Executes adversarial audit after quality gate passes
#
# Triggered by: orchestrator after gate-evaluator passes
# Purpose: Adversarial quality assurance - find problems self-validation missed
#
# Usage: Called automatically by orchestrator, not manually
# Environment:
#   - PHASE: Current SDLC phase number (0-8)
#   - PROJECT_PATH: Path to project being audited
#   - GATE_RESULT: Result of gate evaluation (passed|failed)

set -euo pipefail

# Source logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/shell/logging_utils.sh"

# Set context for logging
sdlc_set_context skill="adversarial-validator" phase="${PHASE:-unknown}"

# Configuration
CONFIG_FILE="${SCRIPT_DIR}/../skills/adversarial-validator/config/audit_config.yml"
AUDIT_SCRIPT="${SCRIPT_DIR}/../skills/adversarial-validator/scripts/audit_phase.py"

# Inputs from orchestrator
PHASE="${PHASE:-0}"
PROJECT_PATH="${PROJECT_PATH:-.}"
GATE_RESULT="${GATE_RESULT:-unknown}"

sdlc_log_info "Post-gate audit hook triggered" \
  "phase=$PHASE" \
  "gate_result=$GATE_RESULT" \
  "project=$PROJECT_PATH"

# Only run if gate passed (adversarial audit is post-pass validation)
if [[ "$GATE_RESULT" != "passed" ]]; then
  sdlc_log_info "Gate did not pass, skipping adversarial audit" \
    "gate_result=$GATE_RESULT"
  exit 0
fi

# Check if adversarial audit is enabled
AUDIT_ENABLED=$(yq eval '.adversarial_audit.enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")

if [[ "$AUDIT_ENABLED" != "true" ]]; then
  sdlc_log_info "Adversarial audit disabled in config, skipping" \
    "config_file=$CONFIG_FILE"
  exit 0
fi

# Check if this phase should be audited
PHASES_TO_AUDIT=$(yq eval '.adversarial_audit.phases[]' "$CONFIG_FILE" 2>/dev/null)

if ! echo "$PHASES_TO_AUDIT" | grep -q "^${PHASE}$"; then
  sdlc_log_info "Phase not configured for audit, skipping" \
    "phase=$PHASE" \
    "audited_phases=$PHASES_TO_AUDIT"
  exit 0
fi

sdlc_log_info "Running adversarial audit" \
  "phase=$PHASE" \
  "project=$PROJECT_PATH"

# Run adversarial audit
AUDIT_RESULT=0
AUDIT_REPORT=""

if python3 "$AUDIT_SCRIPT" --phase "$PHASE" --project-path "$PROJECT_PATH"; then
  AUDIT_RESULT=0
  AUDIT_DECISION=$(yq eval '.decision' ".agentic_sdlc/audits/phase-${PHASE}-audit.yml" 2>/dev/null || echo "UNKNOWN")

  sdlc_log_info "Adversarial audit completed" \
    "decision=$AUDIT_DECISION" \
    "report=.agentic_sdlc/audits/phase-${PHASE}-audit.yml"

  # Check decision
  case "$AUDIT_DECISION" in
    "FAIL")
      sdlc_log_error "Adversarial audit FAILED" \
        "phase=$PHASE" \
        "reason=CRITICAL or GRAVE findings detected"

      # Extract findings summary
      CRITICAL_COUNT=$(yq eval '.summary.critical' ".agentic_sdlc/audits/phase-${PHASE}-audit.yml" 2>/dev/null || echo "0")
      GRAVE_COUNT=$(yq eval '.summary.grave' ".agentic_sdlc/audits/phase-${PHASE}-audit.yml" 2>/dev/null || echo "0")

      sdlc_log_error "Audit findings summary" \
        "critical=$CRITICAL_COUNT" \
        "grave=$GRAVE_COUNT"

      # Attempt auto-correction if enabled
      AUTO_CORRECT=$(yq eval '.adversarial_audit.auto_correct.enabled' "$CONFIG_FILE" 2>/dev/null || echo "false")

      if [[ "$AUTO_CORRECT" == "true" ]]; then
        sdlc_log_info "Attempting auto-correction" \
          "max_retries=$(yq eval '.adversarial_audit.auto_correct.max_retries' "$CONFIG_FILE")"

        # Call auto-correction (implementation TBD)
        # For now, escalate to human
        sdlc_log_warning "Auto-correction not yet implemented, escalating to human"
      fi

      # Fail the hook (blocks phase advancement)
      exit 1
      ;;

    "PASS_WITH_WARNINGS")
      sdlc_log_warning "Adversarial audit passed with warnings" \
        "phase=$PHASE"

      MEDIUM_COUNT=$(yq eval '.summary.medium' ".agentic_sdlc/audits/phase-${PHASE}-audit.yml" 2>/dev/null || echo "0")
      LIGHT_COUNT=$(yq eval '.summary.light' ".agentic_sdlc/audits/phase-${PHASE}-audit.yml" 2>/dev/null || echo "0")

      sdlc_log_warning "Non-blocking findings detected" \
        "medium=$MEDIUM_COUNT" \
        "light=$LIGHT_COUNT"

      # TODO: Create GitHub issues for MEDIUM/LIGHT findings
      sdlc_log_info "Creating tech debt issues for findings" \
        "phase=$PHASE"

      # Pass (allow phase advancement)
      exit 0
      ;;

    "PASS")
      sdlc_log_info "Adversarial audit PASSED" \
        "phase=$PHASE" \
        "findings=0"

      # Pass (allow phase advancement)
      exit 0
      ;;

    *)
      sdlc_log_error "Unknown audit decision" \
        "decision=$AUDIT_DECISION"

      # Fail safe: block advancement if decision unclear
      exit 1
      ;;
  esac
else
  AUDIT_RESULT=$?
  sdlc_log_error "Adversarial audit script failed" \
    "exit_code=$AUDIT_RESULT" \
    "script=$AUDIT_SCRIPT"

  # Fail the hook (blocks phase advancement)
  exit 1
fi

# Should not reach here
sdlc_log_error "Unexpected hook execution path"
exit 1
