# SDLC Agêntico — Eval Harness

This directory is the **regression suite for agents and skills**. It exists for
one reason: when prompts, agent definitions, gate YAMLs or skill scripts
change, we need **objective evidence** that behavior did not regress.

> If you cannot prove an agent still works after a refactor, the agent does
> not work — you just don't know yet.

## Layout

```
evals/
├── README.md                    # this file
├── run_all.py                   # entry point — runs every suite
├── _lib/
│   └── harness.py               # shared eval primitives (Case, Suite, Report)
├── gate-evaluator/
│   ├── runner.py                # invokes validate_gate.py against golden inputs
│   └── golden/
│       ├── 001-missing-spec/    # one folder = one case
│       │   ├── case.yml         # case description + expected decision
│       │   └── project/         # synthetic project state
│       └── ...
├── code-reviewer/               # (planned) golden PRs with known issues
├── threat-modeler/              # (planned)
└── requirements-analyst/        # (planned)
```

## How to run

```bash
# Run every suite
python3 evals/run_all.py

# Run a single suite
python3 evals/gate-evaluator/runner.py

# JSON output for CI
python3 evals/run_all.py --json
```

Exit codes:

- `0` — every case passed
- `1` — at least one case failed
- `2` — harness error (missing dependency, malformed case)

## Authoring a golden case

A case has two artifacts:

1. `case.yml` — declarative metadata. **Never executable code.**
2. `project/` — a synthetic project tree the agent will operate on.

Minimal `case.yml`:

```yaml
case_id: 001-missing-spec
description: Phase 2→3 must reject when no spec.md exists
agent: gate-evaluator
inputs:
  from_phase: 2
  to_phase: 3
  project_id: synthetic-001
expected:
  decision: reject          # approve | reject | escalate
  passed: false
  has_blocker_of_type: artifact
```

The runner loads `case.yml`, points the agent at `project/`, and asserts each
field of `expected`. Any new key in `expected` that the runner does not
understand triggers a harness error (no silent passes).

## Why this design

- **Cases as folders, not Python tests** — non-developers (PMs, QA) can write
  golden cases by editing YAML and dropping files. No `pytest` literacy needed.
- **One case per folder** — git diffs are scoped, review is trivial, deletion
  is a single `rm -rf`.
- **Synthetic projects, not fixtures** — the project tree IS the test data.
  Reviewers can read it as they would a real repo.
- **Decision-based assertions** — we assert what the agent decided, not how.
  Refactors that preserve decisions do not break evals.

## CI integration (planned)

Workflow `.github/workflows/evals.yml` (to be added) runs `evals/run_all.py`
on every PR that touches `.claude/agents/**`, `.claude/skills/**`, or
`evals/**`. PR fails if regression rate exceeds 0%.

## Coverage targets

| Agent / Skill         | Initial cases | Target |
|-----------------------|---------------|--------|
| gate-evaluator        | 4             | 20     |
| code-reviewer         | 0             | 15     |
| threat-modeler        | 0             | 10     |
| requirements-analyst  | 0             | 10     |
| spec-kit-integration  | 0             | 8      |

Track progress in `.project/reports/eval-coverage.yml`.
