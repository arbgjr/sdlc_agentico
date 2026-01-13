# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDLC Agêntico is an AI-driven Software Development Lifecycle framework that orchestrates **28+ specialized agents** through **9 development phases (0-8)**. This is a **configuration and orchestration framework**, not a traditional application codebase.

**Key Features:**
- Security by Design integrated in all phases
- Automatic branch creation for features and fixes
- Infrastructure as Code (IaC) generation
- Automatic documentation generation
- Quality gates between all phases

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
- 28+ agents organized by SDLC phase
- Git hooks for validation and automation
- Quality gates between phases (including Security Gate)
- Complexity levels (0-3) that determine which phases are executed
- Security by Design with mandatory gates and escalation triggers

### Directory Structure
```
.claude/
├── agents/           # Agent specs (markdown) - 28+ specialized roles
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
