# Changelog

All notable changes to SDLC Agêntico will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.1] - 2026-01-14

### Changed

- **Release Pipeline** (`release.yml`)
  - Removed `CLAUDE.md` from package (project-specific, not distributable)
  - Added `CHANGELOG.md` and `LICENSE` to package
  - Excluded `.docs/examples/` from package (development only)
  - Excluded internal documentation files from package:
    - `.claude/memory/` (migrated to `.agentic_sdlc/`)
    - `.claude/guides/` (internal reference)
    - `.claude/best-practices.md` (internal reference)
    - `.claude/quick-reference.md` (internal reference)
  - Updated release notes template to reflect package changes

### Removed

- **`.claude/memory/`**: Removed residual folder (migrated to `.agentic_sdlc/sessions/` in v1.2.0)

## [1.6.0] - 2026-01-14

### Added

- **GitHub Projects V2 Integration** (`github-projects` skill)
  - Create and manage GitHub Projects V2 via GraphQL API
  - Automatic project creation during SDLC start
  - Custom fields: Phase, Priority, Story Points
  - SDLC Kanban columns (Backlog → Done)
  - Scripts: `project_manager.py`

- **GitHub Milestones Integration** (`github-sync` skill)
  - Automatic Milestone creation during sprint planning
  - Sprint to Milestone mapping
  - Issue assignment to Milestones
  - Scripts: `milestone_sync.py`, `issue_sync.py`, `label_manager.py`

- **GitHub Wiki Synchronization** (`github-wiki` skill)
  - Automatic documentation sync to GitHub Wiki
  - ADR publishing with YAML to Markdown conversion
  - Auto-generated Home and Sidebar pages
  - Scripts: `wiki_sync.sh`, `publish_adr.sh`
  - Commands: `/wiki-sync`

- **GitHub Dashboard** (`/github-dashboard` command)
  - Consolidated project status view
  - Project, Milestone, and Wiki status
  - Issues by SDLC phase
  - Quick links to GitHub resources

- **SDLC Label Management**
  - Automatic label creation: `phase:0-8`, `complexity:0-3`, `type:story/task/epic`, `sdlc:auto`
  - Color-coded labels for easy identification
  - Integration with `/sdlc-create-issues`

- **GitHub Projects Scope Verification**
  - Setup script now verifies `project` scope for GitHub CLI
  - Automatic prompt to add scope if missing

### Changed

- **orchestrator agent**: Added full GitHub integration
  - Creates Project V2 during Phase 0
  - Updates Project fields during phase transitions
  - Syncs Wiki and closes Milestone during Phase 7
  - New skills: github-projects, github-wiki, github-sync

- **delivery-planner agent**: Added Milestone integration
  - Automatically creates GitHub Milestone for each sprint
  - Issues assigned to Milestone during sprint planning
  - New skill: github-sync

- **`/sdlc-create-issues` command**: Enhanced with GitHub integration
  - Ensures SDLC labels exist before creating issues
  - Assigns issues to current Milestone
  - Adds issues to GitHub Project V2

- Updated `settings.json` with 3 new skills

### Documentation

- Added GitHub Integration section to README.md
- Updated CLAUDE.md with v1.6.0 documentation
- Updated skills count (16 → 19)
- Updated commands count (10 → 12)

## [1.5.0] - 2026-01-15

### Added

- **Decay Scoring Skill** (`decay-scoring`)
  - Automatic temporal scoring for knowledge nodes
  - Exponential decay algorithm based on age, validation, access, and content type
  - Score thresholds: fresh (0.7+), aging (0.4-0.69), stale (0.2-0.39), obsolete (<0.2)
  - Scripts: `decay_calculator.py`, `decay_tracker.py`, `decay_trigger.py`
  - Commands: `/decay-status`, `/validate-node`

- **Curation Trigger System** (`decay_trigger.py`)
  - Automatic review queue generation
  - Priority-based suggestions (critical, high, medium, low)
  - Corpus health assessment (healthy, needs_attention, critical)
  - Suggested actions: archive, review, validate

- **Access Tracking** (`decay_tracker.py`)
  - Track node access patterns with timestamps
  - Validation history with audit trail
  - Rolling 30-day access counts
  - Access log cleanup for old events

- **Decay-Boosted Search**
  - Integration with `hybrid_search.py`
  - Fresh content boosted in search results
  - Decay score and status returned with results

- **Corpus Health Gate** (`decay-health-gate.yml`)
  - Validates corpus health before releases
  - Blocks if average score < 0.5
  - Blocks if too many obsolete nodes (> 3)
  - Warns if stale ratio > 15%

- **Automation Hooks**
  - `auto-decay-recalc.sh` - Auto-recalculate scores (max every 24h)
  - `track-rag-access.sh` - Track access on RAG queries

### Changed

- Updated `hybrid_search.py` with decay boost integration
- Updated `settings.json` to include decay-scoring skill
- Updated CLAUDE.md with v1.5.0 documentation

## [1.4.0] - 2026-01-14

### Added

- **Semantic Knowledge Graph** (`graph-navigator` skill)
  - Hybrid search combining text + graph traversal
  - Multi-hop neighbor queries (find related nodes)
  - Shortest path finding between nodes
  - Transitive closure for dependency analysis
  - Graph statistics and centrality metrics
  - Commands: neighbors, path, closure, stats, validate

- **Concept Extraction** (`concept_extractor.py`)
  - Automatic extraction of concepts from corpus documents
  - Seed-based matching for technologies, patterns, domains
  - Pattern-based extraction (CamelCase, kebab-case)
  - Confidence scoring for extracted concepts
  - Saved as YAML files in `nodes/concepts/`

- **Hybrid Search** (`hybrid_search.py`)
  - Combined text + graph search for RAG corpus
  - TF-IDF based text search with caching
  - Graph expansion from text results
  - Filtering by phase, concept, and node type
  - Integrated with `rag-query` skill

- **Graph Visualization** (`graph_visualizer.py`)
  - Mermaid diagram generation
  - DOT format export (for Graphviz)
  - Subgraph generation around specific nodes
  - Filtering by type and phase
  - Graph metrics and centrality analysis

- **Graph Integrity Gate** (`graph-integrity.yml`)
  - Validates graph.json and adjacency.json
  - Checks for orphan edges
  - Validates relation types
  - Concept and relation coverage thresholds

- **Auto Graph Sync Hook** (`auto-graph-sync.sh`)
  - Automatically updates graph when corpus nodes are modified
  - Incremental updates for single file changes
  - Triggered by PostToolUse on Write operations

- **Reorganized Corpus Structure**
  - `nodes/` directory with subdirectories for decisions, learnings, patterns, concepts
  - `schema/context.json` with semantic relation definitions
  - `graph.json` as main graph with nodes and edges
  - `adjacency.json` for fast traversal index
  - `index.yml` for text search
  - `.cache/` for search result caching

### Changed

- Updated corpus structure for v1.4.0 compatibility
- Enhanced `rag-query` skill with hybrid search support
- Updated CLAUDE.md with v1.4.0 documentation

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

[Unreleased]: https://github.com/arbgjr/mice_dolphins/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arbgjr/mice_dolphins/releases/tag/v1.0.0
