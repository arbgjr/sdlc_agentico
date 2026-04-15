---
name: copilot-cloud-agent
version: 1.0.0
description: |
  Orchestrates GitHub Copilot Cloud Agent as the default strategy for
  parallel implementation work. Converts SDD tasks into GitHub issues,
  assigns them to @copilot, tracks agent jobs, reviews resulting PRs, and
  feeds back review comments as @copilot replies until merge-ready.

  This is the primary parallelization strategy for Phase 6 (Implementation)
  in Levels 2 and 3. Local parallel-workers (git worktrees) remains the
  fallback for tasks that require local environment access or credentials.

category: implementation
phase: 6
complexity_levels: [1, 2, 3]
user-invocable: false

allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - mcp__github__assign_copilot_to_issue
  - mcp__github__create_pull_request_with_copilot
  - mcp__github__get_copilot_job_status
  - mcp__github__issue_read
  - mcp__github__issue_write
  - mcp__github__pull_request_read
  - mcp__github__pull_request_review_write
  - mcp__github__add_comment_to_pending_review
  - mcp__github__add_reply_to_pull_request_comment
  - mcp__github__list_pull_requests
  - mcp__github__search_pull_requests
  - mcp__github__subscribe_pr_activity
  - mcp__github__unsubscribe_pr_activity

tags:
  - parallelization
  - cloud
  - github
  - copilot
  - phase-6

scripts:
  dispatcher: scripts/dispatcher.py
  status_tracker: scripts/status_tracker.py
  review_relay: scripts/review_relay.py

dependencies:
  system:
    - python >= 3.11
  python:
    - pyyaml
  skills:
    - github-sync
    - sdlc-create-issues
    - gate-evaluator

integration:
  agents:
    - code-reviewer
    - qa-analyst
    - security-scanner
    - delivery-planner

observability:
  loki_labels:
    - skill: copilot-cloud-agent
    - phase: 6
    - strategy: cloud
  metrics:
    - tasks_dispatched
    - tasks_completed
    - tasks_rejected_by_review
    - agent_retry_count
    - review_round_count
    - wallclock_minutes_per_task
---

# Copilot Cloud Agent — Default Parallel Strategy

## Why cloud-first

Git-worktree parallel workers are powerful but pay a heavy local cost:
compute, disk, cognitive overhead, and correlation of state between
branches. GitHub Copilot Cloud Agent inverts this tradeoff — issues are
dispatched to GitHub's infrastructure, each one opens a PR, and the loop
closes via PR review. The machine coordinating the work does no heavy
lifting.

This skill is the **default** path for Phase 6 implementation work.
Local parallel-workers is reserved for tasks that genuinely need local
environment access.

## Contract

### Inputs

- `spec_slug` — the feature slug under `.specify/specs/<slug>/`
- `tasks_filter` (optional) — only dispatch tasks with specific IDs or
  `parallelization_hint: copilot_cloud_agent`

### Outputs

- `.project/issue-mapping.yml` — TASK-NNN → issue number + PR number
- Issues on the repo, assigned to `@copilot`, labeled `sdlc:phase-6`,
  `type:task`, `complexity:<level>`
- PRs authored by Copilot, each targeting the current feature branch
- Loki logs with the metrics listed above

### Invariants

1. **No task dispatched without a context bundle.** Each TASK-NNN has a
   `.specify/specs/<slug>/tasks/TASK-NNN-*.md` (story-context document).
   The issue body IS that document — verbatim. Paraphrasing breaks
   Principle IX.
2. **No PR merged automatically.** Human review + `code-reviewer` agent
   review are both required. Auto-merge is opt-in per repo policy.
3. **No task dispatched with `parallelization_hint: human_only`.**
   Those bypass this skill entirely and go through GitHub project board.
4. **No secrets in task bodies or comments.** The dispatcher scans for
   patterns matching `*_KEY|*_SECRET|*_TOKEN|*_PASSWORD` and blocks.

## Phase 6 workflow with this skill

```
delivery-planner (/tasks)
  → produces .specify/specs/<slug>/tasks/TASK-NNN-*.md
  → produces .specify/specs/<slug>/strategy.yml

/phase-6-start
  → copilot-cloud-agent.dispatcher.py
  → for each TASK with parallelization_hint == copilot_cloud_agent:
      create issue with TASK-NNN-*.md as body
      assign @copilot
      record in .project/issue-mapping.yml
  → parallel-workers handles parallelization_hint == local_worker (fallback)
  → human_only tasks routed to GitHub project board

copilot (GitHub Cloud)
  → opens draft PR on branch copilot/<issue-number>-<slug>
  → runs CI

copilot-cloud-agent.status_tracker.py (periodic)
  → polls get_copilot_job_status
  → watches PR CI signals

copilot-cloud-agent.review_relay.py (on PR ready)
  → invokes code-reviewer agent on the PR diff
  → invokes security-scanner (SAST/SCA)
  → if issues found: @copilot is replied with structured feedback
  → if clean: request human review (gate: Principle VII)

human + code-reviewer approval
  → PR merges into feature branch
  → issue closes
  → .project/issue-mapping.yml updated

phase-6-to-7 gate
  → gate-evaluator checks all issues closed, all PRs merged
  → proceeds to Phase 7 (Quality)
```

## Issue body template

Issues created by this skill carry a disciplined shape so Copilot has the
context it needs.

```markdown
<!-- Generated by copilot-cloud-agent — do not edit the header -->

## Task

<one-sentence imperative>

## Acceptance criteria

<verbatim from story-context.md>

## Context bundle

<verbatim Files, ADRs, Patterns, Anti-patterns, Data, Security sections>

## Test plan

<verbatim from story-context.md>

## Out of scope

<verbatim>

## Definition of done

<verbatim>

---
**spec**: `.specify/specs/<slug>/spec.md`
**plan**: `.specify/specs/<slug>/plan.md`
**task**: `.specify/specs/<slug>/tasks/TASK-NNN-*.md`
**constitution**: v1.0.0 — Principles II, III, IV, VII apply
```

## Review relay protocol

When Copilot opens a PR, this skill runs `review_relay.py` which:

1. Fetches the PR diff via `pull_request_read`.
2. Invokes `code-reviewer` (local agent) with the diff + the TASK context.
3. Invokes `security-scanner` (SAST + SCA).
4. Aggregates findings by severity:
   - CRITICAL / HIGH → post structured comment via
     `add_comment_to_pending_review`, tag `@copilot` in the body so the
     cloud agent sees it and retries.
   - MEDIUM → post as review comment, do not tag.
   - LOW → post as threaded comment.
5. If CRITICAL/HIGH, the PR is NOT marked ready for human review. Copilot
   retries. A retry counter is incremented in `issue-mapping.yml`.
6. Cap at 3 automated retries. On the 4th rejection, escalate to human
   and unassign Copilot.

## Metrics promoted to SLOs

| Metric                         | SLO                              |
| ------------------------------ | -------------------------------- |
| `tasks_dispatched` daily       | budget-bound (see ADR-XXX)        |
| `wallclock_minutes_per_task`   | P95 < 90 min                     |
| `agent_retry_count` per task   | P95 <= 1                         |
| `tasks_rejected_by_review`     | < 20% of dispatched              |
| `review_round_count` per task  | P95 <= 2                         |

Burn rate alerts fire via `observability-engineer` Grafana dashboard.

## Pre-flight checks (dispatcher)

Before any issue is created, the dispatcher verifies:

1. `gh auth status` succeeds
2. Target repo has Copilot coding agent enabled:
   `gh api repos/OWNER/REPO --jq '.allow_copilot_coding_agent'` → true
3. The feature branch exists on origin
4. `.specify/specs/<slug>/strategy.yml` designates `copilot_cloud_agent`
   as primary for these tasks
5. Each TASK-NNN file passes secret scan
6. Daily dispatch quota not exceeded (budget-bound)

A failure in any of these blocks dispatch with a specific remediation.

## When NOT to use this skill

- Task requires local-only credentials or infra access
  → use `parallel-workers` (worktrees)
- Task is Level 0 (bug fix, typo) → use `/quick-fix` directly
- Task is exploratory / spike / research → assign to human
- Task touches the Constitution or a framework meta-file → human only

## Failure handling (resilience hooks)

The dispatcher wraps every MCP call with the resilience layer
(`.claude/lib/python/resilience.py`):
- 3 retries with exponential backoff on 5xx
- 15s timeout per call
- Circuit-breaker opens at 50% error rate across 10 calls
- On open circuit: pause dispatch, alert, fall back to parallel-workers

## References

- GitHub Copilot coding agent: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent
- Existing command: `.claude/commands/sdlc-create-issues.md`
- Companion script: `.claude/skills/copilot-cloud-agent/scripts/dispatcher.py`
- Constitution: `.specify/memory/constitution.md` (Principle X)
- ADR to be authored: "Copilot Cloud Agent as default Phase 6 strategy"
