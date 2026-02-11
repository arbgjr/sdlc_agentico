# Agent Teams Manager - Quick Reference

**For Orchestrator**: When parallelization is needed, use this guide to select strategy.

---

## Decision Tree (5 seconds)

```
┌─────────────────────────────────────┐
│ Do I need parallelization?          │
│ (task_count >= 2?)                  │
└─────────────┬───────────────────────┘
              │
              ├─ NO ──→ Use SEQUENTIAL
              │
              ├─ YES
              │
              ▼
┌─────────────────────────────────────┐
│ What phase am I in?                 │
└─────────────┬───────────────────────┘
              │
              ├─ Phase 1, 2, 3 (Research/Architecture)
              │  └─→ Use AGENT TEAMS (if enabled)
              │      └─→ Fallback: SEQUENTIAL
              │
              ├─ Phase 6 (Implementation)
              │  └─→ Use PARALLEL WORKERS
              │
              ├─ Phase 7 (Quality/Review)
              │  └─→ Use AGENT TEAMS (if enabled)
              │      └─→ Fallback: SEQUENTIAL
              │
              └─ Other phases
                 └─→ Use SEQUENTIAL
```

---

## Quick Commands

### Check Strategy (Auto-Detect)

```bash
python3 .claude/skills/agent-teams-manager/scripts/select_strategy.py \
  --phase 1 \
  --task-type research \
  --task-count 3 \
  --json
```

### Force Specific Strategy (Testing)

```bash
python3 .claude/skills/agent-teams-manager/scripts/select_strategy.py \
  --phase 1 \
  --task-type research \
  --task-count 3 \
  --force-strategy agent_teams \
  --json
```

---

## Phase-Strategy Matrix

| Phase | Name | Tasks | Recommended Strategy | Rationale |
|-------|------|-------|---------------------|-----------|
| 1 | Discovery | Research, explore | **Agent Teams** | Parallel exploration + discussion |
| 2 | Requirements | Refine, discuss | **Agent Teams** | Requirements emerge from collaboration |
| 3 | Architecture | Design, debate | **Agent Teams** | Trade-off debate essential |
| 4 | Design System | Design, specify | Sequential | Usually single designer |
| 5 | Planning | Break down, estimate | Sequential | Single planner synthesizes |
| 6 | **Implementation** | Code, test, build | **Parallel Workers** | **File isolation required** |
| 7 | Quality | Review, audit, test | **Agent Teams** | Multiple specialized perspectives |
| 8 | Release | Deploy, document | Sequential | Coordinated release process |
| 9 | Operations | Monitor, respond | Sequential | Single incident commander |

---

## Strategy Characteristics

### Agent Teams

**Best for**: Research, architecture, review
**Pros**:
- ✅ Real-time communication
- ✅ Parallel discussion and debate
- ✅ Multiple perspectives synthesized

**Cons**:
- ❌ 3x token usage
- ❌ Experimental (may be unstable)
- ❌ File conflicts if editing same file

**When to use**:
```python
phase in [1, 2, 3, 7]
AND task_type in ["research", "review", "architecture"]
AND token_budget > 50k
AND agent_teams_enabled == True
```

### Parallel Workers

**Best for**: Implementation (Phase 6)
**Pros**:
- ✅ File isolation (zero conflicts)
- ✅ Automatic PRs and gates
- ✅ Production-ready and stable
- ✅ No extra token usage

**Cons**:
- ❌ Disk space usage (worktrees)
- ❌ No direct agent communication
- ❌ Coordination via polling

**When to use**:
```python
phase == 6
AND task_type == "implementation"
AND task_count >= 2
```

### Sequential

**Best for**: Single tasks, low token budget
**Pros**:
- ✅ Simple and predictable
- ✅ Lowest token usage
- ✅ No coordination overhead

**Cons**:
- ❌ Slower wall-clock time
- ❌ No parallel exploration

**When to use**:
```python
task_count < 2
OR token_budget < 50k
OR (agent_teams_disabled AND phase != 6)
```

---

## Example Invocations

### Research Kafka (Phase 1)

```python
# Orchestrator code:
strategy = select_strategy(
    phase=1,
    task_type="research",
    task_count=3
)
# Returns: "agent_teams" (if enabled)

# Then create team:
create_team(
    name="kafka-research",
    lead="domain-researcher",
    teammates=["doc-crawler", "rag-curator"]
)
```

### Implement Microservices (Phase 6)

```python
# Orchestrator code:
strategy = select_strategy(
    phase=6,
    task_type="implementation",
    task_count=4
)
# Returns: "parallel_workers" (always for Phase 6)

# Then spawn workers:
spawn_parallel_workers(
    tasks_file="tasks.yml",
    max_workers=4
)
```

### Single Architecture Task (Phase 3)

```python
# Orchestrator code:
strategy = select_strategy(
    phase=3,
    task_type="architecture",
    task_count=1
)
# Returns: "sequential" (only 1 task)

# Then execute sequentially:
execute_agent("system-architect", task)
```

---

## Troubleshooting

### Strategy Not As Expected

**Symptom**: Expected `agent_teams`, got `sequential`

**Check**:
1. Is `agent_teams` feature flag enabled in `.claude/settings.json`?
2. Is `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` environment variable set?
3. Is token budget > 50k?
4. Is phase in allowed list ([1, 2, 3, 7])?

**Fix**:
```bash
# Check settings
grep -A5 "agent_teams" .claude/settings.json

# Check env var
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS

# Check token budget
# (integrate with token-status command)
```

### High Token Usage Warning

**Symptom**: Token budget exhausted during Agent Teams execution

**Fix**:
```bash
# Disable Agent Teams temporarily
# Edit .claude/settings.json:
# "agent_teams": false

# Or reduce teammate count
# In team creation: max 3 teammates recommended
```

---

## Integration Checklist

For orchestrator to integrate agent-teams-manager:

- [ ] Import strategy selection function
- [ ] Call select_strategy() when parallelization needed
- [ ] Handle all 3 strategies (agent_teams, parallel_workers, sequential)
- [ ] Log strategy selection rationale (for debugging)
- [ ] Monitor token usage (warn if approaching limit)
- [ ] Fallback to sequential if primary strategy fails
- [ ] Commit results after parallelization completes

---

**Last Updated**: 2026-02-10
**Related**: ADR-001, SKILL.md, select_strategy.py
