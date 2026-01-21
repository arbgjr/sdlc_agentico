# Memory Manager - Enhanced (v2.0)

Sistema de memória híbrido combinando **deep storage (RAG)** com **working memory (Simple Store)**.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Memory Manager v2.0                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │  Simple Store    │         │   RAG Corpus     │    │
│  │  (Working Memory)│         │  (Long-term)     │    │
│  ├──────────────────┤         ├──────────────────┤    │
│  │ • Facts (JSON)   │         │ • ADRs (YAML)    │    │
│  │ • Toolchain      │         │ • Learnings      │    │
│  │ • Repos          │         │ • Patterns       │    │
│  │ • Quick context  │         │ • Decisions      │    │
│  │                  │         │                  │    │
│  │ Fast, ephemeral  │◄───────►│ Indexed, durable │    │
│  └──────────────────┘         └──────────────────┘    │
│           ▲                            ▲               │
│           │                            │               │
│           └──────────┬─────────────────┘               │
│                      │                                 │
│                  Agents use                            │
│              both as needed                            │
└─────────────────────────────────────────────────────────┘
```

## Quando Usar Cada Sistema

| Use Case | Simple Store | RAG Corpus |
|----------|-------------|------------|
| Quick facts | ✅ | ❌ |
| Tool references | ✅ | ❌ |
| Repo metadata | ✅ | ❌ |
| Working context | ✅ | ❌ |
| Cross-session notes | ✅ | ✅ |
| Architecture decisions (ADRs) | ❌ | ✅ |
| Learnings from incidents | ❌ | ✅ |
| Design patterns | ❌ | ✅ |
| Deep knowledge | ❌ | ✅ |

**Rule of thumb:**
- **Simple Store**: "I need to remember this for next hour/day"
- **RAG Corpus**: "This knowledge should persist forever"

## Quick Start

### Simple Store (Working Memory)

```bash
# Remember a fact
python3 scripts/simple_store.py add-fact \
  "API rate limit is 1000 req/min" \
  --tags rate-limit api \
  --project mice_dolphins

# Recall facts
python3 scripts/simple_store.py recall "rate limit"
python3 scripts/simple_store.py recall --tags api --project mice_dolphins

# Add a tool
python3 scripts/simple_store.py add-tool gh \
  --repo "https://github.com/cli/cli" \
  --version "2.40.0" \
  --install "brew install gh" \
  --docs "https://cli.github.com/manual/"

# List tools
python3 scripts/simple_store.py list-tools

# Add a repository
python3 scripts/simple_store.py add-repo sdlc-agentico \
  --url "https://github.com/arbgjr/sdlc_agentico" \
  --branch "main" \
  --description "SDLC Agêntico Framework"

# Search across all memory
python3 scripts/simple_store.py search "database"

# Export memory
python3 scripts/simple_store.py export memory-backup.json
```

### RAG Corpus (Long-term)

```bash
# Add decision to RAG (via memory_ops.py - existing)
python3 scripts/memory_ops.py add-decision \
  --type architectural \
  --title "Use PostgreSQL for primary database" \
  --context "Need relational DB with JSON support"

# Query RAG corpus
python3 ../rag-query/scripts/hybrid_search.py "database decisions"
```

## Directory Structure

```
~/.claude/
├── simple-memory/              # NEW: Simple Store (v2.0)
│   ├── facts.json              # Quick facts
│   ├── toolchain.json          # Tool references
│   ├── repos.json              # Repository metadata
│   └── projects/               # Project-specific context
│       ├── project-a.json
│       └── project-b.json
│
└── memory/                     # LEGACY (migrated to .agentic_sdlc)
    └── ...

.agentic_sdlc/
├── corpus/                     # RAG Corpus (long-term)
│   ├── nodes/
│   │   ├── decisions/          # ADRs
│   │   ├── learnings/          # Lessons learned
│   │   ├── patterns/           # Design patterns
│   │   └── concepts/           # Extracted concepts
│   ├── graph.json              # Semantic graph
│   └── index.yml               # Text index
│
└── projects/                   # Project-specific YAML (structured)
    └── {project-id}/
        ├── manifest.yml
        ├── decisions/
        ├── phases/
        └── docs/
```

## Simple Store JSON Schemas

### facts.json

```json
{
  "facts": [
    {
      "id": "fact-001",
      "text": "API rate limit is 1000 req/min",
      "added": "2026-01-21T10:30:00Z",
      "tags": ["rate-limit", "api"],
      "project": "mice_dolphins",
      "access_count": 5
    }
  ]
}
```

### toolchain.json

```json
{
  "gh": {
    "repo": "https://github.com/cli/cli",
    "version": "2.40.0",
    "install": "brew install gh",
    "docs": "https://cli.github.com/manual/",
    "added": "2026-01-21T10:30:00Z"
  }
}
```

### repos.json

```json
{
  "sdlc-agentico": {
    "url": "https://github.com/arbgjr/sdlc_agentico",
    "branch": "main",
    "description": "SDLC Agêntico Framework",
    "added": "2026-01-21T10:30:00Z"
  }
}
```

### projects/{name}.json

```json
{
  "name": "mice_dolphins",
  "current_phase": 5,
  "active_workers": ["worker-abc123", "worker-def456"],
  "last_commit": "abc123def",
  "blockers": [],
  "created_at": "2026-01-21T10:00:00Z",
  "updated_at": "2026-01-21T10:30:00Z"
}
```

## Integration Examples

### Agent Workflow

```python
from simple_store import SimpleStore
from memory_ops import save_decision

store = SimpleStore()

# 1. Quick fact during implementation
store.add_fact(
    "Redis connection pool size: 50",
    tags=["redis", "config"],
    project="mice_dolphins"
)

# 2. Later, recall when needed
facts = store.recall_facts(query="redis", project="mice_dolphins")
# → Returns: [{"text": "Redis connection pool size: 50", ...}]

# 3. After testing, promote important decision to RAG
save_decision(
    type="technical",
    title="Redis connection pool sizing strategy",
    context="High-throughput API requires connection pooling",
    decision="Use pool size of 50 based on load tests",
    consequences={
        "positive": ["Better performance under load"],
        "negative": ["Higher memory usage"],
        "risks": ["May need tuning in production"]
    },
    phase=5
)
# → Persists to .agentic_sdlc/corpus/nodes/decisions/adr-NNN.yml
```

### Cross-Phase Context

```python
# Phase 5: Code author remembers implementation detail
store.add_fact(
    "User service uses JWT with 1h expiration",
    tags=["auth", "jwt"],
    project="mice_dolphins"
)

# Phase 6: QA analyst recalls during testing
facts = store.recall_facts(query="jwt expiration")
# → Quickly finds: "User service uses JWT with 1h expiration"
```

### Session Continuity

```python
# End of session: Save context
store.save_project_context("mice_dolphins", {
    "current_phase": 5,
    "active_tasks": ["TASK-001", "TASK-002"],
    "blockers": ["Waiting for API key"],
    "notes": "Worker 1 implementing auth, Worker 2 writing tests"
})

# Next session: Load context
context = store.load_project_context("mice_dolphins")
# → Restore state immediately
```

## CLI Commands

### Facts

```bash
# Add fact
python3 scripts/simple_store.py add-fact "Fact text" \
  --tags tag1 tag2 \
  --project project-name

# Recall facts
python3 scripts/simple_store.py recall "query"
python3 scripts/simple_store.py recall --tags tag1 --project project-name
python3 scripts/simple_store.py recall --limit 20

# Delete fact
python3 scripts/simple_store.py delete-fact fact-001
```

### Toolchain

```bash
# Add tool
python3 scripts/simple_store.py add-tool <name> \
  --repo <url> \
  --version <version> \
  --install <command> \
  --docs <url>

# List tools
python3 scripts/simple_store.py list-tools

# Get tool info
python3 scripts/simple_store.py list-tools | jq '.gh'
```

### Repositories

```bash
# Add repo
python3 scripts/simple_store.py add-repo <name> <url> \
  --branch <branch> \
  --description "Description"

# List repos
python3 scripts/simple_store.py list-repos
```

### Search

```bash
# Search all memory types
python3 scripts/simple_store.py search "database"
```

### Export

```bash
# Export all memory
python3 scripts/simple_store.py export backup.json
```

## Observability

All operations logged to Loki:

```json
{
  "skill": "memory-manager",
  "phase": 0,
  "operation": "add_fact",
  "fact_id": "fact-001",
  "tags": ["api", "rate-limit"],
  "project": "mice_dolphins"
}
```

**Loki queries:**

```logql
# All memory operations
{skill="memory-manager"}

# Facts added
{skill="memory-manager", operation="add_fact"}

# Recalls by project
{skill="memory-manager", operation="recall_facts"} | json | line_format "{{.project}}"
```

## Migration from Legacy

Simple Store is **additive** - existing `.agentic_sdlc/` structure unchanged.

**No migration required** - both systems coexist:
- **Simple Store**: New working memory layer
- **RAG Corpus**: Existing long-term storage

## Performance

| Operation | Simple Store | RAG Corpus |
|-----------|-------------|------------|
| Add fact | < 10ms | ~100ms (indexing) |
| Recall | < 50ms | ~200ms (search) |
| Search | < 100ms | ~500ms (semantic) |
| Storage | JSON (KB) | YAML + graph (MB) |

## Limitations

- **Simple Store**: Max ~1000 facts per project (performance degrades)
- **RAG Corpus**: Max ~10,000 nodes (requires graph optimization)

**Best practice:** Periodically promote important facts to RAG corpus, then delete from Simple Store.

## References

- Source: [claude-orchestrator memory system](https://github.com/reshashi/claude-orchestrator/blob/main/docs/MEMORY.md)
- Analysis: `.agentic_sdlc/corpus/nodes/learnings/LEARN-claude-orchestrator-patterns.yml`
- Epic: Issue #33
- Task: Issue #36
