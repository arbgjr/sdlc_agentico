---
name: sdlc-create-issues
description: |
  Cria issues no GitHub a partir das tasks geradas pelo SDLC.
  Opcionalmente atribui ao Copilot Coding Agent para implementacao automatica.
  Integra com GitHub Projects, Milestones e Labels SDLC.

  Examples:
  - <example>
    Context: Tasks ja foram geradas
    user: "/sdlc-create-issues"
    assistant: "Vou criar issues no GitHub para cada task pendente"
    </example>
  - <example>
    Context: Quer que Copilot implemente
    user: "/sdlc-create-issues --assign-copilot"
    assistant: "Vou criar issues e atribuir ao @copilot para implementacao automatica"
    </example>
---

# Criar Issues no GitHub a partir do SDLC

## Instrucoes

Voce deve criar issues no GitHub a partir das tasks geradas pelo processo SDLC,
com integracao completa a Projects V2, Milestones e Labels SDLC.

## Pre-requisitos

### 1. Garantir Labels SDLC Existem

```bash
python3 .claude/skills/github-sync/scripts/label_manager.py ensure
```

### 2. Verificar Milestone do Sprint

```bash
python3 .claude/skills/github-sync/scripts/milestone_sync.py list
```

Se nao existir, criar:
```bash
python3 .claude/skills/github-sync/scripts/milestone_sync.py create \
  --title "Sprint 1" \
  --description "Sprint goal" \
  --due-date "$(date -d '+14 days' +%Y-%m-%d)"
```

## Processo

### 1. Localizar Tasks

Busque por tasks em:
- `.specify/tasks/*.md` (Spec Kit)
- `.agentic_sdlc/projects/*/tasks/*.yml` (Memory Manager)
- `.claude/memory/tasks/*.yml` (Legacy)
- Contexto da conversa atual

### 2. Para Cada Task, Criar Issue com Labels SDLC

Use o script issue_sync.py ou GitHub CLI:

```bash
# Opcao 1: Via script (recomendado)
python3 .claude/skills/github-sync/scripts/issue_sync.py create \
  --title "[TASK-XXX] Titulo da Task" \
  --body-file <arquivo_da_task> \
  --phase 5 \
  --type task \
  --milestone "Sprint 1"

# Opcao 2: Via gh CLI com labels SDLC
gh issue create \
  --title "[TASK-XXX] Titulo da Task" \
  --body-file <arquivo_da_task> \
  --label "sdlc:auto,phase:5,type:task" \
  --milestone "Sprint 1"
```

### 3. Formato do Body da Issue

```markdown
## Contexto

[Link para a Spec original]
[Link para o Technical Plan]

## Descricao

[Descricao detalhada da task]

## Criterios de Aceite

- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Arquivos Relevantes

- `src/caminho/arquivo.py`
- `tests/test_arquivo.py`

## Dependencias

- Depende de: #123 (outra issue)
- Bloqueado por: [descricao]

## Notas para o Implementador

[Dicas, restricoes, padroes a seguir]

---
*Gerado pelo SDLC Agentico - Fase 4 (Planejamento)*
```

### 4. Se --assign-copilot

Adicione `--assignee "@copilot"` ao comando:

```bash
python3 .claude/skills/github-sync/scripts/issue_sync.py create \
  --title "[TASK-XXX] Titulo" \
  --body-file task.md \
  --phase 5 \
  --type task \
  --milestone "Sprint 1" \
  --assignee "@copilot"
```

### 5. Adicionar ao GitHub Project (Opcional)

Se o projeto tiver um GitHub Project V2 configurado:

```bash
# Obter URL da issue criada
ISSUE_URL="https://github.com/owner/repo/issues/123"

# Adicionar ao project
python3 .claude/skills/github-projects/scripts/project_manager.py add-item \
  --project-number 1 \
  --issue-url "$ISSUE_URL"
```

### 6. Registrar Issues Criadas

Salve mapeamento task -> issue:

```yaml
# .claude/memory/issue-mapping.yml
mapping:
  - task_id: "TASK-001"
    issue_number: 123
    assigned_to: "@copilot"
    created_at: "2026-01-11T..."

  - task_id: "TASK-002"
    issue_number: 124
    assigned_to: "human"
    created_at: "2026-01-11T..."
```

## Output Esperado

```yaml
issues_created:
  total: 5
  assigned_to_copilot: 3
  assigned_to_human: 2

  issues:
    - number: 123
      title: "[TASK-001] Implementar endpoint de autenticacao"
      assignee: "@copilot"
      url: "https://github.com/owner/repo/issues/123"

    - number: 124
      title: "[TASK-002] Criar testes de integracao"
      assignee: "armando_jr"
      url: "https://github.com/owner/repo/issues/124"

next_steps:
  - "Acompanhe PRs em: gh pr list --author app/copilot-workspace"
  - "Revise PRs: gh pr review <numero>"
  - "Mencione @copilot em PRs para solicitar mudancas"
```

## Verificacoes Pre-Criacao

Antes de criar issues, verifique:

1. **Autenticacao GitHub CLI**
   ```bash
   gh auth status
   ```

2. **Repositorio Correto**
   ```bash
   gh repo view --json nameWithOwner
   ```

3. **Copilot Agent Habilitado** (se --assign-copilot)
   ```bash
   gh api repos/OWNER/REPO --jq '.allow_copilot_coding_agent'
   ```

4. **Tasks Existentes**
   ```bash
   ls .specify/tasks/ 2>/dev/null || ls .claude/memory/tasks/ 2>/dev/null
   ```

## Tratamento de Erros

- Se GitHub CLI nao autenticado: Instrua usuario a executar `gh auth login`
- Se Copilot Agent nao habilitado: Instrua a habilitar via Settings
- Se tasks nao encontradas: Instrua a executar `/speckit.tasks` primeiro
