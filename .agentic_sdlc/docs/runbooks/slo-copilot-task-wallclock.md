# Runbook — copilot_task_wallclock

**SLO target**: P95 wallclock from `dispatcher.create_issue` to PR merged ≤ 90 minutes
**Owner**: copilot-cloud-agent
**Priority**: P2 — burning this SLO means Phase 6 throughput is degraded but not stopped

## Symptom

- Grafana panel "Copilot task wallclock P95" crosses 90 min
- `.project/issue-mapping.yml` has tasks in `in_progress` or `ci_failing`
  state older than 90 minutes
- Burn-rate alert fires for `copilot_task_wallclock`

## Triage (first 5 minutes)

1. **List currently slow tasks**:
   ```bash
   python3 .claude/skills/copilot-cloud-agent/scripts/status_tracker.py --json \
     | jq '.entries[] | select(.state != "merged") | {task_id, state, created_at}'
   ```
2. **Inspect one slow PR** end-to-end:
   ```bash
   gh pr view <pr-number> --json url,statusCheckRollup,reviews
   ```
3. **Check review-relay history on that PR**:
   ```bash
   python3 .claude/skills/copilot-cloud-agent/scripts/review_relay.py --pr <N>
   ```

## Common causes (ranked by frequency)

1. **CI is red and flapping** — Copilot retries, each retry is ~ 10 min.
   If CI is unreliable, wallclock balloons through retries, not through
   slow agent work.
2. **Story-context document is ambiguous** — Copilot's first pass is
   wrong, review_relay rejects CRITICAL, Copilot retries, review rejects
   again. This is the `agent_retry_rate` co-burning with wallclock.
3. **Copilot queue backpressure** — org-level Copilot cloud agent capacity
   throttles concurrent jobs. Appears as PRs that never move off draft.
4. **Dispatcher dispatched stale tasks** — story-context was frozen at
   `plan-<slug>-v1` but plan has since been amended to v2.

## Mitigation

| Cause | Action |
|---|---|
| CI flapping | Stabilize CI first. Pause further dispatch via `max_concurrent: 1` hotfix in settings.json. |
| Ambiguous story-context | Pause dispatch for that slug. Return to `/clarify <slug>` then `/tasks <slug>` to regenerate story-context. Dispatch new batch. |
| Copilot capacity | Reduce `sdlc.parallelization.strategies.copilot_cloud_agent.max_concurrent` temporarily. Route overflow to parallel-workers for local-env-permissive tasks. |
| Stale tasks | Unassign `@copilot` on in-flight issues for the affected slug; close PRs; re-dispatch from new frozen plan. |

## Rollback

Dispatcher writes every action to `.project/issue-mapping.yml`. To
rollback a batch:

```bash
python3 .claude/skills/copilot-cloud-agent/scripts/status_tracker.py --json \
  | jq '.entries[] | select(.dispatcher=="copilot-cloud-agent" and .spec_slug=="<slug>") | .issue_url' \
  | xargs -I{} gh issue close {}
```

## Escalation

- Sustained burn > 6h with no single root cause isolated → escalate
  to incident-commander; start a timeline doc under
  `.project/incidents/<date>-copilot-slowness.md`.
- If Copilot agent is returning errors (not just slow) at >10% rate →
  fall back immediately to `parallel_workers` via
  `selection_rules` override.

## Post-incident RCA

Mandatory fields in the RCA:

- Did `agent_retry_count` P95 co-burn? If yes → fix traces back to
  Planning Phase, not Dev Cycle.
- Does any Copilot billing signal (premium request count) correlate?
  A quota spike masquerading as latency must be separated.

## Teach the framework

If CI instability is the root cause ≥ 3 times, the `dispatcher.py`
preflight must grow a "CI health check" gate: refuse to dispatch
when the base branch CI is failing.
