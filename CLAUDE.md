# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDLC Agêntico is an AI-driven Software Development Lifecycle framework that orchestrates 26+ specialized agents through 8 development phases. This is a **configuration and orchestration framework**, not a traditional application codebase.

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
# Start SDLC workflow
/sdlc-start "Description of feature or project"

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
- 26+ agents organized by SDLC phase
- Git hooks for validation and automation
- Quality gates between phases
- Complexity levels (0-3) that determine which phases are executed

### Directory Structure
```
.claude/
├── agents/           # Agent specs (markdown) - one per specialized role
├── skills/           # Reusable capabilities with scripts
│   └── gate-evaluator/gates/  # YAML quality gate definitions
├── commands/         # Slash commands for user interaction
├── hooks/            # Git automation (validate-commit, check-gate, etc.)
└── settings.json     # Central configuration

.docs/                # User documentation and playbook
.scripts/             # Installation automation
```

### Phase Flow
```
Phase 0 (Preparation) → intake-analyst, compliance-guardian
Phase 1 (Discovery)   → domain-researcher, doc-crawler, rag-curator
Phase 2 (Requirements)→ product-owner, requirements-analyst, ux-writer
Phase 3 (Architecture)→ system-architect, adr-author, data-architect, threat-modeler
Phase 4 (Planning)    → delivery-planner
Phase 5 (Implementation)→ code-author, code-reviewer, test-author
Phase 6 (Quality)     → qa-analyst, security-scanner, performance-analyst
Phase 7 (Release)     → release-manager, cicd-engineer, change-manager
Phase 8 (Operations)  → incident-commander, rca-analyst, metrics-analyst, observability-engineer
```

### Complexity Levels
- **Level 0 (Quick Flow)**: Bug fixes, typos → Phases 5, 6 only
- **Level 1 (Feature)**: Simple features → Phases 2, 5, 6
- **Level 2 (BMAD Method)**: New product/service → Phases 0-7
- **Level 3 (Enterprise)**: Compliance-critical → All phases + human approval at every gate

## Key Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Central configuration for agents, phases, gates, hooks |
| `.claude/skills/gate-evaluator/gates/*.yml` | Quality gate definitions per phase transition |
| `.docs/playbook.md` | Development principles, standards, and practices |

## Hook System

Hooks are triggered automatically:
- `PreToolUse`: Validates commits, checks gates before push
- `PostToolUse`: Formats Python files with black, reminds about ADR updates
- `UserPromptSubmit`: Detects current SDLC phase

## Integrations

- **GitHub Copilot Coding Agent**: Issues can be assigned to `@copilot` for automatic implementation
- **Spec Kit**: `specify` CLI for specification-driven development
- **GitHub CLI**: `gh` for repository operations

## Development Playbook Principles

1. **Quality is responsibility of who creates** - Tests, observability, clarity are part of delivery
2. **Small changes preferred** - Reduce risk, facilitate review
3. **Decisions must be recorded** - As ADRs when affecting maintenance, scale, or cost
4. **Observability is part of delivery** - Nothing ships without being observable
5. **System design required when** - Changing boundaries, integrations, data, or NFRs
