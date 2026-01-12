---
description: "Mostra o status atual do workflow SDLC"
---

# Status do Workflow SDLC

Use @memory-manager para carregar o estado atual e exibir:

## 1. Informacoes do Projeto

```yaml
project:
  id: string
  name: string
  complexity_level: number
  status: string
```

## 2. Fase Atual

```yaml
current_phase:
  number: number
  name: string
  started_at: datetime
  progress: percentage
  blockers: list[string]
```

## 3. Artefatos da Fase

Liste os artefatos produzidos/pendentes na fase atual:

```yaml
artifacts:
  completed:
    - type: string
      path: string
  pending:
    - type: string
      description: string
```

## 4. Decisoes Tomadas

Liste ADRs criados nesta fase:

```yaml
decisions:
  - id: string
    title: string
    status: string
```

## 5. Proximos Passos

```yaml
next_steps:
  - step: string
    agent: string
    priority: string
```

## 6. Gate Status

Se proximo a transicao, mostre status do gate:

```yaml
gate:
  name: string
  ready: boolean
  missing_items: list[string]
  blockers: list[string]
```

## Formato Visual

```
=== SDLC Status ===

Projeto: {nome}
Complexidade: Level {N}
Status: {ativo/pausado}

Fase Atual: {N} - {nome}
Progresso: [=========>      ] 60%

Artefatos:
  [x] requirements.md
  [x] user-stories/
  [ ] nfr.md (pendente)

Decisoes: 2 ADRs criados
Blockers: Nenhum

Proximo Gate: Phase 2 -> 3
Status: 2/3 criterios atendidos

Proximos Passos:
  1. Completar NFR document
  2. Obter aprovacao do PO
  3. Avancar para Arquitetura
```
