# Changelog

All notable changes to SDLC Agêntico will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- `.scripts/install-security-tools.sh` (+92 linhas, -17 linhas)

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

[Unreleased]: https://github.com/arbgjr/mice_dolphins/compare/v1.7.0...HEAD
[1.7.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/arbgjr/mice_dolphins/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/arbgjr/mice_dolphins/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arbgjr/mice_dolphins/releases/tag/v1.0.0
