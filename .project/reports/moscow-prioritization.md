# Priorização de Issues — Matriz MoSCoW

**Data**: 2026-04-15
**Escopo**: 109 issues abertas no repositório `arbgjr/sdlc_agentico`
**Método**: MoSCoW (Must / Should / Could / Won't)

## Critérios de Classificação

| Categoria | Critério |
|-----------|----------|
| **Must have** | Bloqueia release, corrige correção funcional quebrada, fundação para outras entregas, compatibilidade com plataforma primária, marcador 🔴 |
| **Should have** | Alto valor estratégico, épicos funcionais, qualidade do core, automação essencial, marcador 🟡 com aplicação imediata |
| **Could have** | Enhancements pontuais, pesquisa com uso concreto previsto, marcador 🟢 com caminho de integração |
| **Won't have (now)** | Explicitamente deferido, especulativo, pesquisa sem consumidor, duplicado por item de maior prioridade |

---

## MUST HAVE — 13 issues (fundação e correções bloqueantes)

Sem estas entregas o framework tem regressões funcionais, perde a base da reestruturação em `agentic-sdlc/*` ou falha na compatibilidade dual Claude/Copilot.

| # | Título | Razão |
|---|--------|-------|
| #93 | [C2] Generic Diagrams - Django shown for .NET projects | Bug de correção de saída — quebra confiança no sdlc-import |
| #97 | [L3] Output Directory Not Configurable via CLI | Bug — viola contrato documentado em CLAUDE.md (`project_artifacts_dir`) |
| #100 | [L6] No Rollback on Failure | Bug — segurança operacional, pode corromper `.project/` |
| #99 | [L5] No Incremental Import | Bug — torna reruns caros e inseguros |
| #139 | 🔴 Documentar compatibilidade worktrees + Claude Code Agent Teams | Marcador vermelho explícito; afeta parallel-workers |
| #142 | [CORE] Análise de separação core vs engine-specific | Pré-requisito da reorganização em `agentic-sdlc` |
| #141 | [CORE] Configurar organização agentic-sdlc no GitHub | Infraestrutura raiz da multi-edition |
| #39  | [EPIC] Compatibilidade Dual Claude Code + GitHub Copilot | Épico estratégico — garante alcance da plataforma |
| #43  | [TASK-001] Configurar Husky e Git Hooks | Base dos hooks para edição Copilot |
| #45  | [TASK-002] GitHub Actions - Quality Gates | Gates obrigatórios em CI |
| #46  | [TASK-003] GitHub Actions - Automação de Fases | Automação essencial do SDLC |
| #44  | [TASK-007] AGENTS.md Unificado | Fonte canônica de agentes para as editions |
| #94  | [G3] No Parallelization - Single-threaded execution | Impede SLA aceitável em projetos reais |

---

## SHOULD HAVE — 39 issues (valor alto, podem aguardar os Must)

| # | Título | Agrupamento |
|---|--------|-------------|
| #40 | [TASK-004] GitHub Actions - Sincronização (Wiki, Projects, Labels) | Dual compat (pós-MVP) |
| #41 | [TASK-005] GitHub Actions - Manutenção RAG | Dual compat |
| #42 | [TASK-008] `.vscode/settings.json` para Copilot | Dual compat |
| #47 | [TASK-006] Script de Build para Instruções Copilot | Dual compat |
| #48 | [TASK-009] Documentar Equivalências Claude ↔ Copilot | Dual compat |
| #49 | [TASK-010] Testes de Validação (Smoke Tests) | Dual compat |
| #50 | Epic #1: Multi-Model Configuration System | Multi-model |
| #53 | Task 1.1: Design Model Selection Strategy (ADR-020) | Multi-model |
| #54 | Task 1.2: Model Configuration Schema | Multi-model |
| #55 | Task 1.3: Model Selector Library | Multi-model |
| #56 | Task 1.4: Integrate Model Selector with Agent Execution | Multi-model |
| #57 | Task 1.5: Cost Tracking Dashboard | Multi-model |
| #58 | Task 1.6: Model Selection Quality Gate | Multi-model |
| #75 | Task 1.7: Migration Documentation | Multi-model |
| #76 | Task 1.8: Integration Testing | Multi-model |
| #66 | Task 3.1: Reverse Engineering Architecture (ADR-022) | Reverse eng. |
| #67 | Task 3.2: Language Detection (10 languages) | Reverse eng. |
| #68 | Task 3.2b: IaC/DevOps/QA Detection | Reverse eng. |
| #69 | Task 3.3: Decision Extractor | Reverse eng. |
| #70 | Task 3.4: Architecture Visualizer | Reverse eng. |
| #71 | Task 3.5: Threat Model Generator (STRIDE) | Reverse eng. |
| #72 | Task 3.6: Tech Debt Detector | Reverse eng. |
| #73 | Task 3.7: `/onboard-legacy` Command | Reverse eng. |
| #74 | Task 3.8: Validation Quality Gate | Reverse eng. |
| #95 | [L1] No Metrics in CI/CD Format | Bug importante |
| #96 | [L2] No Execution Time per Step | Bug importante |
| #98 | [L4] No Language Priority Configuration | Bug importante |
| #92 | Pattern Detection for Terraform and Database IaC | Enhancement direcionado |
| #143 | [CORE] Repo `agentic-sdlc/core` com estrutura base | Migração estrutural |
| #144 | [CORE] Migrar agentes, skills e fases para core | Migração estrutural |
| #145 | [CORE] Repo `agentic-sdlc/claude-edition` | Migração estrutural |
| #146 | [CORE] Versionamento core ↔ editions | Migração estrutural |
| #147 | [CORE] Repo `agentic-sdlc/docs` | Migração estrutural |
| #148 | [CORE] Validação end-to-end + arquivamento monorepo | Migração estrutural |
| #78 | Task 0.0: Review awesome-copilot for Reusable Resources | Discovery dual compat |
| #119 | 🟡 Prompt engineering oficial da Anthropic nos agentes | Qualidade do core |
| #134 | 🟡 Incorporar Agentic Design Patterns ao corpus | Qualidade do core |
| #140 | 🟡 Instalação global do framework em 3 camadas | Distribuição |
| #137 | 🟢 Sequential Thinking como MCP padrão (não único) | Integração pragmática |

---

## COULD HAVE — 56 issues (valor positivo, sem bloquear roadmap)

### Épico Ralph TUI / Autonomous SDLC Loop (12 issues)

Tem valor estratégico mas depende de fundação e dos Musts. Pode ser entregue após os blocos acima.

#80, #81, #82, #83, #84, #85, #86, #87, #88, #89, #90, #91

### Épico Leigo-Friendly Mode (8 issues)

Valioso, mas atende audiência secundária do framework enquanto o core ainda estabiliza.

#51, #59, #60, #61, #62, #63, #64, #65, #77

### Pesquisa 🟢 com integração provável (15 issues)

Importação/avaliação de fontes externas com caminho de consumo razoável.

#101, #102, #103, #104, #105, #106, #107, #108, #109, #110, #111, #113, #114, #115, #135

### Pesquisa 🟡 com avaliação dirigida (19 issues)

Pesquisa com potencial, mas sem gatilho de uso imediato comprovado.

#112, #116, #117, #118, #120, #121, #122, #123, #124, #125, #126, #127, #128, #129, #130, #131, #132, #133, #136, #138

---

## WON'T HAVE (now) — 1 issue

| # | Título | Razão |
|---|--------|-------|
| #149 | Deferred: `refactoring-surgeon` agent | Explicitamente deferido pelo autor com critérios de reabertura (ADR-003, etc.). Manter fechado até disparador documentado. |

---

## Sequência Recomendada de Execução

1. **Desbloqueio de correção** (paralelo): #93, #97, #99, #100, #139
2. **Infraestrutura dual compat** (sequencial): #39 → #43 → #45 → #46 → #44 → #94
3. **Reestruturação agentic-sdlc** (sequencial): #141 + #142 → #143 → #144/#146 → #145 → #147 → #148
4. **Should completos**: dual compat restante → multi-model → reverse engineering
5. **Could**: Ralph TUI → Leigo Mode → pesquisas direcionadas
6. **Won't**: reavaliar #149 somente com ADR-003 documentado

## Observações

- **Épicos contam como unidade**: o #39 (dual compat) entrou em Must porque é pré-requisito estratégico; demais tasks do épico ficaram em Should porque parcelamento é viável.
- **Bugs L1–L6 foram divididos**: bugs que quebram correção/segurança subiram para Must; os que apenas degradam observabilidade ficaram em Should.
- **Pesquisa (🟢/🟡) majoritariamente em Could**: seguindo disciplina do CLAUDE.md ("três testes" antes de adicionar framework), research sem consumidor não sobe para Should.
- **Reestruturação em editions (#141–#148)**: apenas os gatilhos iniciais (#141, #142) entraram em Must; o resto é Should pois pode ocorrer incrementalmente.
