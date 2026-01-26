# Catálogo de Agentes

Documentação completa dos **34 agentes** do SDLC Agêntico:
- **30 agentes orquestrados** (parte do fluxo automático por fase)
- **4 agentes consultivos** (invocados sob demanda via @mention)

## Novos Agentes (v2.0)

| Agente | Fase | Propósito |
|--------|------|-----------|
| `iac-engineer` | 3, 5 | Gera e mantém Infrastructure as Code (Terraform, Bicep, K8s) |
| `doc-generator` | 7 | Gera documentação técnica automaticamente |

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAPA DE AGENTES (32)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FASE 0          FASE 1          FASE 2          FASE 3                    │
│  Preparação      Descoberta      Requisitos      Arquitetura               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ intake-  │    │ domain-  │    │ product- │    │ system-  │              │
│  │ analyst  │    │researcher│    │ owner    │    │ architect│              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │compliance│    │ doc-     │    │requirem. │    │ adr-     │              │
│  │ guardian │    │ crawler  │    │ analyst  │    │ author   │              │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘              │
│                  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│                  │ rag-     │    │ ux-      │    │ data-    │              │
│                  │ curator  │    │ writer   │    │ architect│              │
│                  └──────────┘    └──────────┘    └──────────┘              │
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
│                  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│                  │ test-    │    │performan.│    │ change-  │              │
│                  │ author   │    │ analyst  │    │ manager  │              │
│                  └──────────┘    └──────────┘    └──────────┘              │
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
│  ┌──────────┐                                                              │
│  │observab. │                                                              │
│  │ engineer │                                                              │
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

### doc-crawler

**Propósito**: Extrai e normaliza documentação oficial de tecnologias.

**Quando usar**:
- Capturar documentação oficial de novas tecnologias
- Indexar changelogs e release notes
- Mapear versões e compatibilidades
- Preparar conteúdo para o RAG

**Output principal**:
```yaml
crawl_result:
  source:
    name: "Nome da tecnologia"
    official_url: "https://..."
  versions:
    latest: "X.Y.Z"
    supported: [list]
  documentation_index: [list]
  changelog_summary: [list]
  rag_artifacts: [list]
```

**Skills**: rag-query, memory-manager
**Tools**: Read, Write, Glob, WebSearch, WebFetch

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

### ux-writer

**Propósito**: Especialista em UX Writing e definição de fluxos de usuário.

**Quando usar**:
- Escrever textos de interface (microcopy)
- Definir estados de componentes
- Criar mensagens de erro e sucesso
- Mapear fluxos de tela e eventos

**Output principal**:
```yaml
ux_writing_spec:
  feature: "Nome da feature"
  tone_of_voice:
    style: [formal | casual | friendly]
  screens: [list com elementos e estados]
  messages:
    success: [list]
    error: [list]
    warning: [list]
  flow:
    steps: [list]
  analytics_events: [list]
```

**Skills**: rag-query
**Tools**: Read, Write, Glob, Grep

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

### data-architect

**Propósito**: Arquiteto de dados responsável por modelagem e contratos de API.

**Quando usar**:
- Modelar dados (entidades, relacionamentos)
- Definir contratos de API (OpenAPI, GraphQL)
- Especificar eventos e schemas
- Criar data dictionaries

**Output principal**:
```yaml
data_architecture:
  entities: [list com atributos e relacionamentos]
  api_contracts:
    endpoints: [list]
    schemas: [list]
  events: [list com producers e consumers]
  data_dictionary: [list com campos e validações]
  migrations: [list]
```

**Skills**: rag-query, memory-manager
**Tools**: Read, Write, Glob, Grep

---

### iac-engineer (NOVO)

**Propósito**: Engenheiro de IaC responsável por gerar e manter código de infraestrutura.

**Quando usar**:
- Gerar Terraform para Azure/AWS/GCP
- Criar manifests Kubernetes (Deployments, Services, ConfigMaps)
- Definir pipelines de CI/CD
- Implementar GitOps workflows

**Output principal**:
```yaml
iac_output:
  provider: azure | aws | kubernetes
  resources:
    - type: string
      name: string
      path: string
  files_created:
    - path: string
      purpose: string
  security_checks:
    - check: string
      status: pass | fail | warn
  next_steps:
    - action: string
      command: string
```

**Princípios**:
1. **Menor privilégio** - Apenas permissões necessárias
2. **Infraestrutura imutável** - Não modificar em produção
3. **GitOps** - Tudo versionado, nada manual
4. **Security by Default** - Segurança desde o início

**Templates Suportados**:
| Provider | Recursos |
|----------|----------|
| Azure | Container Apps, AKS, PostgreSQL, Key Vault, Service Bus |
| AWS | ECS/Fargate, EKS, RDS, Secrets Manager, SQS |
| K8s | Deployment, Service, ConfigMap, Secret, Ingress, NetworkPolicy |

**Skills**: iac-generator, security-scanner
**Tools**: Read, Write, Edit, Glob, Grep, Bash

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

### performance-analyst

**Propósito**: Analista de performance e resiliência do sistema.

**Quando usar**:
- Definir testes de carga e stress
- Analisar latência e throughput
- Validar degradação graciosa
- Verificar timeouts e retries

**Output principal**:
```yaml
performance_report:
  test_scenarios: [load, stress, spike, soak]
  results:
    latency:
      p50: "Xms"
      p95: "Xms"
      p99: "Xms"
    throughput: "X rps"
    error_rate: "X%"
  slo_compliance: [list]
  recommendations: [list]
  verdict: PASS | FAIL
```

**Skills**: rag-query
**Tools**: Read, Write, Glob, Grep, Bash

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

### change-manager

**Propósito**: Gestor de mudanças para comunicação, janelas de deploy e aprovações.

**Quando usar**:
- Comunicar mudanças para stakeholders
- Definir janelas de deploy
- Obter aprovações necessárias
- Coordenar rollback se necessário

**Output principal**:
```yaml
change_request:
  id: "CHG-YYYY-MMDD-NNN"
  category: [standard | normal | emergency | major]
  schedule:
    deploy_window: "HH:MM - HH:MM UTC"
    rollback_deadline: "HH:MM UTC"
  approvals:
    required: [list]
    obtained: [list]
  communication:
    pre_deploy: [messages]
    post_deploy: [messages]
  rollback_plan:
    trigger_conditions: [list]
    procedure: [steps]
```

**Skills**: rag-query, memory-manager
**Tools**: Read, Write, Glob, Grep, Bash

---

### doc-generator (NOVO)

**Propósito**: Gera documentação técnica automaticamente a partir do código e artefatos.

**Quando usar**:
- Gerar README.md do projeto
- Criar documentação de API (OpenAPI/Swagger)
- Gerar diagramas de arquitetura (Mermaid/PlantUML)
- Produzir guias de onboarding
- Criar runbooks operacionais
- Gerar release notes

**Output principal**:
```yaml
doc_output:
  generated:
    - path: string
      type: readme | api | arch | onboarding | runbook
      sections: number
      words: number
  diagrams:
    - path: string
      type: architecture | sequence | erd | flow
      format: mermaid | plantuml
  validation:
    completeness: percentage
    broken_links: number
    missing_sections: list[string]
  recommendations:
    - section: string
      suggestion: string
```

**Tipos de Documentação**:
| Tipo | Conteúdo |
|------|----------|
| README | Descrição, quick start, instalação, uso |
| API Reference | Endpoints, schemas, autenticação, exemplos |
| Architecture | Componentes, fluxos, ADRs |
| Onboarding | Setup, estrutura, convenções |
| Runbook | Procedimentos, troubleshooting, métricas |

**Integração com SDLC**:
| Fase | Documentação |
|------|--------------|
| 2 | User Stories, Requisitos |
| 3 | Architecture, ADRs |
| 5 | API Docs, Code Comments |
| 7 | Release Notes, Changelog |
| 8 | Runbooks, Playbooks |

**Skills**: doc-blueprint
**Tools**: Read, Write, Glob, Grep

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

### observability-engineer

**Propósito**: Engenheiro de observabilidade para dashboards, alertas e tracing.

**Quando usar**:
- Configurar dashboards de monitoramento
- Definir alertas e thresholds
- Implementar tracing distribuído
- Configurar golden signals

**Output principal**:
```yaml
observability_config:
  logging:
    format: "json"
    schema: [fields]
  metrics:
    golden_signals: [latency, traffic, errors, saturation]
    custom_metrics: [list]
  tracing:
    tool: "OpenTelemetry"
    sampling_rate: X
  dashboards: [list]
  alerts:
    critical: [list]
    warning: [list]
  slos: [list with targets]
  runbooks: [list]
```

**Skills**: rag-query, memory-manager
**Tools**: Read, Write, Glob, Grep, Bash

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

## Agentes Consultivos (Especialistas sob Demanda)

Estes agentes **não fazem parte da orquestração automática** do SDLC. São especialistas que podem ser invocados explicitamente via `@mention` quando necessário.

**Quando usar agentes consultivos**:
- Quando precisar de expertise específica durante uma fase
- Para validar decisões ou requisitos
- Para simular entrevistas ou revisões

### requirements-interrogator

**Propósito**: Elimina ambiguidade de requisitos em system design.

**Quando usar**:
- Requisitos vagos (sem números, limites, SLAs)
- Falta clareza sobre volume, latência, consistência
- Restrições não especificadas

**Invocação**: `@requirements-interrogator analise os requisitos de...`

**Exemplo de perguntas**:
- "Qual o volume esperado de requisições por segundo?"
- "Qual latência é aceitável para esta operação?"
- "Qual o tamanho máximo de payload?"
- "É aceitável perder dados em caso de falha?"

---

### tradeoff-challenger

**Propósito**: Ataca decisões fracas e força trade-offs explícitos em arquitetura.

**Quando usar**:
- Decisões sem justificativa clara
- Tecnologia escolhida sem comparativo
- Falta de análise de alternativas

**Invocação**: `@tradeoff-challenger desafie a decisão de...`

**Exemplo de desafios**:
- "Por que PostgreSQL e não MongoDB para este caso?"
- "Qual o custo de usar microserviços vs monolito?"
- "O que acontece se esta dependência falhar?"
- "Como escala quando dobrar a carga?"

---

### failure-analyst

**Propósito**: Analisa falhas e resiliência do sistema.

**Quando usar**:
- Design envolve filas, jobs, tempo real
- Preocupação com consistência eventual
- Identificar pontos únicos de falha
- Analisar cenários de degradação

**Invocação**: `@failure-analyst analise os pontos de falha de...`

**Pontos de análise**:
- Single Points of Failure (SPOF)
- Estratégias de retry e backoff
- Circuit breakers e fallbacks
- Degradação graciosa
- Recuperação de desastres

---

### interview-simulator

**Propósito**: Simula entrevista de system design para treino ou validação.

**Quando usar**:
- Treinar defesa de arquitetura
- Preparar para apresentação a stakeholders
- Validar completude do design

**Invocação**: `@interview-simulator simule entrevista para o sistema de...`

**Formato da simulação**:
1. Clarifying questions (requisitos)
2. High-level design review
3. Deep dive em componentes
4. Trade-off discussions
5. Bottleneck analysis
6. Follow-up questions

---

**Nota**: Estes agentes não estão em `settings.json` como parte da orquestração porque são invocados sob demanda, não automaticamente por fase.

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
