---
name: gate-check
description: |
  Verificacao de quality gate entre fases do SDLC.
  Avalia criterios, executa commit se aprovado, e avanca fase automaticamente.

  Examples:
  - <example>
    user: "/gate-check phase-2-to-3"
    assistant: "Vou avaliar o gate de Requisitos para Arquitetura"
    </example>
---

# Verificacao de Quality Gate

## Instrucoes

Este comando avalia quality gates e, se aprovado:
1. Executa commit dos artefatos da fase (via `phase-commit`)
2. Atualiza status no GitHub Project
3. Notifica arquivos para revisao
4. Extrai learnings da sessao
5. Avanca para proxima fase automaticamente

## Processo Automatizado

```bash
# 1. Carregar biblioteca de fallback
source .claude/lib/fallback.sh
source .claude/lib/logging.sh

# 2. Identificar gate
GATE="${1:-$(detect_current_gate)}"
log_info "Avaliando gate: $GATE" "gate-check"

# 3. PRÉ-GATE: Analisar erros da fase (NOVO v1.7.8)
log_info "Analisando erros da fase antes de avaliar gate" "gate-check"

# 3a. Consultar Loki por erros
ERRORS_JSON="/tmp/phase_errors_${GATE}.json"
python3 .claude/skills/session-analyzer/scripts/query_phase_errors.py \
  --json > "$ERRORS_JSON" 2>/dev/null || true

# 3b. Se encontrou erros, classificar e notificar
if [ -s "$ERRORS_JSON" ]; then
    CLASSIFIED_JSON="/tmp/classified_errors_${GATE}.json"
    python3 .claude/skills/session-analyzer/scripts/classify_error.py \
      --error-json "$ERRORS_JSON" --output "$CLASSIFIED_JSON"

    SDLC_BUGS=$(jq -r '.summary.sdlc_bugs' "$CLASSIFIED_JSON" 2>/dev/null || echo "0")
    PROJECT_ISSUES=$(jq -r '.summary.project_issues' "$CLASSIFIED_JSON" 2>/dev/null || echo "0")

    # Notificar bugs do SDLC
    if [ "$SDLC_BUGS" -gt 0 ]; then
        log_error "🐛 $SDLC_BUGS bugs do SDLC Agêntico detectados" "gate-check"
        echo "⚠️  Bugs serão reportados ao owner. Pode haver problemas de funcionamento."
        check_service github && .claude/skills/session-analyzer/scripts/report_sdlc_bug.sh "$CLASSIFIED_JSON" || true
    fi

    # Notificar problemas do projeto
    if [ "$PROJECT_ISSUES" -gt 0 ]; then
        log_warn "⚠️  $PROJECT_ISSUES problemas do projeto detectados" "gate-check"
        read -p "Continuar mesmo com problemas? (y/N): " -n 1 -r
        echo ""
        [[ ! $REPLY =~ ^[Yy]$ ]] && log_info "Gate ABORTADO pelo usuário" "gate-check" && exit 1
    fi

    rm -f "$ERRORS_JSON" "$CLASSIFIED_JSON" 2>/dev/null || true
fi

# 4. Executar gate-evaluator
trace_id=$(trace_start "gate-check-$GATE")
python3 .claude/skills/gate-evaluator/evaluate.py --gate "$GATE"
RESULT=$?
trace_end "$trace_id" "$([ $RESULT -eq 0 ] && echo success || echo error)"

# 5. Se PASSED, executar acoes pos-gate
if [ $RESULT -eq 0 ]; then
    log_info "Gate $GATE PASSED" "gate-check"
    
    # 4a. Commit dos artefatos (phase-commit)
    .claude/skills/phase-commit/scripts/phase-commit.sh
    
    # 4b. Atualizar GitHub Project (se disponivel)
    if check_service github; then
        python3 .claude/skills/github-projects/scripts/project_manager.py update-phase
    fi
    
    # 4c. Extrair learnings (session-analyzer)
    .claude/skills/session-analyzer/scripts/analyze.sh --extract-learnings

    # 4d. Indexar ADRs no corpus RAG (rag-curator)
    python3 .claude/skills/rag-curator/scripts/index_adrs.py

    # 4e. Criar GitHub Issues das tasks (após Phase 3)
    if [[ "$GATE" == "phase-3-to-4" ]] && check_service github; then
        log_info "Criando GitHub Issues das tasks" "gate-check"
        python3 .claude/skills/github-sync/scripts/create_issues_from_tasks.py --assign-copilot
    fi

    # 4f. Notificar arquivos para revisao
    # (implementado no orchestrator)
else
    log_warn "Gate $GATE BLOCKED" "gate-check"
fi
```

## Gates Disponiveis

| Gate | De | Para | Artefatos Chave |
|------|-----|------|-----------------|
| phase-0-to-1 | Preparacao | Descoberta | Intake, Compliance |
| phase-1-to-2 | Descoberta | Requisitos | Research Brief |
| phase-2-to-3 | Requisitos | Arquitetura | Specs, User Stories, **ODRs** |
| phase-3-to-4 | Arquitetura | Planejamento | ADRs, Design Docs, **ODRs** |
| phase-4-to-5 | Planejamento | Implementacao | Sprint Plan |
| phase-5-to-6 | Implementacao | Qualidade | Codigo, Testes |
| phase-6-to-7 | Qualidade | Release | Security Scan |
| phase-7-to-8 | Release | Operacao | Deploy, Runbook |

## Output Esperado

```yaml
gate_evaluation:
  gate: "phase-2-to-3"
  evaluated_at: "2026-01-11T..."
  evaluator: "gate-evaluator"

  artifacts:
    - name: "Spec"
      required: true
      found: true
      location: ".specify/specs/portal-historico.md"

    - name: "User Stories"
      required: true
      found: true
      count: 5

  quality_checks:
    - check: "Specs completas"
      passed: true

    - check: "Criterios de aceite definidos"
      passed: true

    - check: "ODRs aprovados"
      passed: true

  blockers: []

  score: 1.0
  verdict: "PASSED"

  # Acoes executadas apos aprovacao
  post_gate_actions:
    - action: "phase-commit"
      status: "completed"
      commit: "abc123"
    - action: "github-project-update"
      status: "completed"
    - action: "session-analyzer"
      status: "completed"
      learnings_extracted: 3

  next_phase:
    number: 3
    name: "Arquitetura e Design"
    agents: ["system-architect", "adr-author"]
```

## Integracao com Orchestrator

Quando executado pelo @orchestrator, o gate-check:

1. Registra resultado no memory-manager
2. Atualiza manifest do projeto
3. Dispara transicao de fase automaticamente
4. Notifica stakeholders se necessario

## Fallback

Se algum servico falhar:

```yaml
fallback_behavior:
  github_unavailable: "Skip GitHub update, mark for retry"
  phase_commit_fail: "Warn user, continue evaluation"
  session_analyzer_fail: "Log error, continue"
```

## Uso

```
/gate-check                    # Avalia gate da fase atual
/gate-check phase-2-to-3       # Avalia gate especifico
/gate-check --force            # Registra como passed mesmo com warnings
/gate-check --no-commit        # Avalia sem commitar
/gate-check --verbose          # Output detalhado
```
