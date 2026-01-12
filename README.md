# SDLC Agêntico

Sistema de desenvolvimento de software orientado por agentes de IA que automatiza e coordena todo o ciclo de vida do desenvolvimento.

## O Que É

O SDLC Agêntico é um framework que usa **26 agentes especializados** para guiar seu projeto através de **8 fases** do ciclo de desenvolvimento, desde a ideia inicial até a operação em produção.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SDLC AGÊNTICO                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Ideia → [Intake] → [Discovery] → [Requirements] → [Architecture]      │
│                                         ↓                               │
│  Produção ← [Release] ← [Quality] ← [Implementation] ← [Planning]      │
│                                                                         │
│  26 Agentes | 8 Fases | Quality Gates | GitHub Copilot Integration     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Instalar dependências
./.scripts/setup-sdlc.sh

# 2. Iniciar Claude Code
claude

# 3. Iniciar um workflow
/sdlc-start "Criar API de autenticação com OAuth2"
```

## Funcionalidades

### Agentes Especializados

| Fase | Agentes | O Que Fazem |
|------|---------|-------------|
| **Preparação** | intake-analyst, compliance-guardian | Analisam demandas, validam compliance |
| **Descoberta** | domain-researcher, rag-curator | Pesquisam tecnologias, gerenciam conhecimento |
| **Requisitos** | product-owner, requirements-analyst | Priorizam backlog, escrevem user stories |
| **Arquitetura** | system-architect, adr-author, threat-modeler | Definem design, documentam decisões, analisam segurança |
| **Planejamento** | delivery-planner | Planejam sprints, estimam esforço |
| **Implementação** | code-author, code-reviewer, test-author | Escrevem código, revisam, criam testes |
| **Qualidade** | qa-analyst, security-scanner | Validam qualidade, escaneiam vulnerabilidades |
| **Release** | release-manager, cicd-engineer | Coordenam releases, gerenciam pipelines |
| **Operação** | incident-commander, rca-analyst, metrics-analyst | Gerenciam incidentes, analisam causa raiz, rastreiam métricas |

### Quality Gates

Cada transição de fase passa por um **quality gate** que valida:
- Artefatos obrigatórios existem
- Critérios de qualidade foram atendidos
- Aprovações necessárias foram obtidas

### Níveis de Complexidade (BMAD)

| Level | Nome | Quando Usar | Fases |
|-------|------|-------------|-------|
| 0 | Quick Flow | Bug fix, typo | 5, 6 |
| 1 | Feature | Feature simples | 2, 5, 6 |
| 2 | BMAD Method | Produto/serviço novo | 0-7 |
| 3 | Enterprise | Crítico, compliance | 0-8 + aprovações |

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
| `/sdlc-start` | Inicia novo workflow SDLC |
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
├── agents/           # 26 agentes especializados
├── skills/           # 8 skills reutilizáveis
├── commands/         # 8 comandos do usuário
├── hooks/            # 4 hooks de validação
├── memory/           # Persistência de contexto
└── settings.json     # Configuração central

.scripts/
└── setup-sdlc.sh     # Script de instalação

.docs/
├── AGENTS.md         # Catálogo de agentes
├── COMMANDS.md       # Referência de comandos
├── QUICKSTART.md     # Guia rápido
├── INFRASTRUCTURE.md # Setup e integração
└── playbook.md       # Playbook do SDLC
```

## Requisitos

- **Python** 3.11+
- **Node.js** 18+
- **Claude Code** CLI
- **GitHub CLI** (`gh`)
- **Copilot Pro+/Business/Enterprise** (para coding agent)

## Instalação

```bash
# Automática (recomendado)
./.scripts/setup-sdlc.sh

# Manual
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
