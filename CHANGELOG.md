# Changelog

All notable changes to SDLC Agêntico will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0] - 2026-01-14

### Added

- **Document Processing Skill** (`document-processor`)
  - Extract text/data from PDF, XLSX, DOCX files
  - PDF extraction with OCR fallback for scanned documents
  - Excel formula validation using LibreOffice headless
  - Word tracked changes detection (OOXML parsing)
  - Zero-error policy for generated documents
  - Commands: `/doc-extract`, `/doc-validate`, `/doc-create`

- **Frontend Testing Skill** (`frontend-testing`)
  - E2E testing with Playwright
  - Screenshot capture with console error logging
  - Server lifecycle management (`with_server.py`)
  - Integration with qa-analyst for Phase 6
  - Commands: `/frontend-test`, `/frontend-screenshot`, `/frontend-check`

- **Automatic Document Detection Hook** (`detect-documents.sh`)
  - Detects PDF/XLSX/DOCX files on user prompt
  - Suggests document-processor skill when documents found

- **Skill-Agent Integration**
  - `intake-analyst` → `document-processor` (Phase 0)
  - `domain-researcher` → `document-processor` (Phase 1)
  - `requirements-analyst` → `document-processor` (Phase 2)
  - `qa-analyst` → `frontend-testing` (Phase 6)

- **Frontend Quality Gates** (conditional)
  - Phase 5→6: `frontend_build_passing`
  - Phase 6→7: `frontend_e2e_pass_rate`, `frontend_console_error_count`

- **Design Patterns Documentation**
  - Validation-First Pattern
  - Multi-Tool Strategy Pattern
  - Confidence Scoring Pattern
  - Parallel Agent Execution Pattern
  - Reconnaissance-Then-Action Pattern
  - Zero-Error Policy Pattern
  - Location: `.agentic_sdlc/corpus/patterns/anthropic-skills-patterns.md`

- **CI Pipeline Enhancement**
  - New job `validate-skill-scripts` for Python syntax validation
  - Skill structure validation (SKILL.md presence)

### Changed

- Updated release pipeline to include complete `.docs/` structure
- Release package now includes `.agentic_sdlc/corpus/patterns/`
- Updated `code-author` agent with frontend design guidelines
- Updated documentation (CLAUDE.md, README.md)

### Fixed

- Release pipeline was looking for non-existent doc files

## [1.2.0] - 2026-01-13

### Added

- **Phase Commits** (`phase-commit` skill)
  - Automatic commit at the end of each phase
  - Standardized commit messages per phase

- **Session Learning** (`session-analyzer` skill)
  - Extracts learnings from Claude Code sessions
  - Persists decisions, blockers, and resolutions to RAG corpus

- **Stakeholder Review Notifications**
  - Notifies user about files needing review at each gate

- **Auto-Migration** (`auto-migrate.sh` hook)
  - Automatic migration from `.claude/memory` to `.agentic_sdlc/`

- **Branch Validation** (`ensure-feature-branch.sh` hook)
  - Validates proper branch before creating/editing files

- **New Directory Structure** (`.agentic_sdlc/`)
  - `projects/` - Project-specific artifacts
  - `references/` - External reference documents
  - `templates/` - Reusable templates (ADR, spec, threat-model)
  - `corpus/` - RAG knowledge corpus
  - `sessions/` - Session history

### Changed

- Moved project artifacts from `.claude/memory` to `.agentic_sdlc/`
- Updated all agents to use new directory structure

## [1.1.0] - 2026-01-12

### Added

- **IaC Engineer Agent** (`iac-engineer`)
  - Generates Terraform, Bicep, and Kubernetes manifests
  - Integrated in Phase 3 (Architecture) and Phase 5 (Implementation)

- **Doc Generator Agent** (`doc-generator`)
  - Automatically generates technical documentation
  - Integrated in Phase 7 (Release)

- **Security by Design**
  - Mandatory security gate (`security-gate.yml`)
  - Escalation triggers for CVSS >= 7.0, PII exposure, auth changes
  - Integration with phases 2, 3, 5, 6, 7

- **GitHub Copilot Integration**
  - `/sdlc-create-issues --assign-copilot` command
  - Automatic issue creation and assignment

### Changed

- Updated quality gates for security requirements
- Enhanced agent descriptions and instructions

## [1.0.0] - 2026-01-10

### Added

- Initial release of SDLC Agêntico
- 34 specialized agents (30 orchestrated + 4 consultive)
- 9 development phases (0-8)
- Quality gates between all phases
- BMAD complexity levels (0-3)
- Basic skills: gate-evaluator, memory-manager, rag-query
- Commands: /sdlc-start, /quick-fix, /new-feature, /phase-status, /gate-check
- Hooks: validate-commit, check-gate, auto-branch, detect-phase
- Integration with GitHub CLI and Spec Kit

---

[Unreleased]: https://github.com/arbgjr/mice_dolphins/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arbgjr/mice_dolphins/releases/tag/v1.0.0
