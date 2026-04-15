---
plan_id: agents-contracts-phase-b-technical-plan
spec_ref: agents-contracts-phase-b
status: approved
adr_refs: []
---

# Technical Plan — Phase B Agent Contracts Migration

## Approach

A one-shot migration script reads each agent file, parses its frontmatter
as YAML, inspects the existing fields to infer role, and appends a
contract block **inside the existing frontmatter**. If `contract_version`
already exists, the file is left untouched (idempotency).

The script is deliberately a one-time utility — it lives under
`.claude/skills/migrate-agent-contracts/scripts/` and will be removed
after Phase B closes. The pattern it establishes is the template every
new agent PR must honor.

## Components touched

| Path | Change |
|---|---|
| `.claude/agents/*.md` (34 files) | frontmatter augmented with contract block |
| `.claude/skills/migrate-agent-contracts/SKILL.md` | new (short-lived utility) |
| `.claude/skills/migrate-agent-contracts/scripts/bulk_migrate.py` | new |
| `evals/agent-contracts/runner.py` | allowlist expanded from 6 to ALL agents |
| `.project/reports/migration-contracts-phase-b.yml` | generated run report |

## Technology choices

| Choice | Rationale | Trade-off |
|---|---|---|
| Python + PyYAML | Already in repo's toolchain, stdlib-ish | Adds no new dep |
| In-place edit with anchor detection | Preserves user formatting | Regex-based; fragile to exotic YAML constructs (none seen) |
| Idempotent skip-if-exists | Safe to re-run | If a contract is malformed, re-run does not fix it — report flags |
| Tier-2 minimal contract | Fast migration, low review cost | Less strictness than tier-1; explicit follow-up required |

## Role inference heuristic

```
role_to_defaults = {
  "analyst":     {max_tokens: 25000, sla_p95: 90,  output: markdown},
  "reviewer":    {max_tokens: 30000, sla_p95: 45,  output: yaml},
  "author":      {max_tokens: 40000, sla_p95: 120, output: file_tree},
  "engineer":    {max_tokens: 35000, sla_p95: 180, output: file_tree},
  "architect":   {max_tokens: 40000, sla_p95: 180, output: markdown},
  "scanner":     {max_tokens: 20000, sla_p95: 300, output: yaml},
  "manager":     {max_tokens: 30000, sla_p95: 60,  output: yaml},
  "simulator":   {max_tokens: 30000, sla_p95: 120, output: markdown},
  "generator":   {max_tokens: 25000, sla_p95: 90,  output: file_tree},
  "curator":     {max_tokens: 20000, sla_p95: 60,  output: yaml},
  "commander":   {max_tokens: 30000, sla_p95: 60,  output: yaml},
  "interrogator":{max_tokens: 20000, sla_p95: 60,  output: markdown},
  "challenger":  {max_tokens: 20000, sla_p95: 60,  output: markdown},
  "governance":  {max_tokens: 30000, sla_p95: 120, output: yaml},
  "researcher":  {max_tokens: 30000, sla_p95: 180, output: markdown},
  "designer":    {max_tokens: 30000, sla_p95: 180, output: file_tree},
  "writer":      {max_tokens: 15000, sla_p95: 60,  output: markdown},
  "default":     {max_tokens: 25000, sla_p95: 90,  output: markdown},
}
```

## Rollout

1. Write `bulk_migrate.py` with dry-run mode first.
2. Run dry-run — confirm 34 agents detected, 6 skipped.
3. Run real migration — inspect 2-3 files manually.
4. Expand `evals/agent-contracts/runner.py` allowlist to all agents.
5. Run `python3 evals/run_all.py` — all suites must pass.
6. Commit + push.

## Rollback

Plain `git revert` of the migration commit. Idempotency means the script
can also be re-run after a partial revert.
