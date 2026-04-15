---
name: tasks
description: |
  Shards an approved plan into implementation tasks with context bundles.
  Each task is a self-contained unit ready for Copilot Cloud Agent or
  a human developer. Output drives the Implementation phase.

  Examples:
  - <example>
    user: "/tasks pix-checkout"
    assistant: "Vou quebrar o plan em tasks com context bundles"
    </example>
---

# Shard a Plan into Context-Engineered Tasks

## Invariants

1. `/tasks <slug>` REQUIRES `.specify/specs/<slug>/plan.md` with
   `status: approved`.
2. Every task carries a **context bundle** (Principle IX — BMAD).
3. Tasks are the primary input for Phase 6 (Implementation), regardless
   of whether they are executed by Copilot Cloud Agent, humans, or
   parallel-workers.

## Steps

1. **Load** Constitution + spec + plan + ADRs referenced in plan.

2. **Invoke `delivery-planner`** (acts as Scrum Master in BMAD) to:
   - Break plan into tasks of ≤ 1 day of work each.
   - Identify dependencies (task A before task B).
   - Estimate effort (Fibonacci points).
   - Group into milestones / sprints if Level ≥ 2.

3. For **each task**, produce a self-contained story file at
   `.specify/specs/<slug>/tasks/TASK-NNN-<slug>.md` using the template at
   `.agentic_sdlc/templates/story-context.md`, containing:
   - **Task description** — what, not how
   - **Acceptance criteria** — copied verbatim from spec
   - **Context bundle**:
     - Paths of files the implementer will likely touch
     - ADRs applicable to this task (quote the decision)
     - Patterns to follow (link `.agentic_sdlc/corpus/patterns/`)
     - Anti-patterns to avoid (link `.project/corpus/nodes/learnings/`)
   - **Test plan** — unit + integration scope
   - **Out of scope** — explicit list to prevent scope creep
   - **Parallelization hint**: `copilot_cloud_agent | local_worker | human_only`

4. **Write** `.specify/specs/<slug>/tasks.md` as an index:
   ```markdown
   # Tasks — pix-checkout

   | ID       | Title                       | Points | Depends on | Parallelizable |
   | -------- | --------------------------- | ------ | ---------- | -------------- |
   | TASK-001 | PIX provider interface      | 3      | —          | yes            |
   | TASK-002 | QR code rendering           | 5      | TASK-001   | yes            |
   | ...      | ...                         | ...    | ...        | ...            |
   ```

5. **Emit strategy plan** for Phase 6:
   - Count of `parallelization_hint: copilot_cloud_agent` tasks → default route
   - Count of `human_only` tasks → assign via GitHub project board
   - Count of `local_worker` → parallel-workers worktrees

## Output

- `.specify/specs/<slug>/tasks.md` (index)
- `.specify/specs/<slug>/tasks/TASK-NNN-*.md` (one per task, context-engineered)
- `.specify/specs/<slug>/strategy.yml`:
  ```yaml
  strategy:
    primary: copilot_cloud_agent
    fallback: parallel_workers
    human_only_count: 2
    parallel_count: 8
    sequential_count: 1
  ```

## Do NOT

- Do NOT write code. Tasks describe WHAT to implement, not HOW.
- Do NOT omit the context bundle. A story without context bundle is a
  ticket with a Jira ID — useless for Copilot Cloud Agent.
- Do NOT merge multiple concerns into one task. If a task has "and" in
  its title, it is probably two tasks.
