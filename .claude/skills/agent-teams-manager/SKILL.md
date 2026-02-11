---
name: agent-teams-manager
description: |
  Manages parallelization strategies (Agent Teams vs Parallel Workers) for SDLC phases.
  Detects optimal strategy based on phase, complexity, and task characteristics.
  Coordinates team creation, messaging, and task dependencies for Agent Teams.
  Falls back to parallel-workers for implementation phases requiring file isolation.
  Use when: coordinating parallel work, research phases, architecture discussions, quality reviews.
allowed-tools:
  - Read
  - Bash
  - TaskCreate
  - TaskUpdate
  - TaskList
user-invocable: false
version: "1.0.0"
---

# Agent Teams Manager

> **Philosophy**: Hybrid approach - Agent Teams for research/discussion phases, Parallel Workers for implementation phases.

## Quick Start

**Example** (orchestrator auto-selects strategy):
```python
# Phase 1 (Discovery) - Auto-selects Agent Teams
strategy = select_strategy(phase=1, complexity=2, task_count=3)
# Returns: "agent_teams" (research benefits from discussion)

# Phase 6 (Implementation) - Auto-selects Parallel Workers
strategy = select_strategy(phase=6, complexity=2, task_count=3)
# Returns: "parallel_workers" (isolation prevents conflicts)
```

## When to Use This Skill

Use this skill when:
- **Orchestrator needs to parallelize work** across multiple agents
- **Phase 1, 2, 3, or 6** with 2+ concurrent tasks
- **Research/architecture discussions** benefit from real-time collaboration
- **Debugging with competing hypotheses** (Agent Teams enables debate)
- **Code reviews** requiring multiple specialized perspectives

DO NOT use when:
- Single-agent sequential execution is sufficient
- Phase 6 (Implementation) editing same files (use parallel-workers instead)
- Token budget is critical (Agent Teams uses 3x tokens)
- Feature flag `agent_teams` is disabled

## Core Workflows

### Workflow 1: Strategy Selection (Auto)

**Use when**: Orchestrator needs to decide parallelization approach

**Steps**:
1. Read `.claude/settings.json` → Check `sdlc.feature_flags.agent_teams`
2. If `agent_teams: false` → Return "parallel_workers" (only option)
3. If `agent_teams: true`:
   - Check current phase number
   - Check complexity level (0-3)
   - Check task count
   - Check task characteristics (research vs implementation)
4. Apply strategy selection logic:
   - **Phase 1, 2, 3, 6** AND research/review → "agent_teams"
   - **Phase 6 (Implementation)** AND file editing → "parallel_workers"
   - **Task count < 2** → "sequential"
   - **Token budget exhausted** → "sequential"
5. Log decision with rationale

**Strategy Selection Logic**:
```markdown
IF agent_teams flag is disabled:
  RETURN "parallel_workers" (fallback)

IF phase in [1, 2, 3, 6] AND task_type in ["research", "review", "architecture"]:
  RETURN "agent_teams"  # Discussion benefits from real-time collaboration

IF phase == 6 AND task_type == "implementation":
  RETURN "parallel_workers"  # File isolation prevents conflicts

IF task_count < 2:
  RETURN "sequential"  # No parallelization needed

ELSE:
  RETURN "sequential"  # Conservative default
```

**Example**:
```markdown
# Phase 1 (Discovery): 3 domain-researcher tasks
- Current phase: 1
- Task type: research
- Task count: 3
→ Decision: "agent_teams" (research benefits from discussion)

# Phase 6 (Implementation): 4 code-author tasks
- Current phase: 6
- Task type: implementation
- Task count: 4
→ Decision: "parallel_workers" (file isolation required)

# Phase 3 (Architecture): 2 architects debating
- Current phase: 3
- Task type: architecture
- Task count: 2
→ Decision: "agent_teams" (architecture requires trade-off debate)
```

**Common Issues**:
- **Problem**: Agent Teams not available (experimental flag not set)
- **Solution**: Fallback to parallel_workers or sequential. Log warning.

---

### Workflow 2: Create Agent Team

**Use when**: Strategy selection returned "agent_teams"

**Steps**:
1. Validate prerequisites:
   - `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment
   - Team name is unique (check `~/.claude/teams/`)
   - Phase is in allowed list ([1, 2, 3, 6])
2. Define team structure:
   - Lead agent (coordinates, synthesizes, makes decisions)
   - Teammate agents (execute tasks, provide perspectives)
   - Shared task list
3. Create team configuration:
   ```bash
   claude team create {team-name} \
     --lead {lead-agent} \
     --teammates {agent1},{agent2},{agent3}
   ```
4. Assign tasks to teammates:
   ```bash
   # Each teammate claims tasks from shared list
   claude team assign {team-name} {teammate} {task-id}
   ```
5. Monitor team progress:
   - Check task statuses
   - Watch for blockers
   - Facilitate messaging if needed
6. Synthesize results:
   - Lead agent collects teammate outputs
   - Creates final deliverable
   - Commits to git

**Example**:
```markdown
# Phase 1 (Discovery): Research Kafka best practices
1. Create team:
   - Lead: domain-researcher (coordinates)
   - Teammate 1: doc-crawler (searches official docs)
   - Teammate 2: domain-researcher-2 (searches patterns)
   - Teammate 3: rag-curator (indexes findings)

2. Assign tasks:
   - doc-crawler → "Fetch Kafka official documentation"
   - domain-researcher-2 → "Research Kafka patterns in corpus"
   - rag-curator → "Index findings for future queries"

3. Teammates message each other:
   - doc-crawler: "Found Kafka Streams API docs"
   - domain-researcher-2: "Event Sourcing pattern common"
   - Lead synthesizes: "Kafka Streams + Event Sourcing recommended"

4. Lead commits decision as ADR
```

**Common Issues**:
- **Problem**: Experimental flag not set → Team creation fails
- **Solution**: Check `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, warn user

- **Problem**: Teammates editing same file → Merge conflicts
- **Solution**: Detect file collision, switch to parallel_workers strategy

---

### Workflow 3: Spawn Parallel Workers

**Use when**: Strategy selection returned "parallel_workers"

**Steps**:
1. Delegate to `parallel-workers` skill:
   - Read tasks from Phase 5 (Planning) output
   - Create git worktrees for isolation
   - Spawn workers with assigned tasks
   - Monitor PR creation
   - Run automation loop
2. Wait for workers to complete
3. Merge PRs through gate-evaluator

**Example**:
```markdown
# Phase 6 (Implementation): 3 parallel tasks
1. Call parallel-workers skill:
   /parallel-spawn --batch tasks.yml

2. Workers execute in isolation:
   - Worker 1: Implements authentication
   - Worker 2: Implements payment gateway
   - Worker 3: Writes integration tests

3. PRs created automatically
4. Security gate validates before merge
```

**Common Issues**:
- **Problem**: Disk space exhausted (worktrees use disk)
- **Solution**: Cleanup old worktrees, reduce max_workers

---

### Workflow 4: Fallback to Sequential

**Use when**: Strategy selection returned "sequential"

**Steps**:
1. Log reason for sequential execution:
   - Task count too small (< 2)
   - Token budget exhausted
   - Feature flags disabled
2. Execute tasks one by one:
   - Call agent for task 1
   - Wait for completion
   - Call agent for task 2
   - Repeat
3. Commit after all tasks complete

**Example**:
```markdown
# Single research task - no parallelization needed
1. Strategy: "sequential" (task_count=1)
2. Execute: domain-researcher researches Kafka
3. Commit: ADR created
```

---

## Strategy Selection Reference

### Phase-Specific Recommendations

| Phase | Name | Recommended Strategy | Rationale |
|-------|------|---------------------|-----------|
| 1 | Discovery | **agent_teams** | Research benefits from parallel exploration and discussion |
| 2 | Requirements | **agent_teams** | Requirements emerge from collaborative refinement |
| 3 | Architecture | **agent_teams** | Architecture requires debate of trade-offs and alternatives |
| 6 | Implementation | **parallel_workers** | File isolation prevents merge conflicts |
| 7 | Quality | **agent_teams** | QA benefits from multiple specialized perspectives |

### Task Type Detection

**Research Tasks** (Agent Teams preferred):
- Keywords: "research", "explore", "investigate", "analyze", "compare"
- Agents: domain-researcher, doc-crawler, rag-curator
- Output: Documentation, ADRs, learnings

**Implementation Tasks** (Parallel Workers preferred):
- Keywords: "implement", "code", "write", "build", "develop"
- Agents: code-author, test-author, iac-engineer
- Output: Source code, tests, infrastructure

**Review Tasks** (Agent Teams preferred):
- Keywords: "review", "audit", "validate", "assess", "evaluate"
- Agents: code-reviewer, qa-analyst, security-scanner
- Output: Reports, findings, recommendations

### Token Budget Considerations

| Strategy | Token Multiplier | When to Use |
|----------|------------------|-------------|
| Sequential | 1x | Token budget < 50k or task_count = 1 |
| Parallel Workers | 1x | Token budget normal, implementation phase |
| Agent Teams | 3x | Token budget healthy (> 100k), research/review |

---

## Configuration

### Feature Flag (`.claude/settings.json`)

```json
{
  "sdlc": {
    "feature_flags": {
      "agent_teams": false  // Experimental - disable by default
    },
    "parallelization": {
      "strategies": {
        "parallel_workers": {
          "enabled": true,
          "phases": [6],
          "max_workers": 5
        },
        "agent_teams": {
          "enabled": false,  // Follows feature_flags.agent_teams
          "phases": [1, 2, 3, 6],
          "token_budget_multiplier": 3.0
        }
      },
      "strategy_selection": "auto"  // or "manual"
    }
  }
}
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Yes | `0` | Enable experimental Agent Teams feature in Claude Code |

**To enable Agent Teams**:
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## Integration

### With Other Skills

- **parallel-workers**: Fallback when Agent Teams unavailable or inappropriate
- **gate-evaluator**: Validates outputs from both strategies
- **phase-commit**: Commits results after parallelization completes
- **rag-curator**: Indexes learnings from Agent Team discussions

### With Agents

- **orchestrator** (Phase 0-9): Primary consumer - calls this skill for parallelization decisions
- **delivery-planner** (Phase 5): Generates task lists consumed by parallelization strategies
- **system-architect** (Phase 3): Uses Agent Teams for architecture debates

---

## Troubleshooting

### Common Issues

**Issue**: Agent Teams feature not available

**Solution**:
```bash
# Check environment variable
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS

# Should output: 1
# If not, enable:
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

**Issue**: High token usage with Agent Teams

**Solution**:
- Monitor token budget: `/token-status`
- Reduce teammate count (max 3 recommended)
- Switch to parallel_workers for implementation
- Disable agent_teams flag if budget critical

---

**Issue**: Team status shows "lag" or stale data

**Solution**:
```bash
# Manually refresh task list
claude team refresh {team-name}

# Check teammate status
claude team status {team-name}
```

---

**Issue**: Teammates editing same file → Merge conflicts

**Solution**:
- **Prevention**: Use parallel_workers for implementation (isolates files)
- **Detection**: Monitor file paths in tasks, warn if overlap detected
- **Recovery**: Coordinate manual merge or reassign tasks

---

## Examples

### Example 1: Phase 1 Discovery with Agent Teams

**Scenario**: Research Kafka for new event-driven architecture

**Input**:
```yaml
phase: 1
complexity: 2
tasks:
  - "Research Kafka official documentation"
  - "Find Kafka patterns in corpus"
  - "Index Kafka learnings for future use"
```

**Process**:
```markdown
1. Read settings → agent_teams enabled
2. Detect: Phase 1, research tasks, 3 tasks
3. Strategy: "agent_teams" (research benefits from discussion)
4. Create team:
   - Lead: domain-researcher
   - Teammates: doc-crawler, rag-curator
5. Teammates work in parallel:
   - doc-crawler fetches official docs
   - rag-curator searches corpus
   - Lead synthesizes findings
6. Team discusses via messaging
7. Lead creates ADR with recommendations
8. Commit to git
```

**Output**:
```markdown
ADR-015: Adopt Kafka for Event-Driven Architecture
- Kafka Streams API for event processing
- Event Sourcing pattern recommended
- Indexed 15 Kafka patterns in corpus
```

---

### Example 2: Phase 6 Implementation with Parallel Workers

**Scenario**: Implement 3 microservices concurrently

**Input**:
```yaml
phase: 6
complexity: 2
tasks:
  - "Implement authentication service"
  - "Implement payment gateway"
  - "Write integration tests"
```

**Process**:
```markdown
1. Read settings → agent_teams enabled
2. Detect: Phase 6, implementation tasks, 3 tasks, file editing
3. Strategy: "parallel_workers" (file isolation required)
4. Delegate to parallel-workers skill
5. Workers execute in isolated worktrees
6. PRs created automatically
7. Security gate validates
8. Merge to main
```

**Output**:
```markdown
3 PRs created:
- PR #42: feat(auth): Add authentication service
- PR #43: feat(payment): Add payment gateway integration
- PR #44: test(integration): Add E2E tests

All passed security gate, merged to main.
```

---

### Example 3: Fallback to Sequential

**Scenario**: Single architecture task, no parallelization needed

**Input**:
```yaml
phase: 3
complexity: 1
tasks:
  - "Create ADR for database selection"
```

**Process**:
```markdown
1. Read settings → agent_teams enabled
2. Detect: Phase 3, 1 task
3. Strategy: "sequential" (task_count < 2, no parallelization needed)
4. Execute: system-architect creates ADR
5. Commit to git
```

**Output**:
```markdown
ADR-016: Use PostgreSQL for Relational Data
- Single task, no parallelization overhead
- Completed in 5 minutes
```

---

## Anti-Patterns to Avoid

❌ **DON'T**:
- Use Agent Teams for Phase 6 implementation (file conflicts)
- Enable Agent Teams when token budget < 50k
- Create teams for single-task scenarios
- Hardcode strategy selection (use auto-detection)

✅ **DO**:
- Use hybrid approach (teams for research, workers for code)
- Monitor token usage with Agent Teams
- Fallback to parallel_workers when teams unavailable
- Log strategy selection rationale

---

**Skill maintained by**: SDLC Agêntico Core Team
**Last updated**: 2026-02-10
**Related**: ADR-018 (Agent Teams vs Parallel Workers)
