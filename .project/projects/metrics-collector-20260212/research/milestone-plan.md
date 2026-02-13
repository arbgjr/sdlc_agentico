# Plano de Milestones — SDLC Agêntico

**Versão atual:** v3.0.3  
**Total de issues abertas:** 119 (100 originais + 8 Core Extraction + 11 Dual Compat)  
**Milestones planejados:** 11  
**Data do planejamento:** 2026-02-06  
**Última atualização:** 2026-02-06 (reorganização: Core Extraction antes de Dual Compat)

---

## Visão Geral do Roadmap

```
v3.0.3 (atual)
  │
  ├── v3.1.0  ─ sdlc-import Maturity             (9 issues)   Due: 2026-02-09
  ├── v3.2.0  ─ Agent Quality & Infrastructure    (9 issues)   Due: 2026-02-13
  ├── v3.3.0  ─ Multi-Model Intelligence          (9 issues)   Due: 2026-02-19
  ├── v3.4.0  ─ Autonomous Execution Loop        (13 issues)   Due: 2026-02-25
  ├── v3.5.0  ─ Legacy Onboarding                 (9 issues)   Due: 2026-03-03  ┐
  ├── v3.6.0  ─ Research: Skills & Patterns       (11 issues)  Due: 2026-03-03  ├ PARALELAS
  ├── v3.7.0  ─ Research: Intelligence & Memory    (6 issues)  Due: 2026-03-03  ┘
  ├── v3.8.0  ─ Research: Tools & Integration     (14 issues)  Due: 2026-03-07
  ├── v3.9.0  ─ Core Extraction & Org Setup        (8 issues)  Due: 2026-03-14
  ├── v3.10.0 ─ Dual Compatibility: copilot-ed.   (11 issues)  Due: 2026-03-19
  │
  └── v4.0.0  ─ easy-edition (Leigo-Friendly)      (9 issues)  Due: 2026-03-28
```

---

## Mapa de Paralelismo para Agentes IA

> Milestones no mesmo grupo podem ser executados simultaneamente por agentes diferentes.

```
                   SEQUENCIAL                  PARALELO
            ┌──────────────────────┐    ┌──────────────────┐
  Semana 1  │ v3.1.0 (import)     │    │                  │
            ├──────────────────────┤    │                  │
  Semana 2  │ v3.2.0 (agents)     │    │                  │
            ├──────────────────────┤    │                  │
  Semana 3  │ v3.3.0 (models)     │    │                  │
            ├──────────────────────┤    │                  │
  Semana 4  │ v3.4.0 (autonomous) │    │                  │
            ├──────────────────────┤    ├──────────────────┤
  Semana 5  │                      │    │ v3.5.0 (legacy)  │
            │                      │    │ v3.6.0 (research)│
            │                      │    │ v3.7.0 (research)│
            ├──────────────────────┤    ├──────────────────┤
  Semana 6  │ v3.8.0 (research)   │    │                  │
            ├──────────────────────┤    │                  │
  Semana 7  │ v3.9.0 (core extr.) │    │                  │
            ├──────────────────────┤    │                  │
  Semana 8  │ v3.10.0 (dual comp) │    │                  │
            ├──────────────────────┤    │                  │
  Semana 9  │ v4.0.0 (easy-ed.)   │    │                  │
            └──────────────────────┘    └──────────────────┘
```

### Regras de Dependência

| Milestone | Depende de | Pode paralelizar com | Agentes IA necessários |
|-----------|-----------|----------------------|------------------------|
| v3.1.0 | — | — | 1 |
| v3.2.0 | v3.1.0 | — | 1 |
| v3.3.0 | v3.2.0 | — | 1 |
| v3.4.0 | v3.3.0 | — | 1 |
| **v3.5.0** | **v3.4.0** | **v3.6.0, v3.7.0** | **1 (de 3)** |
| **v3.6.0** | **v3.4.0** | **v3.5.0, v3.7.0** | **1 (de 3)** |
| **v3.7.0** | **v3.4.0** | **v3.5.0, v3.6.0** | **1 (de 3)** |
| v3.8.0 | v3.6.0, v3.7.0 | — | 1 |
| v3.9.0 | v3.5.0 ~ v3.8.0 | — | 1 |
| v3.10.0 | v3.9.0 | — | 1 |
| v4.0.0 | v3.10.0 | — | 1 |

**Throughput máximo:** 3 agentes IA simultâneos na Semana 5.  
**Caminho crítico:** v3.1→v3.2→v3.3→v3.4→v3.6→v3.8→v3.9→v3.10→v4.0 (9 semanas)

---

## Milestones Detalhados

### v3.1.0 — sdlc-import Maturity (9 issues)

**Tipo de versão:** MINOR (inclui novos recursos além de bug fixes)  
**Due date:** 2026-02-09  
**Paralelismo:** Sequencial (fundação)

| # | Issue | Labels |
|---|-------|--------|
| 92 | Pattern Detection for Terraform Conventions and Database IaC | enhancement |
| 93 | Generic Diagrams - Django shown for .NET projects | bug |
| 94 | No Parallelization - Single-threaded execution | bug |
| 95 | No Metrics in CI/CD Format | bug |
| 96 | No Execution Time per Step | bug |
| 97 | Output Directory Not Configurable via CLI | bug |
| 98 | No Language Priority Configuration | bug |
| 99 | No Incremental Import | bug |
| 100 | No Rollback on Failure | bug |

**Sinergia:**
- Paralelização (#94) + Import Incremental (#99) + Rollback (#100) = **triângulo de confiabilidade**
- Métricas CI/CD (#95) + Tempo de Execução (#96) = **observabilidade**
- Output Dir (#97) + Language Priority (#98) = **configurabilidade**
- Pattern Detection (#92) + Diagramas (#93) = **precisão de análise**

---

### v3.2.0 — Agent Quality & Infrastructure (9 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.1.0  
**Due date:** 2026-02-13  
**Paralelismo:** Sequencial

| # | Issue | Labels |
|---|-------|--------|
| 78 | Review awesome-copilot for Reusable Resources | research |
| 119 | Aplicar prompt engineering oficial da Anthropic nos 38 agentes | documentation, enhancement |
| 128 | Avaliar docsify para documentação navegável | documentation, enhancement |
| 135 | Adicionar persona de pensamento crítico em agentes estratégicos | agents, enhancement |
| 136 | Adicionar campo traits ao template de agentes | agents, enhancement |
| 137 | Configurar Sequential Thinking como MCP padrão (não único) | infrastructure |
| 138 | Implementar web research graduado para validação | enhancement, security, skills |
| 139 | Documentar compatibilidade worktrees + Claude Code Agent Teams | documentation, skills |
| 140 | Implementar instalação global do framework em 3 camadas | infrastructure |

**Sinergia:**
- Prompt engineering (#119) + Pensamento crítico (#135) + Traits (#136) = **evolução de agentes**
- Sequential Thinking (#137) + Web research (#138) = **raciocínio melhorado**
- Instalação global (#140) + Docsify (#128) = **adoção facilitada**

---

### v3.3.0 — Multi-Model Intelligence (9 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.2.0  
**Due date:** 2026-02-19  
**Paralelismo:** Sequencial (depende de v3.2.0)

| # | Issue | Labels |
|---|-------|--------|
| 50 | Epic #1: Multi-Model Configuration System | type:epic |
| 53 | Task 1.1: Design Model Selection Strategy (ADR-020) | phase:3 |
| 54 | Task 1.2: Implement Model Configuration Schema | phase:5 |
| 55 | Task 1.3: Implement Model Selector Library | phase:5 |
| 56 | Task 1.4: Integrate Model Selector with Agent Execution | phase:5 |
| 57 | Task 1.5: Implement Cost Tracking Dashboard | phase:5 |
| 58 | Task 1.6: Create Model Selection Quality Gate | phase:6 |
| 75 | Task 1.7: Migration Documentation | phase:7 |
| 76 | Task 1.8: Integration Testing | phase:6 |

**Pipeline linear:** ADR (#53) → Schema (#54) → Library (#55) → Integração (#56) → Dashboard (#57) → Gate (#58) → Docs (#75) → Testes (#76)

---

### v3.4.0 — Autonomous Execution Loop (13 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.3.0 (multi-model otimiza custos da execução autônoma)  
**Due date:** 2026-02-25  
**Paralelismo:** Sequencial

| # | Issue | Labels |
|---|-------|--------|
| 80 | [EPIC] Autonomous SDLC Loop - Ralph TUI Integration | type:epic |
| 81 | Implement DAG-Based Task Scheduler | phase:5 |
| 82 | Implement Session Checkpoint with File-Based Lock | phase:5 |
| 83 | Implement Crash Recovery Mechanism | phase:5 |
| 84 | Implement Smart Parallelism Hints & Auto-Commit | phase:5 |
| 85 | Implement Real-Time Agent Tracing Parser | phase:5 |
| 86 | Implement Hierarchical Trace Visualizer (Rich) | phase:5 |
| 87 | Create /sdlc-trace Command and Monitoring Loop | phase:5 |
| 88 | Convert Agent Prompts to Handlebars Templates | phase:5 |
| 89 | Implement Plugin Discovery System | type:task |
| 90 | Implement JSONL Audit Trail Logger | type:task |
| 91 | Integration Testing & Documentation | documentation |
| 133 | Estudar padrão Ralph para execução autônoma contínua | research |

**Camadas:**
- **Execução:** DAG (#81) + Checkpoint (#82) + Recovery (#83) + Parallelism (#84)
- **Observabilidade:** Tracing (#85) + Visualizer (#86) + /sdlc-trace (#87) + Audit (#90)
- **Extensibilidade:** Handlebars (#88) + Plugins (#89)
- **Validação:** Integration Testing (#91) + Ralph Study (#133)

---

### v3.5.0 — Legacy Onboarding (9 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.4.0  
**Due date:** 2026-03-03  
**Paralelismo:** ⚡ PODE EXECUTAR EM PARALELO com v3.6.0 e v3.7.0

| # | Issue | Labels |
|---|-------|--------|
| 66 | Task 3.1: Design Reverse Engineering Architecture (ADR-022) | phase:3 |
| 67 | Task 3.2: Implement Language Detection (10 languages) | phase:5 |
| 68 | Task 3.2b: Implement IaC/DevOps/QA Detection | phase:5 |
| 69 | Task 3.3: Implement Decision Extractor | phase:5 |
| 70 | Task 3.4: Implement Architecture Visualizer | phase:5 |
| 71 | Task 3.5: Implement Threat Model Generator (STRIDE) | phase:5 |
| 72 | Task 3.6: Implement Tech Debt Detector | phase:5 |
| 73 | Task 3.7: Implement /onboard-legacy Command | phase:5 |
| 74 | Task 3.8: Create Validation Quality Gate | phase:6 |

**Pipeline:** Discovery (#66→#67→#68) → Análise (#69→#70→#71→#72) → Comando (#73) → Gate (#74)

---

### v3.6.0 — Research: Skills & Patterns (11 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.4.0  
**Due date:** 2026-03-03  
**Paralelismo:** ⚡ PODE EXECUTAR EM PARALELO com v3.5.0 e v3.7.0

| # | Issue | Labels |
|---|-------|--------|
| 101 | Importar skills selecionadas de everything-claude-code | research |
| 102 | Estudar padrões de orquestração swarm do claude-flow | research |
| 103 | Integrar oh-my-claudecode como plugin de modos de execução | research |
| 104 | Integrar Skill_Seekers para geração automática de skills | research |
| 105 | Avaliar OpenSkills como sistema de distribuição de skills | research |
| 108 | Catalogar e importar skills do awesome-claude-skills | research |
| 109 | Importar skills de pesquisa, otimização e verificação | research |
| 110 | Estudar Learning Lab e CCPI do plugins-plus-skills | research |
| 111 | Implementar GitHub Actions agents e skill evaluation | research |
| 120 | Estudar padrões de execução paralela do Auto-Claude | research |
| 134 | Incorporar Agentic Design Patterns ao corpus de conhecimento | research |

---

### v3.7.0 — Research: Intelligence & Memory (6 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.4.0  
**Due date:** 2026-03-03  
**Paralelismo:** ⚡ PODE EXECUTAR EM PARALELO com v3.5.0 e v3.6.0

| # | Issue | Labels |
|---|-------|--------|
| 106 | Evoluir sistema RAG com knowledge graph temporal (Graphiti) | research |
| 107 | Avaliar PageIndex como alternativa RAG sem vector database | research |
| 112 | Avaliar Agent Lightning para otimização contínua de agentes (RL) | research |
| 116 | Estudar modelo de learning agents do Agno | research |
| 126 | Estudar Supermemory para evolução do corpus | research |
| 131 | Estudar AgentAudit para anti-alucinação | research |

---

### v3.8.0 — Research: Tools & Integration (14 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.6.0, v3.7.0 (resultados de pesquisa alimentam integração)  
**Due date:** 2026-03-07  
**Paralelismo:** Sequencial (convergência das pesquisas)

| # | Issue | Labels |
|---|-------|--------|
| 113 | Instalar CC Workflow Studio como editor visual de agentes | research |
| 114 | Integrar reverse-api-engineer para Discovery de APIs | research |
| 115 | Avaliar agentuse como formato alternativo agents-as-markdown | research |
| 117 | Avaliar claude-code-templates e analytics dashboard | research |
| 118 | Estabelecer monitoramento contínuo do awesome-claude-code | research |
| 121 | Evoluir frontend-testing com Stagehand e padrão MS ISE | research |
| 122 | Avaliar crawlee-python como backend para doc-crawler | research |
| 123 | Avaliar codemap para análise de dependências e blast radius | research |
| 124 | Estudar padrões de agentic coding do DeepCode | research |
| 125 | Avaliar OCR e tradução para document-processor | research |
| 127 | Avaliar BrowserMCP e BrowserStack MCP para testes cross-browser | research |
| 129 | Avaliar PlanExe como acelerador de planejamento | research |
| 130 | Avaliar Liam ERD para documentação visual de schemas | research |
| 132 | Usar codeflow para análise rápida de codebases | research |

---

### v3.9.0 — Core Extraction & Org Setup (8 issues) 🆕

**Tipo de versão:** MINOR  
**Dependência:** v3.5.0 ~ v3.8.0 (todas as melhorias concluídas antes da extração)  
**Due date:** 2026-03-14  
**Paralelismo:** Sequencial (ponto de convergência)

| # | Issue | Labels |
|---|-------|--------|
| 141 | Criar org agentic-sdlc e repo core no GitHub | infrastructure |
| 142 | Extrair core: settings.json, agentes, skills, hooks, gates | infrastructure |
| 143 | Criar sistema de herança de configuração (core → edition) | infrastructure |
| 144 | Definir interface de abstração para CLI backends | architecture |
| 145 | Criar CI/CD para core: testes de contrato e validação | ci/cd |
| 146 | Documentar arquitetura core + editions (ADR) | documentation |
| 147 | Criar template-edition como scaffolding para novas editions | infrastructure |
| 148 | Validar core extraction com smoke tests end-to-end | testing |

**Sinergia:**
- Org + Repo (#141) → Extração (#142) → Herança (#143) = **fundação core**
- Abstração CLI (#144) + Template (#147) = **framework de editions**
- CI/CD (#145) + Smoke Tests (#148) + ADR (#146) = **validação e governança**

---

### v3.10.0 — Dual Compatibility: copilot-edition (11 issues)

**Tipo de versão:** MINOR  
**Dependência:** v3.9.0 (core extraído → edition construída sobre core)  
**Due date:** 2026-03-19  
**Paralelismo:** Sequencial (depende do core)

| # | Issue | Labels |
|---|-------|--------|
| 39 | [EPIC] Implementar Compatibilidade Dual: Claude Code + GitHub Copilot | type:epic |
| 40 | [TASK-004] GitHub Actions - Sincronização | phase:5 |
| 41 | [TASK-005] GitHub Actions - Manutenção RAG | phase:5 |
| 42 | [TASK-008] Configurar .vscode/settings.json para Copilot | phase:5 |
| 43 | [TASK-001] Configurar Husky e Git Hooks | phase:5 |
| 44 | [TASK-007] Criar AGENTS.md Unificado | phase:5 |
| 45 | [TASK-002] GitHub Actions - Quality Gates | phase:5 |
| 46 | [TASK-003] GitHub Actions - Automação de Fases | phase:5 |
| 47 | [TASK-006] Script de Build para Instruções Copilot | phase:5 |
| 48 | [TASK-009] Documentar Equivalências Claude ↔ Copilot | documentation |
| 49 | [TASK-010] Smoke Tests de Validação | testing |

**Sinergia:**
- GitHub Actions (#40,41,45,46) = **automação CI/CD completa**
- Copilot config (#42,47) + AGENTS.md (#44) + Equivalências (#48) = **documentação unificada**
- Husky (#43) + Smoke Tests (#49) = **validação de qualidade**

**Nota:** Esta milestone agora é construída SOBRE o core extraído em v3.9.0, como a primeira "edition" oficial do framework.

---

### v4.0.0 — easy-edition / Leigo-Friendly Mode (9 issues)

**Tipo de versão:** MAJOR (novo paradigma de UX + nova edition)  
**Dependência:** v3.10.0 (copilot-edition valida a arquitetura de editions)  
**Due date:** 2026-03-28  
**Paralelismo:** Sequencial

| # | Issue | Labels |
|---|-------|--------|
| 51 | Epic #2: Leigo-Friendly Mode (No-Code SDLC) | type:epic |
| 59 | Task 2.1: Design Leigo Wizard UX/Architecture (ADR-021) | phase:3 |
| 60 | Task 2.2: Create 6 Application Templates | phase:5 |
| 61 | Task 2.3: Implement Natural Language Question Engine | phase:5 |
| 62 | Task 2.4: Implement Auto-Stack Selection | phase:5 |
| 63 | Task 2.5: Implement GitHub Operations Abstraction | phase:5 |
| 64 | Task 2.6: Implement One-Click Deployment | phase:5 |
| 65 | Task 2.8: Implement /leigo-start Command | phase:5 |
| 77 | Task 2.7: Create Leigo Documentation Portal | phase:7 |

**Justificativa MAJOR:**
- Nova interface de interação (wizard/NL)
- Novo público-alvo (não-técnicos)
- Abstrações que mudam o contrato de uso
- Segunda "edition" oficial, validando a arquitetura multi-edition

---

## Justificativa de Versionamento Semântico

| Versão | Tipo | Justificativa |
|--------|------|---------------|
| v3.1.0 | MINOR | Novos recursos em sdlc-import (parallelism, incremental, rollback) + bug fixes |
| v3.2.0 | MINOR | Novas capacidades em agentes e infraestrutura |
| v3.3.0 | MINOR | Novo sistema de seleção de modelos |
| v3.4.0 | MINOR | Nova engine de execução autônoma |
| v3.5.0 | MINOR | Novo pipeline de onboarding de projetos legacy |
| v3.6.0 | MINOR | Novos skills e patterns da comunidade |
| v3.7.0 | MINOR | Novas capacidades de inteligência e memória |
| v3.8.0 | MINOR | Novas integrações de ferramentas |
| v3.9.0 | MINOR | Extração do core e setup da organização multi-edition |
| v3.10.0 | MINOR | Primeira edition: compatibilidade GitHub Copilot |
| **v4.0.0** | **MAJOR** | **Novo paradigma: No-Code SDLC para não-técnicos (easy-edition)** |

## Ordem de Entrega e Dependências

```
v3.1.0 ──→ v3.2.0 ──→ v3.3.0 ──→ v3.4.0 ──┬──→ v3.5.0 (Legacy) ─────────┐
  │           │           │           │      ├──→ v3.6.0 (Research 1) ──┐   │
  │  Bugs     │ Fundação  │ Models    │ Exec │──→ v3.7.0 (Research 2) ──┤   │
  │  fixados  │ sólida    │ otimiz.   │ Loop │                          │   │
  └───────────┴───────────┴───────────┘      │   v3.8.0 (Research 3) ◄──┘   │
                                              │        │                     │
                                              │   v3.9.0 (Core Extraction) ◄─┘
                                              │        │
                                              │   v3.10.0 (copilot-edition)
                                              │        │
                                              └── v4.0.0 (easy-edition) ── MAJOR
```

### Timeline Visual (Gantt)

```
Semana │ 1    │ 2    │ 3    │ 4    │ 5         │ 6    │ 7    │ 8     │ 9
───────┼──────┼──────┼──────┼──────┼───────────┼──────┼──────┼───────┼──────
v3.1.0 │██████│      │      │      │           │      │      │       │
v3.2.0 │      │██████│      │      │           │      │      │       │
v3.3.0 │      │      │██████│      │           │      │      │       │
v3.4.0 │      │      │      │██████│           │      │      │       │
v3.5.0 │      │      │      │      │██████ AG-A│      │      │       │
v3.6.0 │      │      │      │      │██████ AG-B│      │      │       │
v3.7.0 │      │      │      │      │██████ AG-C│      │      │       │
v3.8.0 │      │      │      │      │           │██████│      │       │
v3.9.0 │      │      │      │      │           │      │██████│       │
v3.10.0│      │      │      │      │           │      │      │███████│
v4.0.0 │      │      │      │      │           │      │      │       │██████
───────┴──────┴──────┴──────┴──────┴───────────┴──────┴──────┴───────┴──────
         Feb 9  Feb 13 Feb 19 Feb 25   Mar 3     Mar 7  Mar 14 Mar 19  Mar 28
```

**Legenda:** AG-A, AG-B, AG-C = Agentes IA independentes executando em paralelo

> A nova arquitetura garante que o core seja extraído (v3.9.0) e validado com a copilot-edition (v3.10.0) antes de construir a easy-edition (v4.0.0). Isso minimiza risco e maximiza reuso.
