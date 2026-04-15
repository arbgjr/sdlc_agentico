---
spec_id: agents-contracts-phase-b
status: approved
created_at: 2026-04-15T00:00:00Z
constitution_version: "1.0.0"
applicable_principles: [I, V, VII, XI]
clarify_rounds_completed: 1
last_clarified_at: 2026-04-15T00:00:00Z
complexity_level: 1
sdlc_command: /new-feature
---

# Phase B: Migrate Remaining Framework Agents to Contract v1.0

## Problem

Constitution v1.0.0 Principle XI requires every agent under
`.claude/agents/` to carry a formal contract in its frontmatter. Phase A
(prior session) migrated 6 priority agents to the strict contract form.
The remaining 34 agents have no contract, which means:

- They are not testable by `evals/agent-contracts/runner.py`.
- The orchestrator cannot type-check agent pipelines that include them.
- Context budgets are implicit and untracked.
- Failure modes are undocumented, so resilience wrappers cannot be
  selectively applied.

## Solution

Apply a **tier-2 minimal contract** to every non-priority agent, derived
from its existing frontmatter (name, description, skills, allowed/denied
tools). Tier-2 contracts require:

1. `contract_version: "1.0"` (so the eval recognizes them).
2. `inputs` — at minimum `{ name: request, type: markdown, required: true }`.
3. `outputs` — derived from the agent's role (document|code|review|decision).
4. `context_budget.max_tokens` — from a default table keyed on agent role.
5. `preconditions`, `postconditions` — one entry each, derived from role.
6. `failure_modes` — one default entry.
7. `sla.wallclock_seconds_p95` — from role-based default.
8. `observability.emit_event` — `<agent>.completed`.

Agents that need tier-1 strict contracts (complex I/O, high-stakes
decisions) are promoted later case-by-case.

## Acceptance criteria

- given: an agent file in `.claude/agents/<name>.md` without a contract
  when: the bulk migration script runs
  then: that file has a valid contract_version=1.0 frontmatter block,
        passes YAML parse, and does not lose any original content

- given: the migration completed
  when: `python3 evals/run_all.py` runs
  then: `agent-contracts` suite passes for all agents (not just the 6)
        AND all existing suites still pass (no regression)

- given: an agent already has a contract (priority 6)
  when: the migration script runs
  then: that file is skipped — pre-existing contract is preserved verbatim

- given: the migration ran once
  when: the migration script runs again
  then: it is idempotent (no double-insertion, no diff)

## Out of scope

- Filling tier-1 contracts for complex agents (code-author, adr-author,
  compliance-guardian etc.) — those are follow-up work.
- Editing agent bodies (only frontmatter changes).
- Converting `allowed_tools` ↔ `allowed-tools` naming inconsistency
  (separate tech-debt ticket).
- Creating runbooks for SLOs.

## Non-functional requirements

- The migration must complete in under 60 seconds total.
- The migration must be atomic per file: either the full contract is
  inserted or the file is untouched.
- The migration must produce a report YAML recording every file touched,
  every skipped, and every error (zero tolerance for silent skips).
