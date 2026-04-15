# Agent Contract Template

Every agent under `.claude/agents/*.md` MUST declare an explicit contract
in its YAML frontmatter. A contract makes the agent testable, reviewable,
and composable.

The fields below are *in addition* to the existing Claude Code agent
frontmatter (`name`, `description`, `tools`, etc.). They are consumed by
`evals/agent-contracts/runner.py` (future) to validate that agents
respect their declared shapes.

## Required frontmatter fields

```yaml
---
# Standard fields (existing)
name: <agent-slug>
description: |
  One-paragraph purpose.
model: opus | sonnet | haiku

# --- Contract fields (NEW — REQUIRED as of Constitution v1.0.0) ---

contract_version: "1.0"

inputs:
  - name: <input_name>
    type: string | path | yaml | markdown | json
    required: true | false
    description: <one-liner>
  - ...

outputs:
  - name: <output_name>
    type: file | yaml | markdown | json | stdout
    path_pattern: .specify/specs/*/spec.md        # if type=file
    description: <one-liner>
    contains:
      - <invariant the output must satisfy>
      - ...

context_budget:
  max_tokens: 30000              # hard cap per invocation
  required_files:                # always loaded into context
    - .specify/memory/constitution.md
    - .agentic_sdlc/docs/playbook.md
  optional_files:
    - .specify/specs/<slug>/spec.md
  corpus_queries:
    - "ADRs for <domain>"

preconditions:
  - <must hold before the agent runs>
  - "feature branch is current with base"

postconditions:
  - <must hold after successful run>
  - "every file in outputs exists and is non-empty"

failure_modes:
  - trigger: <observable condition>
    severity: critical | high | medium | low
    recovery: <what the orchestrator should do>

sla:
  wallclock_seconds_p95: 60
  max_retries: 2

observability:
  emit_event: <event_name>
  metrics:
    - tokens_consumed
    - tool_calls
    - tool_failures

allowed_tools:
  - Read
  - Write
  - Edit
  - mcp__github__issue_read
denied_tools:
  - Task
---
```

## Example: gate-evaluator contract (FILLED)

```yaml
contract_version: "1.0"

inputs:
  - name: from_phase
    type: integer
    required: true
    description: Current SDLC phase (0..8)
  - name: to_phase
    type: integer
    required: true
    description: Target SDLC phase (1..9)
  - name: project_dir
    type: path
    required: true
    description: Absolute path to the project root

outputs:
  - name: gate_result
    type: yaml
    description: Structured decision (approve/reject/escalate) with evidence
    contains:
      - decision in [approve, reject, escalate]
      - passed is boolean
      - score in [0.0, 1.0]
      - artifact_checks is list
      - quality_checks is list
      - blockers is list

context_budget:
  max_tokens: 30000
  required_files:
    - .specify/memory/constitution.md
    - .claude/skills/gate-evaluator/gates/phase-<from>-to-<to>.yml
  corpus_queries: []

preconditions:
  - "gate YAML file exists"

postconditions:
  - "if decision == approve then all required artifacts present"
  - "if decision == escalate then human_approval_required is true"

failure_modes:
  - trigger: "gate YAML not found"
    severity: high
    recovery: "raise GateNotFoundError to caller with remediation hint"
  - trigger: "gate YAML malformed"
    severity: critical
    recovery: "block, escalate to playbook-governance"

sla:
  wallclock_seconds_p95: 8
  max_retries: 1

observability:
  emit_event: gate.decision
  metrics:
    - gate_decision
    - artifact_check_pass_rate
    - quality_check_pass_rate

allowed_tools:
  - Read
  - Glob
  - Grep
  - Bash  # for shell-style quality checks
denied_tools:
  - Task
  - Write  # gate-evaluator is read-only; approvals flip status via /analyze
```

## Why this matters

A contract turns an agent from "a blob of prose" into **a composable
component with a verifiable interface**. Specifically:

1. **Testability** — `evals/agent-contracts/runner.py` can assert every
   agent's outputs match its declared shape.
2. **Composability** — orchestrator can type-check agent pipelines
   (`/specify` output → `/plan` input) before running them.
3. **Debuggability** — when an agent misbehaves, the contract tells you
   what preconditions or postconditions likely broke.
4. **Cost control** — `context_budget` is enforced by the token
   counter; overruns are visible in logs.

## Migration plan

- [ ] Phase A — new agents MUST include contract fields from inception.
- [ ] Phase B — existing agents are migrated in priority order:
  - gate-evaluator
  - code-reviewer
  - requirements-analyst
  - system-architect
  - threat-modeler
  - security-scanner
  - orchestrator
- [ ] Phase C — `evals/agent-contracts/` runner enforces contract presence.
- [ ] Phase D — CI fails PRs that add agents without contracts.
