---
name: odr-create
description: |
  Cria um novo Organizational Decision Record (ODR) para decisões de negócio/organizacionais.
  Use para decisões que afetam budget, timeline, escopo, stakeholders ou estratégia.
  Para decisões técnicas/arquiteturais, use /adr-create.
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
user-invocable: true
argument-description: |
  Título da decisão organizacional
example-usage: |
  /odr-create "Decisão de build vs buy para módulo de autenticação"
  /odr-create "Extensão de timeline do MVP em 2 semanas"
  /odr-create "Priorização: Feature A sobre Feature B"
---

# Comando: /odr-create

## Propósito

Criar um novo Organizational Decision Record (ODR) para documentar e versionar decisões organizacionais/negócio.

## Quando Usar

Use ODR (não ADR) quando a decisão envolve:
- **Budget**: Mudanças de orçamento > 10%
- **Timeline**: Alterações de prazo > 2 semanas
- **Escopo**: Adição/remoção de features significativas
- **Stakeholders**: Mudança de responsáveis ou aprovadores
- **Estratégia**: Build vs buy, parceiros, fornecedores
- **Priorização**: Conflito entre features ou requisitos

## Workflow

1. **Receber título** da decisão organizacional
2. **Coletar contexto** de negócio
3. **Identificar stakeholders** (decision_maker, consulted, informed)
4. **Listar alternativas** com prós/contras
5. **Documentar trade-offs**
6. **Gerar ODR** no formato YAML
7. **Salvar** em `.agentic_sdlc/projects/{project-id}/decisions/`
8. **Indexar** para RAG corpus

## Template Base

```yaml
odr:
  id: "ODR-{next_id}"
  title: "{user_input}"
  created_at: "{timestamp}"
  updated_at: "{timestamp}"
  status: "draft"
  
  business_context: |
    {contexto coletado}
  
  stakeholders:
    decision_maker:
      name: "{nome}"
      role: "{papel}"
    consulted: []
    informed: []
  
  alternatives:
    - id: "A"
      title: ""
      pros: []
      cons: []
  
  trade_offs: []
  
  decision:
    chosen_alternative: null
    description: ""
    rationale: ""
  
  consequences:
    positive: []
    negative: []
    risks: []
  
  approvals: []
  
  relationships:
    related_odrs: []
    derived_adrs: []
    related_issues: []
    sdlc_phase: {current_phase}
  
  metadata:
    category: "business"
    impact_level: "medium"
    reversible: true
    project_id: "{project_id}"
    tags: []
```

## Ações do Agente

### 1. Obter Contexto do Projeto

```bash
# Verificar projeto atual
PROJECT_ID=$(cat .agentic_sdlc/.current-project 2>/dev/null || echo "default")
CURRENT_PHASE=$(yq '.project.current_phase' .agentic_sdlc/projects/$PROJECT_ID/manifest.yml 2>/dev/null || echo "0")
```

### 2. Gerar ID Único

```bash
# Encontrar próximo ID de ODR
LAST_ODR=$(ls .agentic_sdlc/projects/$PROJECT_ID/decisions/odr-*.yml 2>/dev/null | sort -V | tail -1)
if [ -z "$LAST_ODR" ]; then
  NEXT_ID="001"
else
  LAST_NUM=$(basename "$LAST_ODR" .yml | sed 's/odr-//')
  NEXT_ID=$(printf "%03d" $((10#$LAST_NUM + 1)))
fi
```

### 3. Coletar Informações (Interativo)

Perguntar ao usuário:
1. Qual o contexto de negócio desta decisão?
2. Quem é o responsável pela decisão final?
3. Quem deve ser consultado? (inputs necessários)
4. Quais alternativas estão sendo consideradas?
5. Qual é o deadline para esta decisão?

### 4. Gerar e Salvar ODR

```python
import yaml
from datetime import datetime
from pathlib import Path

def create_odr(title: str, project_id: str, context: str, stakeholders: dict, alternatives: list) -> str:
    """Cria novo ODR e retorna o ID."""
    
    decisions_dir = Path(f".agentic_sdlc/projects/{project_id}/decisions")
    decisions_dir.mkdir(parents=True, exist_ok=True)
    
    # Encontrar próximo ID
    existing = list(decisions_dir.glob("odr-*.yml"))
    next_num = len(existing) + 1
    odr_id = f"ODR-{next_num:03d}"
    
    odr = {
        "odr": {
            "id": odr_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "draft",
            "business_context": context,
            "stakeholders": stakeholders,
            "alternatives": alternatives,
            "trade_offs": [],
            "decision": {
                "chosen_alternative": None,
                "description": "",
                "rationale": ""
            },
            "consequences": {
                "positive": [],
                "negative": [],
                "risks": []
            },
            "approvals": [],
            "relationships": {
                "related_odrs": [],
                "derived_adrs": [],
                "related_issues": [],
                "sdlc_phase": None
            },
            "metadata": {
                "category": "business",
                "impact_level": "medium",
                "reversible": True,
                "project_id": project_id,
                "tags": []
            }
        }
    }
    
    # Salvar
    odr_file = decisions_dir / f"odr-{next_num:03d}.yml"
    with open(odr_file, "w") as f:
        yaml.dump(odr, f, default_flow_style=False, allow_unicode=True)
    
    return odr_id
```

### 5. Indexar para RAG

Após criar o ODR, indexá-lo no corpus:

```bash
# Copiar para corpus de decisões
cp ".agentic_sdlc/projects/$PROJECT_ID/decisions/odr-$NEXT_ID.yml" \
   ".agentic_sdlc/corpus/decisions/"

# Atualizar índice de decay (se decay-scoring ativo)
if [ -f ".agentic_sdlc/corpus/decay_index.json" ]; then
    python3 .claude/skills/decay-scoring/scripts/decay_tracker.py add-node "odr-$NEXT_ID"
fi
```

## Output Esperado

```
✅ ODR criado com sucesso!

📋 ODR-001: Decisão de build vs buy para módulo de autenticação

Status: draft
Fase SDLC: 3 (Architecture)
Categoria: strategic

Próximos passos:
1. Completar contexto de negócio
2. Identificar alternativas com prós/contras
3. Coletar inputs de stakeholders consultados
4. Documentar trade-offs
5. Submeter para aprovação

Arquivo: .agentic_sdlc/projects/my-project/decisions/odr-001.yml

💡 Use /alignment-status para ver todos os ODRs e seu status.
```

## Integração com Gates

ODRs são verificados automaticamente nos gates:
- Phase 2→3: Se budget > R$100k, requer ODR aprovado
- Phase 3→4: Se 3+ stakeholders, requer ODR aprovado
- Qualquer phase: Decisões estratégicas requerem ODR

## Referências

- Guia ADR vs ODR: `.docs/guides/adr-vs-odr.md`
- Template ODR: `.agentic_sdlc/templates/odr-template.yml`
- Schema: `.claude/skills/memory-manager/SKILL.md`
