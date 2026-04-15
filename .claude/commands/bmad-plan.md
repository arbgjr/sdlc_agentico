---
name: bmad-plan
description: |
  Executes the BMAD Planning Phase for a Level ≥ 2 feature:
  produces PRD shard, Architecture shard, and shardedstories with
  context bundles BEFORE any code is written. The mandatory predecessor
  to /bmad-dev.

  Examples:
  - <example>
    user: "/bmad-plan pix-checkout"
    assistant: "Vou executar Planning Phase: PRD + Architecture + Stories shardadas"
    </example>
---

# BMAD Planning Phase

## Invariants

1. Planning is a SINGLE deliberative pass. It does NOT parallelize.
   It produces the plan bundle that subsequent parallel work consumes.
2. Planning MUST complete end-to-end before `/bmad-dev` runs.
3. Planning output is **immutable** for the Dev Cycle: any change
   during Dev Cycle requires re-entry to Planning (versioned).

## Steps

1. **Detect complexity level** (should be 2 or 3). If 0 or 1, refuse
   and suggest `/quick-fix` or `/new-feature`:
   ```bash
   python3 .claude/skills/bmad-integration/scripts/detect_level.py --text "<desc>"
   ```

2. **Load the Constitution** via `/constitution`. Quote principles
   II, III, V, VIII, IX in the outputs.

3. **Run `/specify <description>`** to produce
   `.specify/specs/<slug>/spec.md`. This is the PRD shard.

4. **Run `/clarify <slug>`** until zero questions remain.

5. **Run `/analyze <slug>` to flip spec to `status: approved`.**

6. **Run `/plan <slug>`** to produce the Architecture shard:
   - `.specify/specs/<slug>/plan.md`
   - `.specify/specs/<slug>/data-model.md`
   - `.specify/specs/<slug>/api-contracts.yml`
   - `.specify/specs/<slug>/threat-model.yml`
   - ADRs under `.project/corpus/nodes/decisions/`

7. **Run `/tasks <slug>`** to shard the plan into story-context tasks:
   - `.specify/specs/<slug>/tasks.md` (index)
   - `.specify/specs/<slug>/tasks/TASK-NNN-*.md` (context-engineered)
   - `.specify/specs/<slug>/strategy.yml` (parallelization routing)

8. **Gate-check phase-2-to-3 and phase-3-to-4** — both must pass.
   If either rejects, Planning Phase is incomplete; loop back to the
   failing step.

9. **Freeze** the plan bundle: tag a commit
   `plan-<slug>-v1` on the feature branch. Any further Planning work
   increments the version.

## Output

```yaml
planning_phase:
  slug: pix-checkout
  level: 2
  artifacts:
    prd: .specify/specs/pix-checkout/spec.md
    architecture: .specify/specs/pix-checkout/plan.md
    data_model: .specify/specs/pix-checkout/data-model.md
    api_contracts: .specify/specs/pix-checkout/api-contracts.yml
    threat_model: .specify/specs/pix-checkout/threat-model.yml
    tasks_index: .specify/specs/pix-checkout/tasks.md
    strategy: .specify/specs/pix-checkout/strategy.yml
  adrs_created: [ADR-042, ADR-043]
  stories_count: 12
  strategy_primary: copilot_cloud_agent
  frozen_at: plan-pix-checkout-v1
  next_command: /bmad-dev pix-checkout
```

## Do NOT

- Do NOT write application code here. Planning is deliberation.
- Do NOT skip /clarify. Specs with unresolved ambiguity destroy
  the BMAD context-engineering premise.
- Do NOT approve specs that have not passed /analyze. The gate will
  catch this but doing it manually is a bad smell.
