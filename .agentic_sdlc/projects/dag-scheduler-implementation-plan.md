# Technical Implementation Plan: DAG-Based Task Scheduler for SDLC Agêntico

## Executive Summary

This plan integrates a **DAG (Directed Acyclic Graph) based task scheduler** into the existing parallel workers infrastructure, enabling intelligent task orchestration based on dependency relationships. Inspired by Ralph TUI's orchestration patterns, this implementation will deliver **30-40% faster Phase 5 execution** through optimized parallelism and dependency-aware scheduling.

**Priority**: HIGH (Epic: "Autonomous SDLC Loop")
**Estimated Impact**: 2-3x speedup in Phase 5 implementation tasks
**Estimated Effort**: 2 weeks (MVP)

## Current State Analysis

**Existing Infrastructure** (solid foundation):
- ✅ Worker state machine with 6 states (UNKNOWN → NEEDS_INIT → WORKING → PR_OPEN → MERGED/ERROR)
- ✅ Git worktrees for isolated execution (`~/.worktrees/{project}/{task-id}/`)
- ✅ JSON state persistence (atomic writes)
- ✅ Automation loop (5s polling)
- ✅ Observability with Loki/Grafana
- ✅ Task specification via `tasks.yml`

**Critical Gaps** (need DAG scheduler):
- ❌ No topological sorting (tasks spawn in list order)
- ❌ No dependency validation (circular deps not detected)
- ❌ No dynamic spawning (all workers spawn at once)
- ❌ No critical path analysis
- ❌ No retry mechanism for transient failures

**Integration Points Identified**:
1. **worker_manager.py:spawn_batch()** - Intercept to build DAG
2. **loop.py** - Replace with DAG-aware polling loop
3. **state_tracker.py** - Sync worker completion to DAG
4. **gate-evaluator** - Add DAG integrity gate

---

## Proposed Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│              DAG Scheduler Layer (NEW)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DAGScheduler                 DependencyGraph          │
│  - build_dag()                (NetworkX)               │
│  - get_ready_tasks()          - topological_sort()     │
│  - mark_completed()           - cycle_detection()      │
│  - critical_path              - longest_path()         │
│                                                         │
│  ParallelismHint              LockManager              │
│  - task_type → max_workers    - file-based locks       │
│  - tests: 10 workers          - crash recovery         │
│  - refactors: 1 worker        - checkpoints            │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Existing Infrastructure (PRESERVE)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  worker_manager        state_tracker                   │
│  - spawn()             - load_state()                  │
│  - terminate()         - save_state()                  │
│  - spawn_batch() ◀─── ENHANCED WITH DAG                │
│                                                         │
│  loop.py              worktree_manager                 │
│  - poll_workers ◀──── ENHANCED WITH DAG                │
│  - spawn_ready        - create()                       │
│                       - cleanup()                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. DAGScheduler (`dag_scheduler.py`)

**Responsibilities**:
- Parse `tasks.yml` and build dependency graph
- Validate: no cycles, valid task IDs
- Track task states: PENDING → READY → RUNNING → COMPLETED/FAILED
- Spawn workers for READY tasks (dependencies satisfied)
- Calculate critical path for optimization
- Persist state for crash recovery

**Key Methods**:
```python
class DAGScheduler:
    def __init__(tasks: List[TaskNode], max_concurrent: int = 3)
    def get_ready_tasks() -> List[TaskNode]  # All deps satisfied
    def mark_completed(task_id: str) -> None
    def mark_failed(task_id: str) -> None  # Cascades to dependents
    def is_complete() -> bool
    def get_critical_path() -> List[str]  # Longest duration path
    def to_dict() -> dict  # For persistence
```

#### 2. LockManager (`lock_manager.py`)

**Responsibilities**:
- File-based locks for resource coordination (database migrations, etc.)
- Checkpoint management for crash recovery
- Timeout handling to prevent deadlocks

**Key Methods**:
```python
class LockManager:
    def acquire(resource: str, holder: str, timeout: float = 300)
    def is_locked(resource: str) -> bool
    def cleanup_expired() -> int

class CheckpointManager:
    def save(scheduler_state: dict, metadata: dict) -> None
    def load() -> Optional[dict]
    def clear() -> None
```

#### 3. Enhanced Loop (`loop.py`)

**Changes**:
- DAG-aware polling: syncs worker completion to DAG
- Dynamic spawning: spawns newly ready tasks as dependencies complete
- Checkpoint-based recovery: resumes from last checkpoint on crash

---

## Implementation Plan

### Phase 1: MVP (Week 1-2) - Core DAG Scheduler

**Deliverables**:
1. ✅ `dag_scheduler.py` with core graph operations
2. ✅ `lock_manager.py` with file-based locks and checkpoints
3. ✅ Integration with `worker_manager.py` (add `spawn_batch_with_dag()`)
4. ✅ Unit tests for cycle detection, topological sort, dependency resolution

**Implementation Order**:

**Step 1: Create `dag_scheduler.py`**
- Location: `.claude/skills/parallel-workers/scripts/dag_scheduler.py`
- Dependencies: `networkx>=3.0` (add to requirements.txt)
- Classes: `TaskNode`, `TaskStatus`, `DAGScheduler`, `ParallelismHint`
- Key features:
  - Build graph from task list with dependencies
  - Validate no cycles (fail fast with clear error)
  - Topological sort for execution order
  - `get_ready_tasks()` - returns tasks with all deps satisfied
  - `mark_completed()` - updates state and unblocks dependents
  - `to_dict()`/`from_dict()` - state persistence

**Step 2: Create `lock_manager.py`**
- Location: `.claude/skills/parallel-workers/scripts/lock_manager.py`
- Classes: `LockManager`, `CheckpointManager`
- Key features:
  - File-based locks using `fcntl.flock()` (atomic)
  - Timeout handling (default 5 minutes)
  - Checkpoint save/load for crash recovery
  - Expired lock cleanup

**Step 3: Integrate with `worker_manager.py`**
- Add method: `spawn_batch_with_dag(spec_file, max_concurrent=3, use_dag=True)`
- Load tasks from YAML → build DAG → spawn initial ready tasks
- Add method: `_spawn_ready_tasks()` - spawns tasks up to max_concurrent
- Feature flag: `SDLC_USE_DAG_SCHEDULER` env var (rollback strategy)

**Step 4: Unit Tests**
- Location: `.claude/skills/parallel-workers/tests/test_dag_scheduler.py`
- Test cases:
  - ✅ Linear DAG (A → B → C)
  - ✅ Diamond pattern (A → B,C → D)
  - ✅ Cycle detection (A → B → C → A)
  - ✅ Dependency resolution (blocked vs ready)
  - ✅ Failure cascade (failed task skips dependents)
  - ✅ Critical path calculation
  - ✅ State serialization (to_dict/from_dict)

**Milestone**: MVP passes all unit tests

---

### Phase 2: Integration (Week 2-3) - DAG-Aware Loop

**Deliverables**:
1. ✅ Enhanced `loop.py` with DAG-aware polling
2. ✅ Worker state synchronization with DAG
3. ✅ Integration tests (worker spawning, checkpoint recovery)
4. ✅ Quality gate: `dag-integrity-gate.yml`

**Implementation Order**:

**Step 5: Enhance `loop.py`**
- Create new file: `.claude/skills/parallel-workers/scripts/loop.py` (replace existing)
- Class: `DAGAutomationLoop`
- Key features:
  - Load DAG from spec or resume from checkpoint
  - Poll worker states every 5 seconds
  - Sync worker completion (MERGED) to DAG (mark_completed)
  - Spawn newly ready tasks dynamically
  - Save checkpoint after every state change
  - Graceful shutdown (SIGINT/SIGTERM handlers)

**Step 6: Sync with `state_tracker.py`**
- Add method: `sync_worker_to_dag(scheduler: DAGScheduler)`
- Logic: For each task in DAG, check worker state file
  - `MERGED` → `mark_completed()`
  - `ERROR` → `mark_failed()`
  - `WORKING`/`PR_OPEN` → `mark_running()`

**Step 7: Integration Tests**
- Location: `.claude/skills/parallel-workers/tests/test_dag_integration.py`
- Test cases:
  - ✅ `spawn_batch_with_dag()` creates DAG and spawns initial tasks
  - ✅ Checkpoint saved after spawning
  - ✅ Lock acquisition/release works correctly
  - ✅ Concurrent lock attempts block properly
  - ✅ Checkpoint recovery restores DAG state

**Step 8: Quality Gate**
- Location: `.claude/skills/gate-evaluator/gates/dag-integrity-gate.yml`
- Checks:
  - `dag_all_completed`: All tasks in terminal state
  - `dag_no_critical_failures`: No failures on critical path
  - `dag_execution_time`: Actual time within expected bounds

**Milestone**: Integration tests pass, gate evaluates correctly

---

### Phase 3: Enhancements (Week 3-4) - Smart Parallelism

**Deliverables**:
1. ✅ Parallelism hints from spec file
2. ✅ Smart `max_concurrent` calculation per task type
3. ✅ Resource locks for serialized tasks (database migrations)
4. ✅ End-to-end test with real Phase 5 execution

**Implementation Order**:

**Step 9: Enhance `tasks.yml` Schema**
- Add `parallelism` section with hints:
  ```yaml
  parallelism:
    hints:
      test: {max_workers: 10, can_parallel: true}
      implementation: {max_workers: 3, can_parallel: true}
      refactor: {max_workers: 1, can_parallel: false}
      database: {max_workers: 1, requires_lock: "db_migration"}
  ```
- Add task fields: `type`, `estimated_duration`, `priority`

**Step 10: Smart Parallelism in DAGScheduler**
- Method: `get_max_concurrent_for_tasks(tasks) -> int`
- Logic: Find most restrictive hint among ready tasks
  - If any task has `can_parallel: false` → return 1 (serialize)
  - Otherwise → return min(max_workers) across ready tasks
- Respect resource locks (check `LockManager.is_locked()`)

**Step 11: End-to-End Test**
- Location: `.claude/skills/parallel-workers/tests/test_dag_e2e.py`
- Test case: Diamond pattern with 4 tasks
  - E2E-001 (docs) → E2E-002 (docs) ↘
                                     → E2E-004 (docs)
  - E2E-001 (docs) → E2E-003 (docs) ↗
- Verify:
  - ✅ E2E-001 runs first
  - ✅ E2E-002 and E2E-003 run in parallel
  - ✅ E2E-004 runs last
  - ✅ Execution time = 3 units (not 4 sequential)

**Milestone**: E2E test passes with 25%+ speedup vs sequential

---

## Key Design Decisions

### 1. Use NetworkX for Graph Operations

**Rationale**:
- Battle-tested library (Python standard)
- Built-in cycle detection (`simple_cycles()`)
- Topological sort (`topological_sort()`)
- Longest path calculation (`dag_longest_path()`)
- No need to reinvent graph algorithms

**Alternatives Considered**:
- ❌ Custom graph implementation (too much complexity)
- ❌ Airflow integration (too heavyweight for single-project use)

### 2. File-Based Locks (Not Database)

**Rationale**:
- No external dependencies (no Redis, no PostgreSQL needed)
- Atomic operations via `fcntl.flock()`
- Works across processes on same machine
- Simple cleanup (just delete lock files)

**Alternatives Considered**:
- ❌ Redis locks (requires Redis server)
- ❌ Database locks (requires database connection)

### 3. Checkpoint-Based Recovery (Not Log Replay)

**Rationale**:
- Simple JSON state snapshots
- Fast recovery (just load last checkpoint)
- Easy debugging (human-readable JSON)
- No need for complex event sourcing

**Alternatives Considered**:
- ❌ Event sourcing (too complex for this use case)
- ❌ No persistence (lose progress on crash)

---

## Critical Files

### Files to Create

| Path | Purpose | Lines |
|------|---------|-------|
| `.claude/skills/parallel-workers/scripts/dag_scheduler.py` | Core DAG scheduler | ~400 |
| `.claude/skills/parallel-workers/scripts/lock_manager.py` | Locks + checkpoints | ~200 |
| `.claude/skills/parallel-workers/tests/test_dag_scheduler.py` | Unit tests | ~300 |
| `.claude/skills/parallel-workers/tests/test_dag_integration.py` | Integration tests | ~200 |
| `.claude/skills/parallel-workers/tests/test_dag_e2e.py` | E2E test | ~100 |
| `.claude/skills/gate-evaluator/gates/dag-integrity-gate.yml` | Quality gate | ~50 |

### Files to Modify

| Path | Changes | Lines Changed |
|------|---------|---------------|
| `.claude/skills/parallel-workers/scripts/worker_manager.py` | Add `spawn_batch_with_dag()` | +80 |
| `.claude/skills/parallel-workers/scripts/state_tracker.py` | Add `sync_worker_to_dag()` | +30 |
| `.claude/skills/parallel-workers/scripts/loop.py` | Replace with DAG-aware loop | ~200 (rewrite) |
| `.claude/skills/parallel-workers/requirements.txt` | Add `networkx>=3.0` | +1 |

### Storage Locations

| Path | Purpose |
|------|---------|
| `~/.claude/dag-checkpoints/{project}.checkpoint.json` | DAG scheduler state |
| `~/.claude/dag-locks/*.lock` | Resource locks |
| `~/.claude/worker-states/*.json` | Worker states (existing) |

---

## Testing Strategy

### Unit Tests (test_dag_scheduler.py)

**Test Matrix**:

| Test Case | DAG Pattern | Expected Behavior |
|-----------|-------------|-------------------|
| `test_simple_linear_dag` | A → B → C | Execution order: [A, B, C] |
| `test_diamond_pattern` | A → B,C → D | A first, D last, B,C parallel |
| `test_cycle_detection` | A → B → C → A | Raises `ValueError` with cycle path |
| `test_no_dependencies_ready` | A, B, C (independent) | All ready immediately |
| `test_completed_dependency_unblocks` | A → B | After A completes, B ready |
| `test_failure_skips_dependents` | A → B → C, A fails | B and C marked SKIPPED |
| `test_linear_critical_path` | A(10) → B(20) → C(5) | Critical path: [A, B, C] |
| `test_round_trip_serialization` | Any DAG | `to_dict()` → `from_dict()` preserves state |

### Integration Tests (test_dag_integration.py)

**Test Scenarios**:
1. ✅ `spawn_batch_with_dag()` creates DAG and spawns only ready tasks
2. ✅ Checkpoint created after spawning
3. ✅ Lock manager handles concurrent acquisition correctly
4. ✅ Checkpoint recovery restores DAG state from JSON

### End-to-End Test (test_dag_e2e.py)

**Diamond Execution Test**:
- 4 tasks: E2E-001 → (E2E-002, E2E-003) → E2E-004
- All tasks type `docs` (max_workers: 5)
- Expected execution time: 3 units (not 4 sequential)
- Verify 25% speedup

---

## Risk Mitigation

### Risk 1: Cycle Detection Failure

**Risk**: Circular dependencies not detected, causing deadlock

**Mitigation**:
- NetworkX `simple_cycles()` runs at DAG construction (fail fast)
- Clear error message with cycle path: "A → B → C → A"
- Unit test: `test_cycle_detection`

### Risk 2: File Lock Deadlock

**Risk**: Lock never released, blocking all tasks

**Mitigation**:
- 5-minute timeout on all lock acquisitions
- Expired lock cleanup (`cleanup_expired()` in loop)
- Lock info includes timestamp for debugging
- Unit test: `test_lock_timeout`

### Risk 3: Checkpoint Corruption

**Risk**: Crash during checkpoint write corrupts state

**Mitigation**:
- Atomic writes (temp file + rename)
- Schema validation on load (Pydantic if needed)
- Backup of previous checkpoint
- Fallback: restart from beginning if recovery fails

### Risk 4: Regression in Existing Functionality

**Risk**: DAG integration breaks existing workers

**Mitigation**:
- Feature flag: `SDLC_USE_DAG_SCHEDULER=false` disables DAG
- Existing `spawn_batch()` preserved as fallback
- Integration tests verify worker lifecycle unchanged
- Gradual rollout: test on non-critical projects first

---

## Success Criteria

### Functional Requirements

| ID | Requirement | Acceptance Criteria | Test |
|----|-------------|---------------------|------|
| F1 | Diamond pattern execution | B and C execute in parallel after A completes | `test_diamond_pattern` |
| F2 | Cycle detection | Circular deps rejected with clear error | `test_cycle_detection` |
| F3 | Critical path calculation | Longest duration path identified correctly | `test_linear_critical_path` |
| F4 | Failure cascade | Failed task dependents marked SKIPPED | `test_failure_skips_dependents` |
| F5 | Checkpoint recovery | State restored after crash/restart | `test_recover_from_crash` |

### Performance Requirements

| ID | Metric | Target | Measurement |
|----|--------|--------|-------------|
| P1 | Execution speedup | 30-40% faster than sequential | `test_parallel_speedup` E2E |
| P2 | Lock acquisition time | < 100ms (uncontested) | Benchmark test |
| P3 | Checkpoint save time | < 50ms | Benchmark test |
| P4 | Memory overhead | < 10MB for 100 tasks | Profile test |

### Observability Requirements

| ID | Requirement | Implementation |
|----|-------------|----------------|
| O1 | Progress logging | `_log_progress()` in loop every 5s |
| O2 | Error reporting | Structured logging with task context |
| O3 | Visualization | Mermaid diagram generation |
| O4 | Metrics | Progress %, completion count, failed count |

---

## Verification Steps

### Manual Testing Procedure

**Before Merge**:

1. **Unit Tests**:
   ```bash
   cd .claude/skills/parallel-workers
   pytest tests/test_dag_scheduler.py -v
   # Expected: All tests pass
   ```

2. **Integration Tests**:
   ```bash
   pytest tests/test_dag_integration.py -v
   # Expected: All tests pass
   ```

3. **End-to-End Test**:
   ```bash
   pytest tests/test_dag_e2e.py -v
   # Expected: Diamond pattern executes in parallel with 25%+ speedup
   ```

4. **Quality Gate**:
   ```bash
   python3 .claude/skills/gate-evaluator/scripts/evaluate_gate.py dag-integrity-gate
   # Expected: All checks pass
   ```

5. **Rollback Test**:
   ```bash
   export SDLC_USE_DAG_SCHEDULER=false
   python3 .claude/skills/parallel-workers/scripts/loop.py
   # Expected: Falls back to existing sequential execution
   ```

### Real Phase 5 Execution

**Test Project**: Create simple 4-task project with diamond dependencies
```yaml
tasks:
  - id: TASK-A
    description: "Create base class"
    dependencies: []
  - id: TASK-B
    description: "Implement feature X"
    dependencies: [TASK-A]
  - id: TASK-C
    description: "Implement feature Y"
    dependencies: [TASK-A]
  - id: TASK-D
    description: "Integration test"
    dependencies: [TASK-B, TASK-C]
```

**Expected Behavior**:
1. TASK-A spawns first
2. After TASK-A completes (MERGED), TASK-B and TASK-C spawn in parallel
3. After both complete, TASK-D spawns
4. Total time < sequential execution time

---

## Rollout Plan

### Phase 1: Internal Testing (Week 1-2)

**Scope**: MVP on non-critical test project
- ✅ Core DAG scheduler implemented
- ✅ Unit tests pass
- ✅ Integration tests pass
- ❌ Not enabled by default

**Activation**: Manual via flag
```bash
export SDLC_USE_DAG_SCHEDULER=true
```

### Phase 2: Beta Testing (Week 3)

**Scope**: Enhanced features on selected projects
- ✅ Parallelism hints implemented
- ✅ Quality gate integrated
- ✅ E2E test passes
- ❌ Still not default

**Participants**: Review with team, gather feedback

### Phase 3: General Availability (Week 4)

**Scope**: Enable by default for all projects
- ✅ All tests pass
- ✅ Documentation complete
- ✅ Rollback procedure documented
- ✅ Enabled by default

**Activation**: Default to `true`
```python
USE_DAG_SCHEDULER = os.environ.get("SDLC_USE_DAG_SCHEDULER", "true").lower() == "true"
```

---

## Documentation Updates

### Files to Create/Update

| Path | Changes |
|------|---------|
| `.claude/skills/parallel-workers/README.md` | Add DAG scheduler section |
| `.agentic_sdlc/corpus/nodes/decisions/ADR-dag-scheduler.yml` | Document decision |
| `.docs/features/dag-scheduler.md` | User guide |
| `CLAUDE.md` | Update parallel-workers section |

### User Guide Outline

**`.docs/features/dag-scheduler.md`**:
1. Overview: What is DAG scheduling?
2. Benefits: 30-40% faster, automatic dependency resolution
3. Task YAML Schema: How to define dependencies
4. Parallelism Hints: Controlling concurrency per task type
5. Troubleshooting: Common issues and solutions
6. Advanced: Critical path analysis, custom hints

---

## Next Steps (Post-Approval)

1. ✅ **Create feature branch**: `feature/dag-scheduler`
2. ✅ **Implement Phase 1** (MVP - Week 1-2):
   - Create `dag_scheduler.py`
   - Create `lock_manager.py`
   - Integrate with `worker_manager.py`
   - Write unit tests
3. ✅ **Implement Phase 2** (Integration - Week 2-3):
   - Enhance `loop.py`
   - Add state synchronization
   - Write integration tests
   - Add quality gate
4. ✅ **Implement Phase 3** (Enhancements - Week 3-4):
   - Add parallelism hints
   - Write E2E test
   - Real Phase 5 testing
5. ✅ **Merge to main** after all tests pass and quality gate validates
6. ✅ **Monitor** Phase 5 executions for performance improvements

---

## Appendix: Ralph TUI Patterns Adapted

This implementation adapts key patterns from Ralph TUI's autonomous orchestration:

### Pattern 1: DAG-Based Scheduling (PR #169)
**Ralph Implementation**: `src/orchestrator/index.ts`
- Topological sorting for execution order
- Dependency resolution with implicit file-based deps
- Concurrent execution up to max_workers

**SDLC Adaptation**: `dag_scheduler.py`
- NetworkX for graph operations
- Explicit dependencies in tasks.yml
- Smart parallelism hints per task type

### Pattern 2: File-Based Locks (PR #169)
**Ralph Implementation**: `src/orchestrator/task-queue.ts`
```typescript
async withQueueLock<T>(fn: () => Promise<T>): Promise<T> {
  await mkdir(lockPath, { recursive: false });  // Atomic
  const result = await fn();
  await rmdir(lockPath);
}
```

**SDLC Adaptation**: `lock_manager.py`
```python
@contextmanager
def acquire(resource: str, timeout: float = 300):
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Atomic
    yield
    fcntl.flock(fd, fcntl.LOCK_UN)
```

### Pattern 3: Smart Parallelism Hints (PR #169)
**Ralph Implementation**: `src/orchestrator/analyzer.ts`
```typescript
function getParallelismHint(story: Story): number {
  if (/test|spec/i.test(text)) return 10;  // Tests highly parallel
  if (/refactor|migrate/i.test(text)) return 1;  // Refactors sequential
  return 5;  // Default
}
```

**SDLC Adaptation**: `parallelism_hints.py` (part of dag_scheduler.py)
```python
PARALLELISM_RULES = {
    "test": {"max_parallel": 10},
    "refactor": {"max_parallel": 1},
    "implementation": {"max_parallel": 3},
}
```

### Pattern 4: Crash Recovery (Ralph Session Persistence)
**Ralph Implementation**: JSON checkpoint + lock file
- Saves state after each iteration
- Recovers exactly where it stopped
- Lock prevents multiple instances

**SDLC Adaptation**: `CheckpointManager`
- Saves DAG state after every spawn/completion
- Loop resumes from checkpoint on restart
- File lock coordinates multiple processes

---

## Summary

This plan delivers **intelligent task orchestration** for SDLC Agêntico Phase 5, enabling:

✅ **30-40% faster execution** through optimal parallelism
✅ **Zero deadlocks** via cycle detection at initialization
✅ **Crash resilience** through checkpoint-based recovery
✅ **Resource efficiency** with smart parallelism hints
✅ **Clear dependencies** with DAG visualization

**Total Estimated Effort**: 2 weeks (MVP) + 1-2 weeks (enhancements)
**Expected ROI**: 2-3x speedup in Phase 5, reduced manual intervention

**Ready for Implementation**: All components designed, tests defined, integration points identified.
