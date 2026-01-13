# Referência de Comandos

Documentação completa dos comandos disponíveis no SDLC Agêntico.

## Comandos por Nível de Complexidade

| Level | Comando | Descrição | Fases |
|-------|---------|-----------|-------|
| 0 | `/quick-fix` | Bug fixes, typos | 5, 6 |
| 1 | `/new-feature` | Features simples | 2, 5, 6 |
| 2-3 | `/sdlc-start` | Projetos completos | 0-8 |

---

## Comandos do SDLC

### /quick-fix

Inicia fluxo rápido para bug fixes e correções simples (Level 0).

```bash
/quick-fix "Descrição do bug"
```

**Parâmetros**:
- `descrição` (obrigatório): Descrição do bug ou correção

**Critérios de Elegibilidade**:
- Bug simples com causa conhecida
- Alteração em até 3 arquivos
- Sem mudança de API/contrato
- Sem impacto em segurança
- Sem necessidade de revisão de arquitetura

**O que faz**:
1. Cria branch `fix/{descrição}` automaticamente
2. Aciona `code-author` para implementar fix
3. Cria testes para o bug
4. `code-reviewer` faz review
5. Valida build e testes
6. Cria PR para merge

**Escalação Automática**:
- Problema mais profundo → Level 1 (`/new-feature`)
- Impacto em segurança → `security-scanner`
- Mudança de API → `system-architect`

**Exemplo**:
```bash
/quick-fix "Corrigir timeout na conexão com registradora"
```

---

### /new-feature

Inicia fluxo para nova feature em serviço existente (Level 1).

```bash
/new-feature "Nome da feature"
```

**Parâmetros**:
- `nome` (obrigatório): Nome da feature

**Critérios de Elegibilidade**:
- Feature em serviço já existente
- Sem novo serviço ou domínio
- Sem mudança significativa de arquitetura
- Sem requisitos de compliance novos

**O que faz**:
1. Cria branch `feature/{nome}` automaticamente
2. Cria spec em `.agentic_sdlc/projects/{id}/specs/`
3. `requirements-analyst` clarifica requisitos (~10 min)
4. `code-author` + `test-author` implementam (~20-60 min)
5. `code-reviewer` faz review
6. `qa-analyst` valida critérios de aceite
7. Cria PR com resumo da feature

**Gatilhos de Escalação**:
| Situação | Ação |
|----------|------|
| Novo domínio | Escalar para Level 2 (`/sdlc-start`) |
| Mudança de DB schema | Chamar `@data-architect` |
| Novo endpoint público | Chamar `@threat-modeler` |
| Performance crítica | Chamar `@performance-analyst` |
| Requisitos de compliance | Chamar `@compliance-guardian` |

**Exemplo**:
```bash
/new-feature "Exportação de duplicatas em PDF"
```

---

### /sdlc-start

Inicia um novo workflow SDLC completo (Level 2/3).

```bash
/sdlc-start "Descrição da demanda"
```

**Parâmetros**:
- `descrição` (obrigatório): Descrição da feature, bug ou tarefa

**O que faz**:
1. Aciona `intake-analyst` para analisar a demanda
2. Classifica complexidade (Level 0-3)
3. Determina fases necessárias
4. Inicia workflow apropriado

**Exemplos**:
```bash
# Feature nova
/sdlc-start "Criar sistema de notificações push para usuários"

# Bug fix
/sdlc-start "Corrigir erro de timeout na API de pagamentos"

# Tech debt
/sdlc-start "Refatorar módulo de autenticação para usar OAuth2"
```

---

### /phase-status

Mostra o status atual do workflow SDLC.

```bash
/phase-status
```

**Output**:
```yaml
sdlc_status:
  current_phase: 3
  phase_name: "Architecture"
  progress: 60%

  completed_phases:
    - phase: 0
      artifacts: ["intake-result.yml"]
    - phase: 1
      artifacts: ["research-brief.yml"]
    - phase: 2
      artifacts: ["specs/feature.md", "stories/US-001.md"]

  current_work:
    agent: "system-architect"
    task: "Definindo arquitetura de alto nível"

  next_gate: "phase-3-to-4"
  blockers: []
```

---

### /gate-check

Verifica se os critérios do quality gate atual foram atendidos.

```bash
/gate-check                    # Verifica gate da fase atual
/gate-check phase-2-to-3       # Verifica gate específico
/gate-check --force            # Registra como passed (com warnings)
```

**Output**:
```yaml
gate_evaluation:
  gate: "phase-2-to-3"

  artifacts:
    - name: "Spec"
      required: true
      found: true
    - name: "User Stories"
      required: true
      found: true

  quality_checks:
    - check: "Critérios de aceite definidos"
      passed: true

  verdict: "PASSED"
```

**Gates disponíveis**:
| Gate | De → Para |
|------|-----------|
| phase-0-to-1 | Preparação → Descoberta |
| phase-1-to-2 | Descoberta → Requisitos |
| phase-2-to-3 | Requisitos → Arquitetura |
| phase-3-to-4 | Arquitetura → Planejamento |
| phase-4-to-5 | Planejamento → Implementação |
| phase-5-to-6 | Implementação → Qualidade |
| phase-6-to-7 | Qualidade → Release |
| phase-7-to-8 | Release → Operação |

---

### /sdlc-create-issues

Cria issues no GitHub a partir das tasks geradas.

```bash
/sdlc-create-issues                    # Criar issues
/sdlc-create-issues --assign-copilot   # Atribuir ao Copilot
```

**Parâmetros**:
- `--assign-copilot`: Atribui issues ao GitHub Copilot Coding Agent

**O que faz**:
1. Localiza tasks em `.specify/tasks/` ou `.claude/memory/tasks/`
2. Cria issue no GitHub para cada task
3. Aplica labels apropriadas
4. Opcionalmente atribui ao Copilot

**Exemplo de Issue criada**:
```markdown
## [TASK-001] Implementar endpoint de autenticação

### Contexto
Link para spec, technical plan

### Descrição
Implementar POST /api/v1/auth/login com JWT

### Critérios de Aceite
- [ ] Endpoint responde com JWT válido
- [ ] Validação de credenciais funciona
- [ ] Rate limiting implementado

### Arquivos Relevantes
- src/auth/routes.py
- tests/test_auth.py
```

---

## Comandos de Arquitetura

### /adr-create

Cria um novo Architecture Decision Record.

```bash
/adr-create "Título da Decisão"
```

**Parâmetros**:
- `título` (obrigatório): Título descritivo da decisão

**O que faz**:
1. Determina próximo número de ADR
2. Gera slug a partir do título
3. Cria arquivo com template padrão
4. Adiciona ao índice

**Estrutura criada**:
```
docs/adr/
├── 0005-use-postgresql-for-main-db.md  # Novo ADR
└── index.md                             # Atualizado
```

**Comandos adicionais**:
```bash
/adr-create --list                    # Lista ADRs existentes
/adr-create --status 0005 accepted    # Atualiza status
```

---

## Comandos de Segurança

### /security-scan

Executa scan de segurança no código.

```bash
/security-scan                 # Scan completo
/security-scan --type sast     # Apenas análise estática
/security-scan --type sca      # Apenas dependências
/security-scan --type secrets  # Apenas secrets
```

**Tipos de scan**:
| Tipo | Ferramenta | O que detecta |
|------|------------|---------------|
| SAST | bandit, semgrep | SQL injection, XSS, code issues |
| SCA | pip-audit, npm audit | CVEs em dependências |
| Secrets | gitleaks | API keys, passwords expostos |

**Output**:
```yaml
security_report:
  summary:
    critical: 0
    high: 2
    medium: 3

  findings:
    - id: "VULN-001"
      severity: "high"
      category: "SQL Injection"
      file: "src/orders/repository.py:45"
      remediation: "Use parameterized queries"

  verdict: "FAIL"
  blockers: ["VULN-001"]
```

---

## Comandos de Release

### /release-prep

Prepara um novo release para produção.

```bash
/release-prep v1.2.0              # Preparar release
/release-prep v1.2.0 --dry-run    # Apenas validar
/release-prep --changelog         # Apenas gerar changelog
```

**O que faz**:
1. Valida formato de versão (SemVer)
2. Executa `/gate-check` para phase-6-to-7
3. Gera release notes
4. Atualiza CHANGELOG.md
5. Cria tag de versão
6. Documenta rollback plan

**Checklist executado**:
- [ ] Testes passando
- [ ] Security scan OK
- [ ] Code review aprovado
- [ ] Release notes escritas
- [ ] Rollback plan documentado

---

## Comandos de Incidentes

### /incident-start

Inicia workflow de gestão de incidente.

```bash
/incident-start SEV1 "Descrição do problema"
/incident-start SEV2 "API lenta" --assign @alice
```

**Parâmetros**:
- `severidade` (obrigatório): SEV1, SEV2, SEV3, SEV4
- `descrição` (obrigatório): Descrição do problema
- `--assign`: Incident Commander designado

**Severidades**:
| SEV | Impacto | Response Time |
|-----|---------|---------------|
| SEV1 | Sistema indisponível | < 5 min |
| SEV2 | Funcionalidade crítica degradada | < 15 min |
| SEV3 | Funcionalidade secundária afetada | < 1 hora |
| SEV4 | Problema menor | Próximo dia útil |

**O que cria**:
```yaml
incident:
  id: "INC-20260111-001"
  severity: "sev1"
  status: "investigating"
  timeline:
    - time: "14:30"
      event: "Incidente aberto"
```

---

## Resumo de Comandos

| Comando | Propósito | Level | Fase |
|---------|-----------|-------|------|
| `/quick-fix` | Bug fixes rápidos | 0 | 5, 6 |
| `/new-feature` | Features simples | 1 | 2, 5, 6 |
| `/sdlc-start` | Workflow completo | 2-3 | 0-8 |
| `/phase-status` | Ver status atual | Todos | Todas |
| `/gate-check` | Verificar gate | Todos | Entre fases |
| `/sdlc-create-issues` | Criar issues GitHub | 2-3 | 4 → 5 |
| `/adr-create` | Documentar decisão | Todos | 3 |
| `/security-scan` | Scan de segurança | Todos | 6 |
| `/release-prep` | Preparar release | 2-3 | 7 |
| `/incident-start` | Iniciar incidente | Todos | 8 |

---

## Dicas de Uso

### Escolhendo o Comando Certo

```
É um bug fix simples?           → /quick-fix
É feature em serviço existente? → /new-feature
É projeto/serviço novo?         → /sdlc-start
Precisa de compliance?          → /sdlc-start (Level 3)
```

### Workflow Típico - Bug Fix (Level 0)

```bash
/quick-fix "Corrigir validação de CNPJ"
# → Branch fix/corrigir-validacao-cnpj criada
# → Fix implementado e testado
# → PR criada automaticamente
```

### Workflow Típico - Feature (Level 1)

```bash
/new-feature "Exportação PDF"
# → Branch feature/exportacao-pdf criada
# → Spec criada para requisitos
# → Implementação com testes
# → Review e validação
# → PR criada
```

### Workflow Típico - Projeto Completo (Level 2/3)

```bash
# 1. Iniciar projeto
/sdlc-start "Nova API de pagamentos"

# 2. Monitorar progresso
/phase-status

# 3. Antes de avançar fase
/gate-check

# 4. Quando arquitetura decidida
/adr-create "Escolha de database"

# 5. Criar issues para implementação
/sdlc-create-issues --assign-copilot

# 6. Antes do release
/security-scan
/release-prep v1.0.0

# 7. Se der problema
/incident-start SEV2 "API fora do ar"
```

### Atalhos

```bash
# Ver gates disponíveis
/gate-check --list

# Ver ADRs existentes
/adr-create --list

# Dry run de release
/release-prep v1.0.0 --dry-run
```
