# Command: /audit-phase

Run adversarial audit on specified SDLC phase.

## Usage

```
/audit-phase <phase_number> [options]
```

## Arguments

- `<phase_number>` - SDLC phase to audit (0-8)

## Options

- `--thorough` - Run deep audit (slower but more thorough)
- `--report-only` - Generate report without making pass/fail decision
- `--config <path>` - Use custom audit configuration file

## Examples

```bash
# Audit Phase 5 (Implementation)
/audit-phase 5

# Audit Phase 3 with deep analysis
/audit-phase 3 --thorough

# Generate audit report without decision
/audit-phase 6 --report-only
```

## What It Does

1. Loads phase configuration and expected artifacts
2. Runs automated checks (security, quality, completeness)
3. Calls `phase-auditor` agent for LLM-based adversarial analysis
4. Classifies findings by severity (CRITICAL → LIGHT)
5. Makes decision: FAIL, PASS_WITH_WARNINGS, or PASS
6. Generates structured audit report

## When to Use

- **Post-gate validation** - After a phase gate passes, verify with adversarial audit
- **Quality check** - Before releasing, audit critical phases (3, 5, 6)
- **Troubleshooting** - If production issues arise, audit previous phases
- **Process improvement** - Identify patterns in findings to improve self-validation

## Output

Generates audit report at: `.agentic_sdlc/audits/phase-{N}-audit.yml`

Example report structure:
```yaml
phase: 5
phase_name: "Implementation"
audited_at: "2026-01-28T14:23:17Z"
decision: "PASS_WITH_WARNINGS"
summary:
  critical: 0
  grave: 0
  medium: 2
  light: 3
findings:
  - id: "AUDIT-005-001"
    severity: "MEDIUM"
    title: "Test coverage below 80%"
    ...
```

## Integration

This command is automatically called by:
- `post-gate-audit.sh` hook (after gates pass)
- Orchestrator (if adversarial audit enabled)

You can also call it manually for ad-hoc audits.

## Configuration

Configure in `.claude/settings.json`:

```json
{
  "sdlc": {
    "quality_gates": {
      "adversarial_audit": {
        "enabled": true,
        "phases": [3, 5, 6],
        "fail_on": ["CRITICAL", "GRAVE"],
        "warn_on": ["MEDIUM", "LIGHT"]
      }
    }
  }
}
```

## Related

- Agent: `phase-auditor`
- Skill: `adversarial-validator`
- Hook: `post-gate-audit.sh`

---

**Version:** 1.0.0
**Added:** v2.2.1
