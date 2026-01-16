---
name: decay-status
description: Mostra o status de decay do corpus RAG
---

# Decay Status

Verifica a saude atual do corpus RAG e mostra nodes que precisam de atencao.

## Uso

```
/decay-status [--detailed] [--filter STATUS]
```

## Opcoes

- `--detailed`: Mostra scores individuais de cada node
- `--filter STATUS`: Filtra por status (fresh, aging, stale, obsolete)

## Workflow

1. Verificar se o decay index existe
2. Se nao existir ou estiver desatualizado, executar o calculador
3. Mostrar resumo da saude do corpus
4. Listar nodes que precisam de revisao

## Implementacao

Execute os seguintes passos:

### Passo 1: Calcular Scores

```bash
python3 .claude/skills/decay-scoring/scripts/decay_calculator.py --update-nodes
```

### Passo 2: Gerar Relatorio

```bash
python3 .claude/skills/decay-scoring/scripts/decay_trigger.py
```

### Passo 3: Interpretar Resultados

- **Corpus Health**: healthy, needs_attention, ou critical
- **Score Medio**: Deve ser >= 0.5 para releases
- **Review Queue**: Items que precisam de acao imediata

## Thresholds

| Score | Status | Acao |
|-------|--------|------|
| 0.70+ | fresh | Nenhuma |
| 0.40-0.69 | aging | Considerar validacao |
| 0.20-0.39 | stale | Revisao recomendada |
| <0.20 | obsolete | Curadoria obrigatoria |

## Acoes de Remediacao

Para nodes com status stale ou obsolete:

1. **Validar**: Confirmar que o conteudo ainda e relevante
   ```bash
   python3 .claude/skills/decay-scoring/scripts/decay_tracker.py validate NODE_ID
   ```

2. **Atualizar**: Editar o conteudo para refletir estado atual

3. **Arquivar**: Mover nodes obsoletos para arquivo
