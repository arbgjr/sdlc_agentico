<!-- Core Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-red.svg)](https://github.com/arbgjr/sdlc_agentico/releases/tag/v2.0.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

<!-- AI Compatibility -->
[![Claude Code](https://img.shields.io/badge/Compatible%20with%20Claude%20Code-white?logo=claude)](https://code.claude.com/docs/en/sub-agents)
[![Github Copilot](https://img.shields.io/badge/Compatible%20with%20Github%20Copilot-black?logo=githubcopilot)](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)

<!-- CI/CD & Quality -->
[![Tests v2.0](https://github.com/arbgjr/sdlc_agentico/actions/workflows/test-v2.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/test-v2.yml)
[![Doc Validation](https://github.com/arbgjr/sdlc_agentico/actions/workflows/validate-docs.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/validate-docs.yml)
[![CI](https://github.com/arbgjr/sdlc_agentico/actions/workflows/ci.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/ci.yml)
[![Release](https://github.com/arbgjr/sdlc_agentico/actions/workflows/release.yml/badge.svg)](https://github.com/arbgjr/sdlc_agentico/actions/workflows/release.yml)

<!-- Community & Stats -->
[![GitHub Stars](https://img.shields.io/github/stars/arbgjr/sdlc_agentico?style=social)](https://github.com/arbgjr/sdlc_agentico/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/arbgjr/sdlc_agentico?style=social)](https://github.com/arbgjr/sdlc_agentico/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/pulls)

<!-- Maintenance & Activity -->
[![Last Commit](https://img.shields.io/github/last-commit/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/commits/main)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/arbgjr/sdlc_agentico/graphs/commit-activity)
[![Contributors](https://img.shields.io/github/contributors/arbgjr/sdlc_agentico)](https://github.com/arbgjr/sdlc_agentico/graphs/contributors)

<p align="center">
  <img src=".agentic_sdlc/logo.png" alt="SDLC Agêntico Logo" width="400">
</p>

# SDLC Agêntico

Sistema de desenvolvimento de software orientado por agentes de IA que automatiza e coordena todo o ciclo de vida do desenvolvimento.

## O Que É

O SDLC Agêntico é um framework que usa **37 agentes especializados** (33 orquestrados + 4 consultivos) para guiar seu projeto através de **9 fases (0-8)** do ciclo de desenvolvimento, desde a ideia inicial até a operação em produção.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SDLC AGÊNTICO v2.0.0                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Ideia → [Intake] → [Discovery] → [Requirements] → [Architecture]       │
│                                         ↓                               │
│  Produção ← [Release] ← [Quality] ← [Implementation] ← [Planning]       │
│                                                                         │
│  37 Agentes | 9 Fases | Quality Gates | Security by Design              │
│  Auto-Branch | IaC Generation | Doc Generation | GitHub Copilot         │
│                                                                         │
│  📦 v2.0.0: Project Import | 30 Tech Detection | sdlc-import skill      │
│  📚 v1.9.0: Document Enrichment | Research Integration | Versioning     │
│  🔄 v1.8.0: Auto-Update System | Impact Analysis | Version Checker      │
│  📊 v1.7.0: Structured Logging | Loki/Tempo/Grafana Integration        │
│  🔗 v1.6.0: GitHub Projects V2 | Milestones | Wiki Sync                 │
│  ⏰ v1.5.0: Decay Scoring | Content Freshness | Curation Triggers       │
│  🔍 v1.4.0: Semantic Graph | Hybrid Search | Graph Visualization        │
│  📄 v1.3.0: Document Processing | Frontend E2E | Anthropic Patterns     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Requisitos

- **Python** 3.11+
- **Node.js** 18+
- **Claude Code** CLI
- **GitHub CLI** (`gh`)
- **Copilot Pro+/Business/Enterprise** (para coding agent)

## Instalação

### Opção 1: Download Direto (Linux/macOS/WSL)

```bash
# Definir versão desejada (consulte releases para última versão)
VERSION="v2.0.0"

# Download e extração (preserva permissões de execução)
curl -fsSL "https://github.com/arbgjr/sdlc_agentico/releases/download/${VERSION}/sdlc-agentico-${VERSION}.tar.gz" | tar -xzf -

# Executar setup
./.scripts/setup-sdlc.sh
```

> **WSL2**: Use os mesmos comandos acima. O tar.gz preserva as permissões Unix corretamente.
>
> **Releases**: https://github.com/arbgjr/sdlc_agentico/releases

### Opção 2: Via Script Automático

```bash
# Última versão (one-liner)
curl -fsSL https://raw.githubusercontent.com/arbgjr/sdlc_agentico/main/.scripts/setup-sdlc.sh | bash -s -- --from-release

# Versão específica
curl -fsSL https://raw.githubusercontent.com/arbgjr/sdlc_agentico/main/.scripts/setup-sdlc.sh | bash -s -- --from-release --version v2.0.0
```

Se o diretório `.claude/` já existir, o script perguntará o que fazer:
1. Fazer backup e substituir (recomendado)
2. Mesclar (manter existentes, adicionar novos)
3. Substituir sem backup
4. Cancelar

### Opção 3: Clone do Repositório

```bash
# Clonar repositório
git clone https://github.com/arbgjr/sdlc_agentico.git
cd sdlc_agentico

# Executar setup
./.scripts/setup-sdlc.sh
```

### Ferramentas de Segurança (Opcional)

Para usar os recursos de security scanning (`/security-scan`, security gates):

```bash
# Instalar todas as ferramentas
./.scripts/install-security-tools.sh --all

# Ou instalar individualmente
./.scripts/install-security-tools.sh --semgrep   # SAST
./.scripts/install-security-tools.sh --trivy     # SCA/Container
./.scripts/install-security-tools.sh --gitleaks  # Secret Scanner
```

### Instalação Manual

```bash
pip install uv
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
npm install -g @anthropic-ai/claude-code
gh auth login
```

## Quick Start

```bash
# 1. Instalar dependências
./.scripts/setup-sdlc.sh

# 2. Iniciar Claude Code
claude

# 3. Escolher o fluxo adequado
/quick-fix "Corrigir bug X"           # Level 0 - Bug fixes
/new-feature "Nome da feature"        # Level 1 - Features simples
/sdlc-start "Criar nova API"          # Level 2/3 - Projetos completos
```

## Funcionalidades

### Agentes Especializados

| Fase | Agentes | O Que Fazem |
|------|---------|-------------|
| **Preparação** | intake-analyst, compliance-guardian | Analisam demandas, validam compliance |
| **Descoberta** | domain-researcher, doc-crawler, rag-curator | Pesquisam tecnologias, gerenciam conhecimento |
| **Requisitos** | product-owner, requirements-analyst, ux-writer | Priorizam backlog, escrevem user stories |
| **Arquitetura** | system-architect, adr-author, data-architect, threat-modeler, **iac-engineer** | Definem design, documentam decisões, analisam segurança, geram IaC |
| **Planejamento** | delivery-planner | Planejam sprints, estimam esforço |
| **Implementação** | code-author, code-reviewer, test-author, **iac-engineer** | Escrevem código, revisam, criam testes, aplicam IaC |
| **Qualidade** | qa-analyst, security-scanner, performance-analyst | Validam qualidade, escaneiam vulnerabilidades |
| **Release** | release-manager, cicd-engineer, change-manager, **doc-generator** | Coordenam releases, gerenciam pipelines, geram docs |
| **Operação** | incident-commander, rca-analyst, metrics-analyst, observability-engineer | Gerenciam incidentes, analisam causa raiz, rastreiam métricas |

### Quality Gates

Cada transição de fase passa por um **quality gate** que valida:
- Artefatos obrigatórios existem
- Critérios de qualidade foram atendidos
- Aprovações necessárias foram obtidas

### Security by Design

Segurança integrada em todas as fases via `security-gate.yml`:
- **Fase 2**: Requisitos de segurança documentados
- **Fase 3**: Threat model (STRIDE), riscos HIGH/CRITICAL mitigados
- **Fase 5**: Sem secrets hardcoded, validação de input
- **Fase 6**: SAST/SCA executados sem vulnerabilidades críticas
- **Fase 7**: Checklist de segurança completo

**Gatilhos de Escalação Automática**:
- CVSS >= 7.0
- Exposição de PII
- Mudanças em autenticação/autorização
- Alterações em criptografia
- Novos endpoints públicos

### Níveis de Complexidade (BMAD)

| Level | Nome | Comando | Quando Usar | Fases |
|-------|------|---------|-------------|-------|
| 0 | Quick Flow | `/quick-fix` | Bug fix, typo | 5, 6 |
| 1 | Feature | `/new-feature` | Feature simples | 2, 5, 6 |
| 2 | BMAD Method | `/sdlc-start` | Produto/serviço novo | 0-7 |
| 3 | Enterprise | `/sdlc-start` | Crítico, compliance | 0-8 + aprovações |

### Integração GitHub Copilot

O sistema se integra com o **GitHub Copilot Coding Agent**:

```bash
# Criar issues e atribuir ao Copilot
/sdlc-create-issues --assign-copilot

# O Copilot implementa automaticamente e cria PRs
```

### Integração GitHub Nativa (v1.6.0)

O sistema se integra nativamente com:

| Recurso | Automação |
|---------|-----------|
| **GitHub Projects V2** | Criado automaticamente no início do SDLC, atualizado a cada fase |
| **Milestones** | Criado para cada sprint, fechado no release |
| **Wiki** | Sincronizada com ADRs e documentação do projeto |
| **Labels** | Gerenciados automaticamente (`phase:0-8`, `complexity:0-3`, `type:*`) |

```bash
# Ver dashboard consolidado
/github-dashboard

# Sincronizar documentação com Wiki
/wiki-sync

# Criar issues com labels e milestone
/sdlc-create-issues
```

**Fluxo Automático:**
1. `/sdlc-start` → Cria Project V2 + Milestone "Sprint 1"
2. Cada transição de fase → Atualiza campo "Phase" das issues
3. `/release-prep` → Fecha Milestone + Sincroniza Wiki

### Observabilidade (v1.7.0)

O sistema inclui logging estruturado integrado com a stack de observabilidade:

| Componente | Porta | Propósito |
|------------|-------|-----------|
| **Loki** | 3100 | Agregação de logs |
| **Tempo** | 4318 | Tracing distribuído (OTLP) |
| **Grafana** | 3003 | Visualização e dashboards |

**Características:**
- JSON estruturado para ingestão no Loki
- Correlation IDs automáticos para rastreamento
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Labels: `app`, `skill`, `phase`, `level`, `script`
- Dashboard pré-configurado em `.claude/config/logging/dashboards/`

**Variáveis de Ambiente:**
```bash
SDLC_LOG_LEVEL=DEBUG              # Nível de log (default: DEBUG)
SDLC_LOKI_ENABLED=true            # Habilita envio ao Loki
SDLC_LOKI_URL=http://localhost:3100
SDLC_TRACE_ENABLED=true           # Habilita tracing
SDLC_TEMPO_URL=http://localhost:4318
```

**Uso em Python:**
```python
from sdlc_logging import get_logger, log_operation
logger = get_logger(__name__, skill="decay-scoring", phase=6)
logger.info("Processing node", extra={"node_id": "ADR-001"})

with log_operation(logger, "batch_processing"):
    # Operação cronometrada automaticamente
    process_batch()
```

**Uso em Shell:**
```bash
source .claude/lib/shell/logging_utils.sh
sdlc_set_context skill="git-hooks" phase="5"
sdlc_log_info "Validating commit" "commit_hash=$COMMIT_HASH"
```

### Parallel Workers (v2.0) ⚡ NEW

Execução paralela de tarefas em Phase 5 com **2.5x speedup**:

| Feature | Benefício |
|---------|-----------|
| **parallel-workers** | Git worktrees isolados, zero merge conflicts |
| **simple-memory** | Working memory cache < 100ms para fatos rápidos |
| **session-handoff** | Continuidade automática entre sessões |
| **automation-loop** | Monitoramento e transição de estados automática |

**Usage:**
```bash
# Automático: orchestrator detecta e spawna em Phase 4→5 (Complexity 2+)
# Manual:
/parallel-spawn --batch .agentic_sdlc/projects/current/tasks.yml

# Monitoring:
python3 .claude/skills/parallel-workers/scripts/loop.py --project sdlc_agentico
```

**Architecture:**
- Workers isolados em `~/.worktrees/{project}/{task-id}/`
- State machine: NEEDS_INIT → WORKING → PR_OPEN → MERGED
- Platform independent (Linux-first)
- Full observability via Grafana dashboard

### Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões e mudanças.

**Destaques da v2.0.0:**
- **sdlc-import skill**: Importação e engenharia reversa de projetos existentes
- **Language detection expansion**: 10 → 30 tecnologias detectadas (3x aumento)
- **Backend/Infrastructure (9 novas)**: C++, Rust enhanced, Ansible, Jenkins, Chef, Puppet, Gradle, Selenium, Bicep
- **Frontend/Testing (6 novas)**: Playwright, TypeScript enhanced, Vue.js, Svelte, Tailwind CSS, Vite/Webpack
- **Mobile (5 novas)**: React Native, Flutter/Dart, Swift, Kotlin enhanced, Xamarin
- **Production ready**: 255/255 testes passando, zero regressões
- **LSP integration**: clangd-lsp (C++), dart-lsp (Flutter), sourcekit-lsp (Swift)
- **Disambiguation logic**: Chef/Ruby, Ansible/YAML, Gradle/Kotlin
- **Configuration-driven**: language_patterns.yml com 669 linhas (+383)
- **Novo agent**: sdlc-importer para Phase 0 (Preparation)
- **Quality gate**: sdlc-import-gate.yml com 6 validações críticas

**Destaques da v1.7.0:**
- Logging estruturado com integração Loki/Tempo/Grafana
- Módulos Python e Shell para logging consistente
- Dashboard Grafana pré-configurado para SDLC
- Correlation IDs para rastreamento de requisições
- Tracing distribuído com OpenTelemetry

**Destaques da v1.6.0:**
- Integração nativa com GitHub Projects V2
- Milestones automatizados por sprint
- Sincronização de documentação com GitHub Wiki
- Dashboard consolidado do projeto (`/github-dashboard`)

**Destaques da v1.5.0:**
- Decay scoring para freshness de conhecimento
- Sugestões automáticas de curadoria para conteúdo obsoleto
- Resultados de busca priorizados por freshness
- Quality gate de saúde do corpus

## Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/sdlc-start` | Inicia novo workflow SDLC (Level 2/3) |
| `/quick-fix` | Fluxo rápido para bug fixes (Level 0) |
| `/new-feature` | Fluxo para features simples (Level 1) |
| `/phase-status` | Mostra status da fase atual |
| `/gate-check` | Verifica quality gate |
| `/adr-create` | Cria Architecture Decision Record |
| `/security-scan` | Executa scan de segurança |
| `/release-prep` | Prepara release |
| `/incident-start` | Inicia gestão de incidente |
| `/sdlc-create-issues` | Cria issues no GitHub |
| `/decay-status` | Mostra saúde do corpus RAG |
| `/validate-node` | Marca node como validado |
| `/github-dashboard` | Dashboard consolidado do GitHub |
| `/wiki-sync` | Sincroniza documentação com Wiki |
| `/alignment-status` | Mostra status de ODRs e trade-offs |
| `/logs-query` | Consulta logs estruturados (Loki) |
| `/odr-create` | Cria Organizational Decision Record |
| `/sdlc-flags` | Gerencia feature flags do SDLC |
| `/sdlc-version` | Mostra versão e changelog do framework |
| `/simulate` | Simula cenários de decisão arquitetural |

## Estrutura do Projeto

```
.claude/
├── agents/           # 37 agentes especializados (33 + 4 consultivos)
├── skills/           # 28 skills reutilizáveis
├── commands/         # 23 comandos do usuário
├── hooks/            # 18 hooks de automação
├── lib/              # Bibliotecas compartilhadas (v1.7.0)
│   ├── python/       # sdlc_logging.py, sdlc_tracing.py
│   └── shell/        # logging_utils.sh
├── config/           # Configurações centralizadas
│   └── logging/      # logging.yml, dashboards/
└── settings.json     # Configuração central

.agentic_sdlc/        # Artefatos do SDLC (NOVO)
├── projects/         # Projetos gerenciados
├── references/       # Documentos de referência (legal, técnico, business)
├── templates/        # Templates (ADR, spec, threat-model)
├── corpus/           # Corpus de conhecimento RAG
└── sessions/         # Histórico de sessões

.scripts/
├── setup-sdlc.sh             # Script de instalação
└── install-security-tools.sh # Ferramentas de segurança opcionais

.docs/
├── guides/                   # Guias de uso
│   ├── quickstart.md         # Guia rápido
│   ├── infrastructure.md     # Setup e integração
│   └── troubleshooting.md    # Resolução de problemas
├── sdlc/                     # Documentação do SDLC
│   ├── agents.md             # Catálogo de agentes
│   ├── commands.md           # Referência de comandos
│   └── overview.md           # Visão geral do framework
└── engineering-playbook/     # Padrões de engenharia
    ├── manual-desenvolvimento/ # Standards, práticas, qualidade
    └── stacks/               # .NET, Python, Rust, DevOps
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [quickstart.md](.docs/guides/quickstart.md) | Guia rápido de início |
| [infrastructure.md](.docs/guides/infrastructure.md) | Setup e integração |
| [agents.md](.docs/sdlc/agents.md) | Catálogo de agentes |
| [commands.md](.docs/sdlc/commands.md) | Referência de comandos |
| [engineering-playbook](.docs/engineering-playbook/) | Padrões de engenharia |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir |

## Exemplo de Uso

```bash
# 1. Iniciar workflow para nova feature
claude "/sdlc-start Portal de histórico de pedidos para clientes"

# 2. O intake-analyst analisa e classifica (Level 2)
# 3. domain-researcher pesquisa tecnologias
# 4. requirements-analyst escreve user stories
# 5. system-architect define arquitetura
# 6. delivery-planner planeja sprint

# 7. Criar issues para implementação
claude "/sdlc-create-issues --assign-copilot"

# 8. Copilot implementa e cria PRs
# 9. code-reviewer revisa
# 10. security-scanner valida
# 11. release-manager coordena deploy
```

## Métricas Rastreadas

O sistema rastreia automaticamente:

- **DORA Metrics**: Deployment frequency, lead time, CFR, MTTR
- **Code Quality**: Coverage, complexity, tech debt
- **Process**: PR cycle time, review time, rework rate

## Limitações Conhecidas

### Ambiente
- **Sistema Operacional**: Testado em Windows via WSL2.
- **Node.js**: Requer versão 18 ou superior
- **Python**: Requer versão 3.11 ou superior

### Dependências Externas
- **Claude Code CLI**: Requer conta Anthropic ativa com acesso ao Claude Code
- **Spec Kit**: Opcional, mas necessário para comandos de especificação
- **GitHub CLI (gh)**: Necessário para integração com GitHub e Copilot Coding Agent
- **Ferramentas de Segurança**: gitleaks, semgrep, trivy são opcionais (instaláveis via `.scripts/install-security-tools.sh`)

### Funcionalidades
- **Lightweight Agents**: 4 agentes (failure-analyst, interview-simulator, requirements-interrogator, tradeoff-challenger) são minimalistas e dependem da skill `system-design-decision-engine`
- **Gates de Qualidade**: Alguns checks usam padrões glob que podem não encontrar arquivos em estruturas não-padrão
- **Auto-Branch**: Requer que o repositório tenha permissão de push para criar branches

### Integrações
- **GitHub Copilot Coding Agent**: Requer GitHub Copilot Pro+/Business/Enterprise
- **RAG Corpus**: Funcionalidade experimental, corpus precisa ser populado manualmente

## Troubleshooting

Consulte [.docs/guides/troubleshooting.md](.docs/guides/troubleshooting.md) para resolução de problemas comuns.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## Licença

[MIT](LICENSE)

---

**Criado em conjunto com** Claude Code + GitHub Copilot
