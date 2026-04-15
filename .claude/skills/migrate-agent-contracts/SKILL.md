---
name: migrate-agent-contracts
version: 1.0.0
description: |
  One-shot utility skill that migrates every agent under `.claude/agents/`
  to carry a tier-2 contract_version=1.0 frontmatter block, as required
  by Constitution Principle XI. Idempotent — agents that already have a
  contract are skipped verbatim. This skill is scheduled for removal
  after Phase B closes; its value is historical reproducibility.

category: meta
phase: null
complexity_levels: [1]
user-invocable: false

allowed-tools:
  - Read
  - Write
  - Bash

scripts:
  bulk_migrate: scripts/bulk_migrate.py

dependencies:
  python:
    - pyyaml
---

# Migrate Agent Contracts (Phase B)

## Usage

```bash
# Dry run — report what would change, touch nothing
python3 .claude/skills/migrate-agent-contracts/scripts/bulk_migrate.py --dry-run

# Real migration — inserts contracts, writes report
python3 .claude/skills/migrate-agent-contracts/scripts/bulk_migrate.py

# Re-run after partial migration — idempotent
python3 .claude/skills/migrate-agent-contracts/scripts/bulk_migrate.py
```

## Report artifact

`.project/reports/migration-contracts-phase-b.yml` records every decision:

```yaml
migration:
  run_at: 2026-04-15T00:00:00Z
  total_agents_found: 40
  already_contracted: 6
  newly_contracted: 34
  skipped_errors: 0
  per_agent:
    - name: alignment-agent
      action: added_contract
      inferred_role: generic
      max_tokens: 25000
```

## When this skill is deleted

When `.project/reports/migration-contracts-phase-b.yml` shows 100%
coverage and `evals/agent-contracts/runner.py` has run green for at
least one full release cycle, this skill directory should be removed.
The migration it performed is already in git history.
