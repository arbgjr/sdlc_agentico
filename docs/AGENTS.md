# Catálogo de Agentes

Documentação completa dos 26 agentes do SDLC Agêntico.

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAPA DE AGENTES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FASE 0          FASE 1          FASE 2          FASE 3                    │
│  Preparação      Descoberta      Requisitos      Arquitetura               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ intake-  │    │ domain-  │    │ product- │    │ system-  │              │
│  │ analyst  │    │researcher│    │ owner    │    │ architect│              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │compliance│    │ rag-     │    │requirem. │    │ adr-     │              │
│  │ guardian │    │ curator  │    │ analyst  │    │ author   │              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                                                   ┌──────────┐              │
│                                                   │ threat-  │              │
│                                                   │ modeler  │              │
│                                                   └──────────┘              │
│                                                                             │
│  FASE 4          FASE 5          FASE 6          FASE 7                    │
│  Planejamento    Implementação   Qualidade       Release                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ delivery-│    │ code-    │    │ qa-      │    │ release- │              │
│  │ planner  │    │ author   │    │ analyst  │    │ manager  │              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│                  │ code-    │    │ security-│    │ cicd-    │              │
│                  │ reviewer │    │ scanner  │    │ engineer │              │
│                  └──────────┘    └──────────┘    └──────────┘              │
│                  ┌──────────┐                                              │
│                  │ test-    │                                              │
│                  │ author   │                                              │
│                  └──────────┘                                              │
│                                                                             │
│  FASE 8          CROSS-CUTTING                                             │
│  Operação        Transversal                                               │
│  ┌──────────┐    ┌──────────┐                                              │
│  │ incident-│    │orchestra-│                                              │
│  │commander │    │ tor      │                                              │
│  └──────────┘    └──────────┘                                              │
│  ┌──────────┐    ┌──────────┐                                              │
│  │ rca-     │    │ playbook-│                                              │
│  │ analyst  │    │governance│                                              │
│  └──────────┘    └──────────┘                                              │
│  ┌──────────┐                                                              │
│  │ metrics- │                                                              │
│  │ analyst  │                                                              │
│  └──────────┘                                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Fase 0: Preparação

### intake-analyst

**Propósito**: Primeiro ponto de contato para novas demandas. Analisa, classifica e prepara entrada para o SDLC.

**Quando usar**:
- Nova demanda/request chegou
- Precisa classificar tipo (feature, bug, tech debt)
- Identificar stakeholders e restrições

**Output principal**:
```yaml
intake_result:
  id: "REQ-YYYYMMDD-NNN"
  classification:
    type: feature | bug | tech_debt | spike
    priority: critical | high | medium | low
    complexity: 0 | 1 | 2 | 3
  recommended_flow:
    phases: [list]
  next_agent: string
```

**Skills**: rag-query, bmad-integration

---

### compliance-guardian

**Propósito**: Guardião de compliance que valida aderência a políticas, regulamentações e padrões de segurança.

**Quando usar**:
- Feature lida com dados pessoais (LGPD)
- Sistema processa pagamentos (PCI-DSS)
- Requisitos regulatórios aplicáveis

**Output principal**:
```yaml
compliance_assessment:
  applicable_regulations: [LGPD, PCI-DSS, SOC2]
  controls_assessment: [list]
  verdict: APPROVED | NOT_APPROVED
  blockers: [list]
```

**Skills**: rag-query, memory-manager

---

## Fase 1: Descoberta

### domain-researcher

**Propósito**: Pesquisador que busca conhecimento externo e interno sobre tecnologias e domínios.

**Quando usar**:
- Pesquisar tecnologias e frameworks
- Encontrar documentação oficial
- Buscar best practices
- Revisar papers acadêmicos

**Output principal**:
```yaml
research_brief:
  executive_summary: string
  key_findings: [list]
  best_practices: [list]
  anti_patterns: [list]
  recommendations: [list]
```

**Skills**: rag-query, memory-manager
**Tools**: WebSearch, WebFetch

---

### rag-curator

**Propósito**: Gerencia o corpus de conhecimento RAG do projeto.

**Quando usar**:
- Adicionar conhecimento ao corpus
- Atualizar documentação indexada
- Reorganizar conhecimento

**Skills**: rag-query, memory-manager

---

## Fase 2: Requisitos

### product-owner

**Propósito**: Define visão, prioriza backlog e garante valor de negócio.

**Quando usar**:
- Definir visão do produto/feature
- Priorizar backlog
- Escrever épicos
- Definir MVP

**Output principal**:
```yaml
mvp:
  name: string
  hypothesis: string
  success_metrics: [list]
  included: [features]
  excluded: [features with reasons]
prioritization:
  method: RICE | MoSCoW
  ranking: [ordered list]
```

**Skills**: rag-query

---

### requirements-analyst

**Propósito**: Transforma épicos em user stories testáveis com critérios de aceite.

**Quando usar**:
- Escrever user stories
- Definir critérios de aceite
- Identificar edge cases
- Documentar NFRs

**Output principal**:
```yaml
user_story:
  id: "US-NNN"
  story: "Como... Eu quero... Para que..."
  acceptance_criteria:
    - given: string
      when: string
      then: string
  edge_cases: [list]
  out_of_scope: [list]
```

**Skills**: rag-query, spec-kit-integration

---

## Fase 3: Arquitetura

### system-architect

**Propósito**: Define design de alto nível e decisões arquiteturais.

**Quando usar**:
- Definir arquitetura de sistemas
- Escolher tecnologias e padrões
- Identificar trade-offs
- Criar diagramas

**Output principal**:
```yaml
architecture_overview:
  high_level_design:
    style: microservices | monolith | serverless
    components: [list]
  technology_choices: [list]
  nfr_approach: [list]
  adrs_needed: [list]
```

**Skills**: system-design-decision-engine, rag-query, memory-manager

---

### adr-author

**Propósito**: Documenta decisões arquiteturais significativas em ADRs.

**Quando usar**:
- Criar ADRs para decisões importantes
- Documentar trade-offs
- Manter histórico de decisões

**Output principal**: Arquivo `docs/adr/NNNN-slug.md`

**Skills**: rag-query, memory-manager

---

### threat-modeler

**Propósito**: Analisa arquiteturas usando STRIDE para identificar vulnerabilidades.

**Quando usar**:
- Análise de segurança de arquitetura
- Identificar vetores de ataque
- Propor controles de segurança

**Output principal**:
```yaml
threat_model:
  threats: [list with STRIDE categories]
  risk_summary:
    critical: N
    high: N
  mitigation_plan: [list]
```

**Skills**: rag-query, memory-manager

---

## Fase 4: Planejamento

### delivery-planner

**Propósito**: Quebra épicos em sprints e tasks, faz estimativas.

**Quando usar**:
- Planejar sprints
- Estimar esforço
- Identificar dependências
- Criar roadmap

**Output principal**:
```yaml
sprint_plan:
  sprint_number: N
  committed_stories: [list]
  total_points: N
  risks: [list]
release_roadmap:
  releases: [list with dates]
```

**Skills**: rag-query, spec-kit-integration

---

## Fase 5: Implementação

### code-author

**Propósito**: Implementa features seguindo specs e padrões do projeto.

**Quando usar**:
- Implementar features
- Seguir padrões do projeto
- Criar código com testes

**Output**: Código fonte, testes

**Skills**: rag-query, memory-manager
**Tools**: Read, Write, Edit, Glob, Grep, Bash

---

### code-reviewer

**Propósito**: Revisa PRs e fornece feedback construtivo.

**Quando usar**:
- Revisar Pull Requests
- Identificar problemas de código
- Validar aderência a padrões

**Output principal**:
```yaml
review_result:
  verdict: approved | changes_requested
  blockers: [list]
  suggestions: [list]
  nits: [list]
```

**Skills**: rag-query, memory-manager
**Tools**: Read, Glob, Grep, Bash

---

### test-author

**Propósito**: Cria testes unitários, integração e e2e.

**Quando usar**:
- Criar testes para código novo
- Aumentar cobertura
- Identificar edge cases

**Output**: Arquivos de teste

**Skills**: rag-query
**Tools**: Read, Write, Edit, Glob, Grep, Bash

---

## Fase 6: Qualidade

### qa-analyst

**Propósito**: Coordena estratégia de testes e valida qualidade.

**Quando usar**:
- Definir estratégia de testes
- Validar critérios de aceite
- Gerar quality report

**Output principal**:
```yaml
quality_report:
  summary:
    status: approved | approved_with_conditions | rejected
  test_execution:
    passed: N
    failed: N
  acceptance_criteria_status: [list]
```

**Skills**: rag-query

---

### security-scanner

**Propósito**: Analisa código e configurações em busca de vulnerabilidades.

**Quando usar**:
- Scan antes de release
- Análise de dependências
- Verificar secrets expostos

**Output principal**:
```yaml
security_report:
  summary:
    critical: N
    high: N
  findings: [list]
  verdict: PASS | FAIL
```

**Skills**: rag-query
**Tools**: Read, Glob, Grep, Bash

---

## Fase 7: Release

### release-manager

**Propósito**: Coordena o processo de deploy para produção.

**Quando usar**:
- Preparar releases
- Coordenar deploys
- Gerar release notes
- Gerenciar rollbacks

**Output principal**:
- CHANGELOG.md atualizado
- Release notes
- Tag de versão

**Skills**: rag-query, memory-manager, gate-evaluator

---

### cicd-engineer

**Propósito**: Projeta e mantém pipelines de CI/CD.

**Quando usar**:
- Criar pipelines
- Otimizar builds
- Configurar quality gates

**Output principal**: Workflows GitHub Actions, Dockerfile

**Skills**: rag-query

---

## Fase 8: Operação

### incident-commander

**Propósito**: Coordena resposta a incidentes em produção.

**Quando usar**:
- Sistema fora do ar
- Incidente de segurança
- Degradação de performance

**Output principal**:
```yaml
incident:
  id: "INC-YYYYMMDD-NNN"
  severity: sev1 | sev2 | sev3
  timeline: [events]
  status: investigating | mitigating | resolved
```

**Skills**: rag-query, memory-manager

---

### rca-analyst

**Propósito**: Conduz post-mortems e documenta learnings.

**Quando usar**:
- Após incidentes
- Análise de causa raiz
- Documentar learnings

**Output principal**:
```yaml
rca_document:
  root_causes: [list]
  action_items: [list with owners]
  lessons_learned: [list]
```

**Skills**: rag-query, memory-manager

---

### metrics-analyst

**Propósito**: Rastreia métricas DORA, SPACE e gera reports.

**Quando usar**:
- Gerar reports de métricas
- Identificar tendências
- Recomendar melhorias

**Output principal**:
```yaml
metrics_report:
  dora_metrics:
    deployment_frequency: value
    lead_time: value
    change_failure_rate: value
    mttr: value
  dora_classification: Elite | High | Medium | Low
```

**Skills**: rag-query, memory-manager

---

## Cross-Cutting

### orchestrator

**Propósito**: Coordenador central do SDLC. Gerencia fases, gates e escalações.

**Model**: opus (mais capaz)

**Quando usar**: Automaticamente ativado pelo sistema

**Skills**: gate-evaluator, memory-manager, rag-query, bmad-integration

---

### playbook-governance

**Propósito**: Monitora drift do playbook e propõe atualizações.

**Quando usar**:
- Exceções repetidas detectadas
- Padrões emergentes identificados
- Learnings de incidentes

**Skills**: governance-rules, memory-manager, rag-query

---

## Agentes Auxiliares (Existentes)

### requirements-interrogator
Elimina ambiguidade de requisitos. Questiona números, limites, latência, volume.

### tradeoff-challenger
Ataca decisões fracas e força trade-offs explícitos em arquitetura.

### failure-analyst
Analisa falhas e resiliência. Foca em filas, jobs, consistência, pontos únicos de falha.

### interview-simulator
Simula entrevista de system design com perguntas de follow-up.

---

## Como Invocar Agentes

```bash
# Via menção no Claude Code
"@system-architect defina a arquitetura para..."

# Via orchestrator (automático)
/sdlc-start "descrição"  # orchestrator seleciona agentes

# Diretamente (se souber qual precisa)
"Use o threat-modeler para analisar..."
```
