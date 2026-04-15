---
name: analyze
description: |
  Validates that a spec/plan is complete and approves it for the next
  phase. Checks Constitution conformance, artifact completeness, and
  runs the adversarial-validator.

  Examples:
  - <example>
    user: "/analyze pix-checkout"
    assistant: "Vou validar o spec contra a Constituição e gates"
    </example>
---

# Analyze and Approve an SDD Artifact

## Modes

### Mode: spec (default)

Validates `.specify/specs/<slug>/spec.md` for advancement to `approved`.

### Mode: plan

Validates `.specify/specs/<slug>/plan.md` for advancement to `approved`.

### Mode: tasks

Validates `.specify/specs/<slug>/tasks.md` + per-task files.

## Steps (spec mode)

1. **Load** Constitution, spec, and the `phase-2-to-3` gate definition.

2. **Constitution conformance check**:
   - Every principle in `applicable_principles` frontmatter is visibly
     addressed in the spec text (grep for principle IDs / quote fragments).
   - Missing principle coverage → list violations.

3. **Completeness check**:
   - Has acceptance criteria with Given/When/Then? (non-empty)
   - Has NFRs with numbers? (no "fast", "many", "low")
   - Has out-of-scope section? (explicit boundary)
   - Has value hypothesis? (measurable)

4. **Invoke `adversarial-validator`** (the project's existing adversarial
   agent) to challenge the spec. Severity:
   - CRITICAL → block, must fix
   - HIGH → block, must fix or accept via ADR exception
   - MEDIUM/LOW → warn, can proceed

5. **Clarification recency**:
   - `clarify_rounds_completed >= 1` AND
   - `last_clarified_at` within 30 days

6. **Decision**:
   - All checks pass → set `status: approved` in frontmatter, write
     approver/timestamp, emit `approved` outcome.
   - Any block → keep `status: draft`, list blockers, suggest fixes.

## Output

```yaml
analyze:
  artifact: .specify/specs/pix-checkout/spec.md
  mode: spec
  constitution_version: "1.0.0"
  conformance_checks_passed: 11
  completeness_checks_passed: 4
  adversarial_findings:
    critical: 0
    high: 0
    medium: 2
    low: 5
  decision: approved | rejected | needs_clarification
  blockers: []
  status_after: approved
```

## Gate interaction

This command is the canonical mechanism by which a spec/plan/tasks
artifact transitions from `draft` → `approved`. No other command should
set `status: approved` directly.

## Do NOT

- Do NOT approve if `adversarial-validator` reports any CRITICAL finding.
- Do NOT skip the Constitution conformance check. The Constitution is
  the reason SDD exists in this project.
