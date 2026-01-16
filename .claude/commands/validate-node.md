---
name: validate-node
description: Marca um node do corpus como validado/atual
---

# Validate Node

Marca um node do corpus como validado, resetando seu componente de decay de validacao.

## Uso

```
/validate-node NODE_ID [--validator NAME]
```

## Argumentos

- `NODE_ID`: O ID do node a ser validado (ex: adr-001, learning-005)
- `--validator`: Quem esta validando (default: "human")

## Workflow

1. Localizar o node no corpus
2. Atualizar o campo `last_validated_at`
3. Adicionar entrada no `validation_history`
4. Recalcular o decay score do node

## Implementacao

### Passo 1: Validar o Node

```bash
python3 .claude/skills/decay-scoring/scripts/decay_tracker.py validate NODE_ID --validator human
```

### Passo 2: Recalcular Score (Opcional)

```bash
python3 .claude/skills/decay-scoring/scripts/decay_calculator.py --update-nodes
```

## Exemplo de Uso

```
/validate-node adr-001
```

Isso vai:
1. Atualizar `last_validated_at` para agora
2. Adicionar entrada: `{date: now, validator: human, action: validated}`
3. Resetar o componente `validation_score` para 1.0

## Quando Validar

- Apos revisar um ADR e confirmar que ainda e valido
- Quando um learning foi verificado em producao
- Apos atualizar um pattern com informacoes novas
- Periodicamente para manter o corpus saudavel

## Campos Atualizados

```yaml
decay_metadata:
  last_validated_at: "2025-01-14T10:00:00Z"  # Atualizado
  validation_history:
    - date: "2025-01-14T10:00:00Z"           # Adicionado
      validator: "human"
      action: "validated"
```
