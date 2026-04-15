# SLO Runbooks

Each SLO declared in `.claude/config/slos.yml` maps 1:1 to a runbook in
this directory named `slo-<name>.md`. A runbook without action is
decoration; a runbook with action is an incident commander's shortcut.

## Template

Every runbook follows the same structure:

1. **Symptom** — how the operator learns the SLO is burning
2. **Owner** — who is paged / which agent owns response
3. **Triage (first 5 minutes)** — what to check before guessing
4. **Common causes** — ranked by frequency
5. **Mitigation** — the action that stops the bleeding
6. **Rollback** — if mitigation itself goes wrong
7. **Escalation** — when and to whom
8. **Post-incident** — what MUST enter the RCA

## Meta-rule

If a mitigation is executed by an on-call engineer, the runbook MUST
also add a bullet "teach the framework": the fix should migrate from
human action to automated action in the next iteration. A runbook
executed three times without automation is a design defect.

## Index

| SLO | Runbook | Owner | Priority |
|---|---|---|---|
| gate_evaluator_availability | slo-gate-evaluator-availability.md | gate-evaluator | P1 |
| copilot_task_wallclock | slo-copilot-task-wallclock.md | copilot-cloud-agent | P2 |
| copilot_review_rejection_rate | slo-copilot-review-rejection-rate.md | copilot-cloud-agent | P2 |
| resilience_circuit_open_minutes_daily | slo-resilience-circuit-open-minutes-daily.md | resilience | P2 |

## Pending runbooks

The following SLOs are declared in `.claude/config/slos.yml` without a
runbook yet. This is permitted only while the SLO has never burned. On
first burn, the owner MUST author the runbook inline with incident
response.

- `gate_evaluator_decision_latency` — pending (low-incidence, latency
  shows up in normal gate-evaluator incidents)
- `copilot_agent_retry_rate` — pending (covered under the
  copilot_task_wallclock runbook as a symptom)
- `copilot_review_rounds` — pending (distribution metric, not an alert)
- `resilience_retry_exhaustion_rate` — pending (exhaustion is
  covered under circuit-open; write separate runbook on first burn)
- `clarify_rounds_to_approval` — pending (process metric,
  not an operational incident source)
- `constitution_amendment_cadence` — pending (governance metric,
  addressed by playbook-governance, not on-call)
