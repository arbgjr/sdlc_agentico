---
description: 'Output style for quality gate evaluation and validation. Use when checking phase transition criteria or validating deliverables.'
applyTo: '**/{gate,quality,validation,check}*'
---

# Quality Gate Output Style

When evaluating quality gates:

## Evaluation Structure

```
Gate: {gate-name}
Transition: Phase {N} → Phase {N+1}

CHECKS:
✅ {check-id}: {description} - PASS
   Details: {specific evidence}

⚠️  {check-id}: {description} - WARN
   Impact: {severity}
   Recommendation: {action}

❌ {check-id}: {description} - FAIL (BLOCKING)
   Reason: {why it failed}
   Required Fix: {specific action}

DECISION: [APPROVED | CONDITIONAL | BLOCKED]
Rationale: {explanation}
```

## Severity Levels

- **CRITICAL** (❌ blocking) - Must fix before proceeding
- **MAJOR** (⚠️ warning) - Should fix, proceed with risk
- **MINOR** (ℹ️ info) - Nice to have

## Tone

- **Objective and evidence-based** - No opinions, only facts
- **Constructive** - Suggest fixes, not just complaints
- **Consistent** - Same standards for everyone

## Decision Types

### APPROVED ✅
All critical checks passed. Proceed immediately.

### CONDITIONAL ⚠️
Some warnings present. Proceed with documented risks and mitigation plan.

### BLOCKED ❌
Critical failures present. Must resolve before proceeding.

## Example Output

```
Gate: phase-5-to-6 (Implementation → Quality)

CHECKS:
✅ build-passing: Build completes without errors - PASS
   Details: 127 files compiled, 0 errors, 0 warnings

✅ test-coverage: Minimum 80% coverage achieved - PASS
   Details: 87% line coverage, 92% branch coverage

⚠️  code-review: 2 PRs pending review - WARN
   Impact: MAJOR - unreviewed code in release candidate
   Recommendation: Complete reviews before Phase 7

❌ security-scan: 3 HIGH vulnerabilities detected - FAIL (BLOCKING)
   Reason: CVE-2024-12345 in dependency lodash@4.17.20
   Required Fix: Update to lodash@4.17.21+ immediately

DECISION: BLOCKED
Rationale: Security vulnerabilities are release blockers per security-gate.yml.
Must resolve all HIGH+ CVEs before quality approval.

Next Steps:
1. Update lodash dependency
2. Re-run security scan
3. Complete pending code reviews (parallel)
4. Re-evaluate gate
```

## Anti-Patterns

- ❌ Don't approve gates with unacknowledged risks
- ❌ Don't downplay critical failures
- ❌ Don't skip evidence/justification
- ❌ Don't create "soft gates" (all gates must enforce)
