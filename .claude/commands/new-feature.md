---
description: "Inicia fluxo para nova feature em servico existente (Level 1)"
argument-hint: "[nome da feature]"
---

# New Feature Flow (Level 1)

Fluxo para adicionar funcionalidade em servico existente.

## Criterios de Elegibilidade

Este fluxo e apropriado quando:

- Feature em servico ja existente
- Sem novo servico ou dominio
- Sem mudanca significativa de arquitetura
- Sem requisitos de compliance novos

## Nome da Feature

$ARGUMENTS

## Fases Executadas

| Fase | Agentes | Duracao Estimada |
|------|---------|------------------|
| 2 - Requisitos | @requirements-analyst | ~10 min |
| 5 - Implementacao | @code-author, @test-author | ~20-60 min |
| 6 - Validacao | @code-reviewer, @qa-analyst | ~10 min |

## Fluxo de Execucao

### 1. Inicializacao

```yaml
init:
  - action: Criar branch
    command: ".claude/hooks/auto-branch.sh feature {nome}"

  - action: Criar spec
    path: ".agentic_sdlc/projects/{id}/specs/{nome}.spec.md"
    template: ".agentic_sdlc/templates/spec-template.md"

  - action: Registrar no manifest
    update: ".agentic_sdlc/projects/{id}/manifest.yml"
```

### 2. Requisitos (Fase 2)

Use @requirements-analyst para:

1. **Clarificar requisitos** com o usuario
2. **Escrever user stories** com acceptance criteria
3. **Identificar edge cases** e cenarios de erro
4. **Documentar NFRs** se aplicavel

Output: Spec preenchida com requisitos claros

### 3. Quick Design (se necessario)

Se a feature nao for um CRUD simples, use @code-author para:

1. Identificar arquivos afetados
2. Propor abordagem de implementacao
3. Estimar impacto

### 4. Implementacao (Fase 5)

Use @code-author e @test-author em paralelo:

**@code-author:**
- Implementar feature seguindo padroes do projeto
- Manter codigo limpo e legivel
- Documentar decisoes importantes

**@test-author:**
- Criar testes unitarios
- Criar testes de integracao
- Cobrir acceptance criteria

### 5. Review (Fase 5)

Use @code-reviewer para:

- [ ] Qualidade de codigo
- [ ] Cobertura de testes >= 80%
- [ ] Sem issues de seguranca
- [ ] Segue padroes do projeto
- [ ] Documentacao adequada

### 6. Validacao (Fase 6)

Use @qa-analyst para:

- [ ] Acceptance criteria atendidos
- [ ] Sem regressoes
- [ ] Performance aceitavel
- [ ] UX adequada (se aplicavel)

### 7. Finalizacao

1. Criar PR com resumo da feature
2. Atualizar changelog
3. Marcar spec como completa
4. Aguardar aprovacao humana

## Output Esperado

```yaml
feature_result:
  name: "{nome da feature}"
  branch: "feature/{nome}"
  spec_path: ".agentic_sdlc/projects/{id}/specs/{nome}.spec.md"

  requirements:
    user_stories: number
    acceptance_criteria: number
    edge_cases: number

  implementation:
    files_created: number
    files_modified: number
    lines_added: number
    lines_removed: number

  tests:
    unit_tests: number
    integration_tests: number
    coverage: percentage

  review:
    status: approved | changes_requested
    comments: number

  validation:
    ac_passed: number
    ac_total: number

  pr:
    url: "{url do PR}"
    status: open | merged
```

## Integracao com SpecKit

Este fluxo integra com SpecKit para gerenciar especificacoes:

```yaml
spec_kit_integration:
  1_create_spec:
    command: "specify create {nome}"
    output: "{nome}.spec.md"

  2_generate_tasks:
    command: "specify tasks {nome}.spec.md"
    output: "Tasks no GitHub Issues"

  3_track_progress:
    command: "specify status {nome}"
    output: "Progresso das tasks"
```

## Gatilhos de Escalacao

| Situacao | Acao |
|----------|------|
| Novo dominio | Escalar para Level 2 (/sdlc-start) |
| Mudanca de DB schema | Chamar @data-architect |
| Novo endpoint publico | Chamar @threat-modeler |
| Performance critica | Chamar @performance-analyst |
| Requisitos de compliance | Chamar @compliance-guardian |

## Convencao de Commit

```
feat({escopo}): {descricao curta}

{descricao mais detalhada}

- {item 1 implementado}
- {item 2 implementado}

Implements: {spec-name}.spec.md
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Exemplo de Uso

```
/new-feature "Exportacao de duplicatas em PDF"
```

Resultado:
1. Branch: `feature/exportacao-duplicatas-pdf`
2. Spec: Requisitos de exportacao PDF
3. User Stories:
   - Como emissor, quero exportar duplicatas em PDF
   - Como emissor, quero escolher layout do PDF
4. Implementacao: PdfExportService, PdfExportController
5. Testes: PdfExportServiceTests, PdfExportIntegrationTests
6. PR: #125

## Checklist da Feature

### Requisitos
- [ ] User stories claras
- [ ] Acceptance criteria definidos
- [ ] Edge cases identificados
- [ ] NFRs documentados (se aplicavel)

### Implementacao
- [ ] Codigo implementado
- [ ] Segue padroes do projeto
- [ ] Sem hardcoded values
- [ ] Logs adequados
- [ ] Tratamento de erros

### Testes
- [ ] Testes unitarios
- [ ] Testes de integracao
- [ ] Cobertura >= 80%
- [ ] Testes de edge cases

### Review
- [ ] Code review aprovado
- [ ] Sem issues criticos
- [ ] Documentacao atualizada

### Validacao
- [ ] Todos ACs passam
- [ ] Sem regressoes
- [ ] Performance OK
