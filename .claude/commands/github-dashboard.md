---
name: github-dashboard
description: |
  Mostra visao consolidada do projeto no GitHub.
  Exibe status do Project, Milestone e Wiki.

  Examples:
  - <example>
    Context: Quer ver status geral do projeto
    user: "/github-dashboard"
    assistant: "Vou mostrar o dashboard consolidado do GitHub"
    </example>
---

# GitHub Dashboard

## Instrucoes

Exiba uma visao consolidada do status do projeto no GitHub, incluindo
Project V2, Milestones e Wiki.

## Processo

### 1. Coletar Dados

Execute os comandos abaixo para coletar informacoes:

```bash
# Informacoes do repositorio
gh repo view --json nameWithOwner,url

# Projects do repositorio
gh project list --owner @me --format json

# Milestones ativos
gh api repos/{owner}/{repo}/milestones --jq '.[] | {title, open_issues, closed_issues, due_on}'

# Issues por fase SDLC
gh issue list --label "phase:5" --state open --json number,title --jq 'length'

# Verificar se Wiki existe (tentar clonar)
git ls-remote https://github.com/{owner}/{repo}.wiki.git 2>/dev/null && echo "Wiki: Disponivel"
```

### 2. Formatar Output

Apresente os dados no formato abaixo:

```
================================================================================
                    GitHub Dashboard - SDLC: {Project Name}
================================================================================

+-- Project Status -------------------------------------------------------+
|  Backlog:        {count} issues                                          |
|  Requirements:   {count} issues                                          |
|  Architecture:   {count} issues                                          |
|  In Progress:    {count} issues                                          |
|  QA:             {count} issues                                          |
|  Done:           {count} issues                                          |
+-------------------------------------------------------------------------+

+-- Sprint Current ({Milestone Name}) ------------------------------------+
|  Due Date:       {YYYY-MM-DD}                                           |
|  Progress:       {percentage}% ({closed}/{total} issues closed)         |
|  Open Issues:    #{n1}, #{n2}, #{n3}                                    |
|  Burndown:       https://github.com/{owner}/{repo}/milestones           |
+-------------------------------------------------------------------------+

+-- Wiki Status ----------------------------------------------------------+
|  Status:         {Disponivel | Nao inicializada}                        |
|  Last Update:    {timestamp}                                            |
|  ADRs Published: {count}                                                |
+-------------------------------------------------------------------------+

+-- Quick Links ----------------------------------------------------------+
|  Project:  https://github.com/{owner}/{repo}/projects/{n}               |
|  Issues:   https://github.com/{owner}/{repo}/issues                     |
|  Wiki:     https://github.com/{owner}/{repo}/wiki                       |
|  PRs:      https://github.com/{owner}/{repo}/pulls                      |
+-------------------------------------------------------------------------+
```

### 3. Contagem de Issues por Fase

Para contar issues por fase SDLC:

```bash
# Backlog (phase:0 ou phase:1)
gh issue list --label "phase:0" --state open --json number --jq 'length'
gh issue list --label "phase:1" --state open --json number --jq 'length'

# Requirements (phase:2)
gh issue list --label "phase:2" --state open --json number --jq 'length'

# Architecture (phase:3)
gh issue list --label "phase:3" --state open --json number --jq 'length'

# Planning (phase:4)
gh issue list --label "phase:4" --state open --json number --jq 'length'

# In Progress (phase:5)
gh issue list --label "phase:5" --state open --json number --jq 'length'

# QA (phase:6)
gh issue list --label "phase:6" --state open --json number --jq 'length'

# Release (phase:7)
gh issue list --label "phase:7" --state open --json number --jq 'length'

# Done (closed issues com sdlc:auto)
gh issue list --label "sdlc:auto" --state closed --json number --jq 'length'
```

### 4. Status do Milestone

```bash
# Obter milestone atual (primeiro aberto)
gh api repos/{owner}/{repo}/milestones \
  --jq '.[0] | "Sprint: \(.title)\nDue: \(.due_on)\nProgress: \(.closed_issues)/\(.open_issues + .closed_issues)"'
```

### 5. Verificar Wiki

```bash
# Verificar se wiki tem conteudo
if git ls-remote "https://github.com/{owner}/{repo}.wiki.git" &>/dev/null; then
  echo "Wiki: Disponivel"
  # Tentar contar paginas
  WIKI_TMP=$(mktemp -d)
  git clone "https://github.com/{owner}/{repo}.wiki.git" "$WIKI_TMP" --quiet
  echo "Paginas: $(find $WIKI_TMP -name '*.md' | wc -l)"
  rm -rf "$WIKI_TMP"
else
  echo "Wiki: Nao inicializada"
fi
```

## Output Esperado

```yaml
github_dashboard:
  repository:
    name: "owner/repo"
    url: "https://github.com/owner/repo"

  project:
    number: 1
    url: "https://github.com/users/owner/projects/1"
    issues_by_phase:
      backlog: 5
      requirements: 2
      architecture: 1
      planning: 0
      in_progress: 3
      qa: 2
      release: 0
      done: 10

  milestone:
    title: "Sprint 1"
    due_date: "2026-01-28"
    progress_percent: 60
    open_issues: 4
    closed_issues: 6
    url: "https://github.com/owner/repo/milestone/1"

  wiki:
    status: "available"
    pages_count: 8
    adrs_count: 5
    last_update: "2026-01-14"
    url: "https://github.com/owner/repo/wiki"

  links:
    project: "https://github.com/users/owner/projects/1"
    issues: "https://github.com/owner/repo/issues"
    wiki: "https://github.com/owner/repo/wiki"
    pulls: "https://github.com/owner/repo/pulls"
```

## Uso Recomendado

Execute o dashboard periodicamente para:
- Verificar progresso do sprint
- Identificar gargalos (muitas issues em uma fase)
- Verificar se documentacao esta atualizada
- Obter links rapidos para recursos do projeto
