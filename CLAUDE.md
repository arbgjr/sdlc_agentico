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

## Hook System

Hooks are triggered automatically:
- `PreToolUse`: Validates commits, checks gates before push, updates project timestamp
- `PostToolUse`: Formats Python files with black, reminds about ADR updates
- `UserPromptSubmit`: Detects current SDLC phase

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

## Integrations

- **GitHub Copilot Coding Agent**: Issues can be assigned to `@copilot` for automatic implementation
- **Spec Kit**: `specify` CLI for specification-driven development
- **GitHub CLI**: `gh` for repository operations

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

## New Agents (v2.0)

| Agent | Phase | Purpose |
|-------|-------|---------|
| `iac-engineer` | 3, 5 | Generates and maintains Infrastructure as Code |
| `doc-generator` | 7 | Generates technical documentation automatically |

## Development Playbook Principles

1. **Quality is responsibility of who creates** - Tests, observability, clarity are part of delivery
2. **Small changes preferred** - Reduce risk, facilitate review
3. **Decisions must be recorded** - As ADRs when affecting maintenance, scale, or cost
4. **Observability is part of delivery** - Nothing ships without being observable
5. **System design required when** - Changing boundaries, integrations, data, or NFRs
6. **Security by Design** - Security is not a feature, it's a fundamental requirement
