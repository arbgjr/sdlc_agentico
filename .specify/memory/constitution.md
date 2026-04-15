# Project Constitution

> This document encodes the non-negotiable principles every agent, skill,
> command and human contributor must honor. It is loaded as context by
> `/constitution`, `/specify`, `/plan`, `/tasks` and `/implement`, and its
> violations are treated as blockers by the quality gates.
>
> Amendments require an ADR and a bump of the version field below.

**Version**: 1.0.0
**Effective since**: 2026-04-15
**Supersedes**: none

---

## I. Natural-language-first

All agents, skills and orchestration logic are authored as English prose in
markdown files. Programming languages are used **only** as a last resort for:

- External service connectors (HTTP, DB, filesystem, MCP)
- Performance-critical operations that natural language cannot express
- System-level integrations (hooks, shell scripts)

If a pull request introduces Python/Shell/TypeScript where a markdown
specification would suffice, the reviewer MUST require conversion or
justification in an ADR.

## II. Anti-mock policy (ABSOLUTE)

Production code MUST NOT contain:

- Mocks, stubs, fakes, dummies, simulators, emulators, in-memory substitutes
  for any external service or MCP.
- Hardcoded test data, pattern-based bypasses, or "if env==test" shortcuts.
- Placeholders: `lorem`, `foo`, `bar`, `TODO`, `TBD` outside `tests/`.

Test doubles exist **only** under `tests/` directories. When a real service
is unavailable at runtime, use resilience patterns (timeout, retry, circuit
breaker) or return `503 Service Unavailable` with an `x-correlation-id`.

Gate-5 (Implementation → Quality) MUST reject on any violation.

## III. Security by design

Security is a fundamental requirement, not a feature bolted on at the end.
Every feature must:

- Pass STRIDE threat modeling in Phase 3 (Architecture).
- Validate inputs at system boundaries.
- Avoid secrets in source, logs, or artifacts.
- Go through SAST + SCA before release.

Any change that touches authentication, authorization, cryptography, PII, or
a new public endpoint auto-escalates to human approval (see
`sdlc.security_by_design.escalation_triggers`).

CVSS ≥ 7.0 vulnerabilities block release.

## IV. Observability is part of delivery

No code ships without:

- Structured logs with `correlation_id`, `skill`, `phase`, `agent_id`.
- Metrics that answer: "is this feature succeeding and at what latency?"
- Traces on any cross-service boundary.

Observability configs live in `.claude/config/logging/`.

## V. Decisions are ADRs

A decision that affects maintenance, scale, cost, or cross-team boundaries
MUST be recorded as an ADR under `.project/corpus/nodes/decisions/`. Skipping
this is not an acceptable shortcut.

An ADR has: context, decision, alternatives considered (with reasons for
rejection), consequences (positive/negative/neutral), and an enforcement
mechanism where possible.

## VI. Small changes preferred

Pull requests SHOULD be as small as they can be while remaining coherent.
A refactor of 2000 lines in one PR is a bad smell. A feature that spans 20
files but cannot be broken down MUST explain why in the PR description.

## VII. Quality is the author's responsibility

Tests, observability, clarity and documentation are part of delivery — not
a separate QA phase to be "handed off". If a change breaks tests downstream,
the author fixes them or works with the owner — not "someone else later".

## VIII. Spec-Driven Development

Before code is written for any feature above Level 0:

1. A `.specify/specs/<feature>/spec.md` exists with acceptance criteria.
2. A `.specify/specs/<feature>/plan.md` exists with the technical approach.
3. A `.specify/specs/<feature>/tasks.md` exists with actionable tasks.
4. Each artifact has `status: draft | approved | superseded` in its
   frontmatter.

The `phase-2-to-3` gate refuses advancement while these are missing or
`draft`. See also `.claude/commands/specify.md`, `/plan.md`, `/tasks.md`.

## IX. BMAD bifurcation for Level ≥ 2

For complexity Level 2 and 3 work:

1. **Planning Phase** completes end-to-end before Dev Cycle starts.
   Produces: PRD shard, Architecture shard, story-sharded tasks with
   context bundles.
2. **Dev Cycle** consumes stories one by one; stories carry their full
   context bundle so the developer (human or Copilot Cloud Agent) starts
   with everything they need.

See `.claude/commands/bmad-plan.md` and `.claude/commands/bmad-dev.md`.

## X. Parallelism prefers Copilot Cloud Agent

When a phase can parallelize, the default strategy is **Copilot Cloud Agent**:
issues are created, assigned to `@copilot`, and tracked through PR review.
Local `parallel-workers` (git worktrees) is the fallback for tasks that
require local environment access.

See `.claude/skills/copilot-cloud-agent/` and
`sdlc.parallelization.strategies` in `.claude/settings.json`.

## XI. Harness integrity

Every agent, skill or command that changes MUST have its behavior covered
by a golden case in `evals/`. Changes that ship without an eval update are
a regression risk and MUST be rejected by review.

Hooks MUST use `$CLAUDE_PROJECT_DIR` for script resolution (ADR-001).

---

## Amendment procedure

1. Open an ADR describing the proposed change and reasons.
2. If the amendment weakens any principle above, `compliance-guardian`
   must explicitly approve.
3. On merge, bump `Version` at the top of this file and add a row to the
   changelog below.

## Changelog

| Version | Date       | Change                                          |
|---------|------------|-------------------------------------------------|
| 1.0.0   | 2026-04-15 | Initial ratification. Principles I through XI. |
