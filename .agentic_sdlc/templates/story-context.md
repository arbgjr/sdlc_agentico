---
task_id: TASK-NNN
spec_ref: <slug>
status: ready                    # ready | in_progress | in_review | done | blocked
parallelization_hint: copilot_cloud_agent   # copilot_cloud_agent | local_worker | human_only
assignee: "@copilot"             # or "@username" or "unassigned"
estimate_points: 3               # Fibonacci (1, 2, 3, 5, 8, 13)
depends_on: []                   # list of TASK-NNN
adr_refs: [ADR-NNN]              # ADRs applicable to this task
created_at: 2026-04-15T00:00:00Z
---

# Task <TASK-NNN>: <concise title in imperative>

<!--
  BMAD Method story-context document. This file is the SINGLE SOURCE OF
  TRUTH a developer (human or Copilot Cloud Agent) needs to implement the
  task. If they need anything not here, this document is incomplete.

  Principle IX of the Constitution: stories carry their full context
  bundle so the implementer starts with everything they need.
-->

## What

One paragraph, imperative mood. **What** must exist when this task is done,
not how to build it.

## Acceptance criteria

Copied verbatim from `.specify/specs/<slug>/spec.md`. Never paraphrased —
divergence between story and spec is a bug.

- [ ] Given ..., when ..., then ...
- [ ] Given ..., when ..., then ...

## Context bundle

### Files likely to be touched

| Path                                    | Why                                  |
| --------------------------------------- | ------------------------------------ |
| `src/<service>/<module>.py`             | Add the new adapter                  |
| `tests/<service>/test_<module>.py`      | Coverage for the new behavior        |
| `docs/api/<service>.yml`                | Contract needs one new endpoint      |

### Applicable ADRs

Quote the decision text from each ADR that constrains this task.

> **ADR-NNN**: "We use PostgreSQL with logical replication for the
> transactional store because ..."

### Patterns to follow

- Link: `.agentic_sdlc/corpus/patterns/<pattern>.md`
- Summary: "Use the Outbox pattern for publishing domain events."

### Anti-patterns / known failures to avoid

- Link: `.project/corpus/nodes/learnings/<learning>.yml`
- Summary: "Do NOT call the external provider synchronously in the request
  handler — past incident INC-2026-02-01 root-caused to this."

### Data expectations

- Input shape: <link or inline JSON schema>
- Output shape: <link or inline>
- Edge cases to cover: empty list, duplicate id, provider timeout

### Security constraints

- [ ] No secrets in code, logs, or error messages.
- [ ] Input validation at the boundary (Principle III).
- [ ] New public endpoint? → list here and flag for threat-modeler review.

## Test plan

### Unit

- <scenario 1>
- <scenario 2>

### Integration

- <cross-module scenario>

### Do NOT test

- Behavior outside this task's scope (Out of scope section).

## Out of scope

Explicit list. This is the fence. Anything here is a SEPARATE task.

- Do not implement provider B (TASK-NNN+1)
- Do not migrate historical data (TASK-NNN+2)

## Definition of done

- [ ] Acceptance criteria green
- [ ] Tests written and passing (cov ≥ gate threshold)
- [ ] No hardcoded secrets (Principle II)
- [ ] Observability instrumented (Principle IV)
- [ ] Self-review checklist in `.agentic_sdlc/docs/engineering-playbook`
- [ ] If public-facing, threat model updated (Principle III)
- [ ] ADR created if a non-obvious decision was made (Principle V)
