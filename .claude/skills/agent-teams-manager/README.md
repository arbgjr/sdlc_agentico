# Agent Teams Manager Skill

**Version**: 1.0.0
**Status**: Experimental Infrastructure Ready
**Phase**: Testing Pending

---

## Overview

Manages hybrid parallelization strategy for SDLC Agêntico, combining:
- **Agent Teams** (experimental) for research, architecture, and review phases
- **Parallel Workers** (stable) for implementation phase
- **Sequential** execution as fallback

**Purpose**: Maximize benefits of both approaches while mitigating risks.

---

## Files

```
agent-teams-manager/
├── README.md          ← You are here
├── SKILL.md           ← Full documentation (workflows, examples)
├── QUICKREF.md        ← Quick reference for orchestrator
└── scripts/
    └── select_strategy.py  ← Strategy selection logic
```

**Read SKILL.md first** for complete documentation.
**Use QUICKREF.md** for quick orchestrator integration.

---

## Quick Start

### 1. Check Current Strategy (Agent Teams Disabled)

```bash
python3 scripts/select_strategy.py \
  --phase 1 \
  --task-type research \
  --task-count 3

# Output:
# Strategy: sequential
# Rationale: Agent Teams disabled, insufficient parallelization alternatives
```

### 2. Enable Agent Teams (Experimental)

```bash
# Set environment variable
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Edit .claude/settings.json
# Change: "agent_teams": false
# To:     "agent_teams": true
```

### 3. Test Strategy Selection

```bash
python3 scripts/select_strategy.py \
  --phase 1 \
  --task-type research \
  --task-count 3

# Output:
# Strategy: agent_teams
# Rationale: Phase 1 research benefits from parallel discussion
```

---

## When to Use

**Orchestrator calls this skill when**:
- Phase requires parallelization (phases 1, 2, 3, 6, 7)
- Task count >= 2
- Need to decide: Agent Teams, Parallel Workers, or Sequential

**Automatic strategy selection based on**:
- Current SDLC phase
- Task type (research, implementation, review)
- Task count
- Token budget availability
- Feature flags

---

## Integration with Orchestrator

```python
# Orchestrator workflow:

1. Detect parallelization need:
   IF task_count >= 2 AND phase in [1, 2, 3, 6, 7]:
       CALL agent-teams-manager

2. Get strategy:
   strategy, rationale = select_strategy(phase, task_type, task_count)

3. Execute based on strategy:
   IF strategy == "agent_teams":
       create_team(lead, teammates)
       assign_tasks()
       monitor_progress()
       synthesize_results()

   ELIF strategy == "parallel_workers":
       delegate_to_parallel_workers_skill()

   ELIF strategy == "sequential":
       execute_tasks_one_by_one()

4. Commit results
```

---

## Architecture Decision

See **ADR-001**: `.agentic_sdlc/corpus/nodes/decisions/ADR-001-hybrid-parallelization-strategy.yml`

**Decision**: Hybrid approach
- Agent Teams for phases 1, 2, 3, 7 (research, architecture, review)
- Parallel Workers for phase 6 (implementation)
- Sequential as fallback

**Rationale**:
- Maximizes benefits (discussion + file isolation)
- Mitigates risks (experimental feature, token costs)
- Allows gradual rollout (feature flag control)

---

## Testing Status

### Phase 1 (Current) - Infrastructure Complete ✅

- [x] Feature flag configuration
- [x] agent-teams-manager skill created
- [x] select_strategy.py script implemented
- [x] ADR-001 documented
- [x] Quick reference guide
- [ ] **Testing pending** (Phase 1 Discovery scenario)

### Phase 2 (Next Sprint) - Validation

- [ ] Test in Phase 1 (Discovery)
- [ ] Test in Phase 3 (Architecture)
- [ ] Collect metrics (tokens, time, quality)
- [ ] Document learnings

### Phase 3 (Sprint +2) - Production

- [ ] Update playbook with guidelines
- [ ] Update CLAUDE.md
- [ ] Launch in v3.2.0

---

## Feature Flag Control

**Location**: `.claude/settings.json`

```json
{
  "sdlc": {
    "feature_flags": {
      "agent_teams": false  // Change to true to enable
    }
  },
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "0"  // Change to "1"
  }
}
```

**Current Status**: **DISABLED** (experimental)
**Recommendation**: Keep disabled until Phase 1 testing complete

---

## Examples

### Example 1: Phase 1 Discovery

**Scenario**: Research Kafka

```bash
# Strategy selection
python3 scripts/select_strategy.py \
  --phase 1 \
  --task-type research \
  --task-count 3

# Output: agent_teams (if enabled)

# Team structure:
# - Lead: domain-researcher (coordinates)
# - Teammate 1: doc-crawler (official docs)
# - Teammate 2: rag-curator (corpus patterns)
```

### Example 2: Phase 6 Implementation

**Scenario**: Build microservices

```bash
# Strategy selection
python3 scripts/select_strategy.py \
  --phase 6 \
  --task-type implementation \
  --task-count 4

# Output: parallel_workers (always for Phase 6)

# Workers in isolated worktrees:
# - Worker 1: auth-service
# - Worker 2: payment-service
# - Worker 3: integration-tests
# - Worker 4: iac-terraform
```

---

## Known Limitations

### Agent Teams (Experimental)

- 3x token usage
- No session resumption
- File conflicts possible
- Requires Claude Code experimental flag

### Parallel Workers (Stable)

- Disk space usage (worktrees)
- No direct communication
- Coordination via polling

**See SKILL.md** for full limitations and mitigations.

---

## Troubleshooting

### Strategy Not Working

```bash
# 1. Check feature flag
grep "agent_teams" .claude/settings.json

# 2. Check environment variable
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS

# 3. Test strategy selection
python3 scripts/select_strategy.py --phase 1 --task-type research --task-count 3 --json
```

### High Token Usage

```bash
# Monitor tokens
# (use /token-status command)

# Reduce teammates
# Max 3 recommended for Agent Teams

# Disable Agent Teams if budget critical
# Edit settings.json: "agent_teams": false
```

**See SKILL.md** for complete troubleshooting guide.

---

## Related Documentation

- **SKILL.md**: Complete documentation with workflows
- **QUICKREF.md**: Quick reference for orchestrator
- **ADR-001**: Architecture decision record
- **Implementation Summary**: `.agentic_sdlc/docs/agent-teams-implementation-summary.md`

---

## Maintenance

**Maintained by**: SDLC Agêntico Core Team
**Last Updated**: 2026-02-10
**Next Review**: After Phase 1 testing (Sprint +1)

**Feedback**: Report issues or suggestions to [GitHub Issues](https://github.com/anthropics/claude-code/issues)

---

## License

Part of SDLC Agêntico framework
See repository LICENSE file
