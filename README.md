[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# SDLC Agêntico

Sistema de desenvolvimento de software orientado por agentes de IA que automatiza e coordena todo o ciclo de vida do desenvolvimento.

## O Que É

O SDLC Agêntico é um framework que usa **34 agentes especializados** (30 orquestrados + 4 consultivos) para guiar seu projeto através de **9 fases (0-8)** do ciclo de desenvolvimento, desde a ideia inicial até a operação em produção.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SDLC AGÊNTICO v2.0                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Ideia → [Intake] → [Discovery] → [Requirements] → [Architecture]      │
│                                         ↓                               │
│  Produção ← [Release] ← [Quality] ← [Implementation] ← [Planning]      │
│                                                                         │
│  34 Agentes | 9 Fases | Quality Gates | Security by Design             │
│  Auto-Branch | IaC Generation | Doc Generation | GitHub Copilot        │
│  Phase Commits | Session Learning | Stakeholder Reviews (v1.2.0)       │
│  Document Processing | Frontend E2E Testing | Patterns (v1.3.0)        │
│  Semantic Graph | Hybrid Search | Graph Visualization (v1.4.0)         │
│  Decay Scoring | Content Freshness | Curation Triggers (v1.5.0)        │
│  GitHub Projects | Milestones | Wiki Sync | Dashboard (v1.6.0)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
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

### Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo de versões e mudanças.

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

## Estrutura do Projeto

```
.claude/
├── agents/           # 34 agentes especializados (30 + 4 consultivos)
├── skills/           # 19 skills reutilizáveis (+3 em v1.6.0)
├── commands/         # 12 comandos do usuário (+2 em v1.6.0)
├── hooks/            # 9 hooks de automação
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
├── engineering-playbook/     # Padrões de engenharia
│   ├── manual-desenvolvimento/ # Standards, práticas, qualidade
│   └── stacks/               # .NET, Python, Rust, DevOps
└── examples/                 # Exemplos de uso
```

## Requisitos

- **Python** 3.11+
- **Node.js** 18+
- **Claude Code** CLI
- **GitHub CLI** (`gh`)
- **Copilot Pro+/Business/Enterprise** (para coding agent)

## Instalação

### Opção 1: Instalação a partir de Release (Recomendado)

```bash
# Última versão (one-liner)
curl -fsSL https://raw.githubusercontent.com/arbgjr/mice_dolphins/main/.scripts/setup-sdlc.sh | bash -s -- --from-release

# Versão específica
curl -fsSL https://raw.githubusercontent.com/arbgjr/mice_dolphins/main/.scripts/setup-sdlc.sh | bash -s -- --from-release --version v1.2.0
```

Se o diretório `.claude/` já existir, o script perguntará o que fazer:
1. Fazer backup e substituir (recomendado)
2. Mesclar (manter existentes, adicionar novos)
3. Substituir sem backup
4. Cancelar

### Opção 2: Clone do Repositório

```bash
# Clonar repositório
git clone https://github.com/arbgjr/mice_dolphins.git
cd mice_dolphins

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
- **Sistema Operacional**: Testado em Linux e macOS. Windows via WSL2 é suportado, mas não testado extensivamente
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

Consulte [.docs/TROUBLESHOOTING.md](.docs/TROUBLESHOOTING.md) para resolução de problemas comuns.

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## Licença

[MIT](LICENSE)

---

**Criado em conjunto com** Claude Code + GitHub Copilot
