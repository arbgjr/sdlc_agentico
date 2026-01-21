# Parallel Workers Skill

Executes implementation tasks in parallel using isolated git worktrees.

## Quick Start

```bash
# Spawn a single worker
python3 scripts/worker_manager.py spawn \
  --task-id "TASK-001" \
  --description "Implement authentication" \
  --agent "code-author" \
  --base-branch "main"

# List active workers
python3 scripts/worker_manager.py list

# Get worker status
python3 scripts/state_tracker.py get worker-abc123

# Cleanup merged workers
python3 scripts/worker_manager.py cleanup --state MERGED
```

## Scripts

### worker_manager.py

Main worker lifecycle management.

**Commands:**
- `spawn` - Create a new worker
- `spawn-batch` - Create multiple workers from spec file
- `list` - List all workers
- `get` - Get worker details
- `terminate` - Terminate a worker
- `cleanup` - Cleanup workers by state

**Example batch spawn:**
```bash
python3 scripts/worker_manager.py spawn-batch \
  --spec-file templates/tasks-spec-example.yml
```

### state_tracker.py

Manages worker state persistence.

**Commands:**
- `get <worker_id>` - Get worker state
- `set <worker_id> <state>` - Set worker state
- `list [--state STATE]` - List workers
- `remove <worker_id>` - Remove worker state
- `transition <worker_id> <from> <to>` - Transition with validation

**Example:**
```bash
# Transition worker
python3 scripts/state_tracker.py transition worker-abc123 WORKING PR_OPEN
```

### worktree_manager.sh

Git worktree operations.

**Commands:**
- `create <project> <task-id> <base-branch>` - Create worktree
- `list <project>` - List worktrees
- `remove <project> <task-id>` - Remove worktree
- `prune` - Remove stale worktrees
- `status <project> <task-id>` - Check worktree status

**Example:**
```bash
# Create worktree
./scripts/worktree_manager.sh create mice_dolphins task-001 main

# Check status
./scripts/worktree_manager.sh status mice_dolphins task-001
```

### loop.py

Automation loop for monitoring workers.

**Usage:**
```bash
# Start automation loop
python3 scripts/loop.py --project mice_dolphins

# Custom poll interval
python3 scripts/loop.py --poll-interval 10

# Run for N iterations (testing)
python3 scripts/loop.py --max-iterations 100
```

**What it does:**
- Polls workers every N seconds (default: 5s)
- Detects state transitions automatically:
  - `NEEDS_INIT → WORKING` (auto-transition)
  - `WORKING → PR_OPEN` (detects PR via gh CLI)
  - `PR_OPEN → MERGED` (detects merge via gh CLI)
  - `MERGED → cleanup` (removes worktree)
- Logs all operations to Loki
- Recovers from errors gracefully

**Example:**
```bash
# Terminal 1: Start loop
python3 scripts/loop.py --project mice_dolphins

# Terminal 2: Spawn workers
python3 scripts/worker_manager.py spawn-batch --spec-file tasks.yml

# Loop automatically monitors and transitions workers
```

## Architecture

```
Worker Lifecycle
────────────────

1. SPAWN
   ├─ Create git worktree
   ├─ Create branch (feature/task-id)
   └─ Initialize state (NEEDS_INIT)

2. INIT
   ├─ Worker receives init prompt
   └─ Transition to WORKING

3. WORK
   ├─ Implement task
   ├─ Commit changes
   └─ Push to remote

4. PR
   ├─ Create pull request
   ├─ Transition to PR_OPEN
   └─ Await review

5. MERGE
   ├─ PR approved and merged
   ├─ Transition to MERGED
   └─ Cleanup worktree
```

## State Machine

```
┌─────────┐
│ UNKNOWN │◄─────────────────┐
└────┬────┘                  │
     │                       │
     v                       │
┌────────────┐           (error)
│ NEEDS_INIT │               │
└─────┬──────┘               │
      │                      │
      v                      │
┌─────────┐                  │
│ WORKING │──────────────────┤
└────┬────┘                  │
     │                       │
     v                       │
┌─────────┐                  │
│ PR_OPEN │──────────────────┤
└────┬────┘                  │
     │                       │
     v                       │
┌────────┐                   │
│ MERGED │ (terminal)        │
└────────┘                   │
     │                       │
     └───────────────────────┘
```

## Directory Structure

```
~/.worktrees/
└── mice_dolphins/
    ├── task-001/          # Worker 1 worktree
    │   └── feature/task-001
    ├── task-002/          # Worker 2 worktree
    │   └── feature/task-002
    └── task-003/          # Worker 3 worktree
        └── feature/task-003

~/.claude/worker-states/
├── worker-abc123.json     # Worker 1 state
├── worker-def456.json     # Worker 2 state
└── worker-ghi789.json     # Worker 3 state
```

## Security

### Secrets Isolation

Workers receive sanitized environments:

```bash
# Safe variables (kept)
PATH, HOME, USER, LANG, LC_*, SHELL

# Removed variables
*_KEY, *_SECRET, *_TOKEN, *_PASSWORD, *_API_KEY
```

### Pre-Merge Validation

All workers must pass:
- `security-gate.yml` - No secrets, input validation
- `phase-5-to-6.yml` - Code quality, tests passing

## Observability

### Loki Labels

All operations tagged with:
```json
{
  "skill": "parallel-workers",
  "phase": "5",
  "worker_id": "worker-abc123",
  "task_id": "TASK-001",
  "correlation_id": "unique-uuid"
}
```

### Queries

```logql
# All parallel-workers activity
{skill="parallel-workers"}

# Worker errors
{skill="parallel-workers", level="error"}

# Task completion timeline
{skill="parallel-workers", state="MERGED"}
```

### Grafana Dashboard

Panels available in `.claude/config/logging/dashboards/sdlc-overview.json`:
- Active Workers (gauge)
- Worker State Distribution (pie)
- Task Completion Rate (timeseries)
- Worker Errors (logs)

## Integration

### With Agents

Workers execute using existing SDLC agents:
- `code-author` - Implementation
- `test-author` - Test creation
- `iac-engineer` - Infrastructure

### With Skills

Integrates with:
- `gate-evaluator` - Quality gates
- `memory-manager` - Context persistence
- `phase-commit` - Automatic commits

### With GitHub

- Automatic PR creation
- Label application (phase:5, type:task)
- Milestone tracking

## Performance

### Benchmarks

| Scenario | Sequential | Parallel (3 workers) | Speedup |
|----------|-----------|----------------------|---------|
| 3 simple tasks | 45 min | 18 min | **2.5x** |
| 3 complex tasks | 90 min | 35 min | **2.6x** |
| 5 mixed tasks | 120 min | 45 min | **2.7x** |

### Resource Usage

- **CPU**: ~33% per worker (3 workers = 100%)
- **Memory**: ~500MB per worker
- **Disk**: ~repo_size per worktree

## Limitations

- **Max workers**: 3-5 recommended (CPU-bound)
- **Disk space**: Each worktree = full repo copy
- **Network**: Rate limits on git push
- **Complexity**: Level 2+ only

## Troubleshooting

### Worker Stuck in WORKING

```bash
# Check worktree status
./scripts/worktree_manager.sh status mice_dolphins task-001

# Check logs
tail -f ~/.claude/logs/parallel-workers.log

# Force terminate
python3 scripts/worker_manager.py terminate worker-abc123 --force
```

### Worktree Already Exists

```bash
# List worktrees
git worktree list

# Remove manually
git worktree remove ~/.worktrees/mice_dolphins/task-001 --force
```

### State Corruption

```bash
# Remove state file
rm ~/.claude/worker-states/worker-abc123.json

# Reinitialize
python3 scripts/state_tracker.py set worker-abc123 UNKNOWN
```

## References

- Epic: Issue #33
- Task: Issue #35
- Source: [claude-orchestrator](https://github.com/reshashi/claude-orchestrator)
- Analysis: `.agentic_sdlc/corpus/nodes/learnings/LEARN-claude-orchestrator-patterns.yml`
