# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDLC Agêntico is an AI-driven Software Development Lifecycle framework that orchestrates **34 specialized agents (30 orchestrated + 4 consultive)** through **9 development phases (0-8)**. This is a **configuration and orchestration framework**, not a traditional application codebase.

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
- 34 agents organized by SDLC phase (30 orchestrated + 4 consultive)
- Git hooks for validation and automation
- Quality gates between phases (including Security Gate)
- Complexity levels (0-3) that determine which phases are executed
- Security by Design with mandatory gates and escalation triggers

### Directory Structure
```
.claude/
├── agents/           # Agent specs (markdown) - 34 specialized roles
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
| `.docs/DESENVOLVIMENTO.md` | C# development standards and guidelines |
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
