# Learnings from OpenClaw Patterns

**Date**: 2026-02-01
**Source**: [OpenClaw AGENTS.md](https://github.com/openclaw/openclaw/blob/main/AGENTS.md), [Issue #4561](https://github.com/openclaw/openclaw/issues/4561)
**Context**: Comparative analysis to identify gaps and improvement opportunities in SDLC Agêntico

---

## Executive Summary

OpenClaw implements **production-grade multi-agent orchestration** with strong emphasis on:
1. **Agent isolation** and safety
2. **Token budget control** and context optimization
3. **Just-in-time skill loading** (metadata upfront, details on-demand)
4. **Durable artifacts** for handoffs (DECISIONS.md, RUNBOOK.md, memory/)
5. **Runtime plugin system** with explicit enable/disable

**Key Gap Identified**: SDLC Agêntico currently lacks agent isolation, token budget enforcement, and tool access control per agent.

---

## Detailed Patterns Analysis

### 1. Multi-Agent Safety (⚠️ GAP CRÍTICO)

**OpenClaw Pattern**:
```
- Each agent operates with "its own session" (isolated state)
- Agents focus exclusively on assigned changes
- No cross-cutting state changes allowed
- Support concurrent agent operations without branch switching
```

**SDLC Agêntico Current State**:
- ❌ All 38 agents share the same context/session
- ❌ No isolation between orchestrator and phase agents
- ❌ Phase agents can access ALL corpus/memory
- ⚠️ Risk: Agent A can corrupt Agent B's work

**Implication**:
When using parallel workers (Phase 5), each worker should have **isolated context** to prevent corruption. Currently, workers share git worktrees but NOT memory isolation.

**Recommended Action**:
```yaml
# .claude/agents/orchestrator.md
## Agent Session Isolation (NEW)

When spawning phase agents:
1. Create isolated session directory: ~/.claude/agents/<agent-id>/
2. Copy only relevant corpus nodes (filter by phase)
3. Prevent cross-agent state mutations
4. Merge learnings back to main corpus after completion
```

---

### 2. Context Overflow Handling (⚠️ GAP MODERADO)

**OpenClaw Pattern**:
```
Bootstrap files:
- Keep under 5KB each (truncation at 20KB)
- Injected on every run, so brevity matters
- Monitor via /context list

Session pruning:
- cache-ttl mode with 5-minute TTL
- Keep last 3 assistant messages
- Soft-trim large outputs to 4,000 characters
- Hard-clear replaces old results with placeholders
```

**SDLC Agêntico Current State**:
- ⚠️ orchestrator.md = 1,267 lines (~60KB) → **12x over limit**
- ❌ No automatic pruning of session history
- ❌ No token budget enforcement
- ✅ Progressive disclosure planned but not implemented

**Token Drivers (ranked by impact)**:
1. Tool schemas (~2,500 tokens for complex tools)
2. Tool execution outputs accumulating
3. Bootstrap file injection (orchestrator.md too large)
4. Conversation history
5. Skills list metadata

**Recommended Action**:
```yaml
# .claude/settings.json
{
  "sdlc": {
    "context": {
      "max_bootstrap_size_kb": 5,        # Enforce 5KB limit
      "session_pruning": {
        "enabled": true,
        "mode": "cache-ttl",
        "ttl_minutes": 5,
        "keep_last_messages": 3,
        "soft_trim_threshold": 4000
      },
      "token_budget": {
        "per_agent": 50000,              # Hard limit
        "warning_threshold": 40000        # Warn at 80%
      }
    }
  }
}
```

---

### 3. Just-In-Time Skill Loading (✅ OPORTUNIDADE ALTA)

**OpenClaw Pattern**:
```
Canonical approach:
- Store skill METADATA in system prompts (name, when to use, key terms)
- Load detailed instructions ON-DEMAND via read operations
- Memory search + retrieval for semantic recall
```

**Example**:
```markdown
# System Prompt (Always Loaded)
Available skills:
- gate-evaluator: Quality gate validation | Use when: phase transition
- rag-query: Search corpus | Use when: recall decision

# Skill Details (Load Only When Needed)
Read: .claude/skills/gate-evaluator/SKILL.md (only when agent needs it)
```

**SDLC Agêntico Current State**:
- ❌ ALL skills loaded in system prompt (30 skills × ~500 lines = 15,000 lines)
- ❌ ALL agent definitions loaded (38 agents × ~200 lines = 7,600 lines)
- ⚠️ **Total upfront load: ~23KB** (4.6x over 5KB limit)

**Recommended Action**:
```markdown
## Skill Discovery Metadata (< 5KB total)

skills:
  gate-evaluator:
    description: "Quality gate validation between SDLC phases"
    when_to_use: "phase transition, quality check, approval required"
    key_terms: ["gate", "phase", "transition", "quality", "criteria"]
    path: ".claude/skills/gate-evaluator/SKILL.md"

  rag-query:
    description: "Search knowledge corpus for decisions, patterns, learnings"
    when_to_use: "recall past decision, find pattern, search ADR"
    key_terms: ["search", "query", "decision", "ADR", "learning", "pattern"]
    path: ".claude/skills/rag-query/SKILL.md"

## On-Demand Loading

When agent mentions key terms → Claude reads full SKILL.md
When phase transition → Load gate-evaluator details
When architectural question → Load system-architect agent definition
```

**Impact**: Reduce upfront context from 23KB → 5KB (78% reduction)

---

### 4. Durable Artifacts Pattern (✅ OPORTUNIDADE MÉDIA)

**OpenClaw Pattern**:
```
Workflow for converting chat to durable artifacts:

DECISIONS.md         - Major architectural choices (lightweight)
RUNBOOK.md          - Operational procedures (how to run/deploy)
ARCH.md             - Architecture overview (high-level)
memory/YYYY-MM-DD.md - Daily append-only logs
MEMORY.md           - Curated long-term memory (private sessions)
```

**SDLC Agêntico Current State**:
- ✅ ADRs exist (but heavy YAML format)
- ❌ No RUNBOOK.md (operational procedures scattered)
- ❌ No ARCH.md (architecture docs in README/CLAUDE.md)
- ⚠️ Sessions stored as JSONL (not human-readable markdown)
- ❌ No daily memory logs structure

**Comparison**:

| Artifact | OpenClaw | SDLC Agêntico | Gap |
|----------|----------|---------------|-----|
| **Decisions** | DECISIONS.md (markdown, lightweight) | ADR-XXX.yml (YAML, structured) | ⚠️ ADRs too heavy for quick notes |
| **Operations** | RUNBOOK.md | Scattered in docs/ | ❌ No centralized runbook |
| **Architecture** | ARCH.md | README.md, CLAUDE.md | ⚠️ Mixed with other content |
| **Daily logs** | memory/2026-02-01.md | sessions/YYYYMMDD-HHMMSS.jsonl | ❌ Not human-readable |
| **Curated memory** | MEMORY.md | .agentic_sdlc/corpus/ | ✅ Similar concept |

**Recommended Action**:
```bash
# Add to .agentic_sdlc/
.agentic_sdlc/
├── DECISIONS.md           # Lightweight decisions (complement to ADRs)
├── RUNBOOK.md            # How to run/deploy/operate
├── ARCH.md               # High-level architecture
└── memory/
    ├── 2026-02-01.md     # Daily append-only log
    ├── 2026-02-02.md
    └── MEMORY.md         # Curated long-term (private)
```

**DECISIONS.md Example**:
```markdown
# Quick Decisions Log

## 2026-02-01: Use Natural Language First for skills
**Context**: 124 Python scripts, many doing pattern matching
**Decision**: Delete 21 scripts, keep only deterministic/API/I/O critical
**Rationale**: Claude is better at pattern matching than hardcoded scripts
**Impact**: -6,000 lines, cleaner codebase
**ADR**: See LEARN-natural-language-first-principle.md for full analysis
```

---

### 5. Tool Access Control (⚠️ GAP CRÍTICO)

**OpenClaw Pattern**:
```yaml
# Per-agent tool restrictions
agents:
  family-agent:
    tools:
      allow: ["read", "write"]         # Read-only essentially
      deny: ["bash", "git", "delete"]   # No destructive ops

  dev-agent:
    tools:
      allow: "group:fs,group:runtime"
      deny: "group:messaging"

# Tool groups
group:runtime   - bash, git, npm
group:fs        - read, write, edit
group:sessions  - session management
group:ui        - display, notify
group:messaging - slack, email, sms
```

**SDLC Agêntico Current State**:
- ❌ No tool restrictions per agent
- ❌ All agents can use ALL tools (Bash, Git, Write, etc.)
- ⚠️ Risk: intake-analyst (Phase 0) can run Bash commands
- ⚠️ Risk: threat-modeler can execute code

**Example of Current Risk**:
```markdown
# threat-modeler.md (Phase 3)
Agent can theoretically:
- Run Bash commands (security risk)
- Modify production code (out of scope)
- Delete files (destructive)

Expected: Should only READ architecture, WRITE threat-model.yml
```

**Recommended Action**:
```yaml
# .claude/agents/threat-modeler.md frontmatter
---
name: threat-modeler
phase: 3
allowed_tools:
  - Read         # Read architecture files
  - Write        # Write threat-model.yml
  - Grep         # Search codebase
  - Glob         # Find files
denied_tools:
  - Bash         # No command execution
  - Edit         # No code modification
  - Git          # No git operations
  - Task         # No spawning agents
---
```

**Enforcement**:
```python
# .claude/lib/python/tool_enforcer.py
def check_tool_permission(agent: str, tool: str) -> bool:
    agent_config = load_agent_config(agent)

    if tool in agent_config.get("denied_tools", []):
        raise ToolDeniedError(f"{agent} cannot use {tool}")

    allowed = agent_config.get("allowed_tools", [])
    if allowed and tool not in allowed:
        raise ToolNotAllowedError(f"{agent} only allowed: {allowed}")

    return True
```

---

### 6. Token Budget Enforcement (✅ OPORTUNIDADE ALTA)

**OpenClaw Pattern**:
```yaml
agents:
  defaults:
    contextTokens: 100000    # Hard ceiling for context window

# Monitoring
/status                      # Show token usage
/usage tokens               # Detailed breakdown
/context list               # Bootstrap + session size
/context detail             # Per-file token counts
```

**SDLC Agêntico Current State**:
- ❌ No token budget configuration
- ❌ No monitoring of context size
- ❌ No warnings when approaching limits
- ⚠️ Can easily exceed 200K token budget (Sonnet 4.5 limit)

**Recommended Action**:
```yaml
# .claude/settings.json
{
  "sdlc": {
    "token_budget": {
      "global_max": 200000,           # Sonnet 4.5 limit
      "per_agent_max": 50000,         # Each agent capped
      "orchestrator_max": 80000,      # Orchestrator gets more
      "warning_threshold": 0.8,       # Warn at 80%
      "action_on_overflow": "prune"   # Auto-prune or error
    }
  }
}
```

**Monitoring Commands**:
```bash
# Add new commands
/token-status        # Show current usage vs budget
/context-size        # Breakdown by agent/skill/corpus
/prune-context       # Manual pruning trigger
```

---

### 7. Runtime Plugin System (✅ OPORTUNIDADE BAIXA - Nice to Have)

**OpenClaw Pattern**:
```json
// openclaw.plugin.json
{
  "id": "my-skill",
  "name": "My Custom Skill",
  "version": "1.0.0",
  "main": "index.ts",
  "tools": ["custom-tool"],
  "bootstrap": "SKILL.md"
}

// Runtime loading
import { loadPlugin } from 'jiti';
const plugin = await loadPlugin('~/.openclaw/extensions/my-skill');
```

**SDLC Agêntico Current State**:
- ❌ Skills are static (must be in .claude/skills/)
- ❌ No runtime enable/disable (must edit settings.json)
- ⚠️ Adding new skill requires framework change

**Recommended Action** (v3.1.0 - Optional):
```yaml
# .claude/skills/my-skill/skill.json
{
  "id": "my-skill",
  "name": "My Custom Skill",
  "version": "1.0.0",
  "enabled": true,              # Runtime toggle
  "metadata": {
    "description": "What it does",
    "when_to_use": "Trigger conditions",
    "key_terms": ["term1", "term2"]
  },
  "bootstrap": "SKILL.md",
  "scripts": ["scripts/main.py"]
}
```

**Why Low Priority**:
- SDLC Agêntico is configuration-driven (not code-driven like OpenClaw)
- Skills are markdown-based (not TypeScript modules)
- Runtime loading less critical for batch workflows (vs interactive assistant)

---

## Summary: Gaps and Opportunities

### Critical Gaps (High Priority)

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| **Agent isolation** | Concurrent agents can corrupt each other | Medium | P0 |
| **Tool access control** | Security risk (any agent can run Bash) | Low | P0 |
| **Token budget enforcement** | Can exceed 200K limit and fail | Low | P0 |

### Moderate Gaps (Medium Priority)

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| **Just-in-time skill loading** | Context bloat (23KB → 5KB possible) | Medium | P1 |
| **Context pruning** | Session history grows unbounded | Low | P1 |
| **orchestrator.md size** | 1,267 lines (12x over 5KB limit) | High | P1 |

### Opportunities (Low Priority - Nice to Have)

| Opportunity | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| **Durable artifacts** (DECISIONS.md, RUNBOOK.md) | Better handoffs, human-readable logs | Low | P2 |
| **Daily memory logs** (memory/YYYY-MM-DD.md) | Append-only audit trail | Low | P2 |
| **Runtime plugin system** | Dynamic skill loading | High | P3 |

---

## Recommended Implementation Plan

### Phase 1: Critical Gaps (v3.1.0 - Next Release)

**1.1 Tool Access Control**:
```yaml
# Action: Add tool restrictions to each agent frontmatter
- Implement tool_enforcer.py hook
- Update all 38 agents with allowed_tools/denied_tools
- Test enforcement in PreToolUse hook
```

**1.2 Token Budget Enforcement**:
```yaml
# Action: Add budget configuration and monitoring
- Implement token counter in orchestrator
- Add /token-status command
- Warn at 80%, error at 100%
```

**1.3 Agent Session Isolation**:
```yaml
# Action: Isolate parallel workers (Phase 5)
- Create ~/.claude/agents/<agent-id>/ directories
- Copy only relevant corpus nodes per agent
- Merge learnings back after completion
```

**Estimated Effort**: 2-3 days
**Risk**: Low (additive changes, no breaking changes)

---

### Phase 2: Moderate Gaps (v3.2.0)

**2.1 Just-In-Time Skill Loading**:
```yaml
# Action: Skill metadata discovery system
- Extract metadata from all SKILL.md files
- Create skills-index.yml (< 5KB)
- Implement on-demand Read when skill triggered
```

**2.2 Progressive Disclosure for orchestrator.md**:
```yaml
# Action: Split orchestrator.md into modules
- orchestrator.md (< 500 lines) - main workflow
- orchestrator/reference/*.md - detailed guides
- Load reference files on-demand
```

**2.3 Context Pruning**:
```yaml
# Action: Implement cache-ttl pruning
- Keep last 3 messages
- Soft-trim outputs > 4,000 chars
- Hard-clear old tool results
```

**Estimated Effort**: 5-7 days
**Risk**: Medium (requires refactoring orchestrator)

---

### Phase 3: Opportunities (v3.3.0 - Optional)

**3.1 Durable Artifacts**:
```yaml
# Action: Add lightweight decision tracking
- DECISIONS.md for quick notes
- RUNBOOK.md for operations
- ARCH.md for high-level architecture
- memory/YYYY-MM-DD.md for daily logs
```

**3.2 Runtime Plugin System**:
```yaml
# Action: skill.json manifest + dynamic loading
- Define skill.json schema
- Implement skill loader
- Add /skill enable|disable commands
```

**Estimated Effort**: 3-5 days
**Risk**: Low (optional features)

---

## Key Learnings Applied Immediately

Even without implementing the full plan, we can apply these learnings NOW:

### 1. **Skill Documentation Standard** (from openclaw.plugin.json pattern)

Update `.claude/skills/_template/SKILL.md` to include:
```yaml
---
name: skill-name
version: 1.0.0
enabled: true                    # ← NEW: Runtime toggle capability
metadata:
  description: "What it does"
  when_to_use: "Trigger conditions"
  key_terms: ["term1", "term2"]  # ← NEW: Discovery keywords
---
```

### 2. **Agent Documentation Standard** (from tool access control pattern)

Update `.claude/agents/_template.md` to include:
```yaml
---
name: agent-name
phase: 3
model: sonnet
allowed_tools:                   # ← NEW: Whitelist
  - Read
  - Write
  - Grep
denied_tools:                    # ← NEW: Blacklist
  - Bash
  - Git
---
```

### 3. **Token Budget Awareness** (from context monitoring pattern)

Add to `orchestrator.md`:
```markdown
## Token Budget Management

Before loading skills/agents:
1. Check current context size
2. Load only essential bootstrap files
3. Defer detailed instructions to on-demand reads
4. Warn if approaching 80% of 200K budget
```

### 4. **Durable Artifacts Complement** (from DECISIONS.md pattern)

Create lightweight decision log alongside heavy ADRs:
```markdown
# .agentic_sdlc/DECISIONS.md

Quick decisions that don't need full ADR:
- Small tech choices
- Tool selections
- Process tweaks
- Temporary workarounds

(Full architectural decisions still go to ADR-XXX.yml)
```

---

## Conclusion

OpenClaw demonstrates **production-grade multi-agent orchestration** with:
- ✅ Strong safety guarantees (agent isolation)
- ✅ Token budget control (context optimization)
- ✅ Just-in-time loading (metadata upfront, details on-demand)
- ✅ Tool access control (prevent destructive operations)
- ✅ Durable artifacts (human-readable handoffs)

**SDLC Agêntico can adopt these patterns** to improve:
1. **Safety** - Prevent agent conflicts via isolation
2. **Scalability** - Control context growth via budget + pruning
3. **Security** - Restrict tools per agent
4. **Efficiency** - Load skills on-demand, not upfront

**Next Action**: Implement Phase 1 (Critical Gaps) in v3.1.0 release.

---

**Sources**:
- [OpenClaw AGENTS.md](https://github.com/openclaw/openclaw/blob/main/AGENTS.md)
- [OpenClaw Issue #4561: Multi-Agent Best Practices](https://github.com/openclaw/openclaw/issues/4561)
- [OpenClaw Documentation](https://docs.openclaw.ai/start/getting-started)
- [What is OpenClaw? - DigitalOcean](https://www.digitalocean.com/resources/articles/what-is-openclaw)
