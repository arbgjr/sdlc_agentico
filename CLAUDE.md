# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Major Rules

- **This project is natural language first** - All agents, skills, and orchestration logic MUST be implemented using natural language (English) in markdown files. Programming languages are ONLY allowed as a last resort for:
  - External service connectors (APIs, databases, file systems)
  - Performance-critical operations
  - System-level integrations that cannot be expressed in natural language
- This project is compatible with linux and windows
- Always follow the **Anti-Mock Policy** (CRITICAL)

## Project Overview

SDLC Agêntico is an AI-driven Software Development Lifecycle framework that orchestrates **45 specialized agents** through **9 development phases (0-8)**. This is a **configuration and orchestration framework**, not a traditional application codebase.

**Current Version**: v3.0.4 (GitHub Integration Hotfix)

## Anti-Mock Policy (CRITICAL)

**Absolutely prohibited** in production code:

- Mock/stub/fake/dummy implementations of external services or MCP
- Hardcoded test data or pattern-based bypasses
- Keywords: `mock|stub|fake|dummy|simulator|emulator|inmemory`
- Placeholders: `lorem`, `foo`, `bar`, `TODO`, `TBD`

Test doubles are **ONLY** allowed in `tests/` directories.

When services are unavailable, use resilience patterns: timeout, retry, circuit breaker, or return `503 Service Unavailable` with `x-correlation-id`.

## Setup and Workflow Commands

```bash
# Setup
./.agentic_sdlc/scripts/setup-sdlc.sh

# Workflow
/sdlc-start "Description"      # Full SDLC (Level 2/3)
/quick-fix "Bug description"   # Quick fix (Level 0)
/new-feature "Feature name"    # Feature flow (Level 1)
/phase-status                  # Check phase status
/gate-check phase-2-to-3       # Verify quality gate
/adr-create "Decision title"   # Create ADR
/security-scan                 # Run security scan
/release-prep v1.2.0           # Prepare release
/sdlc-create-issues            # Create GitHub issues
/github-dashboard              # View project status
/wiki-sync                     # Sync documentation
```

## Architecture

### Configuration-Driven Design

All behavior is defined in `.claude/settings.json`:

- 45 agents organized by SDLC phase
- Git hooks for validation and automation
- Quality gates between phases (including Security Gate)
- Complexity levels (0-3) that determine phase execution
- Security by Design with mandatory gates

### Directory Structure

```
.claude/
├── agents/           # Agent specs (markdown) - 45 specialized roles
├── skills/           # Reusable capabilities with scripts
├── commands/         # Slash commands
├── hooks/            # Git automation
├── lib/              # Shared libraries (Python/Shell)
├── config/           # Centralized configuration
└── settings.json     # Central configuration

.agentic_sdlc/        # Framework artifacts (APENAS este repo)
├── corpus/           # Knowledge corpus
│   ├── nodes/        # decisions/, learnings/, patterns/, concepts/
│   ├── graph.json    # Semantic knowledge graph
│   └── index.yml     # Text search index
├── references/       # Reference documents
├── sessions/         # Session history
├── templates/        # Templates (ADR, spec, threat-model)
├── scripts/          # Installation automation
└── docs/             # User documentation

.project/             # Project artifacts (TODOS comandos gravam aqui)
├── corpus/           # ADRs inferidos via reverse engineering
├── architecture/     # Auto-generated diagrams
├── security/         # Threat models
├── reports/          # Tech debt reports
└── sessions/         # Session history
```

### Output Directory Configuration (CRITICAL)

**REGRA DE OURO:**

| Setting | Quando Usar | Onde Grava |
|---------|-------------|------------|
| `project_artifacts_dir` | **SEMPRE** - Qualquer comando em qualquer projeto | `.project/` (default) |
| `framework_artifacts_dir` | **APENAS** quando desenvolvendo o próprio framework (este repo) | `.agentic_sdlc/` |

**Configuration in `.claude/settings.json`:**

```json
{
  "sdlc": {
    "output": {
      "project_artifacts_dir": ".project",        // TODOS comandos gravam aqui
      "framework_artifacts_dir": ".agentic_sdlc"  // APENAS artefatos DO framework
    }
  }
}
```

**Priority Order:**

1. `.claude/settings.json` → `sdlc.output.project_artifacts_dir`
2. `import_config.yml` → `general.output_dir` (fallback, deprecated)
3. Default: `.project`

**Examples:**

- `/sdlc-import` em qualquer projeto → `.project/`
- `/new-feature "auth"` em qualquer projeto → `.project/corpus/nodes/decisions/`
- ADRs SOBRE o framework sdlc_agentico → `.agentic_sdlc/corpus/nodes/decisions/`

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

**Cross-Phase Agents (Meta):**

- **orchestrator**: Coordinates phase transitions, evaluates gates
- **playbook-governance**: Monitors drift, detects patterns, proposes updates

### Complexity Levels

- **Level 0 (Quick Flow)**: Bug fixes, typos → Phases 5, 6 → `/quick-fix`
- **Level 1 (Feature)**: Simple features → Phases 2, 5, 6 → `/new-feature`
- **Level 2 (BMAD Method)**: New product/service → Phases 0-7 → `/sdlc-start`
- **Level 3 (Enterprise)**: Compliance-critical → All phases + human approval

### Security by Design

Mandatory security gates in phases 2, 3, 5, 6, 7:

- Phase 2: Security requirements documented
- Phase 3: Threat model (STRIDE), HIGH/CRITICAL risks mitigated
- Phase 5: No hardcoded secrets, input validation
- Phase 6: SAST/SCA executed, no critical/high vulnerabilities
- Phase 7: Security checklist complete

**Auto-escalation triggers:** CVSS >= 7.0, PII exposure, auth/authz changes, cryptography changes, new public endpoints.

### Agent Model Selection

| Model | Use Case | Example Agents |
|-------|----------|----------------|
| **opus** | Complex decisions, architecture, security | system-architect, threat-modeler, compliance-guardian |
| **sonnet** | Implementation, documentation, routine tasks | code-author, doc-generator, test-author, most others |

**Heuristic**: Use `opus` for deep reasoning and trade-off analysis. Use `sonnet` for execution-focused tasks.

### Agent Types

| Type | Count | Description |
|------|-------|-------------|
| **Orchestrated** | 33 | Full agents (200-500 lines) with complete instructions |
| **Consultive (Lightweight)** | 4 | Minimal agents (~20 lines) that delegate to skills |

**Lightweight agents**: `failure-analyst`, `interview-simulator`, `requirements-interrogator`, `tradeoff-challenger`.

## Skills Summary

All skills are located in `.claude/skills/` and automatically available to agents based on phase.

### Core Skills (Phase-Independent)

| Skill | Purpose |
|-------|---------|
| `gate-evaluator` | Evaluates quality gates between phases |
| `rag-query` | Queries RAG knowledge corpus |
| `auto-branch` | Automatic branch creation (fix/, feature/, hotfix/, release/) |
| `phase-commit` | Commits artifacts at end of each phase |
| `session-analyzer` | Extracts learnings from Claude Code sessions |

### Knowledge & Documentation Skills

| Skill | Purpose |
|-------|---------|
| `graph-navigator` | Semantic graph navigation, concept extraction, visualization |
| `decay-scoring` | Temporal scoring for knowledge freshness, curation triggers |
| `doc-blueprint` | Generates documentation blueprints (README, API, Architecture) |
| `doc-generator` | Generates CLAUDE.md and README.md with SDLC signature |
| `document-processor` | Processes PDF, XLSX, DOCX for requirements extraction |
| `document-enricher` | Enriches reference documents with research findings |
| `reference-indexer` | Indexes external reference documents for RAG |

### Infrastructure & Automation Skills

| Skill | Purpose |
|-------|---------|
| `iac-generator` | Generates IaC (Terraform, Bicep, K8s) |
| `parallel-workers` | Parallel task execution using git worktrees (v2.0) |
| `frontend-testing` | E2E testing with Playwright, screenshots, browser logs |

### Integration Skills

| Skill | Purpose |
|-------|---------|
| `github-sync` | Issues, labels, milestones synchronization |
| `github-projects` | GitHub Projects V2 management via GraphQL |
| `github-wiki` | Wiki synchronization via Git |
| `spec-kit-integration` | Integrates with GitHub Spec Kit |
| `bmad-integration` | Integrates with BMAD Method for complexity scaling |

### Observability

Structured logging with Loki/Tempo/Grafana integration available via:

- Python: `.claude/lib/python/sdlc_logging.py`
- Shell: `.claude/lib/shell/logging_utils.sh`
- Config: `.claude/config/logging/logging.yml`
- Dashboard: `.claude/config/logging/dashboards/sdlc-overview.json`

Environment variables: `SDLC_LOG_LEVEL`, `SDLC_LOKI_ENABLED`, `SDLC_LOKI_URL`, `SDLC_TRACE_ENABLED`, `SDLC_TEMPO_URL`.

## Hook System

Hooks trigger automatically:

- **PreToolUse**: Validates commits, checks gates, updates timestamps
- **PostToolUse**: Formats Python files, reminds about ADR updates
- **UserPromptSubmit**: Detects SDLC phase and documents

**Available hooks:** `validate-commit.sh`, `check-gate.sh`, `auto-branch.sh`, `update-project-timestamp.sh`, `detect-phase.sh`, `ensure-feature-branch.sh`, `auto-migrate.sh`, `phase-commit-reminder.sh`, `detect-documents.sh`, `auto-graph-sync.sh`, `auto-decay-recalc.sh`, `track-rag-access.sh`.

## Integrations

- **GitHub Copilot**: Issues assignable to `@copilot` for auto-implementation
- **Spec Kit**: `specify` CLI for spec-driven development
- **GitHub CLI**: `gh` for repository operations
- **GitHub Projects V2**: Automatic project management via GraphQL
- **GitHub Milestones**: Sprint tracking and release coordination
- **GitHub Wiki**: Documentation synchronization via Git

## Key Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Central configuration |
| `.claude/skills/gate-evaluator/gates/*.yml` | Quality gate definitions |
| `.claude/skills/gate-evaluator/gates/security-gate.yml` | Security by Design gate |
| `.agentic_sdlc/templates/*.yml` | Templates (ADR, spec, threat-model) |
| `.agentic_sdlc/docs/playbook.md` | Development principles and practices |
| `.claude/VERSION` | Version and changelog |

## Development Playbook Principles

1. **Quality is responsibility of who creates** - Tests, observability, clarity are part of delivery
2. **Small changes preferred** - Reduce risk, facilitate review
3. **Decisions must be recorded** - As ADRs when affecting maintenance, scale, or cost
4. **Observability is part of delivery** - Nothing ships without being observable
5. **System design required when** - Changing boundaries, integrations, data, or NFRs
6. **Security by Design** - Security is not a feature, it's a fundamental requirement

## Design Patterns (from Anthropic Skills)

| Pattern | Description |
|---------|-------------|
| **Validation-First** | Separate creation from validation, collect ALL errors before reporting |
| **Multi-Tool Strategy** | Python for processing, Node.js for creation, CLI for validation |
| **Zero-Error Policy** | Generated documents must have zero errors |
| **Reconnaissance-Then-Action** | Discover DOM selectors, never hardcode |

Patterns documented at: `.agentic_sdlc/corpus/patterns/anthropic-skills-patterns.md`

## Release Management

**For release procedures**, see: `.agentic_sdlc/docs/release-checklist.md`

**Version History**: Full changelog available in `.claude/VERSION`

**Semantic Versioning**:

- **Major (X.0.0)**: Breaking changes, major architecture changes
- **Minor (x.Y.0)**: New features, new skills, significant enhancements
- **Patch (x.y.Z)**: Bug fixes, documentation updates, minor improvements

---

**Note**: This is a condensed guide. For detailed skill usage, command examples, and implementation details, refer to individual skill documentation in `.claude/skills/*/SKILL.md` or use `/help`.
