---
name: incident-start
description: |
  Inicia workflow de gestao de incidente.
  Cria canal, documenta timeline, coordena resposta.

  Examples:
  - <example>
    user: "/incident-start SEV2 API de pagamentos lenta"
    assistant: "Iniciando workflow de incidente SEV2"
    </example>
---

# Iniciar Incidente

## Instrucoes

Voce deve iniciar o workflow de gestao de incidente.

## Processo

1. **Classificar Severidade**: Determinar SEV1/SEV2/SEV3/SEV4
2. **Gerar ID**: Criar ID unico (INC-YYYYMMDD-NNN)
3. **Criar Ticket**: Documentar incidente
4. **Designar Roles**: IC, Tech Lead, Comms
5. **Iniciar Timeline**: Registrar primeiro evento
6. **Comunicar**: Notificar stakeholders

## Severidades

| SEV | Descricao | Response Time | Escalation |
|-----|-----------|---------------|------------|
| SEV1 | Sistema indisponivel | < 5 min | CTO, CEO |
| SEV2 | Funcionalidade critica degradada | < 15 min | Eng Manager |
| SEV3 | Funcionalidade secundaria afetada | < 1 hora | Tech Lead |
| SEV4 | Problema menor | Proximo dia | Nenhum |

## Template de Incidente

```yaml
incident:
  id: "INC-20260111-001"
  title: "API de Pagamentos Indisponivel"
  severity: "sev1"
  status: "investigating"

  opened_at: "2026-01-11T14:30:00Z"
  opened_by: "@user"

  impact:
    users_affected: "Estimativa"
    description: "Descricao do impacto"

  team:
    incident_commander: "@user"
    tech_lead: "A designar"
    communications: "A designar"

  timeline:
    - time: "14:30"
      event: "Incidente aberto"
      author: "@user"

  runbook: "link para runbook relevante"
```

## Output

Apos iniciar incidente:

```yaml
incident_started:
  id: "INC-20260111-001"
  severity: "sev2"
  status: "investigating"

  actions_taken:
    - "Incidente criado"
    - "Timeline iniciada"
    - "Stakeholders notificados"

  next_steps:
    - "Investigar causa raiz"
    - "Atualizar timeline"
    - "Comunicar a cada 30 min"

  channel: "#inc-20260111-001"
```

## Uso

```
/incident-start SEV1 "Descricao do problema"
/incident-start SEV2 "API lenta" --assign @alice
/incident-start --template database  # Usar template especifico
```
