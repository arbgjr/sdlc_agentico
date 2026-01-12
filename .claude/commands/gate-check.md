---
name: gate-check
description: |
  Verificacao manual de quality gate entre fases do SDLC.
  Avalia se todos os artefatos e criterios foram cumpridos.

  Examples:
  - <example>
    user: "/gate-check phase-2-to-3"
    assistant: "Vou avaliar o gate de Requisitos para Arquitetura"
    </example>
---

# Verificacao de Quality Gate

## Instrucoes

Voce deve avaliar se o projeto atende aos criterios do gate especificado.

## Processo

1. **Identificar Gate**: Determinar qual transicao esta sendo avaliada
2. **Carregar Criterios**: Usar skill `gate-evaluator` para obter criterios
3. **Verificar Artefatos**: Checar se artefatos obrigatorios existem
4. **Avaliar Qualidade**: Verificar criterios de qualidade
5. **Identificar Bloqueadores**: Listar o que impede aprovacao
6. **Emitir Veredicto**: PASSED ou BLOCKED

## Gates Disponiveis

| Gate | De | Para | Artefatos Chave |
|------|-----|------|-----------------|
| phase-0-to-1 | Preparacao | Descoberta | Intake, Compliance |
| phase-1-to-2 | Descoberta | Requisitos | Research Brief |
| phase-2-to-3 | Requisitos | Arquitetura | Specs, User Stories |
| phase-3-to-4 | Arquitetura | Planejamento | ADRs, Design Docs |
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

    - check: "NFRs documentados"
      passed: false
      reason: "Faltam requisitos de performance"

  blockers:
    - "NFRs de performance nao documentados"

  score: 0.85
  verdict: "BLOCKED"

  required_actions:
    - "Adicionar NFRs de performance na spec"
    - "Definir SLAs de tempo de resposta"
```

## Uso

```
/gate-check                    # Avalia gate da fase atual
/gate-check phase-2-to-3       # Avalia gate especifico
/gate-check --force            # Registra como passed mesmo com warnings
```
