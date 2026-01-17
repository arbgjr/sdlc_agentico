---
description: "Inicia um novo workflow SDLC para um projeto ou feature"
argument-hint: "[descricao do projeto/feature]"
---

# Iniciar Workflow SDLC

Voce esta iniciando um novo workflow de desenvolvimento. Este comando:

1. **Detecta nivel de complexidade** do projeto
2. **Cria estrutura no GitHub** (Project V2, Milestone, Labels)
3. **Inicializa memoria persistente** do projeto
4. **Invoca @orchestrator** para coordenar automaticamente

## 1. Detectar Nivel de Complexidade

Analise a descricao fornecida e classifique:

**Level 0 - Quick Flow** (~5 min)
- Bug fix, typo, correcao simples
- Pular para Fase 5 (Implementacao)

**Level 1 - Feature** (~15 min)
- Feature em servico existente
- Executar Fases 2, 5, 6

**Level 2 - Full SDLC** (~30 min+)
- Novo produto, servico ou integracao
- Executar todas as fases

**Level 3 - Enterprise** (variavel)
- Compliance, multi-team, critico
- Todas as fases + aprovacao humana em cada gate

## 2. Preparar GitHub (Level 2+)

Para projetos Level 2 ou superior, execute automaticamente:

```bash
# Carregar biblioteca de fallback
source .claude/lib/fallback.sh

# Verificar pre-requisitos basicos
if ! check_prerequisites github network; then
    log_with_fallback "ERROR" "Pre-requisitos basicos nao atendidos:"
    echo "  - GitHub CLI autenticado: gh auth status"
    echo "  - Rede disponivel: ping github.com"
    exit 1
fi

# Verificar se estamos em repositorio GitHub
if ! check_service repo; then
    log_with_fallback "WARN" "Nao estamos em repositorio GitHub"

    # Criar repositorio automaticamente
    REPO_NAME=$(basename "$(pwd)")
    log_info "Criando repositorio GitHub: $REPO_NAME"

    # Perguntar visibilidade (public/private)
    read -p "Repositorio publico ou privado? (public/private) [public]: " VISIBILITY
    VISIBILITY=${VISIBILITY:-public}

    # Criar repositorio
    if [[ "$VISIBILITY" == "private" ]]; then
        gh repo create "$REPO_NAME" --private --source=. --remote=origin
    else
        gh repo create "$REPO_NAME" --public --source=. --remote=origin
    fi

    if [[ $? -ne 0 ]]; then
        log_error "Falha ao criar repositorio GitHub"
        exit 1
    fi

    log_success "Repositorio GitHub criado: $REPO_NAME"

    # Fazer push inicial (se houver commits)
    if git rev-parse HEAD >/dev/null 2>&1; then
        git push -u origin main || git push -u origin master
    fi
fi

# Criar labels SDLC (se nao existem)
retry_with_backoff "python3 .claude/skills/github-sync/scripts/label_manager.py ensure"

# Criar GitHub Project V2
PROJECT_NUM=$(gh project create --owner @me --title "SDLC: {feature_name}" --format json | jq '.number')

# Configurar campos customizados SDLC (Phase, Priority, Story Points)
python3 .claude/skills/github-projects/scripts/project_manager.py configure-fields \
  --project-number $PROJECT_NUM

# Criar Milestone inicial
# Usar python para calcular data de forma portável (funciona em Linux e macOS)
DUE_DATE=$(python3 -c "import datetime; print((datetime.date.today() + datetime.timedelta(days=14)).isoformat())")
python3 .claude/skills/github-sync/scripts/milestone_sync.py create \
  --title "Sprint 1" \
  --description "Sprint inicial - {feature_name}" \
  --due-date "$DUE_DATE"
```

## 3. Iniciar Memoria do Projeto

Use @memory-manager para:
- Criar registro do projeto com ID unico
- Definir fase inicial baseada no nivel
- Registrar complexidade detectada
- Vincular Project e Milestone do GitHub

## 4. Invocar Orchestrator

**IMPORTANTE**: Este comando DEVE invocar @orchestrator para coordenar o workflow.

```yaml
orchestrator_request:
  type: start_workflow
  project_id: "{generated_id}"
  context:
    current_phase: 0  # Ou fase inicial baseada no nivel
    complexity_level: {detected_level}
    artifacts: []
    pending_decisions: []
  payload:
    description: "{user_description}"
    github_project_number: {PROJECT_NUM}
    github_milestone: "Sprint 1"
```

O @orchestrator ira:
1. Validar pre-requisitos
2. Carregar contexto do memory-manager
3. Iniciar fase apropriada
4. Delegar para agentes especificos
5. Gerenciar transicoes de fase automaticamente
6. Invocar gate-evaluator entre fases
7. Persistir progresso e decisoes

## 5. Formato de Saida

```yaml
sdlc_initiated:
  project_id: string
  description: string
  complexity_level: number
  starting_phase: number
  agents_needed: list[string]
  estimated_duration: string
  github:
    project_number: number
    project_url: string
    milestone: string
  orchestrator_status: "active"
  next_steps:
    - step: string
      agent: string
```

## 6. Fallback sem GitHub

Se GitHub nao estiver disponivel (offline, auth falhou):

1. Log warning para usuario
2. Continuar workflow local
3. Sincronizar com GitHub quando disponivel via `/github-sync`

```bash
if ! check_service github; then
    log_warn "GitHub indisponivel. Workflow continuara local."
    save_state "pending_github_sync" "{...}"
fi
```

## 7. Proximos Passos

O @orchestrator gerenciara automaticamente os proximos passos.

Para intervencao manual, use:
- `/phase-status` para ver progresso
- `/gate-check` para avaliar transicao de fase
- `/github-dashboard` para ver status no GitHub
- `/alignment-status` para ver ODRs pendentes

---

Descricao do projeto/feature: $ARGUMENTS
