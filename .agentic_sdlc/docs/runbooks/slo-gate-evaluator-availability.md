# Runbook — gate_evaluator_availability

**SLO target**: `sdlc_gate_runs_success_total / sdlc_gate_runs_total >= 0.999` (7d window)
**Owner**: gate-evaluator
**Priority**: P1 — burning this SLO blocks every phase transition in the framework

## Symptom

- Grafana panel "Gate availability" drops below 99.9%
- Burn-rate panel shows fast-window rate ≥ 14.4
- Pipeline reports `validate_gate.py` exiting with non-structured error,
  or `/gate-check` command hanging
- Operator sees `GateNotFoundError` or unhandled `yaml.YAMLError` in logs

## Triage (first 5 minutes)

1. **Identify which gate is failing**. Loki query:
   ```logql
   {skill="gate-evaluator", level="error"}
     | json
     | line_format "{{.gate_name}} {{.error_type}}: {{.message}}"
   ```
2. **Check recent commits to gate YAMLs**:
   ```bash
   git log -n 20 --oneline .claude/skills/gate-evaluator/gates/
   ```
3. **Run the eval suite locally** to reproduce:
   ```bash
   python3 evals/gate-evaluator/runner.py
   ```

## Common causes (ranked by frequency)

1. **Malformed gate YAML** — someone hand-edited a gate file and broke
   YAML syntax. The `validate_gate.load_gate_definition` raises.
2. **Shell quality-check with bad quoting** — like the `security/2>/dev/null`
   bug caught by the eval harness on session 1. grep/ls path concatenation
   eats the redirect token.
3. **Missing gate file** — `/gate-check phase-X-to-Y` invoked for a
   pair without a gate YAML.
4. **Path template drift** — gate path patterns like
   `{project_dir}/projects/{id}/...` diverge from actual project layout
   after a repo restructuring.

## Mitigation

| Cause | Action |
|---|---|
| Malformed YAML | `git revert` the offending commit; patch forward separately. |
| Shell quoting | Fix the quoting in the YAML; add a regression case under `evals/gate-evaluator/golden/`. |
| Missing gate file | Copy the nearest gate as a template; at minimum provide `required_artifacts` and set `approval_required: false` to unblock. |
| Path drift | Run `python3 evals/run_all.py`; if a case fails only because paths moved, migrate the case (see 002/003 migrations in session 1). |

## Rollback

Gate files are pure config; `git revert <sha>` on the bad commit is
always safe. No state to unwind.

## Escalation

- If 3 different gates have failed in the same day → page
  playbook-governance agent: there is probably a pattern drift
  (e.g. everybody suddenly uses `validation:` instead of `metric:`).
- If `validate_gate.py` itself has a bug → open P1 issue tagged
  `area:gate-evaluator`; the fix MUST add a golden case that would have
  caught it.

## Post-incident RCA

RCA must include:

1. Which gate(s) failed and for how long.
2. Whether an existing golden case should have caught this (if yes:
   why didn't it? if no: what's the new golden case).
3. Whether ADR needs amendment (gate contract changes always do).

## Teach the framework

After 3 incidents with the same root cause, the detection MUST move from
runbook triage into an eval or a pre-commit hook. Examples graduated
this way: ADR-001 (relative hook paths → `settings-lint` eval).
