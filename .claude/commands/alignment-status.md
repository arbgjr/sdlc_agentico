---
name: alignment-status
description: |
  Exibe dashboard de decisões organizacionais (ODRs) e trade-offs.
  Mostra status, pendências e timeline de decisões.
  Use para: ver ODRs ativos, trade-offs pendentes, histórico de decisões.
allowed-tools:
  - Read
  - Glob
  - Bash
user-invocable: true
argument-description: |
  Filtros opcionais: --project, --pending, --stakeholder, --category
example-usage: |
  /alignment-status
  /alignment-status --pending
  /alignment-status --stakeholder "PM"
  /alignment-status --category strategic
---

# Comando: /alignment-status

## Propósito

Exibir dashboard consolidado de Organizational Decision Records (ODRs), mostrando status de decisões, trade-offs pendentes e timeline de aprovações.

## Workflow

1. **Identificar projeto atual**
2. **Carregar todos os ODRs**
3. **Aplicar filtros** (se fornecidos)
4. **Gerar dashboard** formatado
5. **Exibir resultado**

## Output Esperado

```
════════════════════════════════════════════════════════════════
           ALIGNMENT STATUS - Projeto: {project_name}
════════════════════════════════════════════════════════════════

📋 ODRs Ativos
┌──────────┬────────────────────────────────┬────────────┬─────────────────┬────────────┐
│ ID       │ Título                         │ Status     │ Stakeholders    │ Deadline   │
├──────────┼────────────────────────────────┼────────────┼─────────────────┼────────────┤
│ ODR-001  │ Build vs Buy - Autenticação    │ 🟡 pending │ PM, CTO, SecLead│ 2026-01-20 │
│ ODR-002  │ Extensão de Timeline MVP       │ ✅ approved │ PM, PO          │ -          │
│ ODR-003  │ Priorização: Feature A vs B    │ 📝 draft   │ PO              │ 2026-01-25 │
└──────────┴────────────────────────────────┴────────────┴─────────────────┴────────────┘

⚖️ Trade-offs Pendentes de Decisão
- [ ] ODR-001: Controle total (build) vs Time-to-market (buy)
- [ ] ODR-003: Feature A (receita) vs Feature B (retenção)

📅 Timeline (últimos 30 dias)
├─ 2026-01-15: ODR-002 aprovado por PM
├─ 2026-01-12: ODR-001 aguardando input de CTO
├─ 2026-01-10: ODR-003 criado (draft)
└─ 2026-01-08: ODR-001 criado

📊 Métricas
├─ Total ODRs: 3
├─ Aprovados: 1 (33%)
├─ Pendentes: 2 (67%)
├─ Tempo médio para aprovação: 5 dias
└─ Inputs pendentes: 2

🔗 Links Rápidos
├─ /odr-create "Novo ODR"
├─ /odr-input ODR-001 "Meu feedback"
└─ /odr-approve ODR-001

════════════════════════════════════════════════════════════════
```

## Implementação

### 1. Carregar ODRs

```python
import yaml
from pathlib import Path
from datetime import datetime, timedelta

def load_odrs(project_id: str) -> list:
    """Carrega todos os ODRs de um projeto."""
    decisions_dir = Path(f".agentic_sdlc/projects/{project_id}/decisions")
    odrs = []
    
    for odr_file in decisions_dir.glob("odr-*.yml"):
        with open(odr_file) as f:
            data = yaml.safe_load(f)
            odrs.append(data.get("odr", data))
    
    return sorted(odrs, key=lambda x: x.get("created_at", ""), reverse=True)
```

### 2. Aplicar Filtros

```python
def filter_odrs(odrs: list, filters: dict) -> list:
    """Aplica filtros aos ODRs."""
    result = odrs
    
    if filters.get("pending"):
        result = [o for o in result if o.get("status") in ["draft", "pending_input", "pending_approval"]]
    
    if filters.get("stakeholder"):
        stakeholder = filters["stakeholder"].lower()
        result = [o for o in result if 
            stakeholder in str(o.get("stakeholders", {})).lower()]
    
    if filters.get("category"):
        result = [o for o in result if 
            o.get("metadata", {}).get("category") == filters["category"]]
    
    return result
```

### 3. Formatar Status

```python
def format_status(status: str) -> str:
    """Formata status com emoji."""
    status_map = {
        "draft": "📝 draft",
        "pending_input": "🟡 pending",
        "pending_approval": "🟠 approval",
        "approved": "✅ approved",
        "rejected": "❌ rejected",
        "superseded": "🔄 superseded"
    }
    return status_map.get(status, status)
```

### 4. Extrair Trade-offs Pendentes

```python
def get_pending_tradeoffs(odrs: list) -> list:
    """Extrai trade-offs de ODRs pendentes."""
    tradeoffs = []
    
    for odr in odrs:
        if odr.get("status") in ["draft", "pending_input", "pending_approval"]:
            for to in odr.get("trade_offs", []):
                if to.get("assessment") != "acceptable":
                    tradeoffs.append({
                        "odr_id": odr.get("id"),
                        "description": to.get("description"),
                        "gain": to.get("gain"),
                        "loss": to.get("loss")
                    })
    
    return tradeoffs
```

### 5. Gerar Timeline

```python
def generate_timeline(odrs: list, days: int = 30) -> list:
    """Gera timeline de eventos dos últimos N dias."""
    events = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for odr in odrs:
        # Evento de criação
        created = odr.get("created_at")
        if created:
            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if created_dt.replace(tzinfo=None) > cutoff:
                events.append({
                    "date": created,
                    "odr_id": odr.get("id"),
                    "event": "criado",
                    "status": odr.get("status")
                })
        
        # Eventos de aprovação
        for approval in odr.get("approvals", []):
            if approval.get("approved_at"):
                events.append({
                    "date": approval["approved_at"],
                    "odr_id": odr.get("id"),
                    "event": "aprovado" if approval.get("approved") else "rejeitado",
                    "by": approval.get("stakeholder")
                })
    
    return sorted(events, key=lambda x: x.get("date", ""), reverse=True)
```

### 6. Calcular Métricas

```python
def calculate_metrics(odrs: list) -> dict:
    """Calcula métricas dos ODRs."""
    total = len(odrs)
    approved = len([o for o in odrs if o.get("status") == "approved"])
    pending = len([o for o in odrs if o.get("status") in ["draft", "pending_input", "pending_approval"]])
    
    # Tempo médio para aprovação
    approval_times = []
    for odr in odrs:
        if odr.get("status") == "approved":
            created = datetime.fromisoformat(odr.get("created_at", "").replace("Z", "+00:00"))
            for approval in odr.get("approvals", []):
                if approval.get("approved") and approval.get("approved_at"):
                    approved_at = datetime.fromisoformat(approval["approved_at"].replace("Z", "+00:00"))
                    approval_times.append((approved_at - created).days)
                    break
    
    avg_approval_time = sum(approval_times) / len(approval_times) if approval_times else 0
    
    # Inputs pendentes
    pending_inputs = 0
    for odr in odrs:
        if odr.get("status") == "pending_input":
            for c in odr.get("stakeholders", {}).get("consulted", []):
                if c.get("input_status") == "pending":
                    pending_inputs += 1
    
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "avg_approval_days": round(avg_approval_time, 1),
        "pending_inputs": pending_inputs
    }
```

## Parâmetros

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `--project` | Filtrar por projeto | `--project my-project` |
| `--pending` | Apenas ODRs pendentes | `--pending` |
| `--stakeholder` | Filtrar por stakeholder | `--stakeholder "PM"` |
| `--category` | Filtrar por categoria | `--category strategic` |
| `--days` | Timeline de N dias | `--days 60` |

## Categorias de ODR

- `business` - Decisões de negócio gerais
- `resource` - Budget, equipe, recursos
- `timeline` - Prazos, cronograma
- `scope` - Escopo, features
- `strategic` - Decisões estratégicas (build vs buy, etc)

## Integração

Este comando é usado por:
- **orchestrator**: Para verificar ODRs pendentes antes de gates
- **alignment-agent**: Para mostrar status após criar/atualizar ODR
- **gate-evaluator**: Para verificar se ODRs obrigatórios estão aprovados

## Referências

- Criar ODR: `/odr-create`
- Template: `.agentic_sdlc/templates/odr-template.yml`
- Guia: `.docs/guides/adr-vs-odr.md`
