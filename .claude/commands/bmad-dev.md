---
name: bmad-dev
description: |
  Executes the BMAD Dev Cycle for a feature whose Planning Phase is
  complete and frozen. Consumes story-context tasks and dispatches them
  via the configured parallelization strategy (default:
  copilot-cloud-agent).

  Examples:
  - <example>
    user: "/bmad-dev pix-checkout"
    assistant: "Vou iniciar Dev Cycle — dispatching stories via Copilot Cloud Agent"
    </example>
---

# BMAD Dev Cycle

## Invariants

1. Dev Cycle starts only AFTER `/bmad-plan <slug>` completes and the
   plan is frozen at `plan-<slug>-v<n>`.
2. Each story is dispatched as a self-contained unit; the implementer
   (Copilot Cloud Agent, local worker, or human) gets the story-context
   document verbatim. No further context lookup is required by them.
3. Review is ALWAYS human + code-reviewer agent. Principle VII.

## Steps

1. **Preflight**:
   - `.specify/specs/<slug>/strategy.yml` exists and designates a primary.
   - All TASK-NNN-*.md files parse as valid story-context.
   - Feature branch is current with base.

2. **Route tasks**:
   - `parallelization_hint: copilot_cloud_agent` →
     `python3 .claude/skills/copilot-cloud-agent/scripts/dispatcher.py --spec-slug <slug>`
   - `parallelization_hint: local_worker` →
     `python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn-batch --spec-file .specify/specs/<slug>/tasks.md`
   - `parallelization_hint: human_only` → create GitHub issue, project board

3. **Monitor progress**:
   - Every 2 minutes: run `status_tracker.py --write`.
   - For any PR reaching state `ready`: run `review_relay.py --pr <N> --post`.
   - If `review_relay` posts CRITICAL/HIGH findings, Copilot Cloud Agent
     retries automatically (bounded by `retry_budget_per_task`).

4. **Merge gate**:
   - PR merges only after: CI green + code-reviewer clean + security-scanner clean + 1 human approval.
   - `.project/issue-mapping.yml` is updated on every state change.

5. **Phase 6 exit**:
   - Gate `phase-6-to-7` runs.
   - Gate requires: all mapped issues closed, all PRs merged, no
     outstanding CRITICAL/HIGH findings anywhere.

## Observability

Loki queries relevant during Dev Cycle:

```logql
# Dispatch activity
{skill="copilot-cloud-agent", phase=6}

# Retry rate per task
{skill="copilot-cloud-agent"} | json | line_format "{{.task_id}} retries={{.agent_retry_count}}"

# Review findings over time
{skill="copilot-cloud-agent", source="review_relay"}
```

## Output

```yaml
dev_cycle:
  slug: pix-checkout
  strategy_primary: copilot_cloud_agent
  dispatched:
    copilot_cloud_agent: 8
    local_worker: 1
    human_only: 2
  in_flight: 6
  merged: 5
  blocked: 0
  eta_wallclock_hours: ~4
  next_gate: phase-6-to-7
```

## Do NOT

- Do NOT edit stories mid-cycle. If a story is wrong, pause the
  dispatch, fix in Planning, freeze v2, resume.
- Do NOT skip review_relay. The stub-free path to prod is review-gated.
- Do NOT run Dev Cycle against an unfrozen plan. The dispatcher
  preflight will refuse — that refusal is load-bearing.
