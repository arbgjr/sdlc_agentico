---
name: constitution
description: |
  Loads and displays the project Constitution, the non-negotiable principles
  that every agent, skill and contributor must honor. Use at the start of a
  new feature, before approving any PR, or when orienting a new agent session.

  Examples:
  - <example>
    user: "/constitution"
    assistant: "Vou carregar a constituição do projeto e resumir os 11 princípios"
    </example>
  - <example>
    user: "/constitution amend"
    assistant: "Vou guiá-lo pelo processo de emenda via ADR"
    </example>
---

# Load the Project Constitution

## What this command does

1. Reads `.specify/memory/constitution.md` in full.
2. Emits a structured digest:
   - Current version
   - Each principle with a one-line summary
   - Any principles that have been recently amended (compared to last ADR)
3. Registers that the current session has the Constitution in its context,
   so subsequent `/specify`, `/plan`, `/tasks`, `/implement` invocations
   can reference it without reloading.

## Instructions

### Mode: default (no arguments)

1. Read `.specify/memory/constitution.md`.
2. For each principle (I through XI), print:
   ```
   [I] Natural-language-first — All agents and skills authored as markdown.
   [II] Anti-mock policy (ABSOLUTE) — No mocks/stubs in production code.
   ...
   ```
3. End with: `Constitution v<version> loaded. Amendments require ADR + version bump.`

### Mode: `amend`

1. Ask the user which principle is being amended and the reason.
2. Create ADR skeleton at
   `.project/corpus/nodes/decisions/ADR-XXX-constitution-amendment-<slug>.yml`
   using `.agentic_sdlc/templates/adr-template.yml`.
3. Require `compliance-guardian` approval field in the ADR before merging.
4. On merge, update `.specify/memory/constitution.md`:
   - Bump Version per semver (MAJOR for a principle removal or weakening)
   - Add changelog row
   - If a principle is superseded, prefix its heading with `~~SUPERSEDED~~`

### Mode: `verify`

1. Read `.specify/memory/constitution.md`.
2. For each principle, check concrete enforcement:
   - Principle II → `grep -rnE "(mock|stub|fake|dummy)" src/` outside `tests/`
   - Principle V → every commit with `feat(` has an ADR in
     `.project/corpus/nodes/decisions/` created in the same PR
   - Principle XI → hooks in settings.json use `$CLAUDE_PROJECT_DIR`
     (delegates to `evals/settings-lint/runner.py`)
3. Report violations by principle with paths and severity.

## Output format

```yaml
constitution:
  version: "1.0.0"
  loaded_at: "2026-04-15T10:30:00Z"
  principles:
    - id: I
      name: Natural-language-first
      summary: "Agents and skills authored as markdown first"
    # ... through XI
  amendments_since_last_load: []
  next_actions:
    - "Reference specific principle IDs in PR descriptions"
    - "Quote principle text in ADR 'context' sections"
```

## Gotchas

- Do NOT paraphrase principles — quote verbatim to avoid semantic drift.
- If the file is missing, treat as a CRITICAL failure: block any SDD
  command from proceeding and instruct user to restore it.
- The Constitution is the SOURCE OF TRUTH. Any conflict with CLAUDE.md or
  other docs is resolved in favor of the Constitution.
