# Pre-Compact Session Analysis

## Overview

The Pre-Compact analysis system automatically extracts learnings from Claude Code sessions **before** automatic conversation compaction, ensuring no knowledge is lost during context compression.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Claude Code Session                         │
│                  (approaching context limit)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Triggers auto compaction
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PreCompact Hook (automatic)                     │
│         .claude/hooks/pre-compact-analyzer.py                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Creates analysis marker
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Pending Analysis Marker Created                    │
│  .agentic_sdlc/sessions/pending-analysis/*.marker            │
│  {                                                           │
│    "transcript_path": "/path/to/session.jsonl",              │
│    "trigger": "pre-compact",                                 │
│    "timestamp": "2026-02-09T...",                            │
│    "status": "pending"                                       │
│  }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ User invokes manually or
                         │ automatic processing
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Session Analyzer (manual or scheduled)               │
│  .claude/skills/session-analyzer/scripts/                    │
│         extract_learnings.py --process-markers               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Parses JSONL transcript
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Session Analysis                             │
│  - Decisions identified                                      │
│  - Blockers and resolutions                                  │
│  - Learnings and patterns                                    │
│  - Artifacts created                                         │
│  - Tools used                                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Saves structured output
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Analysis Persisted                              │
│  .project/sessions/session-YYYYMMDD-HHMMSS-{id}.yml          │
│                                                              │
│  session_analysis:                                           │
│    id: abc123                                                │
│    analyzed_at: 2026-02-09T...                               │
│    source_file: /path/to/session.jsonl                       │
│    decisions:                                                │
│      - description: "Chose PostgreSQL for database"          │
│        confidence: high                                      │
│    learnings:                                                │
│      - description: "Always validate input at boundaries"    │
│        type: best-practice                                   │
│    artifacts_created:                                        │
│      - path: src/models/user.py                              │
│        type: write                                           │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. PreCompact Hook

**Location**: `.claude/hooks/pre-compact-analyzer.py`

**Configuration** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/pre-compact-analyzer.py || python .claude/hooks/pre-compact-analyzer.py",
            "description": "Extract learnings from session before automatic compaction"
          }
        ]
      }
    ]
  }
}
```

**Responsibilities**:
- Detect automatic conversation compaction
- Create analysis marker in `.agentic_sdlc/sessions/pending-analysis/`
- Non-blocking (cannot prevent compaction)
- Log actions to stderr (visible to user)

**Input** (from Claude Code):

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/-home-user-project/session.jsonl",
  "cwd": "/home/user/project",
  "hook_event_name": "PreCompact",
  "trigger": "auto",
  "permission_mode": "default"
}
```

### 2. Session Analyzer

**Location**: `.claude/skills/session-analyzer/scripts/extract_learnings.py`

**Responsibilities**:
- Parse JSONL transcript files
- Extract patterns using keyword detection
- Generate structured analysis
- Persist results to `.project/sessions/`

**Usage**:

```bash
# Process pending markers created by PreCompact hook
python3 .claude/skills/session-analyzer/scripts/extract_learnings.py --process-markers

# Analyze most recent session
python3 .claude/skills/session-analyzer/scripts/extract_learnings.py --persist

# Analyze specific session
python3 .claude/skills/session-analyzer/scripts/extract_learnings.py --session-id <uuid> --persist
```

### 3. Analysis Markers

**Location**: `.agentic_sdlc/sessions/pending-analysis/precompact-{session-id}.marker`

**Format**:

```json
{
  "transcript_path": "/path/to/session.jsonl",
  "trigger": "pre-compact",
  "timestamp": "2026-02-09T15:30:00.000000",
  "status": "pending"
}
```

**Lifecycle**:
1. Created by PreCompact hook
2. Processed by session-analyzer
3. Deleted after successful analysis

## Pattern Detection

### Decisions

**Keywords**: `decided`, `chose`, `will use`, `going with`, `recommend`, `optei por`, `vou usar`

**Example extraction**:
> "I **decided** to use PostgreSQL instead of MongoDB because we need ACID transactions."

Extracted as:

```yaml
decisions:
  - description: "use PostgreSQL instead of MongoDB because we need ACID transactions"
    confidence: high
```

### Learnings

**Keywords**: `learned`, `discovered`, `important`, `note`, `avoid`, `always`, `never`, `aprendi`, `importante`

**Example extraction**:
> "**Important**: Always validate user input at system boundaries to prevent injection attacks."

Extracted as:

```yaml
learnings:
  - description: "Always validate user input at system boundaries to prevent injection attacks"
    type: best-practice
```

### Blockers

**Keywords**: `error`, `failed`, `problem`, `doesn't work`, `blocked`, `stuck`, `erro`, `falhou`

**Example detection**:
> Tool result: `Error: Connection refused to database on port 5432`

Extracted as:

```yaml
blockers:
  - description: "Connection refused to database on port 5432"
    resolution: null
```

### Artifacts

**Tracked operations**: `Write`, `Edit` tool uses

**Example**:

```yaml
artifacts_created:
  - path: src/models/user.py
    type: write
  - path: src/config/database.yml
    type: edit
```

## Output Format

**Location**: `.project/sessions/session-{timestamp}-{session-short-id}.yml`

**Structure**:

```yaml
session_analysis:
  id: abc123-def456-789012
  analyzed_at: 2026-02-09T15:30:00
  source_file: /home/user/.claude/projects/.../session.jsonl
  project_path: /home/user/project

  summary:
    total_events: 150
    user_messages: 25
    assistant_messages: 30
    tool_uses: 45
    thinking_blocks: 15

  decisions:
    - description: "use PostgreSQL for database"
      confidence: high
    - description: "implement circuit breaker pattern"
      confidence: medium

  learnings:
    - description: "Always validate at boundaries"
      type: best-practice
    - description: "Mock objects hide real failures"
      type: anti-pattern

  blockers:
    - description: "Connection timeout to external API"
      resolution: "Added retry with exponential backoff"

  artifacts_created:
    - path: src/models/user.py
      type: write
    - path: tests/test_user.py
      type: write
    - path: src/config/database.yml
      type: edit

  tools_used:
    - Write
    - Edit
    - Bash
    - Read
    - Grep
```

## User Experience

### During Compaction

When automatic compaction is triggered:

```
[2026-02-09 15:30:00] ℹ️ PreCompact: Automatic compaction detected (session: abc123)
[2026-02-09 15:30:00] ℹ️ PreCompact: Analyzing session (45123 bytes) before compaction...
[2026-02-09 15:30:00] ✅ PreCompact: Session marked for analysis
[2026-02-09 15:30:00] ℹ️ PreCompact: Use /session-analyzer to extract learnings manually if needed
```

### Manual Processing

User can process markers manually:

```bash
$ python3 .claude/skills/session-analyzer/scripts/extract_learnings.py --process-markers

📊 Processing: abc123-def456-789012.jsonl
======================================================
SESSION ANALYSIS SUMMARY
======================================================

Total events: 150
User messages: 25
Assistant messages: 30
Tool uses: 45

Decisions identified: 3
Learnings identified: 5
Artifacts created: 8

Tools used: Write, Edit, Bash, Read, Grep
======================================================

✅ Analysis saved to: .project/sessions/session-20260209-153000-abc123.yml
✅ Processed 1 pending analysis markers
```

## Integration with RAG

Analysis outputs can be indexed into the RAG corpus:

```bash
# Add learnings to corpus
python3 .claude/skills/rag-curator/scripts/add_node.py \
  --type learning \
  --content "Always validate at system boundaries" \
  --source ".project/sessions/session-20260209-153000-abc123.yml" \
  --metadata "phase=implementation,confidence=high"
```

## Workflow Integration

### Automatic (via PreCompact)

1. Claude Code session approaches context limit
2. PreCompact hook triggers automatically
3. Analysis marker created
4. User sees notification in stderr
5. User processes markers when convenient

### Manual (via gate-check)

```yaml
# In gate-evaluator/gates/phase-5-to-6.yml
post_approval_actions:
  - name: Extract session learnings
    command: |
      python3 .claude/skills/session-analyzer/scripts/extract_learnings.py \
        --persist --process-markers
```

### Scheduled (via cron)

```bash
# Process pending markers every hour
0 * * * * cd /path/to/project && \
  python3 .claude/skills/session-analyzer/scripts/extract_learnings.py \
    --process-markers >> /tmp/session-analysis.log 2>&1
```

## Benefits

### Knowledge Preservation

- **Before compaction**: Learnings extracted from full conversation
- **Structured format**: YAML output easily queryable
- **Historical record**: All sessions analyzed and persisted

### Continuous Improvement

- **Pattern detection**: Identify recurring decisions and learnings
- **RAG enrichment**: Feed knowledge back into future sessions
- **Trend analysis**: Track evolution of project decisions

### Non-Intrusive

- **Non-blocking**: Cannot prevent compaction
- **Asynchronous**: Processing happens independently
- **User-controlled**: Manual processing when convenient

## Limitations

### Detection Accuracy

- Keyword-based detection (not semantic)
- May miss implicit decisions
- May identify false positives

### Performance

- Large sessions (>100KB) take time to analyze
- JSONL parsing can be memory-intensive
- Real-time analysis not guaranteed

### Coverage

- Only analyzes sessions that trigger compaction
- Short sessions may not be analyzed
- Manual sessions not auto-analyzed

## Future Enhancements

### Semantic Analysis

- Use embeddings for decision detection
- Cluster related learnings
- Identify decision patterns

### Integration

- Auto-add to RAG corpus
- Trigger ADR creation for significant decisions
- Generate session-based retrospectives

### Real-time Processing

- Stream processing during session
- Incremental analysis
- Live learning dashboard

## References

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks.md#precompact)
- [Session Analyzer Skill](/.claude/skills/session-analyzer/SKILL.md)
- [RAG Curator Integration](/.claude/skills/rag-curator/SKILL.md)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-09
**Author**: SDLC Agêntico Framework
