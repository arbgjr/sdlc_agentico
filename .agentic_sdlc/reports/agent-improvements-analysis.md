# Análise de Melhorias dos Agentes - SDLC Agêntico

**Data:** 2026-01-28
**Versão Framework:** v2.2.0
**Objetivo:** Identificar onde aplicar padrões de exigência e correções

---

## Executive Summary

Analisados **37 agentes** do framework. Identificados **2 padrões de exigência** aplicados recentemente em `orchestrator.md` e `sdlc-importer.md` que devem ser propagados para **13 agentes** adicionais.

**Padrões Identificados:**
1. **CRITICAL: Real UTC Timestamps** - Timestamps devem ser reais, não ficcionais
2. **Quality Assurance Mandatory** - Garantir que TODAS as etapas foram executadas EXATAMENTE como deveriam

**Impacto:** 13 agentes precisam de melhorias (7 timestamps + 6 completude)

---

## Padrão 1: CRITICAL: Real UTC Timestamps

### Origem

**Arquivo:** `.claude/agents/orchestrator.md` (linhas 56-79)

**Regra Mandatória:**
```markdown
## CRITICAL: Real UTC Timestamps

**MANDATORY RULE:** When generating ANY file with timestamps (JSON, YAML, manifest.yml, etc.),
you MUST use REAL current UTC time with seconds precision, NOT fictional/example/rounded timestamps.

**WRONG - DO NOT USE:**
```json
{"created_at": "2026-01-16T19:30:00Z"}  // ❌ Too rounded, looks fake
{"updated_at": "2026-01-16T22:00:00Z"}  // ❌ Exact hour, suspicious
```

**CORRECT - ALWAYS USE:**
```json
{"created_at": "2026-01-16T23:25:44Z"}  // ✅ Real UTC timestamp with seconds
{"updated_at": "2026-01-16T23:26:12Z"}  // ✅ Natural progression
```

**Verification:** File modification time (`stat`) must match JSON timestamps within seconds.
```

### Agentes que PRECISAM desta seção

| # | Agente | Razão | Prioridade |
|---|--------|-------|------------|
| 1 | `adr-author.md` | Cria ADRs com timestamps | 🔴 ALTA |
| 2 | `threat-modeler.md` | Threat models têm `date: 2026-01-11` | 🔴 ALTA |
| 3 | `doc-generator.md` | Gera documentação com metadata | 🟠 MÉDIA |
| 4 | `release-manager.md` | Cria releases com timestamps | 🔴 ALTA |
| 5 | `rca-analyst.md` | RCAs com timestamps | 🟠 MÉDIA |
| 6 | `metrics-analyst.md` | Métricas com timestamps | 🟠 MÉDIA |
| 7 | `incident-commander.md` | Incidentes com timeline | 🔴 ALTA |

### Onde Inserir

**Localização:** Logo após o frontmatter YAML, antes da seção `## Missao`

**Template:**
```markdown
---
name: {agent-name}
...
---

# {Agent Name} Agent

## CRITICAL: Real UTC Timestamps

**MANDATORY RULE:** When generating ANY file with timestamps (JSON, YAML, etc.), you MUST use REAL current UTC time with seconds precision, NOT fictional/example/rounded timestamps.

**This applies to:**
- {specific artifacts this agent creates}

{rest of agent...}
```

---

## Padrão 2: Garantir Execução Correta de TODAS as Fases/Etapas

### Origem

**Arquivo 1:** `.claude/agents/orchestrator.md` (linha 5 da description)
```yaml
description: |
  Orquestrador central do SDLC Agentico. Coordena todas as 8 fases do ciclo de desenvolvimento,
  gerencia transicoes entre fases, aplica quality gates, mantem contexto persistente e
  **garante que todas as fases foram executadas corretamente**.
```

**Arquivo 2:** `.claude/agents/sdlc-importer.md` (linha 21)
```markdown
## Responsibilities

...
8. **Quality Assurance** - Ensures that all stages of the Reverse Engineering process have been
executed exactly as they were supposed to be.
```

**Padrão:** Agentes devem GARANTIR que TODAS as fases/etapas do seu workflow foram executadas CORRETAMENTE, não apenas "feitas" ou "parcialmente feitas".

### Agentes que PRECISAM desta regra

| # | Agente | Workflow Atual | Falta Verificação de | Prioridade |
|---|--------|----------------|---------------------|------------|
| 1 | `code-author.md` | Checklist linhas 459-467 | TODOS critérios de aceite implementados | 🔴 ALTA |
| 2 | `test-author.md` | Checklist linhas 403-413 | TODOS edge cases cobertos, cobertura >= 80% | 🔴 ALTA |
| 3 | `iac-engineer.md` | Checklist linhas 119-143 | TODOS recursos provisionados | 🔴 ALTA |
| 4 | `threat-modeler.md` | Checklist linhas 423-432 | STRIDE aplicado COMPLETAMENTE (6 categorias) | 🔴 ALTA |
| 5 | `adr-author.md` | Checklist linhas 312-320 | TODOS campos obrigatórios preenchidos | 🟠 MÉDIA |
| 6 | `delivery-planner.md` | Checklist linhas 520-531 | TODAS dependências mapeadas | 🟠 MÉDIA |

### Como Aplicar

**Abordagem 1: Adicionar Responsabilidade Explícita**

Adicionar item no início do agent:
```markdown
## Responsibilities

1. {existing responsibility}
2. {existing responsibility}
...
N. **Quality Assurance** - Ensures that ALL steps of the {workflow-name} process have been executed EXACTLY as they were supposed to be.
```

**Abordagem 2: Adicionar Seção de Validação Final**

Adicionar seção antes do checklist:
```markdown
## Final Validation (MANDATORY)

Before marking task as complete, you MUST verify:

- [ ] ALL acceptance criteria implemented (not just some)
- [ ] ALL checklist items validated (not skipped)
- [ ] ALL artifacts generated (not missing)
- [ ] ALL quality gates passed (not bypassed)

If ANY item is incomplete, the task is NOT complete. Go back and finish it.
```

---

## Correções Específicas por Agente

### 1. `adr-author.md`

**Problema 1:** Falta seção CRITICAL sobre timestamps reais
**Problema 2:** Checklist existe mas sem verificação mandatória de completude

**Correção:**
```markdown
## CRITICAL: Real UTC Timestamps

**MANDATORY RULE:** ADRs must use real UTC timestamps with seconds precision.

**This applies to:**
- ADR metadata (`created_at`, `last_modified`)
- Superseded dates
- Decision dates

## Final Validation (MANDATORY)

Before saving ADR, verify:
- [ ] Context explains problem clearly
- [ ] ALL realistic alternatives documented (not just 2)
- [ ] Pros AND cons balanced (not just pros)
- [ ] Decision is clear and direct
- [ ] Consequences include negatives/risks (not sanitized)
- [ ] References to discussions included
- [ ] File saved in `docs/adr/`
- [ ] Index updated
- [ ] RAG updated
- [ ] Timestamps are REAL (not rounded)
```

### 2. `threat-modeler.md`

**Problema 1:** Threat model tem `date: 2026-01-11` mas sem regra de timestamp real
**Problema 2:** Checklist existe mas sem verificação STRIDE COMPLETO

**Correção:**
```markdown
## CRITICAL: Real UTC Timestamps

**MANDATORY RULE:** Threat models must use real UTC timestamps.

**This applies to:**
- Threat model metadata (`date`, `last_updated`)
- Analysis timestamps
- Mitigation deadlines

## Final Validation (MANDATORY)

Before saving threat model, verify:
- [ ] Components identified
- [ ] Data flows mapped
- [ ] Trust boundaries defined
- [ ] STRIDE applied to EVERY component (not partial):
  - [ ] S: Spoofing threats analyzed
  - [ ] T: Tampering threats analyzed
  - [ ] R: Repudiation threats analyzed
  - [ ] I: Information Disclosure threats analyzed
  - [ ] D: Denial of Service threats analyzed
  - [ ] E: Elevation of Privilege threats analyzed
- [ ] Risks scored with DREAD
- [ ] Mitigations proposed
- [ ] Priorities defined (P0, P1, P2)
- [ ] Blockers identified
- [ ] Mitigation plan created
- [ ] Document registered in RAG
- [ ] Timestamps are REAL (not rounded)

If ANY STRIDE category is missing, analysis is INCOMPLETE.
```

### 3. `code-author.md`

**Problema:** Checklist existe mas sem verificação mandatória de TODOS critérios

**Correção:**
```markdown
## Final Validation (MANDATORY)

Before marking task as complete, you MUST verify:

- [ ] Code implements ALL acceptance criteria (verify spec line by line)
- [ ] Unit tests passing
- [ ] Integration tests passing (if applicable)
- [ ] Lint/format OK
- [ ] NO TODOs/FIXMEs left in code
- [ ] Documentation updated (if public API)
- [ ] Commit message follows standard
- [ ] PR created and ready for review

**CRITICAL:** If you cannot check "implements ALL acceptance criteria",
the implementation is INCOMPLETE. Go back to the spec and finish missing items.
```

### 4. `test-author.md`

**Problema:** Checklist existe mas sem verificação de cobertura COMPLETA

**Correção:**
```markdown
## Final Validation (MANDATORY)

Before marking test suite as complete, you MUST verify:

- [ ] Unit tests for ALL business logic (not just happy path)
- [ ] Integration tests for ALL APIs
- [ ] ALL edge cases covered:
  - [ ] Boundaries (zero, negative, max)
  - [ ] States (null, empty, invalid)
  - [ ] Errors (timeout, not found, no permission)
  - [ ] Concurrent scenarios (if applicable)
- [ ] Error handling tested
- [ ] Reusable fixtures created
- [ ] Mocks ONLY for external dependencies (never for app logic)
- [ ] Coverage >= 80% (verify with pytest --cov)
- [ ] Tests passing locally
- [ ] Tests fast (suite < 5 min)
- [ ] Descriptive names (test_<behavior>_<scenario>)

**CRITICAL:** Run coverage report. If < 80%, add missing tests.
If edge cases not covered, implementation is INCOMPLETE.
```

### 5. `iac-engineer.md`

**Problema:** Checklist existe mas sem verificação de TODOS recursos

**Correção:**
```markdown
## Final Validation (MANDATORY)

Before applying IaC, you MUST verify:

### Security Checklist (100% required)
- [ ] VNet/VPC with private subnets
- [ ] NSG/Security Groups restrictive
- [ ] Private endpoints where possible
- [ ] WAF in front of public services
- [ ] Managed Identity / IAM Roles
- [ ] Least privilege RBAC
- [ ] NO credentials hardcoded
- [ ] Dedicated service accounts
- [ ] Encryption at rest
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Automated backup
- [ ] Retention policies defined
- [ ] Audit logging enabled
- [ ] Security metrics configured
- [ ] Alerts configured
- [ ] Log aggregation setup

### Validation Commands
- [ ] `terraform validate` passed
- [ ] `checkov scan` passed (0 CRITICAL/HIGH)
- [ ] `tfsec scan` passed (0 CRITICAL/HIGH)
- [ ] `terraform plan` reviewed (no surprises)

**CRITICAL:** If ANY security item is missing, infrastructure is NOT PRODUCTION-READY.
Fix all items before applying.
```

### 6. `delivery-planner.md`

**Problema 1:** Checklist existe mas sem verificação de completude
**Problema 2:** Seção "Workflow Automatizado (OBRIGATORIO)" confusa (linhas 264-287)

**Correção 1 (Completude):**
```markdown
## Final Validation (MANDATORY)

Before committing sprint plan, verify:

- [ ] Backlog prioritized received from PO
- [ ] Team capacity calculated (person-days available)
- [ ] Stories broken down into tasks
- [ ] Estimates done by team (not solo)
- [ ] ALL dependencies mapped (not partial):
  - [ ] Technical dependencies
  - [ ] Cross-team dependencies
  - [ ] External dependencies
- [ ] Critical path identified
- [ ] Buffer included (20%)
- [ ] Risks listed WITH mitigations (not just risks)
- [ ] Milestones defined with dates
- [ ] Plan reviewed WITH team (not just sent)
- [ ] Stakeholders aligned (approval received)
- [ ] Task spec generated for parallel workers (Complexity 2+)
- [ ] **Automation scripts executed** (see below)

If ANY item is incomplete, planning is NOT DONE.
```

**Correção 2 (Clarificar Automação):**
```markdown
### Workflow Automatizado (MANDATORY - Post-Planning)

**IMPORTANTE:** Após criar `task-breakdown.yml`, você DEVE executar automaticamente
os 3 scripts de automação EM SEQUÊNCIA:

```bash
# 1. CREATE ALL MILESTONES (must run first)
python3 .claude/skills/github-sync/scripts/create_all_sprints.py \
  .agentic_sdlc/projects/{project-id}/planning/task-breakdown.yml \
  --base-date "2026-01-20"

# Wait for completion, verify: 0 failed

# 2. CREATE ALL ISSUES (must run second)
python3 .claude/skills/github-sync/scripts/bulk_create_issues.py \
  .agentic_sdlc/projects/{project-id}/planning/task-breakdown.yml \
  {project-number}

# Wait for completion, verify: 0 failed

# 3. ASSIGN ISSUES TO MILESTONES (must run last)
python3 .claude/skills/github-sync/scripts/assign_issues_bulk.py \
  .agentic_sdlc/projects/{project-id}/planning/task-breakdown.yml

# Wait for completion, verify: 0 failed
```

**Regras:**
- ✅ Execute automaticamente após gerar task-breakdown.yml
- ✅ Execute em sequência (não paralelo)
- ✅ Aguarde cada script terminar antes do próximo
- ✅ Verifique logs: se houver falhas (> 0 failed), corrija antes de prosseguir
- ❌ NÃO espere comando do usuário para executar
- ❌ NÃO pule scripts "para agilizar"
- ❌ NÃO continue se houver falhas

**Se algum script falhar:**
1. Reporte erro detalhado ao usuário
2. Identifique causa (rate limit? permissão? formato?)
3. Corrija o problema
4. Re-execute apenas o script que falhou
5. Continue sequência após sucesso
```

---

## Agentes Adicionais que Precisam de Revisão

| Agente | Ler para identificar melhorias |
|--------|-------------------------------|
| `doc-generator.md` | Pode precisar timestamps |
| `release-manager.md` | Precisa timestamps |
| `rca-analyst.md` | Precisa timestamps |
| `metrics-analyst.md` | Precisa timestamps |
| `incident-commander.md` | Precisa timestamps |

---

## Plano de Implementação

### Fase 1: Agentes de ALTA Prioridade (timestamps)

1. `adr-author.md` - Adicionar seção CRITICAL + validação
2. `threat-modeler.md` - Adicionar seção CRITICAL + STRIDE completo
3. `incident-commander.md` - Adicionar seção CRITICAL
4. `release-manager.md` - Adicionar seção CRITICAL

### Fase 2: Agentes de ALTA Prioridade (completude)

1. `code-author.md` - Adicionar validação final mandatória
2. `test-author.md` - Adicionar validação de cobertura COMPLETA
3. `iac-engineer.md` - Adicionar validação de TODOS recursos + security checklist

### Fase 3: Agentes de MÉDIA Prioridade

1. `doc-generator.md` - Avaliar necessidade de timestamps
2. `rca-analyst.md` - Adicionar seção CRITICAL
3. `metrics-analyst.md` - Adicionar seção CRITICAL
4. `adr-author.md` - Validação final de completude
5. `delivery-planner.md` - Validação + clarificar automação

---

## Checklist de Verificação

Antes de considerar um agente "corrigido":

- [ ] Leu o agente completamente
- [ ] Identificou se precisa timestamps (cria artefatos com data/hora?)
- [ ] Identificou se precisa completude (tem workflow multi-etapas?)
- [ ] Adicionou seção CRITICAL se necessário (timestamps)
- [ ] Adicionou validação final mandatória se necessário (completude)
- [ ] Verificou que não quebrou formatação existente
- [ ] Testou mentalmente: regras fazem sentido para este agente?

---

## Próximos Passos

1. **Aprovar este plano** com o usuário
2. **Implementar Fase 1** (4 agentes ALTA prioridade timestamps)
3. **Implementar Fase 2** (3 agentes ALTA prioridade completude)
4. **Implementar Fase 3** (5 agentes MÉDIA prioridade)
5. **Validar** que todos os agentes ainda funcionam corretamente
6. **Commit** com mensagem: `refactor(agents): apply strictness patterns to 13 agents`

---

## Resumo Executivo

**Total de Agentes Analisados:** 37
**Total de Agentes que Precisam Melhorias:** 13
**Esforço Estimado:** 3-4 horas (review + correções + testes)

**Benefício:** Todos os agentes seguirão os mesmos padrões de exigência, garantindo:
- Timestamps sempre reais (rastreabilidade correta)
- Workflows sempre completos (qualidade garantida)
- Consistência em todo o framework

---

**Relatório gerado por:** Claude Sonnet 4.5
**Data:** 2026-01-28
**Framework:** SDLC Agêntico v2.2.0
