---
name: parallel-spawn
description: |
  Spawn parallel workers for Phase 5 Implementation tasks.
  Creates isolated git worktrees for concurrent development.
version: "1.0.0"
phase: 5
complexity: [2, 3]
---

# /parallel-spawn

Spawns parallel workers for concurrent task execution in Phase 5 (Implementation).

## Usage

### Single Worker

```bash
/parallel-spawn --task TASK-001 --desc "Implement authentication" --agent code-author
```

### Batch from YAML

```bash
/parallel-spawn --batch tasks.yml
```

## Prerequisites

- **Phase**: Must be in Phase 5 (Implementation)
- **Complexity**: Level 2+ (Level 0/1 remain sequential)
- **Tasks**: Tasks must be independent (no blocking dependencies)
- **Branch**: Must be on feature branch

## Workflow

1. **You provide task spec** (single or batch YAML)
2. **Claude spawns workers** using parallel-workers skill
3. **Automation loop monitors** (optional, can run manually)
4. **Workers execute independently** in isolated worktrees
5. **PRs created automatically** when workers complete
6. **Merge after review** → automation loop cleans up

## Task Spec Format (YAML)

```yaml
project: mice_dolphins
base_branch: main

tasks:
  - id: TASK-001
    description: "Implement user authentication"
    agent: code-author
    priority: 10
    dependencies: []

  - id: TASK-002
    description: "Create unit tests for auth"
    agent: test-author
    priority: 9
    dependencies:
      - TASK-001

  - id: TASK-003
    description: "Generate Terraform for App Service"
    agent: iac-engineer
    priority: 8
    dependencies: []
```

## Examples

### Example 1: Quick spawn (3 independent tasks)

```
User: /parallel-spawn --batch
```

Claude will:
1. Ask for task descriptions
2. Generate task spec
3. Spawn workers
4. Start automation loop (optional)

### Example 2: From existing spec

```
User: /parallel-spawn --batch .agentic_sdlc/projects/current/tasks.yml
```

### Example 3: Manual control

```
User: Spawn 3 workers for these tasks:
- TASK-001: Implement login endpoint
- TASK-002: Write tests
- TASK-003: Add Terraform config
```

Claude will:
1. Create task spec
2. Spawn workers
3. Provide manual commands if automation loop not desired

## Integration with SDLC

### Phase 4 → 5 Transition

The **delivery-planner** agent can generate task specs during planning:

```
Phase 4 (Planning):
  ├─ delivery-planner creates tasks.yml
  └─ Outputs to .agentic_sdlc/projects/current/tasks.yml

Phase 5 (Implementation):
  ├─ /parallel-spawn --batch tasks.yml
  ├─ Workers execute in parallel
  └─ PRs merged → Phase 6 (Quality)
```

### With orchestrator

The **orchestrator** agent can automatically spawn workers when entering Phase 5:

```yaml
on_phase_enter:
  phase: 5
  if: complexity >= 2 AND tasks > 1
  action: spawn_parallel_workers
```

## Monitoring

### Start automation loop (recommended)

```bash
python3 .claude/skills/parallel-workers/scripts/loop.py --project mice_dolphins
```

### Manual monitoring

```bash
# List workers
python3 .claude/skills/parallel-workers/scripts/worker_manager.py list

# Check state
python3 .claude/skills/parallel-workers/scripts/state_tracker.py get worker-abc123

# Cleanup merged
python3 .claude/skills/parallel-workers/scripts/worker_manager.py cleanup --state MERGED
```

### Grafana Dashboard

Import `.claude/config/logging/dashboards/parallel-workers.json` to monitor:
- Active Workers (gauge)
- State Distribution (pie)
- Task Completion Rate (timeseries)
- Errors (logs)

## Limitations

- **Max workers**: 3-5 recommended (CPU-bound)
- **Disk usage**: Each worktree = repo size
- **Complexity**: Level 2+ only (0/1 sequential)
- **Dependencies**: Workers with dependencies spawn after blockers complete

## Troubleshooting

### Workers not spawning

```bash
# Check git status
git status

# Check branch
git branch

# Verify phase
/phase-status
```

### Automation loop not detecting PRs

```bash
# Ensure gh CLI authenticated
gh auth status

# Manually transition
python3 .claude/skills/parallel-workers/scripts/state_tracker.py transition worker-abc123 WORKING PR_OPEN
```

### Cleanup stale workers

```bash
# Force cleanup all
python3 .claude/skills/parallel-workers/scripts/worker_manager.py cleanup

# Prune stale worktrees
.claude/skills/parallel-workers/scripts/worktree_manager.sh prune
```

## See Also

- `/phase-status` - Check current phase
- `/gate-check` - Validate phase transition
- Skill: `.claude/skills/parallel-workers/README.md`
- ADR: `ADR-claude-orchestrator-integration.yml`
