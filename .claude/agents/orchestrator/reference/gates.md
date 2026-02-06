# Quality Gates Reference

Complete reference for quality gates, adversarial audits, and phase validation.

## Overview

Quality gates are checkpoint validations between SDLC phases that ensure deliverables meet required standards before proceeding. Gates prevent defects from propagating and enforce quality discipline.

```
Phase N → Self-Validation → Gate Evaluation → Adversarial Audit → Phase N+1
           (Agent checks)    (gate-evaluator)   (phase-auditor)
```

---

## Pre-Execution Checklist

Before executing any phase, validate:

- [ ] **Verificar atualizações disponíveis (version-checker)**
- [ ] **Detectar cliente ativo (client_resolver)** ← v3.0.0
- [ ] **Carregar perfil do cliente (se multi-client)**
- [ ] **Contexto da fase anterior carregado**
- [ ] **Artefatos de entrada disponíveis**
- [ ] **Agentes da fase identificados**
- [ ] **Skills necessárias disponíveis**

---

## Post-Execution Checklist

After phase execution, before advancing:

- [ ] **Resultados validados contra critérios do gate**
- [ ] **Adversarial audit executado** (se fase configurada)
- [ ] **Decisões persistidas no **
- [ ] **Próximos passos definidos**
- [ ] **Métricas coletadas** (tempo, artefatos, issues)
- [ ] **Status atualizado para stakeholders**
- [ ] **Stakeholders notificados sobre arquivos para revisão**
- [ ] **Commit da fase sugerido/executado** (v1.7.15+)
- [ ] **Learnings da sessão extraídos e persistidos**

---

## Gate Structure

Each gate is defined in a YAML file: `.claude/skills/gate-evaluator/gates/phase-{N}-to-{N+1}.yml`

### Standard Gate Format

```yaml
name: "Phase 2 to 3: Requirements to Architecture"
from_phase: 2
to_phase: 3
description: "Validates requirements completeness before architecture design"

criteria:
  required_artifacts:
    - path: ".agentic_sdlc/requirements/user-stories.md"
      description: "User stories with acceptance criteria"
      validation: "file_exists_and_not_empty"

  quality_checks:
    - name: "No ambiguous requirements"
      validation: "grep -i 'TBD\\|TODO\\|FIXME' requirements/"
      expected_result: "no_matches"
      severity: "CRITICAL"

  stakeholder_approval:
    required: false  # true for Level 3 (enterprise)
    approvers: ["product-owner", "tech-lead"]

  adversarial_audit:
    enabled: true  # Run phase-auditor after gate passes
    phases: [3, 5, 6]  # Critical phases
```

---

## Gate Evaluation Process

1. **Load Gate Definition**
   - Read `.claude/skills/gate-evaluator/gates/phase-{N}-to-{N+1}.yml`
   - Parse criteria (required_artifacts, quality_checks, etc.)

2. **Check Required Artifacts**
   - Verify all `required_artifacts` exist
   - Validate artifact content (not empty, valid format)

3. **Execute Quality Checks**
   - Run validation commands
   - Evaluate results against expected outcomes
   - Classify severity (CRITICAL, HIGH, MEDIUM, LOW)

4. **Stakeholder Approval** (if required)
   - Request approval from specified approvers
   - Block phase advance until approval received

5. **Calculate Gate Score**
   ```python
   score = (passed_checks / total_checks) * 100

   if critical_failures > 0:
       result = "FAILED"
   elif score >= 80:
       result = "PASSED"
   else:
       result = "FAILED"
   ```

6. **Generate Gate Report**
   - Save to `.agentic_sdlc/gates/phase-{N}-to-{N+1}-result.yml`
   - Include: score, passed/failed criteria, recommendations

---

## Adversarial Audit (v2.2.1+)

**Purpose**: Challenge-based validation AFTER gate passes to find problems self-validation missed.

### Workflow

```
Phase Execution
    ↓
Self-Validation (agent checklist)
    ↓
Gate Evaluation (gate-evaluator)
    ↓
Gate PASSED ✓
    ↓
Adversarial Audit (phase-auditor)  ← Automatic
    ↓
Decision: FAIL | PASS_WITH_WARNINGS | PASS
```

### When Executed

Adversarial audit runs AUTOMATICALLY via `post-gate-audit.py` hook when:
- Gate passed
- `adversarial_audit.enabled: true` in settings.json
- Phase is in configured phases list (default: [3, 5, 6])

### How It Works

1. **Hook Triggered**
   ```bash
   PHASE=5 GATE_RESULT=passed python3 .claude/hooks/post-gate-audit.py
   ```

2. **Configuration Check**
   - Is audit enabled globally?
   - Is this phase in the audit list?

3. **Execute Audit**
   - Invoke `phase-auditor` agent with adversarial prompt
   - Automated checks (security, quality, completeness)
   - LLM deep analysis with challenge mindset

4. **Classify Findings**
   - **CRITICAL**: Blocks production, security vulnerabilities, data loss risk
   - **GRAVE**: Incorrect functionality, breaks requirements
   - **MEDIUM**: Poor UX, tech debt, maintainability issues
   - **LIGHT**: Minor improvements, style inconsistencies

5. **Decision Logic**
   ```python
   if critical_count > 0 or grave_count > 0:
       decision = "FAIL"
       if auto_correct_enabled:
           attempt_auto_fix()
           re_execute_phase()
       else:
           escalate_to_human()
   elif medium_count > 0 or light_count > 0:
       decision = "PASS_WITH_WARNINGS"
       create_tech_debt_issues()
       advance_to_next_phase()
   else:
       decision = "PASS"
       advance_to_next_phase()
   ```

---

## Adversarial Audit Configuration

### Settings

```json
// .claude/settings.json
{
  "sdlc": {
    "quality_gates": {
      "adversarial_audit": {
        "enabled": true,
        "phases": [3, 5, 6],  // Critical phases
        "fail_on": ["CRITICAL", "GRAVE"],
        "warn_on": ["MEDIUM", "LIGHT"],
        "auto_correct": {
          "enabled": true,
          "max_retries": 1
        },
        "thoroughness": "normal"  // quick | normal | deep
      }
    }
  }
}
```

### Recommended Phases

| Phase | Reason | Priority |
|-------|--------|----------|
| 3: Architecture | ADRs, threat models, critical decisions | 🔴 HIGH |
| 5: Implementation | Code, tests, security vulnerabilities | 🔴 HIGH |
| 6: Quality | Test coverage, security scans | 🔴 HIGH |
| 2: Requirements | Requirements completeness, ambiguity | 🟠 MEDIUM |
| 7: Release | Release notes, rollback plan | 🟠 MEDIUM |

---

## Auto-Correction

If `auto_correct.enabled: true` and audit fails:

```python
if decision == "FAIL" and auto_correct_enabled():
    logger.info("Attempting auto-correction...")

    for finding in critical_findings:
        try:
            fix_finding(finding)
            logger.info(f"✓ Fixed: {finding['title']}")
        except Exception as e:
            logger.error(f"✗ Could not fix: {e}")
            escalate_to_human(finding)

    # Re-audit after corrections
    if max_retries > 0:
        return run_phase(current_phase, max_retries - 1)
```

---

## Manual Override

If you need to skip audit temporarily:

```bash
# Disable for next execution
export SKIP_ADVERSARIAL_AUDIT=true
/sdlc-start "My feature"

# Or disable globally in settings.json
"adversarial_audit": {
  "enabled": false
}
```

**⚠️ WARNING**: Skipping audit increases risk of production issues. Use only when absolutely necessary.

---

## Audit Reports

Reports saved in: `.agentic_sdlc/audits/phase-{N}-audit.yml`

### Example Report

```yaml
phase: 5
decision: "PASS_WITH_WARNINGS"
timestamp: "2026-02-02T18:45:23Z"
auditor: "phase-auditor"
summary:
  critical: 0
  grave: 0
  medium: 2
  light: 3
  total: 5
findings:
  - id: "AUDIT-005-001"
    severity: "MEDIUM"
    title: "Test coverage 72% (target: 80%)"
    location: "src/services/payment.py"
    recommendation: "Add tests for edge cases in refund flow"
    confidence: 0.85
  - id: "AUDIT-005-002"
    severity: "MEDIUM"
    title: "Missing error handling for network timeout"
    location: "src/api/client.py:142"
    recommendation: "Add try/catch with exponential backoff"
    confidence: 0.92
  - id: "AUDIT-005-003"
    severity: "LIGHT"
    title: "Inconsistent naming: payment_svc vs paymentService"
    location: "src/services/"
    recommendation: "Standardize on snake_case"
    confidence: 0.67
```

---

## Audit Effectiveness Metrics

Track audit effectiveness:

```
Total audits: 142
├─ FAIL: 12 (8.4%)  ← Serious problems found
├─ PASS_WITH_WARNINGS: 87 (61.3%)  ← Tech debt identified
└─ PASS: 43 (30.3%)  ← Clean (rare but possible)

Auto-corrections:
├─ Attempted: 12
├─ Successful: 9 (75%)
└─ Escalated: 3 (25%)
```

**If FAIL rate > 15%**, consider:
- Improving agent self-validation
- Training team on quality standards
- Adding more automated checks

---

## Stakeholder Notification

After passing a gate, orchestrator MUST:

1. **Read `stakeholder_review` field from gate**
2. **Identify files created/modified in phase**
3. **Notify user about files requiring review**

### Notification Format

```
============================================
  ARQUIVOS PARA REVISÃO - Fase {N}
============================================

Os seguintes arquivos foram criados/modificados e precisam de revisão:

ALTA PRIORIDADE:
- [.agentic_sdlc/architecture/adr-001.yml] - Architecture decision
- [.agentic_sdlc/security/threat-model.yml] - STRIDE analysis

MÉDIA PRIORIDADE:
- [docs/api-spec.yml] - API contract

Por favor, revise os arquivos marcados como ALTA PRIORIDADE
antes de prosseguir para a próxima fase.
============================================
```

---

## Useful Commands

```bash
# Manual audit of specific phase
/audit-phase 5

# Audit with deep analysis
/audit-phase 3 --thorough

# View last audit report
/audit-report 5

# Re-audit after manual fixes (report-only mode)
/audit-phase 5 --report-only

# Check gate without advancing
/gate-check phase-2-to-3 --dry-run
```

---

**Version**: 3.0.0
**Last Updated**: 2026-02-02
