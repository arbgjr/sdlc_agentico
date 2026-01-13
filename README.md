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

## Estrutura do Projeto

```
.claude/
├── agents/           # 34 agentes especializados (30 + 4 consultivos)
├── skills/           # 9 skills reutilizáveis
├── commands/         # 10 comandos do usuário
├── hooks/            # 5 hooks de automação
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
├── AGENTS.md         # Catálogo de agentes
├── COMMANDS.md       # Referência de comandos
├── QUICKSTART.md     # Guia rápido
├── INFRASTRUCTURE.md # Setup e integração
├── DESENVOLVIMENTO.md # Padrões de desenvolvimento C#
└── playbook.md       # Playbook do SDLC
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
curl -fsSL https://raw.githubusercontent.com/arbgjr/mice_dolphins/main/.scripts/setup-sdlc.sh | bash -s -- --from-release --version v1.0.0
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
| [QUICKSTART.md](.docs/QUICKSTART.md) | Guia rápido de início |
| [INFRASTRUCTURE.md](.docs/INFRASTRUCTURE.md) | Setup e integração |
| [AGENTS.md](.docs/AGENTS.md) | Catálogo de agentes |
| [COMMANDS.md](.docs/COMMANDS.md) | Referência de comandos |
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

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## Licença

MIT

---

**Criado com** Claude Code + GitHub Copilot
