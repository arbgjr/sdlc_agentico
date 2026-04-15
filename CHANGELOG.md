# Changelog

All notable changes to SDLC Agêntico will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.3.0] - 2026-04-15

### Added — SDD activated natively

- `.specify/memory/constitution.md` v1.0.0 with 11 ratified principles
  (natural-language-first, anti-mock, security-by-design, observability,
  ADR discipline, small-changes, quality-as-author, SDD, BMAD bifurcation,
  Copilot cloud-first, harness integrity).
- Native SDD commands: `/constitution`, `/specify`, `/plan`, `/tasks`,
  `/clarify`, `/analyze`. Each delegates to the right local agents and
  produces artifacts under `.specify/specs/<slug>/`.
- `.agentic_sdlc/templates/story-context.md` — BMAD context-engineered
  story template consumed verbatim by the dispatcher.

### Added — BMAD planning / dev bifurcation

- `/bmad-plan` and `/bmad-dev` commands split the canonical BMAD flow
  (deliberative Planning Phase → executive Dev Cycle with frozen plan).
- `.claude/skills/bmad-integration/scripts/detect_level.py` —
  deterministic complexity classifier (Levels 0–3) with security
  escalators (auth, PII, crypto, payments, CVSS ≥ 7.0).

### Added — Copilot Cloud Agent as DEFAULT parallel strategy

- New skill `.claude/skills/copilot-cloud-agent/` with `dispatcher.py`,
  `status_tracker.py`, `review_relay.py`.
- `review_relay` runs local SAST (bandit + ruff) plus an in-process
  secret scanner scoped to diff added-lines; posts structured findings
  with `@copilot` retry tag on CRITICAL/HIGH.
- `settings.json` `sdlc.parallelization`: `copilot_cloud_agent` is
  `default_strategy`; `parallel_workers` demoted to
  `fallback_when_local_env_required`; four explicit `selection_rules`.

### Added — Agent contracts

- `.agentic_sdlc/templates/agent-contract.md` normative template.
- 6 priority agents carry full tier-1 strict contracts (code-reviewer,
  requirements-analyst, system-architect, threat-modeler,
  security-scanner, orchestrator).
- 34 remaining agents carry tier-2 auto-migrated contracts via
  `.claude/skills/migrate-agent-contracts/scripts/bulk_migrate.py`
  (idempotent, role-inferring, one-shot utility scheduled for removal
  after first full release cycle).
- Total coverage: **40 / 40 agents**.

### Added — Resilience layer

- `.claude/lib/python/resilience.py`: stdlib-only `@with_retry`,
  `@with_timeout`, `@with_circuit_breaker`, composite `@resilient`.

### Added — Eval harness (regression suite)

- `evals/` tree with shared primitives (`_lib/harness.py`), discovery
  runner (`run_all.py`), and **9 suites / 79 golden cases**:
  agent-contracts (47), bmad-detect-level (8), code-reviewer (4),
  gate-evaluator (4), parallelization-routing (5), resilience (5),
  runbooks (3), settings-lint (1), threat-modeler (2).

### Added — SLOs and runbooks

- `.claude/config/slos.yml` with 10 SLOs (SLI queries, targets,
  burn-rate windows).
- `.claude/config/logging/dashboards/slo-burn-rate.json` Grafana panel.
- `.agentic_sdlc/docs/runbooks/` with 4 authored runbooks and 6
  explicitly-pending SLOs.

### Added — Architectural Decision Records

- **ADR-001** — hooks must resolve paths via `$CLAUDE_PROJECT_DIR`.
- **ADR-002** — Copilot Cloud Agent as default Phase 6 strategy.

### Changed — Blocking Phase 2→3 gate

- `.claude/skills/gate-evaluator/gates/phase-2-to-3.yml` rewritten as a
  real blocker. Refuses advancement unless
  `.specify/specs/<slug>/spec.md` has `status: approved`,
  `constitution_version` frontmatter, Given/When/Then criteria, and
  `clarify_rounds_completed >= 1`. Previous version was echo-only.

### Fixed

- `.claude/skills/gate-evaluator/gates/phase-3-to-4.yml`: shell quoting
  bug (`security/2>/dev/null` → `security/ 2>/dev/null`) that silently
  failed the threat_model check. Caught by the new eval harness.
- `.claude/skills/gate-evaluator/scripts/validate_gate.py`: extracted
  from inline code in `SKILL.md` into an actual script; supports both
  `metric/threshold` and `check/validation` YAML dialects.
- `.claude/settings.json`: all 12 hook commands converted from relative
  paths to `${CLAUDE_PROJECT_DIR:-.}` form (ADR-001). Fixes total
  session lockup when Bash cwd drifts into a subdirectory.
- `.claude/agents/sdlc-importer.md`: normalized from bare markdown
  headers to proper YAML frontmatter — was the only outlier in the
  40-agent catalogue.
- `.claude/lib/python/resilience.py`: renamed log `extra.name` to
  `extra.breaker_name` to avoid collision with `LogRecord.name`.

### Deferred

- `refactoring-surgeon` agent (named-smell → named-refactoring catalog).
  Tracked in issue #149 with full design, eval-first requirements, and
  explicit unblocking conditions. Deliberately not built now.
- **Expansion packs structure** (item #9 of original plan). Not built
  without at least two concrete domain packs requesting it — avoids
  speculative abstraction.

### Breaking

- Hooks registered with relative `.claude/hooks/*` paths will stop
  working with cwd drift. Follow ADR-001 in custom forks.
- `/gate-check phase-2-to-3` now rejects projects without an approved
  spec. To unblock, author via `/specify` → `/clarify` → `/analyze`.

## [3.0.3] - 2026-02-06

### Fixed - Docs Version Sync

- **Version references updated across all documentation and source files**
  - README.md: badge, banner, install commands updated to v3.0.3
  - CLAUDE.md: "Current Version" was still showing v2.3.3, updated to v3.0.3
  - .claude/VERSION: version field and release notes updated
  - All Python hook/command version headers updated (6 files)
  - Orchestrator agent and 6 reference documents version footers updated
  - PowerShell setup script version and examples updated
  - tests/__init__.py docstring updated
  - researches/milestone-plan.md current version updated

### Added

- CHANGELOG entries for v3.0.1 and v3.0.2 (previously untracked releases)

## [3.0.2] - 2026-02-06

### Fixed

- fix(gates): correct hardcoded paths in gate evaluator
- refactor(memory): remove memory-manager skill, consolidate into RAG

## [3.0.1] - 2026-02-04

### Fixed

- docs(claude.md): remove memory-manager references, update skill list
- docs(CLAUDE.md): optimize file size from 73k to 12k chars (83% reduction)
- docs(CLAUDE.md): add Natural Language First policy as critical rule
- refactor: update documentation and feature flags
- feat: Remove obsolete scripts and update documentation
- fix(paths): implement dynamic path resolution for project artifacts

## [3.0.0] - 2026-02-02

### Major - Python-First Framework Refactoring

**Focus**: 100% Python hooks + Progressive Disclosure pattern + Natural Language First

#### Week 3 Day 19.5 - Final Hooks Conversion

- **100% Python Hooks Achieved** (14/14):
  - ✅ `detect-client.sh` → removed (direct Python call)
  - ✅ `validate-framework-structure.sh` → `validate-framework-structure.py` (159 lines)
  - ✅ `post-gate-audit.sh` → `post-gate-audit.py` (377 lines)
  - ✅ All hooks compile successfully (`python3 -m py_compile`)
  - ✅ Windows compatibility: 73% → **100%**
  - ✅ Zero shell dependencies in critical path

#### Week 3 Days 20-21 - Orchestrator Refactoring

- **Progressive Disclosure Pattern**:
  - ✅ `orchestrator.md` (1,267 lines) → `orchestrator/SKILL.md` (490 lines)
  - ✅ Created 6 reference files in `reference/` subdirectory:
    - `phases.md` (244 lines) - Phase 0-8 detailed definitions
    - `complexity.md` (267 lines) - Complexity levels 0-3
    - `gates.md` (382 lines) - Quality gate structure and evaluation
    - `coordination.md` (525 lines) - Agent coordination patterns
    - `security.md` (407 lines) - Security escalation rules
    - `integrations.md` (446 lines) - External integrations (GitHub, Spec Kit, etc.)
  - ✅ **Token reduction**: 5,068 → 1,800 tokens (**64% reduction**)
  - ✅ **File size reduction**: 1,267 → 490 lines (**61% reduction**)

#### Week 4 Days 23-24 - Regression Testing

- **Comprehensive Test Suite** (8 suites, 38 tests, **100% pass rate**):
  1. Python Hooks Compilation (14/14 tests) ✅
  2. Configuration Validity (3/3 tests) ✅
  3. Orchestrator Structure (4/4 tests) ✅
  4. Windows Compatibility (4/4 tests) ✅
  5. Agent Integrity (3/3 tests) ✅
  6. Critical Skills (5/5 tests) ✅
  7. File Permissions (2/2 tests) ✅
  8. Documentation Consistency (3/3 tests) ✅

- **Gilfoyle Audit Results**:
  - ✅ **ZERO critical issues found**
  - ✅ All regression checks passed
  - ✅ Windows compatibility 100% verified
  - ✅ Verdict: **GREEN - PRODUCTION READY**

#### Week 4 Day 25 - Documentation

- **Migration Guide**: `v3-migration-guide.md` (442 lines)
  - Complete migration procedure from v2.3.3 → v3.0.0
  - 6-step migration process
  - Rollback procedures
  - Known issues documented
  - Post-migration checklist

- **Test Report**: `v3.0.0-regression-test-report.md` (287 lines)
  - Detailed test execution results
  - Performance benchmarks
  - Platform compatibility matrix

### Changed

- **Component Counts**:
  - Agents: 39 (33 orchestrated + 4 consultive + 1 meta + 1 importer)
  - Skills: 31
  - Commands: 29
  - Hooks: 14 (**100% Python**)

- **Scripts Reduction**:
  - Before: 175 scripts
  - After: 55 scripts
  - Reduction: **68%** ⬇️
  - Natural Language First: 110 scripts eliminated

### Performance

- **Hook Execution**:
  - All hooks within 10% baseline performance
  - validate-commit: ~85ms
  - check-gate: ~160ms
  - detect-phase: ~50ms

- **Orchestrator Loading**:
  - Load time: ~500ms → ~200ms (**60% faster**)
  - Token usage: 5,068 → 1,800 (**64% reduction**)

### Platform Compatibility

- **Linux**: ✅ Ubuntu 22.04, Fedora 39, WSL2
- **Windows**: ✅ 100% native support (no shell dependencies)
- **macOS**: ⚠️ Not tested (assumed compatible, Python stdlib only)

### Breaking Changes

- **None** - Fully backward compatible
- All workflows continue to function without changes
- Settings automatically updated to use Python hooks

### Known Issues

1. **worktree_manager.sh** - One shell script remains in `parallel-workers` skill
   - Impact: MINOR (optional skill, Level 2+ only, doesn't affect Windows)
   - Planned fix: Migrate to `pygit2` in v3.1.0

2. **orchestrator.md.backup** - Backup file present alongside new structure
   - Impact: NONE (not loaded, 50KB disk space)
   - Action: Can be safely deleted after v3.0.0 verification

### Migration Required?

- **No** - Framework automatically uses Python hooks
- **Optional**: Review migration guide for detailed changelog
- **Rollback**: `git checkout v2.3.3` if issues occur

## [2.1.12] - 2026-01-27

### Fixed - CRITICAL Framework Deletion Bug

- **clean_agentic_sdlc()** - Now preserves framework files:
  - ✅ **Bug**: v2.1.11 did `rm -rf ".agentic_sdlc"` - deleted EVERYTHING
  - ✅ **Impact**: Users lost framework (scripts, templates, schemas, docs) after cleanup
  - ✅ **Fix**: Selective removal of artifact directories only
  - ✅ **Preserved**: scripts/, templates/, schemas/, docs/, logo.png, splash.py
  - ✅ **Removed**: corpus/, architecture/, security/, reports/, references/, sessions/
  - ✅ **Safety**: Creates .gitkeep in cleaned directories
  - ✅ **Feedback**: Logs which framework files were preserved

### Recovery

- **Autoritas Project** - Framework successfully restored from backup:
  - Backup used: `.agentic_sdlc.backup-20260127-201155`
  - Restored: scripts/, templates/, schemas/, docs/, logo.png, splash.py
  - Verified: All framework functionality intact after restoration

## [2.1.11] - 2026-01-27

### Fixed - CRITICAL Migration Bug

- **Setup Script** - Migration now offered in fresh installs:
  - ✅ **Root Cause**: v2.1.10 only offered migration during upgrades, not fresh installs
  - ✅ **Solution**: `check_and_migrate_artifacts()` now called at main() entry point
  - ✅ **Impact**: Migration verification runs ALWAYS, independent of install origin
  - ✅ **Tested**: Validated on Autoritas project (12 files migrated successfully)

### Added - Standalone Migration Script

- **migrate-artifacts.sh** - Manual migration tool:
  - ✅ Can be executed at any time: `./\.agentic_sdlc/scripts/migrate-artifacts.sh`
  - ✅ Interactive migration with 3 options (migrate now, later, cancel)
  - ✅ Auto-detects artifacts in .agentic_sdlc/ that should be in .project/
  - ✅ Displays file counts and sizes before migration
  - ✅ Creates timestamped backups before cleanup
  - ✅ Verifies migration success with file count comparison
  - ✅ Comprehensive progress reporting and colored output

### Changed - Migration Flow

- **Always Check Artifacts** - New behavior:
  - Before: Only checked during version upgrades (confirm_update)
  - After: ALWAYS checked at start of installation (main entry point)
  - Prevents: Artifacts stuck in .agentic_sdlc/ on fresh installs
  - Benefit: Consistent behavior regardless of install method

## [2.1.10] - 2026-01-27

### Added - Smart Update System & Artifact Migration

- **Enhanced Setup Script** - Intelligent update detection and migration:
  - ✅ `detect_installed_version()` - 3-method version detection (VERSION file, git tags, directory existence)
  - ✅ `check_project_artifacts_in_agentic_sdlc()` - Detects misplaced project artifacts
  - ✅ `migrate_project_artifacts()` - Safe migration from .agentic_sdlc/ to .project/ with user confirmation
  - ✅ `clean_agentic_sdlc()` - Backup + removal workflow with timestamped backups
  - ✅ `confirm_update()` - Interactive upgrade with 3 options:
    - [1] Migrate and update (RECOMMENDED)
    - [2] Continue without migration (CRITICAL WARNING with data loss details)
    - [3] Cancel update
  - ✅ Visual improvements - colored boxes, formatted prompts, numbered menus
  - ✅ `--force` flag for automation without prompts

- **Uninstall Script** - Interactive removal for symlink installations:
  - ✅ `uninstall-local.sh` - Menu-driven uninstall with 3 options:
    - [1] Restore from backup (.backup-YYYYMMDD-HHMMSS)
    - [2] Clean uninstall (remove symlinks only)
    - [3] Complete cleanup (remove everything)
  - ✅ Automatic backup detection and restoration
  - ✅ Safety confirmations before destructive operations

- **Audit System** - Comprehensive analysis framework:
  - ✅ CRITICAL-AUDIT-v2.0.0-autoritas.md - 22 problems categorized:
    - 2 CRITICAL: Output directory ignored, framework files copied
    - 3 GRAVE: Reconciliation missing, debug logging absent, low conversion rate
    - 4 MEDIUM: UX issues
    - 5 LIGHT: Minor improvements
    - 8 SUGGESTIONS: Feature enhancements
  - ✅ Evidence-based root cause analysis
  - ✅ Detailed recommendations with effort estimates

### Changed - Migration Workflow

- **Data Preservation First** - Critical warnings before any data loss:
  - Shows detailed file counts and sizes before deletion
  - Requires explicit user confirmation for data loss scenarios
  - Creates automatic backups (.agentic_sdlc.backup-YYYYMMDD-HHMMSS)
  - RED warning boxes for critical operations

### Fixed

- **Update Safety** - Prevents accidental data loss during framework upgrades
- **Legacy Installations** - Handles old .agentic_sdlc/ project installations gracefully
- **Symlink Management** - Proper cleanup and restoration for local installations

### Security

- **Backup Everything** - Never deletes without creating a backup first
- **Explicit Consent** - Interactive confirmations for all destructive operations
- **Rollback Ready** - All backups timestamped and preserved

## [2.0.5] - 2026-01-24

### Fixed - Large Project Support

- **sdlc-import**: Increased max_project_size from 500,000 to 900,000 LOC
  - Supports very large projects (monorepos, enterprise legacy systems)
  - Projects 500k-900k LOC now get full analysis instead of sampled
  - Improves ADR and threat model quality for enterprise projects

## [2.0.4] - 2026-01-24

### Added - sdlc-import v2.1.0 Advanced Analysis & Testing

- **ADR Validator** - Validação automática de Architecture Decision Records:
  - ✅ LGPD compliance checking (data privacy, consent, retention)
  - ✅ RLS (Row-Level Security) technology validation
  - ✅ JWT authentication pattern detection
  - ✅ Multi-tenancy pattern validation
  - ✅ Configuration: `adr_validation_rules.yml`

- **Graph Generator** - Knowledge graph automation:
  - ✅ Semantic graph generation from codebase
  - ✅ Concept extraction with confidence scoring
  - ✅ Adjacency matrix for fast traversal
  - ✅ Quality gate: `graph-integrity.yml`

- **Issue Creator** - GitHub integration:
  - ✅ Automatic issue creation from analysis
  - ✅ Priority-based filtering (P0-P3)
  - ✅ GitHub CLI integration
  - ✅ Markdown formatting with metadata

- **Migration Analyzer** - Database migration analysis:
  - ✅ EF Core migrations (C#/.NET)
  - ✅ Alembic migrations (Python)
  - ✅ Flyway migrations (Java/SQL)
  - ✅ Table/index detection
  - ✅ RLS policy detection
  - ✅ Configuration: `migration_patterns.yml`

### Testing

- **999 new unit tests** across 4 modules:
  - 306 tests: ADRValidator (LGPD, RLS, JWT, multi-tenancy)
  - 234 tests: GraphGenerator (structure, concepts, adjacency)
  - 184 tests: IssueCreator (priority, GitHub CLI, formatting)
  - 275 tests: MigrationAnalyzer (EF Core, Alembic, Flyway)
- **100% coverage** in validators, generators, analyzers
- **2,844 lines** of test code added

### Documentation

- IMPLEMENTATION_SUMMARY_v2.1.0.md - Complete v2.1.0 feature documentation
- Configuration files with validation rules and patterns

## [2.0.3] - 2026-01-24

### Added - Auto-Update System Enhancements

- **Orchestrator Integration** - Version-checker agora verificado automaticamente no início de workflows:
  - ✅ Verificação automática em Phase 0 (Intake)
  - ✅ AskUserQuestion integration com 4 opções (update/changelog/skip/later)
  - ✅ Impact analysis mostrado antes de atualizar
  - ✅ Nunca bloqueia workflow (graceful degradation)

- **Migration Script Validation** - Security hardening completo:
  - ✅ Validação de shebang obrigatória (`#!/bin/bash`)
  - ✅ Verificação de permissões executáveis
  - ✅ Detecção de padrões perigosos (`rm -rf /`, `dd if=`, `mkfs.*`, `fdisk`, `parted`)
  - ✅ Timeout enforcement (300s)
  - ✅ Exit code validation (não-zero = rollback crítico)

- **Telemetria de Adoção** - Observabilidade completa:
  - ✅ Logging estruturado com Loki
  - ✅ Métricas: from_version, to_version, migrations_executed, error_count
  - ✅ Grafana queries prontas para Version Adoption Rate
  - ✅ Rastreamento de rollbacks e falhas

### Changed - Breaking Changes

- **Migration Failures Now Critical** - Antes: warnings ignorados, agora: rollback automático
- **Validation Required** - Migration scripts devem passar validação ou update falha

### Fixed

- **Update Executor** - Comportamento aprimorado:
  - Migration scripts agora validados antes de execução
  - Rollback automático em timeout de migration
  - Telemetria completa de sucesso/falha

### Testing

- **103 tests (+10 novos)** - 100% pass rate
- **90%+ coverage** em update_executor (antes 85%)
- Novos testes:
  - 5 testes de validação de migration scripts
  - 3 testes de telemetria (get_version_from_commit)
  - 2 testes de integração (validation fails, migration timeout)

### Documentation

- **Orchestrator Agent** - 135 linhas de documentação de integração
- **IMPLEMENTATION_SUMMARY.md** - Atualizado com status v2.0.3
- **Reports** - `version-checker-enhancements-v2.0.3.md` (análise completa)

## [2.0.2] - 2026-01-23

### Fixed - sdlc-import Critical Workflow Fixes

- fix(sdlc-import): Force LLM when config llm.enabled=true (ignora --no-llm flag)
- fix(sdlc-import): Force threat modeling when config enabled=true (no defer)
- fix(sdlc-import): Populate phase-artifacts/phase-1-discovery/ with JSON logs
- fix(sdlc-import): Index original ADRs in references/original-adrs/
- fix(sdlc-import): Auto-push feature branch to remote after analysis
- chore(sdlc-import): Add TODO.md for v2.1.0 planned features

## [2.0.1] - 2026-01-23

### Fixed - sdlc-import Exclude Patterns

- fix(sdlc-import): Add .terraform and IaC artifacts to exclude_patterns
- fix(sdlc-import): Add bin/obj/.NET build artifacts
- fix(sdlc-import): Add Migrations, packages, coverage, docs
- fix(sdlc-import): Increase max_project_size from 100k to 500k LOC
- fix(sdlc-import): Large projects (1.6GB, 22M LOC) now analyze correctly

## [2.0.0] - 2026-01-23

### Added - Legacy Project Onboarding (Epic #52)

- **sdlc-import skill** - Importação e engenharia reversa de projetos existentes:
  - 🚀 **Language detection expansion**: 10 → 30 tecnologias (3x aumento)
  - ✅ **Backend/Infrastructure (9 novas)**: C++, Rust enhanced, Ansible, Jenkins, Chef, Puppet, Gradle, Selenium, Bicep
  - ✅ **Frontend/Testing (6 novas)**: Playwright, TypeScript enhanced, Vue.js, Svelte, Tailwind CSS, Vite/Webpack
  - ✅ **Mobile (5 novas)**: React Native, Flutter/Dart, Swift, Kotlin enhanced, Xamarin
  - ✅ **LSP integration**: clangd-lsp (C++), dart-lsp (Flutter), sourcekit-lsp (Swift)
  - ✅ **Disambiguation logic**: Chef/Ruby (via metadata.rb), Ansible/YAML (via ansible.cfg), Gradle/Kotlin
  - ✅ **Configuration-driven**: language_patterns.yml expandido de 286 para 669 linhas (+383 linhas)
  - ✅ **Brace expansion**: Suporte para glob patterns como `**/*.{cpp,h,hpp}`
  - Scripts:
    - `project_analyzer.py` - Análise completa de projetos
    - `language_detector.py` - Detecção de 30 tecnologias
    - `decision_extractor.py` - Extração de ADRs com confidence scoring
    - `architecture_visualizer.py` - Geração de diagramas Mermaid e DOT
    - `threat_modeler.py` - STRIDE threat modeling
    - `tech_debt_detector.py` - Detecção de dívida técnica (P0-P3)

- **sdlc-importer agent** - Novo agente para Phase 0 (Preparation):
  - Orquestra importação de projetos existentes
  - Integração com quality gate sdlc-import-gate.yml
  - Criação automática de branch feature/import-*

- **Comando /sdlc-import** - Importação de projetos:
  - Opções: `--skip-threat-model`, `--create-issues`, `--no-llm`
  - Output: 5-15 ADRs inferidos, 3-5 diagramas, threat model STRIDE

- **Quality Gate**: sdlc-import-gate.yml com 6 validações críticas:
  - `minimum_languages`: Mínimo 1 linguagem detectada
  - `high_confidence_decisions`: Mínimo 3 ADRs HIGH confidence
  - `architecture_diagrams`: Mínimo 2 diagramas gerados
  - `threat_model_exists`: Threat model STRIDE criado
  - `tech_debt_prioritized`: Dívida técnica categorizada (P0-P3)
  - `documentation_complete`: Todos artefatos gerados

- **Documentação**:
  - ADR: `ADR-022-automated-legacy-project-onboarding.yml`
  - SKILL.md: Documentação completa do sdlc-import skill
  - README.md: Guia de uso com exemplos
  - IMPLEMENTATION_SUMMARY.md: Resumo técnico da implementação
  - BENCHMARK_VALIDATION.md: Benchmarks de detecção de linguagens

### Changed - Language Detection

- **language_patterns.yml** - Expansão massiva:
  - Novas seções: `iac`, `config_mgmt_tools`, `cicd`, `frontend_frameworks`, `build_tools`, `mobile_frameworks`
  - Frameworks multi-linguagem: Selenium (Java/Python/JS), Playwright (TypeScript/Python)
  - Dependency files expandidos para suportar novas tecnologias

- **8 novos métodos de detecção**:
  - `_detect_iac_tools()` - Bicep, Ansible
  - `_detect_config_mgmt_tools()` - Chef, Puppet
  - `_detect_cicd_tools()` - Jenkins
  - `_detect_frontend_frameworks()` - Vue.js, Svelte
  - `_detect_build_tools()` - Vite, Webpack
  - `_detect_mobile_frameworks()` - React Native, Flutter, Swift, Xamarin
  - `_detect_testing_frameworks()` - Selenium, Playwright (multi-language)
  - `_expand_braces()` - Expansão de padrões glob com chaves

### Testing

- **255/255 testes passando** (100% success rate):
  - 87 integration tests (11 language stacks: Django, React, Spring, ASP.NET, Gin, Rails, C++, Flutter, Vue, Ansible, Playwright)
  - 168 unit tests
  - Zero regressões em funcionalidade existente

- **5 novos integration tests**:
  - `test_cpp_integration.py` - C++/CMake/Conan/Boost
  - `test_flutter_integration.py` - Flutter/Dart mobile
  - `test_vue_integration.py` - Vue.js + Vite
  - `test_ansible_integration.py` - Ansible IaC com disambiguation
  - `test_playwright_integration.py` - Playwright E2E testing

- **10 novos unit tests** em `test_language_detector.py`:
  - C++/CMake, Bicep, Ansible, Jenkins, Vue, Svelte, Playwright, Flutter, Swift, Vite

### Fixed

- **Framework list overwriting**: Mudança de assignment (`=`) para `extend()` nos métodos de detecção
- **Boost detection**: Implementação de `_expand_braces()` para suportar padrões `**/*.{cpp,h,hpp}`
- **Testing framework detection**: Separação de frameworks legacy (pattern direto) e multi-language (dict de patterns)

### Security

- **Anti-Mock Policy**: Documentação estendida no CLAUDE.md
- **Threat modeling**: Integração com security-guidance plugin
- **Quality gates**: Validação de todos artefatos antes de commit

### Breaking Changes

- Nenhuma (additive only)

## [1.7.16] - 2026-01-17

### Added

- **phase-commit/scripts/phase-commit.sh** - Script completo de commit automático:
  - 📦 **Funcionalidade**: Faz commit **E PUSH** automaticamente ao final de cada fase
  - ✅ Detecção automática da fase atual (manifest.yml ou project.yml)
  - ✅ Mapeamento de tipo de commit por fase (docs/feat/test/chore)
  - ✅ Push automático com configuração de upstream se necessário
  - ✅ Atualização de manifest.yml com commit hash e timestamp
  - ✅ Logs estruturados com Loki (skill="phase-commit")
  - ✅ Tratamento de erros com rollback seguro

- **Hooks de automação**:
  - ✅ `phase-commit-reminder.sh` executado automaticamente após criar artefatos
  - ✅ Hooks configurados para task-breakdown.yml, ADRs, specs
  - ✅ Execução transparente sem intervenção do usuário

### Changed

- **phase-commit-reminder.sh**: Agora **EXECUTA** o commit automaticamente
  - ANTES: Apenas lembrava o usuário (reminder)
  - DEPOIS: Executa `phase-commit.sh` automaticamente
  - Detecta PROJECT_ID e PHASE do contexto
  - Logs de execução e resultado

- **orchestrator.md**: Workflow de commit atualizado
  - Instruções explícitas para execução automática
  - Documentação de commit+push integrado
  - Verificação de sucesso antes de prosseguir

- **phase-commit/SKILL.md**: Documentação atualizada
  - Skill FAZ commit E push (não apenas commit)
  - Push detecta upstream e configura automaticamente
  - Tratamento de erros documentado

- **settings.json**: Hooks configurados
  - `PostToolUse` para task-breakdown.yml
  - `PostToolUse` para ADRs (adr-*.yml)
  - `PostToolUse` para specs (*.spec.md)

### Fixed

- **Problema crítico**: Commits e pushes não eram feitos automaticamente
  - Artefatos ficavam apenas no repositório local
  - Agora executa commit+push ao final de cada fase
  - Referência: Issue relatada no projeto satra

- **Hook não configurado**: phase-commit-reminder.sh não estava em settings.json
  - Agora configurado em PostToolUse para artefatos SDLC

## [1.7.15] - 2026-01-17

### Added

- **github-sync/create_all_sprints.py** - Script automático de criação de milestones:
  - 📦 **Funcionalidade**: Cria todos os milestones de uma vez a partir do task-breakdown.yml
  - ✅ Extrai configuração automática de sprints (nome, descrição, duração)
  - ✅ Calcula datas de vencimento baseadas em duration_weeks
  - ✅ Suporta Sprint 0, EPICs 001-005 e Sprint 6 Polish
  - ✅ Usa milestone_sync.py como biblioteca
  - ✅ Evita duplicação (detecta milestones existentes)
  - ✅ Base date configurável (default: hoje)

- **github-sync/assign_issues_bulk.py** - Script de atribuição em massa de issues:
  - 📦 **Funcionalidade**: Atribui automaticamente issues aos milestones corretos
  - ✅ Mapeia TASK-XXX → Milestone title baseado em assigned_sprint
  - ✅ Busca issues via `gh issue list` (limit 200)
  - ✅ Resolve milestone title → milestone number automaticamente
  - ✅ Cache de milestone numbers para performance
  - ✅ Rate limiting (0.3s entre atualizações)
  - ✅ Resumo detalhado (updated/skipped/failed)

- **Uso**:
  ```bash
  # Criar todos os milestones
  python3 .claude/skills/github-sync/scripts/create_all_sprints.py \
    task-breakdown.yml \
    --base-date 2026-01-20

  # Atribuir issues aos milestones
  python3 .claude/skills/github-sync/scripts/assign_issues_bulk.py \
    task-breakdown.yml
  ```

- **Output esperado**:
  ```
  Creating 7 sprint milestones...
  Base date: 2026-01-20

  Creating Sprint 0 - Infrastructure & Setup (due: 2026-01-27)...
  Milestone criado: #2 - Sprint 0 - Infrastructure & Setup

  Creating Sprint 1 - EPIC-001: Ingestão de Dados (due: 2026-02-10)...
  Milestone criado: #3 - Sprint 1 - EPIC-001: Ingestão de Dados

  ============================================================
  ✓ Created: 7
  ✗ Failed: 0
  ============================================================

  Mapping 114 tasks to milestones...

  ✓ Issue #50 (TASK-001) → Milestone #2 (Sprint 0 - Infrastructure & Setup)
  ✓ Issue #51 (TASK-002) → Milestone #2 (Sprint 0 - Infrastructure & Setup)
  ✓ Issue #52 (TASK-003) → Milestone #3 (Sprint 1)

  ============================================================
  ✓ Updated: 114
  ⊘ Skipped: 0
  ✗ Failed: 0
  ============================================================
  ```

### Fixed

- **assign_issues_bulk.py**: Corrigido uso de milestone title em vez de número
  - Problema: `gh issue edit --milestone {number}` falhava com "not found"
  - Solução: Usar título do milestone: `gh issue edit --milestone "{title}"`
  - Referência: Issue relatada no projeto satra (122 issues mapeadas)

## [1.7.14] - 2026-01-17

### Added

- **github-sync/bulk_create_issues.py** - Script de criação em massa de issues GitHub:
  - 📦 **Funcionalidade**: Cria múltiplas issues a partir de task-breakdown.yml
  - ✅ Suporta estrutura completa de EPICs, Stories e Tasks
  - ✅ Adiciona metadata: Epic, Sprint, Type, Priority, Story Points
  - ✅ Formata acceptance criteria como checkboxes
  - ✅ Inclui dependencies e technical notes
  - ✅ Aplica labels automaticamente (phase, priority, type)
  - ✅ Rate limiting (0.5s entre requisições)
  - ✅ Resumo detalhado de criação (success/failed)

- **Estrutura suportada**:
  - Sprint 0 Infrastructure
  - EPICs 001-005 (Ingestão, Métricas, Alertas, Dashboard, Notificações)
  - Sprint 6 Polish & QA
  - Mapping automático de tasks para sprints

- **Uso**:
  ```bash
  python3 .claude/skills/github-sync/scripts/bulk_create_issues.py \
    task-breakdown.yml \
    <project-number>
  ```

- **Output esperado**:
  ```
  ✓ Created issue #123: [TASK-001] Setup PostgreSQL
  ✓ Created issue #124: [TASK-002] Configure Redis

  ============================================================
  Issue Creation Summary
  ============================================================
  ✓ Successfully created: 45
  ✗ Failed: 0
  Total: 45/45
  ============================================================
  ```

## [1.7.13] - 2026-01-17

### Fixed

- **Todos os scripts Python** - Corrigido formato YAML gerado com aspas mal escapadas:
  - 🐛 **Problema**: PyYAML gerava YAML inválido quando strings continham aspas duplas
    ```yaml
    # YAML INVÁLIDO gerado
    acceptance_criteria:
      - "Estado anterior para "cruza""  # ❌ Erro de parsing
    ```
  - 🐛 **Consequência**: Erro ao carregar YAML:
    ```
    yaml.constructor.ConstructorError: while constructing a mapping
    found unexpected ':' in "<string>"
    ```
  - ✅ **Solução**: Adicionado `default_style="'"` em todos os `yaml.dump()`
  - ✅ **Resultado**: PyYAML agora usa aspas simples por padrão, evitando conflito
    ```yaml
    # YAML VÁLIDO gerado
    acceptance_criteria:
      - 'Estado anterior para "cruza"'  # ✓ Parsing correto
    ```

### Changed

- **7 arquivos Python corrigidos**:
  - `.claude/skills/memory-manager/scripts/memory_ops.py` (5 ocorrências)
  - `.claude/skills/alignment-workflow/scripts/consensus_manager.py` (1 ocorrência)
  - `.claude/skills/decay-scoring/scripts/decay_calculator.py` (1 ocorrência)
  - `.claude/skills/decay-scoring/scripts/decay_tracker.py` (2 ocorrências)
  - `.claude/skills/rag-query/scripts/hybrid_search.py` (1 ocorrência)
  - `.claude/skills/graph-navigator/scripts/concept_extractor.py` (1 ocorrência)
  - `.claude/skills/session-analyzer/scripts/extract_learnings.py` (1 ocorrência)

- **Todos os yaml.dump() agora usam**:
  ```python
  yaml.dump(data, f,
      default_flow_style=False,
      allow_unicode=True,
      default_style="'",  # ← NOVO: força aspas simples
      sort_keys=False     # onde aplicável
  )
  ```

## [1.7.12] - 2026-01-17

### Fixed

- **memory-manager/memory_ops.py** - Script agora aceita argumentos CLI e cria manifest completo:
  - 🐛 **Problema**: Script ignorava argumentos `--project-name`, `--description`, etc. e apenas executava testes
  - 🐛 **Consequência**: `/sdlc-start` criava diretórios mas NÃO criava `manifest.yml` do projeto
  - ✅ **Solução**: Implementado CLI com argparse e comando `init`
  - ✅ Nova função `init_project()` cria manifest completo com todos os metadados
  - ✅ Cria arquivo `.current-project` apontando para projeto ativo
  - ✅ Comando `test` preserva comportamento antigo para testes

### Added

- **memory_ops.py** - CLI completo:
  - Comando `init` para inicializar projeto
  - Parâmetros: `--project-name`, `--description`, `--complexity`, `--phase`
  - Parâmetros GitHub: `--github-project`, `--github-milestone`, `--github-url`
  - Gera `project_id` único (format: `proj-{uuid[:8]}`)
  - Cria manifest.yml com estrutura completa (artifacts, decisions, team, metadata)

### Changed

- **manifest.yml** - Estrutura padronizada:
  - Campos: project_id, name, description, created_at, updated_at
  - current_phase, complexity_level, status, phases_completed
  - artifacts (specs, adrs, diagrams, tests, documentation)
  - decisions, team (owner, contributors), metadata, tags
  - github (project_number, project_url, milestone) - opcional

## [1.7.11] - 2026-01-17

### Fixed

- **fallback.sh** - Adicionada validação de repositório GitHub antes de executar `gh` commands:
  - 🐛 **Problema**: Scripts falhavam sem mensagem clara quando não há remote git configurado
    ```
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/usr/lib/python3.12/json/__init__.py", line 293, in load
    json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    ```
  - ✅ **Solução**: Nova função `is_github_repo()` valida remote git + gh CLI access
  - ✅ Novo check service `repo` verifica se estamos em repositório GitHub válido
  - ✅ Mensagens claras orientando como configurar git remote

- **sdlc-start.md** - Criação automática de repositório GitHub quando não existir:
  - ✅ Detecta se estamos em repositório GitHub via `check_service repo`
  - ✅ **Se não estiver em repo**: cria automaticamente com `gh repo create`
  - ✅ Pergunta visibilidade (public/private) antes de criar
  - ✅ Usa nome do diretório atual como nome do repositório
  - ✅ Faz push inicial se houver commits locais
  - ✅ Continua workflow automaticamente após criação

- **wiki_sync.sh** - Mensagens de erro melhoradas:
  - ✅ Detecta ausência de remote git antes de tentar `gh repo view`
  - ✅ Instruções claras de troubleshooting (gh auth status, git remote -v)

- **publish_adr.sh** - Mesmas melhorias de validação

### Added

- **fallback.sh** - Nova função `is_github_repo()` para validação reutilizável
- **check_service** - Novo serviço `repo` para validar repositório GitHub

### Changed

- **check_service wiki** - Agora valida repositório GitHub antes de testar wiki

## [1.7.10] - 2026-01-17

### Fixed

- **github-projects/project_manager.py** - Corrigido criação de campos SINGLE_SELECT:
  - 🐛 **Problema**: Comando `gh project field-create` falhava ao criar campos Phase e Priority
    ```
    Erro ao criar campo 'Phase': passing `--single-select-options` is required for SINGLE_SELECT data type
    ```
  - ✅ **Solução**: Adicionado parâmetro `--single-select-options` ao comando
  - ✅ Formata opções como string separada por vírgulas (ex: "Backlog,In Progress,Done")
  - ✅ Remove TODO obsoleto sobre GraphQL (gh CLI suporta nativamente)

### Changed

- **create_single_select_field()** agora exibe quantidade de opções criadas no log

## [1.7.9] - 2026-01-17

### Fixed

- **install-security-tools.sh** - Corrigido suporte para PEP 668 (externally-managed-environment):
  - 🐛 **Problema**: Script falhava em distribuições Linux modernas (Debian 12+, Ubuntu 23.04+, Fedora 38+)
    ```
    error: externally-managed-environment
    × This environment is externally managed
    ```
  - ✅ **Solução**: Usa `pipx` por padrão em sistemas Linux (isolamento por aplicação)
  - ✅ Detecta PEP 668 automaticamente via `/usr/lib/python3.*/EXTERNALLY-MANAGED`
  - ✅ Instala `pipx` automaticamente se não existir (apt/dnf/pacman)
  - ✅ Fallback para `pip3 --user` em sistemas sem PEP 668
  - ✅ Aviso se ferramenta não estiver no PATH após instalação

### Changed

- **Estratégia de instalação do Semgrep** (por prioridade):
  1. **pipx** (recomendado - isolado, compatível com PEP 668)
  2. **brew** (macOS)
  3. **pip3 --user** (fallback para sistemas antigos)

### Added

- Função `has_pep668()` - Detecta sistemas com PEP 668 ativo
- Função `ensure_pipx()` - Instala pipx automaticamente se necessário
  - Suporte para: apt (Debian/Ubuntu), dnf (Fedora/RHEL), pacman (Arch)

### Technical Details

**Distribuições afetadas**:
- ✅ Debian 12+ (Bookworm)
- ✅ Ubuntu 23.04+ (Lunar Lobster)
- ✅ Fedora 38+
- ✅ Arch Linux (rolling)
- ✅ Pop!_OS 22.04+

**Arquivos modificados**:
- `\.agentic_sdlc/scripts/install-security-tools.sh` (+92 linhas, -17 linhas)

**Referências**:
- PEP 668: https://peps.python.org/pep-0668/
- pipx: https://pipx.pypa.io/

## [1.7.8] - 2026-01-16

### Added

- **Análise Proativa de Learnings e Erros** - Fluxo completo de aprendizado contínuo:

  **INÍCIO da sessão** (UserPromptSubmit hook):
  - ✅ Novo hook `query-phase-learnings.sh` consulta corpus RAG
  - ✅ Exibe learnings/warnings anteriores da fase ao usuário
  - ✅ Dicas e problemas conhecidos antes de iniciar trabalho

  **FIM da fase** (gate-check pré-gate):
  - ✅ Novo script `query_phase_errors.py` consulta Loki por erros da fase
  - ✅ Novo script `classify_error.py` classifica erros automaticamente:
    - Bug do SDLC Agêntico → Reporta ao owner (arbgjr)
    - Problema do projeto → Notifica usuário com decisão continuar/abortar
  - ✅ Novo script `report_sdlc_bug.sh` cria GitHub issue automaticamente
  - ✅ Análise de erros ANTES de avaliar gate (previne avanço com problemas)

  **Notificações ao usuário**:
  - 🐛 Bugs do SDLC: Aviso + auto-report ao owner
  - ⚠️  Problemas do projeto: Prompt "Continuar mesmo com problemas? (y/N)"
  - ✓ Decisão consciente do usuário sobre prosseguir

### Changed

- **gate-check.md** - Adicionada etapa 3 (PRÉ-GATE) antes da avaliação:
  1. Consulta Loki por erros
  2. Classifica erros (SDLC vs projeto)
  3. Notifica usuário e permite decisão
  4. Reporta bugs do SDLC ao owner
  5. Só então avalia gate

- **settings.json** - Adicionado hook `query-phase-learnings.sh` ao UserPromptSubmit

### Technical Details

**Arquivos criados**:
- `.claude/hooks/query-phase-learnings.sh` (142 linhas)
- `.claude/skills/session-analyzer/scripts/query_phase_errors.py` (182 linhas)
- `.claude/skills/session-analyzer/scripts/classify_error.py` (183 linhas)
- `.claude/skills/session-analyzer/scripts/report_sdlc_bug.sh` (107 linhas)

**Arquivos modificados**:
- `.claude/commands/gate-check.md` - Adicionada análise pré-gate (linhas 36-69)
- `.claude/settings.json` - Adicionado hook UserPromptSubmit (linha 134)

**Fluxo completo**:
```
INÍCIO → Consulta RAG learnings → Exibe ao usuário
   ↓
TRABALHO → Logs enviados ao Loki
   ↓
FIM → Consulta Loki erros → Classifica → Notifica → Decide → Avalia gate
   ↓
APÓS GATE → Extrai learnings → Grava no RAG
```

**Padrões de classificação**:
- SDLC bugs: `.claude/`, `manifest.json not found`, `update-phase command not found`
- Project issues: `test failed`, `syntax error`, `npm ERR`, `docker failed`

## [1.7.7] - 2026-01-16

### Added

- **Automação GitHub completa** - Corrigidos 4 gaps críticos de integração:

  **Gap #1**: sdlc-start.md agora chama `configure-fields` após criar Project
  - Project V2 é criado com campos customizados (Phase, Priority, Story Points)
  - Fixes: Project sem campos customizados após criação

  **Gap #2**: project_manager.py agora tem comando `update-phase`
  - Novo comando detecta fase atual do projeto e atualiza campo Phase
  - Mapeia fase SDLC (0-8) para coluna do Project (Backlog → Done)
  - Fixes: gate-check.md chamava comando inexistente

  **Gap #3**: Criação automática de GitHub Issues das tasks
  - Novo script `create_issues_from_tasks.py` criado
  - Parse de tasks.md e criação automática de issues no GitHub
  - Issues atribuídas ao Milestone correto
  - Issues adicionadas ao Project V2 automaticamente
  - Opção `--assign-copilot` para atribuir ao GitHub Copilot
  - gate-check.md chama automaticamente após Phase 3 (gate-3-to-4)
  - Fixes: Tasks criadas mas nunca convertidas em GitHub Issues

  **Gap #4**: Milestone atualizado com issues criadas
  - Issues são associadas ao Milestone durante criação
  - Fixes: Milestone ficava "0 open, 0 closed"

### Fixed

- **Integração GitHub** - Workflow agora executa corretamente:
  - Phase 0: Cria Project + campos customizados + Milestone
  - Phase 3→4: Cria GitHub Issues automaticamente das tasks
  - Transições de fase: Atualiza campo Phase no Project
  - Milestone: Rastreia issues do sprint atual

### Technical Details

**Arquivos modificados**:
- `.claude/commands/sdlc-start.md` - Adiciona chamada configure-fields (linha 52-54)
- `.claude/commands/gate-check.md` - Adiciona criação de issues após gate-3-to-4 (linha 60-64)
- `.claude/skills/github-projects/scripts/project_manager.py`:
  - Adiciona função `update_phase_from_manifest()` (linha 318-406)
  - Adiciona comando `update-phase` ao argparse (linha 516-518, 575-576)
  - Adiciona import `Path` (linha 19)

**Arquivos criados**:
- `.claude/skills/github-sync/scripts/create_issues_from_tasks.py` (210 linhas)
  - Parse de tasks.md
  - Criação de issues via gh CLI
  - Adição ao Project V2
  - Atribuição ao Milestone

**Evidências do problema** (projeto satra):
- current_phase: 4, gates 0-to-5 passados
- tasks.md criado com 17+ tarefas
- MAS: 0 issues no GitHub, Project vazio, Milestone não atualizado
- Causa: Automação inexistente

## [1.7.6] - 2026-01-16

### Fixed

- **Timestamps reais UTC** - Adicionada instrução CRÍTICA no orchestrator.md
  - Instruções movidas para `.claude/agents/orchestrator.md` (vai no pacote de release)
  - CLAUDE.md não vai no pacote, então instruções lá não funcionam
  - Agentes devem usar timestamps reais UTC com segundos, não valores fictícios
  - Fixes: Manifests com timestamps suspeitos (19:30:00, 22:00:00)

- **Release package** - Removidos README.md e CHANGELOG.md do pacote
  - Arquivos são específicos do repositório, não devem ser distribuídos
  - Apenas LICENSE é incluído no pacote de release
  - Fixes: Pacotes continham arquivos desnecessários

### Changed

- **README.md** - Atualizado badge de versão para v1.7.4

## [1.7.5] - 2026-01-16

### Fixed

- **Release package** - Tentativa de adicionar instruções de timestamp no CLAUDE.md
  - ⚠️ INCORRETO: CLAUDE.md não vai no pacote, instruções não funcionam
  - Corrigido na v1.7.6 movendo para orchestrator.md

## [1.7.4] - 2026-01-16

### Added

- **rag-curator skill** - Curador do corpus RAG para indexação automática de conhecimento
  - Criado `index_adrs.py` para copiar ADRs de projetos para corpus
  - Indexação automática executada em cada gate-check
  - Suporte para indexar projeto específico ou todos os projetos
  - Estrutura completa: `.agentic_sdlc/corpus/nodes/{decisions,learnings,concepts,patterns}`

### Fixed

- **gate-check command** - Corrigido comando do session-analyzer
  - Alterado de `analyze.py` para `analyze.sh` (comando correto)
  - Adicionada chamada ao rag-curator após session-analyzer
  - Fixes: ADRs criados não eram indexados automaticamente no corpus RAG

- **Estrutura do corpus** - Atualizada para v1.4.0
  - Criado `corpus/nodes/` com subdiretorios: decisions/, learnings/, concepts/, patterns/
  - Fixes: Skills graph-navigator e github-wiki esperavam `nodes/` mas não existia

## [1.7.3] - 2026-01-16

### Fixed

- **Compatibilidade com Python 3** - Corrigido uso de `python` para `python3` em todos os scripts
  - Substituído `python` por `python3` em documentação (CLAUDE.md, skills, agents, commands)
  - Afetados: github-sync, github-projects, graph-navigator, decay-scoring, session-analyzer, alignment-workflow
  - Total: 15 arquivos corrigidos (124 linhas alteradas)
  - Fixes: `python: command not found` em ambientes onde `python` não está disponível

## [1.7.2] - 2026-01-16

### Fixed

- **memory-manager skill** - Scripts ausentes causavam erro ao executar SDLC
  - Criado `memory_ops.py` com todas as operações de memória (save_decision, load_decision, save_learning, etc)
  - Criado `memory_store.py` como wrapper/alias para compatibilidade
  - Criado `__init__.py` para permitir import como pacote Python
  - Adicionado `README.md` com documentação e exemplos de uso
  - Corrigido uso de `datetime.utcnow()` deprecado para `datetime.now(timezone.utc)`
  - Estrutura de armazenamento em `.agentic_sdlc/` conforme v1.2.0

## [1.7.0] - 2026-01-15

### Added

- **Structured Logging System** (`sdlc_logging.py`)
  - JSON formatter for Loki ingestion
  - Loki Push API handler with batching
  - Correlation IDs (auto-generated or inherited)
  - Context managers for operations (`log_operation`)
  - Specialized functions: `log_phase_transition`, `log_gate_evaluation`, `log_security_event`
  - Console formatter with colors for development
  - Environment variables: `SDLC_LOG_LEVEL`, `SDLC_LOKI_URL`, `SDLC_LOKI_ENABLED`, `SDLC_JSON_LOGS`

- **OpenTelemetry Tracing** (`sdlc_tracing.py`)
  - Tempo integration via OTLP HTTP (port 4318)
  - Span creation and context propagation
  - Graceful degradation when OpenTelemetry not installed
  - Trace context injection/extraction for distributed tracing
  - Environment variables: `SDLC_TRACE_ENABLED`, `SDLC_TEMPO_URL`

- **Shell Logging Utilities** (`logging_utils.sh`)
  - JSON structured output for Loki
  - Async push to Loki Push API
  - Correlation ID management across scripts
  - Operation timing (`sdlc_operation_start`, `sdlc_operation_end`)
  - Legacy compatibility: `log_info`, `log_error`, `log_warn`, `log_ok`
  - Context management: `sdlc_set_context`, `sdlc_new_correlation_id`

- **Centralized Configuration** (`logging.yml`)
  - Handler configuration (console, file, loki)
  - Tracing settings
  - Label definitions for Loki
  - Logger overrides per module

- **Grafana Dashboard** (`sdlc-overview.json`)
  - Log Volume by Level (timeseries)
  - Errors by Skill (bar gauge)
  - Activity by SDLC Phase (stat)
  - Gate Evaluations (logs)
  - Security Events (logs)
  - Live Logs with JSON parsing
  - Variables: skill, phase, level

- **New Directory Structure**
  - `.claude/lib/python/` - Python logging modules
  - `.claude/lib/shell/` - Shell logging utilities
  - `.claude/config/logging/` - Configuration and dashboards

### Changed

- **All 13 Shell Hooks** migrated to use structured logging:
  - `validate-commit.sh` (skill=git-hooks, phase=5)
  - `auto-branch.sh` (skill=git-hooks, phase=5)
  - `detect-phase.sh` (skill=orchestrator)
  - `check-gate.sh` (skill=gate-evaluator)
  - `auto-migrate.sh` (skill=memory-manager)
  - `detect-documents.sh` (skill=document-processor, phase=0)
  - `ensure-feature-branch.sh` (skill=git-hooks, phase=5)
  - `phase-commit-reminder.sh` (skill=phase-commit)
  - `auto-decay-recalc.sh` (skill=decay-scoring)
  - `auto-graph-sync.sh` (skill=graph-navigator)
  - `detect-adr-need.sh` (skill=adr-author, phase=3)
  - `track-rag-access.sh` (skill=rag-query)
  - `update-project-timestamp.sh` (skill=memory-manager)

- Python scripts can gradually adopt logging via `from sdlc_logging import get_logger`

### Documentation

- Added Observability section to README.md
- Added v1.7.0 highlights to README.md
- Updated project structure documentation
- Updated CLAUDE.md with logging references

## [1.6.1] - 2026-01-14

### Changed

- **Release Pipeline** (`release.yml`)
  - Removed `CLAUDE.md` from package (project-specific, not distributable)
  - Added `CHANGELOG.md` and `LICENSE` to package
  - Excluded `\.agentic_sdlc/docs/examples/` from package (development only)
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

- Updated release pipeline to include complete `\.agentic_sdlc/docs/` structure
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

[Unreleased]: https://github.com/arbgjr/sdlc_agentico/compare/v3.0.3...HEAD
[3.0.3]: https://github.com/arbgjr/sdlc_agentico/compare/v3.0.2...v3.0.3
[3.0.2]: https://github.com/arbgjr/sdlc_agentico/compare/v3.0.1...v3.0.2
[3.0.1]: https://github.com/arbgjr/sdlc_agentico/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/arbgjr/sdlc_agentico/compare/v2.3.3...v3.0.0
[1.7.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/arbgjr/sdlc_agentico/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/arbgjr/sdlc_agentico/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arbgjr/sdlc_agentico/releases/tag/v1.0.0
