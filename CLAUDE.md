# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Major Rules
- Always follow the **Anti-Mock Policy** (CRITICAL)

## Project Overview

SDLC Agêntico is an AI-driven Software Development Lifecycle framework that orchestrates **36 specialized agents (32 orchestrated + 4 consultive)** through **9 development phases (0-8)**. This is a **configuration and orchestration framework**, not a traditional application codebase.

**Key Features:**
- Security by Design integrated in all phases
- Automatic branch creation for features and fixes
- Infrastructure as Code (IaC) generation
- Automatic documentation generation
- Quality gates between all phases
- Commit automation per phase (v1.2.0)
- Session learning and knowledge extraction (v1.2.0)
- Stakeholder review notifications (v1.2.0)
- Automatic migration to `.agentic_sdlc/` (v1.2.0)
- Document processing (PDF, XLSX, DOCX) for requirements extraction (v1.3.0)
- Frontend E2E testing with Playwright integration (v1.3.0)
- Automatic document detection hook (v1.3.0)
- Semantic knowledge graph with hybrid search (v1.4.0)
- Automatic concept extraction from documents (v1.4.0)
- Graph visualization with Mermaid diagrams (v1.4.0)
- Graph integrity quality gate (v1.4.0)
- Decay scoring for knowledge freshness (v1.5.0)
- Automatic curation suggestions for obsolete content (v1.5.0)
- Search results boosted by content freshness (v1.5.0)
- Native GitHub Projects V2 integration (v1.6.0)
- Automatic Milestone creation per sprint (v1.6.0)
- GitHub Wiki synchronization with ADRs (v1.6.0)
- Consolidated GitHub dashboard command (v1.6.0)
- Structured logging with Loki/Tempo/Grafana integration (v1.7.0)
- Python and Shell logging utilities with correlation IDs (v1.7.0)
- Pre-configured Grafana dashboard for SDLC observability (v1.7.0)
- Professional documentation generator with SDLC signature (v1.8.1)
- Auto-detection of languages, frameworks, and project structure (v1.8.1)
- Automatic document enrichment with research findings (v1.9.0)
- Hybrid search for document matching (keyword + text + category) (v1.9.0)
- Versioned enriched documents with immutable originals (v1.9.0)
- Knowledge graph integration with 'enriches' relations (v1.9.0)

## Anti-Mock Policy (CRITICAL)

**Absolutely prohibited** in production code:

- Mock/stub/fake/dummy implementations of external services or MCP
- Hardcoded test data or pattern-based bypasses
- Keywords: `mock|stub|fake|dummy|simulator|emulator|inmemory`
- Placeholders: `lorem`, `foo`, `bar`, `TODO`, `TBD`

Test doubles are **ONLY** allowed in `tests/` directories.

When services are unavailable, use resilience patterns:

- Timeout, retry, circuit breaker
- Return `503 Service Unavailable` with `x-correlation-id`

## Setup Commands

```bash
# Install all dependencies (Python 3.11+, uv, Node.js 18+, Claude Code, Spec Kit, gh)
./.scripts/setup-sdlc.sh

# Verify installation
specify check
claude --version
gh auth status
```

## Workflow Commands

```bash
# Start SDLC workflow (full - Level 2/3)
/sdlc-start "Description of feature or project"

# Quick fix flow (Level 0 - bug fixes, typos)
/quick-fix "Description of the bug"

# New feature flow (Level 1 - feature in existing service)
/new-feature "Feature name"

# Check current phase status
/phase-status

# Verify quality gate before phase transition
/gate-check phase-2-to-3

# Create Architecture Decision Record
/adr-create "Decision title"

# Run security scan
/security-scan

# Prepare release
/release-prep v1.2.0

# Start incident response
/incident-start SEV2 "Description"

# Create GitHub issues (optionally assign to Copilot)
/sdlc-create-issues --assign-copilot

# View consolidated GitHub dashboard (v1.6.0)
/github-dashboard

# Sync documentation with GitHub Wiki (v1.6.0)
/wiki-sync
```

## Architecture

### Configuration-Driven Design
All behavior is defined in `.claude/settings.json`, which configures:
- 36 agents organized by SDLC phase (32 orchestrated + 4 consultive)
- Git hooks for validation and automation
- Quality gates between phases (including Security Gate)
- Complexity levels (0-3) that determine which phases are executed
- Security by Design with mandatory gates and escalation triggers

### Directory Structure
```
.claude/
├── agents/           # Agent specs (markdown) - 36 specialized roles
├── skills/           # Reusable capabilities with scripts
│   └── gate-evaluator/gates/  # YAML quality gate definitions (including security-gate.yml)
├── commands/         # Slash commands for user interaction
├── hooks/            # Git automation (validate-commit, auto-branch, etc.)
├── lib/              # Shared libraries (v1.7.0)
│   ├── python/       # sdlc_logging.py, sdlc_tracing.py
│   └── shell/        # logging_utils.sh
├── config/           # Centralized configuration (v1.7.0)
│   └── logging/      # logging.yml, dashboards/
└── settings.json     # Central configuration

.agentic_sdlc/        # SDLC artifacts and project state (NEW)
├── projects/         # Project-specific artifacts
├── references/       # External reference documents (legal, technical, business)
├── templates/        # Reusable templates (ADR, spec, threat-model)
├── corpus/           # RAG knowledge corpus
└── sessions/         # Session history

.docs/                # User documentation and playbook
.scripts/             # Installation automation
```

### Phase Flow
```
Phase 0 (Preparation)    → intake-analyst, compliance-guardian
Phase 1 (Discovery)      → domain-researcher, doc-crawler, rag-curator
Phase 2 (Requirements)   → product-owner, requirements-analyst, ux-writer
Phase 3 (Architecture)   → system-architect, adr-author, data-architect, threat-modeler, iac-engineer
Phase 4 (Planning)       → delivery-planner
Phase 5 (Implementation) → code-author, code-reviewer, test-author, iac-engineer
Phase 6 (Quality)        → qa-analyst, security-scanner, performance-analyst
Phase 7 (Release)        → release-manager, cicd-engineer, change-manager, doc-generator
Phase 8 (Operations)     → incident-commander, rca-analyst, metrics-analyst, observability-engineer
```

### Cross-Phase Agents (Meta-Agents)

Two agents operate across all phases and are not tied to a specific phase:

| Agent | Purpose | When Activated |
|-------|---------|----------------|
| **orchestrator** | Coordinates phase transitions, manages workflow state, evaluates gates | Automatically during `/sdlc-start`, phase transitions |
| **playbook-governance** | Monitors drift from playbook, detects emerging patterns, proposes updates | When exceptions occur, during retrospectives |

These agents act as supervisors ensuring consistency and continuous improvement across the entire SDLC.

### Complexity Levels
- **Level 0 (Quick Flow)**: Bug fixes, typos → Phases 5, 6 only → Use `/quick-fix`
- **Level 1 (Feature)**: Simple features → Phases 2, 5, 6 → Use `/new-feature`
- **Level 2 (BMAD Method)**: New product/service → Phases 0-7 → Use `/sdlc-start`
- **Level 3 (Enterprise)**: Compliance-critical → All phases + human approval at every gate

### Security by Design
Security is mandatory in phases 2, 3, 5, 6, 7 via `security-gate.yml`:
- Phase 2: Security requirements documented
- Phase 3: Threat model (STRIDE) required, HIGH/CRITICAL risks mitigated
- Phase 5: No hardcoded secrets, input validation
- Phase 6: SAST/SCA executed, no critical/high vulnerabilities
- Phase 7: Security checklist complete

**Escalation Triggers** (auto-escalate to security team):
- CVSS >= 7.0
- PII exposure
- Auth/authorization changes
- Cryptography changes
- New public endpoints

### Agent Model Selection

Agents use different models based on task complexity:

| Model | Use Case | Agents |
|-------|----------|--------|
| **opus** | Complex decisions, architecture, security analysis | system-architect, threat-modeler, compliance-guardian |
| **sonnet** | Implementation, documentation, routine tasks | code-author, doc-generator, test-author, most others |

**Heuristic**: Use `opus` when the agent needs deep reasoning, trade-off analysis, or security-critical decisions. Use `sonnet` for execution-focused tasks.

### Agent Types

| Type | Count | Description |
|------|-------|-------------|
| **Orchestrated** | 30 | Full agents with 200-500 lines, complete instructions |
| **Consultive (Lightweight)** | 4 | Minimal agents (~20 lines) that delegate to skills |

**Lightweight agents**: `failure-analyst`, `interview-simulator`, `requirements-interrogator`, `tradeoff-challenger`. These are intentionally minimal and rely on the `system-design-decision-engine` skill for their logic.

## Key Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Central configuration for agents, phases, gates, hooks |
| `.claude/skills/gate-evaluator/gates/*.yml` | Quality gate definitions per phase transition |
| `.claude/skills/gate-evaluator/gates/security-gate.yml` | Security by Design gate (mandatory) |
| `.agentic_sdlc/templates/*.yml` | Templates for ADR, spec, threat-model |
| `.docs/playbook.md` | Development principles, standards, and practices |
| `.docs/engineering-playbook/manual-desenvolvimento/` | Development standards and guidelines |
| `.claude/lib/python/sdlc_logging.py` | Python logging module with Loki handler (v1.7.0) |
| `.claude/lib/shell/logging_utils.sh` | Shell logging functions (v1.7.0) |
| `.claude/config/logging/logging.yml` | Centralized logging configuration (v1.7.0) |

## Hook System

Hooks are triggered automatically:
- `PreToolUse`: Validates commits, checks gates before push, updates project timestamp
- `PostToolUse`: Formats Python files with black, reminds about ADR updates
- `UserPromptSubmit`: Detects current SDLC phase, detects documents in project (v1.3.0)

### Available Hooks
| Hook | Purpose |
|------|---------|
| `validate-commit.sh` | Validates commit messages and content |
| `check-gate.sh` | Verifies quality gate before push |
| `auto-branch.sh` | Creates branches automatically (fix/, feature/, hotfix/, release/) |
| `update-project-timestamp.sh` | Updates project manifest with real UTC timestamp |
| `detect-phase.sh` | Detects current SDLC phase from context |
| `ensure-feature-branch.sh` | Verifies proper branch before creating files (v1.2.0) |
| `auto-migrate.sh` | Migrates artifacts from `.claude/memory` to `.agentic_sdlc` (v1.2.0) |
| `phase-commit-reminder.sh` | Reminds to commit after passing a gate (v1.2.0) |
| `detect-documents.sh` | Detects PDF/XLSX/DOCX files and suggests document-processor (v1.3.0) |
| `auto-graph-sync.sh` | Updates semantic graph when corpus nodes are modified (v1.4.0) |
| `auto-decay-recalc.sh` | Recalculates decay scores periodically (v1.5.0) |
| `track-rag-access.sh` | Tracks access patterns on RAG queries (v1.5.0) |

**Note:** All hooks use structured logging via `logging_utils.sh` (v1.7.0) with skill and phase context.

## Integrations

- **GitHub Copilot Coding Agent**: Issues can be assigned to `@copilot` for automatic implementation
- **Spec Kit**: `specify` CLI for specification-driven development
- **GitHub CLI**: `gh` for repository operations
- **GitHub Projects V2**: Automatic project management via GraphQL (v1.6.0)
- **GitHub Milestones**: Sprint tracking and release coordination (v1.6.0)
- **GitHub Wiki**: Documentation synchronization via Git (v1.6.0)

## Skills

Available skills for automation:

| Skill | Purpose |
|-------|---------|
| `gate-evaluator` | Evaluates quality gates between phases |
| `memory-manager` | Manages project context and state persistence |
| `rag-query` | Queries the RAG knowledge corpus |
| `spec-kit-integration` | Integrates with GitHub Spec Kit |
| `bmad-integration` | Integrates with BMAD Method for complexity scaling |
| `auto-branch` | Automatic branch creation based on work type |
| `iac-generator` | Generates Infrastructure as Code (Terraform, Bicep, K8s) |
| `doc-blueprint` | Generates documentation blueprints (README, API, Architecture) |
| `reference-indexer` | Indexes external reference documents for RAG |
| `phase-commit` | Commits artifacts at the end of each phase (v1.2.0) |
| `session-analyzer` | Extracts learnings from Claude Code sessions (v1.2.0) |
| `document-processor` | Processes PDF, XLSX, DOCX documents for requirements extraction (v1.3.0) |
| `frontend-testing` | E2E testing with Playwright, screenshots, browser logs (v1.3.0) |
| `graph-navigator` | Semantic graph navigation, concept extraction, visualization (v1.4.0) |
| `decay-scoring` | Temporal scoring for knowledge freshness, curation triggers (v1.5.0) |
| `github-sync` | Base skill for GitHub synchronization: issues, labels, milestones (v1.6.0) |
| `github-projects` | GitHub Projects V2 management via GraphQL API (v1.6.0) |
| `github-wiki` | GitHub Wiki synchronization via Git (v1.6.0) |
| `parallel-workers` | Parallel task execution using git worktrees (v2.0) |
| `doc-generator` | Generates CLAUDE.md and README.md with SDLC Agêntico signature (v1.8.1) |

## New Skills (v2.0) - Claude Orchestrator Integration

### parallel-workers

Executes Phase 5 (Implementation) tasks in parallel using isolated git worktrees.

**Key Features:**
- **2.5x speedup** for parallel tasks (3 workers)
- **Zero merge conflicts** (isolated worktrees)
- **Platform independent** (Linux-first, no macOS dependencies)
- **Automated monitoring** via automation loop
- **Full observability** (Loki/Grafana integration)

**Usage:**
```bash
# Spawn single worker
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn \
  --task-id "TASK-001" \
  --description "Implement authentication" \
  --agent "code-author"

# Spawn batch from spec
python3 .claude/skills/parallel-workers/scripts/worker_manager.py spawn-batch \
  --spec-file tasks.yml

# Start automation loop (monitors all workers)
python3 .claude/skills/parallel-workers/scripts/loop.py
```

**Worker State Machine:**
```
NEEDS_INIT → WORKING → PR_OPEN → MERGED
     ↑                     ↓
     └─────────ERROR───────┘
```

**Components:**
- `worker_manager.py` - Lifecycle management
- `state_tracker.py` - State persistence
- `worktree_manager.sh` - Git worktree operations
- `loop.py` - Automation loop (5s polling)

**Storage:**
- Worker state: `~/.claude/worker-states/*.json`
- Worktrees: `~/.worktrees/{project}/{task-id}/`

**See:** `.claude/skills/parallel-workers/README.md`

### simple-memory (memory-manager v2.0)

Lightweight JSON-based working memory complementing RAG corpus.

**Architecture:**
```
┌───────────────────┐         ┌───────────────────┐
│  Simple Store     │         │   RAG Corpus      │
│  (Working Memory) │◄───────►│   (Long-term)     │
│                   │         │                   │
│ • Facts (JSON)    │         │ • ADRs (YAML)     │
│ • Toolchain       │         │ • Learnings       │
│ • Repos           │         │ • Patterns        │
│ • Quick context   │         │ • Decisions       │
│                   │         │                   │
│ Fast, ephemeral   │         │ Indexed, durable  │
└───────────────────┘         └───────────────────┘
```

**Usage:**
```bash
# Remember quick facts
python3 .claude/skills/memory-manager/scripts/simple_store.py add-fact \
  "API rate limit is 1000 req/min" \
  --tags rate-limit api

# Recall facts
python3 .claude/skills/memory-manager/scripts/simple_store.py recall "rate limit"

# Add tool reference
python3 .claude/skills/memory-manager/scripts/simple_store.py add-tool gh \
  --repo "https://github.com/cli/cli" \
  --version "2.40.0"

# Search all memory
python3 .claude/skills/memory-manager/scripts/simple_store.py search "database"
```

**When to Use:**
- **Simple Store**: Quick facts, tool refs, working context (< 1 day)
- **RAG Corpus**: Architecture decisions, learnings, patterns (forever)

**Storage:** `~/.claude/simple-memory/`

**See:** `.claude/skills/memory-manager/README.md`

### session-handoff (session-analyzer v2.0)

Generates session handoff summaries for cross-session continuity.

**Output Structure:**
```markdown
# Session Summary: YYYY-MM-DD - repository

## Completed
- [tasks completed]

## Pending
- [tasks pending]

## Context for Next Session
- Phase, files modified, tools used, decisions, blockers
```

**Usage:**
```bash
# Generate handoff for latest session
python3 .claude/skills/session-analyzer/scripts/handoff.py

# Specify project
python3 .claude/skills/session-analyzer/scripts/handoff.py --project /path/to/project
```

**Automatic Generation:**
- **Hook**: `session-analyzer.sh` invokes after gate-check
- **Timing**: End of each SDLC phase
- **Output**: `.agentic_sdlc/sessions/YYYYMMDD-HHMMSS-{repo}.md`

**See:** `.claude/skills/session-analyzer/SKILL.md`

**ADR:** `.agentic_sdlc/corpus/nodes/decisions/ADR-claude-orchestrator-integration.yml`
**Analysis:** `.agentic_sdlc/corpus/nodes/learnings/LEARN-claude-orchestrator-patterns.yml`
**Epic:** Issue #33
**Tasks:** Issues #35 (parallel-workers), #36 (simple-memory), #37 (session-handoff), #34 (automation-loop)

## New Skills (v1.3.0) - Document Processing & Frontend Testing

### document-processor

Processes enterprise documents with production-grade quality:

```bash
# Extract text/tables from documents
/doc-extract requirements.pdf
/doc-extract financials.xlsx
/doc-extract spec.docx

# Validate document integrity
/doc-validate report.xlsx  # Check Excel formulas
/doc-validate contract.docx  # Check formatting
```

**Features:**
- PDF extraction with OCR support for scanned documents
- Excel formula validation using LibreOffice headless
- Word tracked changes detection (OOXML parsing)
- Zero-error policy for generated documents

**Dependencies (optional):**
```bash
./.scripts/setup-sdlc.sh --install-optional
# Or manually: pip install pdfplumber openpyxl python-docx
# System: apt install poppler-utils tesseract-ocr libreoffice
```

### frontend-testing

E2E testing for web applications using Playwright:

```bash
# Run E2E tests
/frontend-test http://localhost:3000

# Capture screenshots
/frontend-screenshot http://localhost:3000 homepage

# Health check
/frontend-check http://localhost:3000
```

**Features:**
- Reconnaissance-then-action pattern
- Server lifecycle management (with_server.py)
- Console error capture and reporting
- Integration with qa-analyst for Phase 6

**Dependencies (optional):**
```bash
pip install playwright pytest-playwright
playwright install chromium
```

### Design Patterns (from Anthropic Skills)

These skills implement patterns extracted from official Anthropic skills:

| Pattern | Description |
|---------|-------------|
| **Validation-First** | Separate creation from validation, collect ALL errors before reporting |
| **Multi-Tool Strategy** | Python for processing, Node.js for creation, CLI for validation |
| **Zero-Error Policy** | Generated documents must have zero errors |
| **Reconnaissance-Then-Action** | Discover DOM selectors, never hardcode |

Patterns documented at: `.agentic_sdlc/corpus/patterns/anthropic-skills-patterns.md`

### Skill Integration with Agents (v1.3.0)

Skills are automatically available to agents based on their phase:

| Agent | Skills | Phase |
|-------|--------|-------|
| `intake-analyst` | document-processor | 0 |
| `domain-researcher` | document-processor | 1 |
| `requirements-analyst` | document-processor | 2 |
| `qa-analyst` | frontend-testing | 6 |

**Quality Gates with Frontend Testing:**
- Phase 5→6: `frontend_build_passing` (conditional)
- Phase 6→7: `frontend_e2e_pass_rate`, `frontend_console_error_count` (conditional)

All frontend checks are conditional (`has_frontend`) and only applied when project has frontend code.

## New Skills (v1.9.0) - Document Enrichment

### document-enricher

Automatically enriches existing reference documents with research findings:

```bash
# Search for related documents
/doc-search OAuth 2.1 migration

# Manually enrich document
/doc-enrich DOC-001 research.json
```

**Features:**
- Hybrid search for document matching (keyword + text + category similarity)
- Automatic enrichment during research phases
- Versioned enriched documents (`.enriched.v1.md`, `.enriched.v2.md`)
- Immutable original documents
- Knowledge graph integration with 'enriches' relations
- Quality gate validation (`enrichment-quality.yml`)

**How It Works:**
1. **Step 0** (new in research agents): Check for related documents
2. If similarity > 0.6: Extract original content
3. Execute research (web, academic, community)
4. Merge original + research findings
5. Create `.enriched.vN.md` + `ENRICH-{id}.yml` corpus node
6. Update graph with 'enriches' relation

**Enriched Document Format:**
```markdown
# {Title} - Enhanced Research Edition

**Original Document**: `{path}`
**Research Topic**: {topic}
**Version**: v{n}

## Original Content Summary
{original}

## Research Findings
{research}

### Sources
- [{title}]({url}) - Accessed {date}

## Synthesis
{combined_analysis}
```

**Modified Agents (v1.9.0):**
All research agents now include "Step 0: Check for Related Documents":
- `domain-researcher` - Research academic/web sources
- `doc-crawler` - Extract and index documentation
- `requirements-analyst` - Analyze requirements
- `adr-author` - Document architecture decisions
- `threat-modeler` - Model security threats

**Quality Gates:**
- `enrichment_has_sources`: Research findings must cite sources
- `original_preserved`: Original document unchanged (hash check)
- `graph_relation_created`: Graph contains 'enriches' relation
- `enrichment_version_incremented`: Versions increment sequentially

**See:** `.docs/enrichment-guide.md` - Complete user guide

## New Skills (v1.4.0) - Semantic Knowledge Graph

### graph-navigator

Navigate and query the semantic knowledge graph:

```bash
# Build graph from corpus
python3 .claude/skills/graph-navigator/scripts/graph_builder.py --infer

# Search with graph expansion
python3 .claude/skills/rag-query/scripts/hybrid_search.py "database" --mode hybrid

# Find related decisions
python3 .claude/skills/graph-navigator/scripts/graph_manager.py neighbors ADR-001 --hops 2

# Find path between decisions
python3 .claude/skills/graph-navigator/scripts/graph_manager.py path ADR-001 ADR-010

# Generate visualization
python3 .claude/skills/graph-navigator/scripts/graph_visualizer.py --format mermaid

# Extract concepts from documents
python3 .claude/skills/graph-navigator/scripts/concept_extractor.py --output save
```

**Features:**
- Hybrid search combining text + graph traversal
- Multi-hop neighbor queries (find related nodes)
- Shortest path between nodes
- Transitive closure (all dependencies)
- Concept extraction with confidence scores
- Mermaid diagram generation
- DOT format export for Graphviz

**Semantic Relations:**
| Relation | Meaning |
|----------|---------|
| `supersedes` | Replaces previous decision |
| `implements` | Implements a pattern |
| `addresses` | Addresses a requirement |
| `dependsOn` | Depends on another decision |
| `relatedTo` | Generic bidirectional relation |
| `isA` | Concept hierarchy |

**Corpus Structure (v1.4.0):**
```
.agentic_sdlc/corpus/
├── nodes/                  # Reorganized node storage
│   ├── decisions/          # ADRs
│   ├── learnings/          # Lessons learned
│   ├── patterns/           # Design patterns
│   └── concepts/           # Extracted concepts
├── graph.json              # Semantic graph
├── adjacency.json          # Fast traversal index
├── index.yml               # Text search index
└── schema/context.json     # Relation definitions
```

**Quality Gate:**
- `graph-integrity.yml` validates graph structure before release
- Checks for orphan edges, valid relations, coverage thresholds

## New Skill (v1.5.0) - Decay Scoring

### decay-scoring

Sistema de pontuacao temporal para nodes de conhecimento do corpus RAG:

```bash
# Calculate decay scores for all nodes
python3 .claude/skills/decay-scoring/scripts/decay_calculator.py

# Update node files with scores
python3 .claude/skills/decay-scoring/scripts/decay_calculator.py --update-nodes

# Generate curation report
python3 .claude/skills/decay-scoring/scripts/decay_trigger.py

# Record node validation
python3 .claude/skills/decay-scoring/scripts/decay_tracker.py validate NODE_ID

# Track node access
python3 .claude/skills/decay-scoring/scripts/decay_tracker.py access NODE_ID
```

**Decay Algorithm:**
```
decay_score = 0.40 * age_score + 0.30 * validation_score + 0.20 * access_score + 0.10 * type_bonus
```

**Score Thresholds:**
| Score | Status | Action |
|-------|--------|--------|
| 0.70-1.00 | `fresh` | No action |
| 0.40-0.69 | `aging` | Consider validation |
| 0.20-0.39 | `stale` | Review recommended |
| 0.00-0.19 | `obsolete` | Curation required |

**Features:**
- Exponential decay based on content age
- Validation tracking with history
- Access frequency monitoring
- Content type stability multipliers
- Automatic curation suggestions
- Search results boosted by freshness

**Slash Commands:**
- `/decay-status` - Show corpus decay health and review queue
- `/validate-node NODE_ID` - Mark node as validated/current

**Quality Gate:**
- `decay-health-gate.yml` validates corpus health before releases
- Blocks if average score < 0.5 or too many obsolete nodes

**Node Schema Addition:**
```yaml
decay_metadata:
  last_validated_at: "2025-01-14T10:00:00Z"
  last_accessed_at: "2025-01-14T08:30:00Z"
  access_count_30d: 5
  decay_score: 0.85
  decay_status: fresh
```

## New Skills (v1.6.0) - GitHub Integration

### github-sync

Base skill for GitHub synchronization:

```bash
# Ensure SDLC labels exist
python3 .claude/skills/github-sync/scripts/label_manager.py ensure

# Create milestone for sprint
python3 .claude/skills/github-sync/scripts/milestone_sync.py create \
  --title "Sprint 1" \
  --description "MVP delivery" \
  --due-date "2026-01-28"

# Create issue with SDLC labels
python3 .claude/skills/github-sync/scripts/issue_sync.py create \
  --title "[TASK-001] Implement feature" \
  --phase 5 \
  --type task \
  --milestone "Sprint 1"
```

**Features:**
- Automatic SDLC label management (`phase:0-8`, `complexity:0-3`, `type:*`)
- Milestone CRUD operations
- Issue creation with automatic labeling
- Integration with `/sdlc-create-issues`

### github-projects

GitHub Projects V2 management via GraphQL:

```bash
# Create project
python3 .claude/skills/github-projects/scripts/project_manager.py create "SDLC: Feature X"

# Configure custom fields
python3 .claude/skills/github-projects/scripts/project_manager.py configure-fields --project-number 1

# Add issue to project
python3 .claude/skills/github-projects/scripts/project_manager.py add-item \
  --project-number 1 \
  --issue-url "https://github.com/owner/repo/issues/123"

# Update field value
python3 .claude/skills/github-projects/scripts/project_manager.py update-field \
  --project-number 1 \
  --item-id ITEM_ID \
  --field "Phase" \
  --value "In Progress"
```

**Features:**
- Project V2 creation and configuration
- Custom fields: Phase, Priority, Story Points
- SDLC Kanban columns (Backlog → Done)
- Item management and field updates

### github-wiki

GitHub Wiki synchronization:

```bash
# Full sync
.claude/skills/github-wiki/scripts/wiki_sync.sh

# Dry run
.claude/skills/github-wiki/scripts/wiki_sync.sh --dry-run

# Publish specific ADR
.claude/skills/github-wiki/scripts/publish_adr.sh path/to/adr.yml

# Publish all ADRs
.claude/skills/github-wiki/scripts/publish_adr.sh --all
```

**Features:**
- Automatic Home and Sidebar generation
- ADR YAML to Markdown conversion
- Project documentation sync
- Git-based (no API required)

**Slash Commands:**
- `/github-dashboard` - Consolidated project status
- `/wiki-sync` - Manual Wiki synchronization

**Automatic Integration:**
- Phase 0: Creates Project V2 + Milestone
- Phase transitions: Updates Project fields
- Phase 7: Closes Milestone + Syncs Wiki

## New Skills (v1.8.1) - Documentation Generation

### doc-generator

Automatically generates professional documentation for projects by analyzing the codebase:

```bash
# Generate CLAUDE.md and README.md
/doc-generate

# Or run script directly
python3 .claude/skills/doc-generator/scripts/generate_docs.py

# Force overwrite existing files
python3 .claude/skills/doc-generator/scripts/generate_docs.py --force

# Generate in specific directory
python3 .claude/skills/doc-generator/scripts/generate_docs.py --output-dir /path/to/project
```

**What it Generates:**
- `CLAUDE.md` - Guidance for Claude Code with tech stack, architecture, directory structure, development workflow
- `README.md` - Project documentation with features, tech stack, getting started, usage, deployment
- **SDLC Agêntico Signature** - Both files include: `🤖 Generated with SDLC Agêntico by @arbgjr`

**Automatic Detection:**
- **Languages**: Python, JavaScript, TypeScript, Java, C#, Go, Rust, Ruby (by file extensions)
- **Frameworks**: Django, Flask, FastAPI, React, Next.js, Vue, Angular, Express, .NET, Maven, Gradle
- **Project Structure**: Directory tree (max 3 levels, excludes node_modules, .git, venv, etc.)
- **Tests**: Test files and directories (pytest, jest, mocha patterns)
- **Docker**: Dockerfile presence
- **CI/CD**: GitHub Actions workflows

**Language-Specific Commands:**
The generator provides smart defaults based on detected stack:

| Stack | Install | Run | Test |
|-------|---------|-----|------|
| **Python/Django** | `pip install -r requirements.txt` | `python manage.py runserver` | `pytest` |
| **Python/Flask** | `pip install -r requirements.txt` | `python main.py` | `pytest` |
| **Node.js/React** | `npm install` | `npm start` | `npm test` |
| **Java/Maven** | `mvn install` | - | `mvn test` |

**Integration with Orchestrator:**
- **Phase 0 (Intake)**: Generate initial docs for new projects
- **Phase 7 (Release)**: Update docs before release with latest stack changes
- **On-Demand**: Via `/doc-generate` command anytime

**Template Customization:**
Templates are located in `.claude/skills/doc-generator/templates/`:
- `CLAUDE.md.template` - Claude Code guidance template
- `README.md.template` - Project README template

Use `{{placeholder}}` syntax for variable substitution. Generated docs are starting points - always review and enhance with project-specific details.

**Post-Generation Workflow:**
1. Review generated files for accuracy
2. Customize placeholders (features list, usage examples)
3. Add project-specific architecture diagrams or API docs
4. Commit with: `docs: generate CLAUDE.md and README.md with SDLC signature`

## New Agents (v2.0)

| Agent | Phase | Purpose |
|-------|-------|---------|
| `iac-engineer` | 3, 5 | Generates and maintains Infrastructure as Code |
| `doc-generator` | 7 | Generates technical documentation automatically |

## Observability (v1.7.0)

### Logging Infrastructure

The project includes structured logging integrated with the observability stack:

| Component | Port | Purpose |
|-----------|------|---------|
| **Loki** | 3100 | Log aggregation |
| **Tempo** | 4318 | Distributed tracing (OTLP) |
| **Grafana** | 3003 | Visualization and dashboards |

### Python Logging

```python
import sys
sys.path.insert(0, '.claude/lib/python')
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="decay-scoring", phase=6)
logger.info("Processing node", extra={"node_id": "ADR-001"})

# Timed operations
with log_operation(logger, "batch_processing"):
    process_batch()
```

### Shell Logging

```bash
source .claude/lib/shell/logging_utils.sh
sdlc_set_context skill="git-hooks" phase="5"
sdlc_log_info "Validating commit" "commit_hash=$COMMIT_HASH"
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SDLC_LOG_LEVEL` | DEBUG | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `SDLC_LOKI_ENABLED` | true | Enable Loki log shipping |
| `SDLC_LOKI_URL` | http://localhost:3100 | Loki Push API URL |
| `SDLC_TRACE_ENABLED` | false | Enable OpenTelemetry tracing |
| `SDLC_TEMPO_URL` | http://localhost:4318 | Tempo OTLP endpoint |
| `SDLC_JSON_LOGS` | false | Force JSON output to console |

### Loki Labels

All logs are tagged with:
- `app`: sdlc-agentico
- `env`: development/production
- `level`: debug/info/warning/error/critical
- `skill`: Name of the skill or hook
- `phase`: SDLC phase number (0-8)
- `script`: Script filename

### Grafana Dashboard

Import `.claude/config/logging/dashboards/sdlc-overview.json` into Grafana for:
- Log Volume by Level (timeseries)
- Errors by Skill (bar gauge)
- Activity by SDLC Phase (stat)
- Gate Evaluations (logs panel)
- Security Events (logs panel)
- Live Logs with JSON parsing

## Development Playbook Principles

1. **Quality is responsibility of who creates** - Tests, observability, clarity are part of delivery
2. **Small changes preferred** - Reduce risk, facilitate review
3. **Decisions must be recorded** - As ADRs when affecting maintenance, scale, or cost
4. **Observability is part of delivery** - Nothing ships without being observable
5. **System design required when** - Changing boundaries, integrations, data, or NFRs
6. **Security by Design** - Security is not a feature, it's a fundamental requirement

---

## Release Checklist

**CRITICAL**: Before creating any release tag, ALL these items MUST be verified and updated:

### 1. Version Files Update

**Files that MUST be updated with new version:**

- [ ] `.claude/VERSION` - Update `version:` and `build_date:` fields
  ```yaml
  version: "X.Y.Z"  # ← UPDATE THIS
  build_date: "YYYY-MM-DD"  # ← UPDATE THIS
  ```

- [ ] `.claude/VERSION` - Add new changelog entry at the TOP
  ```yaml
  changelog:
    - version: "X.Y.Z"  # ← ADD NEW ENTRY HERE
      date: "YYYY-MM-DD"
      changes:
        - "feat: Description"
  ```

### 2. README.md Updates

**Files that MUST be updated:**

- [ ] **README.md Line 3** - Version badge
  ```markdown
  [![Version](https://img.shields.io/badge/version-X.Y.Z-red.svg)](https://github.com/arbgjr/sdlc_agentico/releases/tag/vX.Y.Z)
  ```

- [ ] **README.md Line 41** - ASCII art header
  ```
  │                         SDLC AGÊNTICO vX.Y.Z                            │
  ```

- [ ] **README.md Lines 44-56** - Feature timeline (add new version line if major feature)
  ```
  │  Feature Name | Description | Component Name (vX.Y.Z)        │
  ```

- [ ] **README.md Line 75** - Installation example VERSION variable
  ```bash
  VERSION="vX.Y.Z"  # ← UPDATE THIS
  ```

- [ ] **README.md Line 96** - Script installation example
  ```bash
  --version vX.Y.Z  # ← UPDATE THIS
  ```

### 3. Skill/Module Versions (if applicable)

If releasing a new skill or major skill update:

- [ ] Update skill `SKILL.md` metadata:
  ```yaml
  version: X.Y.Z  # Skill version
  ```

- [ ] Update skill README.md references
- [ ] Update IMPLEMENTATION_SUMMARY.md (if exists)

### 4. Pre-Release Verification

**Before creating tag:**

- [ ] Run all tests: `pytest .claude/skills/*/tests/ -v`
- [ ] Verify no uncommitted changes: `git status`
- [ ] Verify current branch is `main`: `git branch --show-current`
- [ ] Pull latest changes: `git pull origin main`
- [ ] Check last commit includes version updates: `git log -1`

### 5. Tag Creation

**Create annotated tag with proper message:**

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z - Feature Name

Brief description of release.

Features:
- Feature 1
- Feature 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Push tag:**

```bash
git push origin vX.Y.Z
```

### 6. Release Automation

**The GitHub Action will automatically:**

- ✅ Create draft release
- ✅ Generate `.tar.gz` and `.zip` packages
- ✅ Attach assets to release

**You MUST manually:**

- [ ] Edit draft release on GitHub
- [ ] Update release notes (copy from tag message or enhance)
- [ ] Mark as "Latest Release"
- [ ] Publish release (remove draft status)

### 7. Post-Release Verification

**After publishing release:**

- [ ] Verify release is marked as "Latest": `gh release list | head -1`
- [ ] Verify assets were uploaded: `gh release view vX.Y.Z`
- [ ] Test installation from release:
  ```bash
  curl -fsSL "https://github.com/arbgjr/sdlc_agentico/releases/download/vX.Y.Z/sdlc-agentico-vX.Y.Z.tar.gz" | tar -tzf - | head
  ```
- [ ] Check badges in README.md are working (visit GitHub repo page)

### 8. Common Mistakes to Avoid

❌ **DO NOT:**
- Create tag before updating `.claude/VERSION`
- Forget to update README.md badges and examples
- Use version numbers that don't match git tag
- Skip updating changelog in `.claude/VERSION`
- Reference non-existent release URLs in README
- Create release without proper tag message

✅ **ALWAYS:**
- Update ALL version references in one commit BEFORE tagging
- Use semantic versioning (major.minor.patch)
- Add Co-Authored-By line in tag messages
- Test release package before announcing
- Update feature timeline in README for major features

### 9. Release Types

**Version Numbering Guide:**

- **Major (X.0.0)**: Breaking changes, major architecture changes
- **Minor (x.Y.0)**: New features, new skills, significant enhancements
- **Patch (x.y.Z)**: Bug fixes, documentation updates, minor improvements

**Examples:**
- v1.8.0 → v1.8.1: Bug fix (patch)
- v1.8.1 → v1.9.0: New skill added (minor)
- v1.9.0 → v2.0.0: Breaking changes to SDLC workflow (major)

### 10. Rollback Procedure

**If release has critical issues:**

```bash
# 1. Delete release
gh release delete vX.Y.Z --yes

# 2. Delete tag locally and remotely
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# 3. Fix issues in new commit
git add .
git commit -m "fix: critical issue"

# 4. Create new patch version (X.Y.Z+1)
# Follow checklist from step 1
```

---

## Version History Quick Reference

**Current Version**: v1.8.1 (Auto-Update System)

**Recent Releases**:
- v1.8.1 (2026-01-23): Auto-Update System with impact analysis
- v1.7.16 (2026-01-17): Phase Commit Automation
- v1.7.0 (2026-01-16): Structured Logging with Loki/Tempo/Grafana
- v1.6.0 (2026-01-15): GitHub Projects V2 Integration
- v1.5.0 (2026-01-14): Decay Scoring System
- v1.4.0 (2026-01-13): Semantic Knowledge Graph

**Update this list with each new release.**
