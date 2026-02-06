# Workflow Coordination Reference

Agent resolution, phase commits, learnings extraction, and workflow coordination.

## Overview

The orchestrator coordinates multiple agents across phases, managing:
- Client-aware agent/skill resolution (v3.0.0)
- Phase transition and commits
- Learning extraction from sessions
- Multi-agent coordination patterns

---

## Client-Aware Agent Resolution (v3.0.0)

### Concept

Starting in v3.0.0, the orchestrator supports **profile-based multi-tenancy** where clients can customize agents, skills, gates, and templates without forking the framework.

**Key Principle**: Each client profile is an "overlay" on top of the base framework. When loading resources, check client-specific overrides first, then fall back to base.

---

### Client Detection

At workflow start, detect the active client:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".claude/lib/python")))
from client_resolver import ClientResolver

# Initialize resolver
resolver = ClientResolver()

# Detect active client (priority order)
client_id = resolver.detect_client()

# Priority:
# 1. $SDLC_CLIENT environment variable
# 2. .project/.client file (persisted)
# 3. Auto-detect from profile markers
# 4. Fallback to "generic" (base framework)

print(f"Active client: {client_id}")
```

---

### Agent Resolution

Use client-aware path resolution:

```python
# BEFORE v3.0.0 (direct path)
agent_path = Path(".claude/agents/code-reviewer.md")

# AFTER v3.0.0 (client-aware)
try:
    agent_path = resolver.resolve_agent("code-reviewer", client_id)
    # Returns:
    # - .sdlc_clients/{client_id}/agents/code-reviewer.md (if exists) ← OVERRIDE
    # - .claude/agents/code-reviewer.md (fallback) ← BASE
except FileNotFoundError:
    # Agent not found in client or base
    raise
```

**Resolution Logic**:
1. Check `.sdlc_clients/{client}/agents/{agent}.md`
2. If found → use client-specific version
3. If not found → fall back to `.claude/agents/{agent}.md`
4. If neither exists → raise FileNotFoundError

---

### Skill Resolution

Same pattern for skills:

```python
# Resolve skill directory
skill_path = resolver.resolve_skill("gate-evaluator", client_id)

# Returns:
# - .sdlc_clients/{client_id}/skills/gate-evaluator/ (if exists) ← OVERRIDE
# - .claude/skills/gate-evaluator/ (fallback) ← BASE
```

---

### Profile Loading

Load client profile to check customizations:

```python
profile = resolver.load_profile(client_id)

# Check for custom gates
custom_gates = profile.get("gates", {}).get("additions", [])
for gate in custom_gates:
    gate_name = gate["name"]
    gate_path = gate["path"]
    after_phase = gate["after_phase"]
    print(f"Custom gate: {gate_name} after phase {after_phase}")

# Check for agent overrides
agent_overrides = profile.get("agents", {}).get("overrides", [])
for override in agent_overrides:
    agent_name = override["name"]
    reason = override["reason"]
    print(f"Overridden agent: {agent_name} - {reason}")

# Check for skill additions
skill_additions = profile.get("skills", {}).get("additions", [])
for skill in skill_additions:
    skill_name = skill["name"]
    print(f"Client-specific skill: {skill_name}")
```

---

### Client Version Compatibility

Before executing workflow, validate client profile compatibility:

```python
client_info = resolver.get_client_info(client_id)
if client_info:
    min_version = client_info.get("framework", {}).get("min_version")
    max_version = client_info.get("framework", {}).get("max_version")

    # Check framework version (from .claude/VERSION)
    import yaml
    with open(".claude/VERSION") as f:
        framework_version = yaml.safe_load(f)["version"]

    # Validate (implement semantic version comparison)
    if not is_version_compatible(framework_version, min_version, max_version):
        raise VersionIncompatibleError(
            f"Framework v{framework_version} incompatible with client "
            f"requirements: {min_version} <= v <= {max_version}"
        )
```

---

### Workflow Integration Example

```python
def start_sdlc_workflow(description: str):
    """Start SDLC workflow with client awareness."""

    # 1. Detect client (FIRST STEP)
    resolver = ClientResolver()
    client_id = resolver.detect_client()
    print(f"🎯 Active client: {client_id}")

    # 2. Load client profile
    profile = resolver.load_profile(client_id)
    client_name = profile.get("client", {}).get("name", client_id)
    print(f"📋 Profile: {client_name}")

    # 3. Validate version compatibility
    validate_client_compatibility(resolver, client_id)

    # 4. Detect complexity level
    complexity = detect_complexity(description)

    # 5. Load agents with client-aware resolution
    for phase in get_phases_for_complexity(complexity):
        agents = get_agents_for_phase(phase)

        for agent_name in agents:
            # Use client-aware resolution
            agent_path = resolver.resolve_agent(agent_name, client_id)

            # Log which version is being used
            if ".sdlc_clients/" in str(agent_path):
                print(f"  ✓ {agent_name} (client-specific)")
            else:
                print(f"  ✓ {agent_name} (base)")

            # Load and execute agent
            agent = load_agent(agent_path)
            results = agent.execute(phase_context)

    # 6. Execute workflow phases
    for phase in phases:
        execute_phase(phase, client_id, resolver)
```

---

### Client-Specific Gates

Clients can define custom quality gates:

```yaml
# .sdlc_clients/acme-corp/profile.yml
gates:
  additions:
    - name: "compliance-check"
      path: "gates/compliance-check.yml"
      after_phase: 2
      required: true
```

When evaluating gates, check both client and base:

```python
# Resolve gate path
gate_path = resolver.resolve_gate(f"phase-{N}-to-{N+1}", client_id)

# Returns:
# - .sdlc_clients/{client}/gates/phase-{N}-to-{N+1}.yml (if exists)
# - .claude/skills/gate-evaluator/gates/phase-{N}-to-{N+1}.yml (base)
```

---

### Logging and Observability

All client resolution events are logged to Loki:

```python
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="orchestrator", phase=phase)

logger.info(
    "Agent resolved",
    extra={
        "agent": agent_name,
        "client": client_id,
        "path": str(agent_path),
        "is_override": ".sdlc_clients/" in str(agent_path)
    }
)
```

---

### Error Handling

```python
try:
    agent_path = resolver.resolve_agent(agent_name, client_id)
except FileNotFoundError:
    logger.error(
        f"Agent {agent_name} not found for client {client_id} or base",
        extra={"agent": agent_name, "client": client_id}
    )
    # Fallback strategy:
    # 1. Try base framework version
    # 2. If still not found, skip agent with warning
    # 3. Or fail workflow depending on criticality

except VersionIncompatibleError as e:
    logger.error(f"Version incompatibility: {e}")
    # Suggest upgrade/downgrade
    # Block workflow execution
```

---

### Best Practices

1. **Always detect client first** before loading any resources
2. **Log all overrides** for observability and debugging
3. **Validate version compatibility** before workflow execution
4. **Fail gracefully** if resources not found (with clear messages)
5. **Test client profiles** in isolation before production use
6. **Document client-specific customizations** in profile.yml
7. **Monitor client adoption** via Loki/Grafana metrics

---

## Stakeholder Notification

After passing a gate, notify stakeholders about files requiring review:

### Process

1. **Read `stakeholder_review` field from gate YAML**
2. **Identify files created/modified in current phase**
3. **Categorize by priority** (HIGH, MEDIUM, LOW)
4. **Format notification message**
5. **Display to user**

### Notification Format

```
============================================
  ARQUIVOS PARA REVISÃO - Fase {N}
============================================

Os seguintes arquivos foram criados/modificados e precisam de revisão:

ALTA PRIORIDADE:
- [.agentic_sdlc/architecture/adr-001.yml] - Architecture decision: Kafka for event bus
- [.agentic_sdlc/security/threat-model.yml] - STRIDE analysis

MÉDIA PRIORIDADE:
- [docs/api-spec.yml] - API contract
- [README.md] - Updated setup instructions

Por favor, revise os arquivos marcados como ALTA PRIORIDADE
antes de prosseguir para a próxima fase.
============================================
```

---

## Phase Commit (v1.7.15+)

After successfully passing a gate:

### Automatic Commit Process

1. **Execute phase-commit skill automatically**
   ```bash
   python3 .claude/skills/phase-commit/scripts/phase-commit.py "$PROJECT_ID" "$PHASE" "complete phase"
   ```

2. **What phase-commit does**:
   - Stages all artifacts created in phase
   - Creates conventional commit message
   - Commits locally
   - **Pushes to remote** (if not disabled)
   - Updates manifest.yml with commit hash
   - Logs structured data to Loki

3. **Verify commit+push success**
   - Check git status
   - Verify remote tracking updated

4. **Handle failures**:
   - If commit fails → block phase advance
   - If push fails → keep local commit, warn user, don't block
   - Report error with suggested manual fix

### Example Commit Message

```
feat(phase-3): complete architecture design

Phase: 3 - Architecture
Artifacts:
- ADR-001: Select Kafka for event bus
- ADR-002: PostgreSQL for transactional data
- threat-model.yml: STRIDE analysis complete

Gate: phase-3-to-4 (passed)
Score: 95/100

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Learning Extraction

At the end of each phase (or session):

### Process

1. **Invoke session-analyzer skill**
   ```python
   from session_analyzer import extract_learnings

   learnings = extract_learnings(
       project_id=project_id,
       phase=current_phase,
       session_path=session_file
   )
   ```

2. **Extract key information**:
   - Decisions made (what, why, alternatives, consequences)
   - Blockers encountered (problem, root cause, resolution)
   - Patterns identified (recurring themes, anti-patterns)
   - Technical debt created
   - Success metrics achieved

3. **Persist learnings**:
   - Save to `.agentic_sdlc/sessions/YYYYMMDD-HHMMSS-{repo}.md`
   - Format as structured markdown
   - Include correlation IDs for traceability

4. **Feed RAG corpus** (if learning is significant):
   - Create learning node: `.agentic_sdlc/corpus/nodes/learnings/LEARN-{id}.yml`
   - Update knowledge graph with relations
   - Index for future retrieval

### Learning Node Example

```yaml
# .agentic_sdlc/corpus/nodes/learnings/LEARN-003.yml
id: LEARN-003
type: learning
title: "Kafka rate limiting prevents DDoS but adds latency"
source: "session:20260202-184523-sdlc"
phase: 3
timestamp: "2026-02-02T18:50:12Z"

context:
  decision: "ADR-001: Use Kafka for event bus"
  blocker: "Kafka throughput exceeded during load test"

resolution:
  approach: "Implemented rate limiting with token bucket"
  trade_off: "Added 50ms p99 latency but prevented DDoS"
  outcome: "Acceptable for our SLAs"

lessons:
  - "Always load test integration points"
  - "Rate limiting is essential for public-facing event streams"
  - "Monitor p99 latency after rate limiting"

tags:
  - kafka
  - performance
  - security
  - rate-limiting
```

---

## Multi-Agent Coordination Patterns

### Sequential Execution (Default)

Agents execute one after another in phase:

```
Phase 5:
  code-author → test-author → code-reviewer → refactoring-advisor
     ↓             ↓              ↓                  ↓
   Code         Tests         Review            Refactor
```

### Parallel Execution (v2.0+)

Independent tasks run concurrently using git worktrees:

```
Phase 5 (with parallel workers):
  ┌─ Worker 1: code-author (task-001) ──┐
  ├─ Worker 2: code-author (task-002) ──┤→ Merge → code-reviewer
  └─ Worker 3: code-author (task-003) ──┘
```

See: `integrations.md` for parallel worker details.

---

## Orchestrator Input/Output Formats

### Input Format

```yaml
orchestrator_request:
  type: [start_workflow | advance_phase | gate_check | escalate | query_status]
  project_id: string
  context:
    current_phase: number (0-8)
    complexity_level: number (0-3)
    artifacts: list[artifact_reference]
    pending_decisions: list[decision]
  payload:
    # Depends on request type
    description: string  # For start_workflow
    from_phase: number   # For advance_phase
    to_phase: number
```

### Output Format

```yaml
orchestrator_response:
  request_id: string
  timestamp: datetime
  action_taken: string

  phase_status:
    current_phase: number
    phase_name: string
    progress: percentage
    blockers: list[blocker]

  gate_result:
    passed: boolean
    score: float
    missing_items: list[string]

  delegations:
    - agent: string
      task: string
      status: string

  escalations:
    - type: string
      reason: string
      approvers: list[string]
      deadline: datetime

  next_steps:
    - step: string
      agent: string
      priority: string

  metrics:
    phase_duration: duration
    artifacts_created: number
    decisions_made: number
```

---

**Version**: 3.0.3
**Last Updated**: 2026-02-02
