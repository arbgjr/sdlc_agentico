---
name: sdlc-flags
description: |
  Gerencia feature flags do SDLC Agêntico.
  Permite habilitar/desabilitar funcionalidades.
allowed-tools:
  - Read
  - Write
  - Bash
user-invocable: true
version: "1.0.0"
---

# /sdlc-flags

Gerencia feature flags do SDLC Agêntico para experimentação controlada.

## Uso

```
/sdlc-flags [subcommand] [args]
```

## Subcomandos

| Comando | Descrição |
|---------|-----------|
| `list` | Lista todas as flags |
| `get <flag>` | Valor de uma flag |
| `enable <flag>` | Habilita uma flag |
| `disable <flag>` | Desabilita uma flag |
| `reset` | Restaura defaults |

## Feature Flags Disponíveis

| Flag | Default | Descrição |
|------|---------|-----------|
| `github_projects` | true | Integração com GitHub Projects V2 |
| `wiki_sync` | true | Sincronização automática de Wiki |
| `rag_indexing` | true | Indexação automática do RAG |
| `session_analyzer` | true | Análise de sessões |
| `auto_commit` | false | Commits automáticos por fase |
| `copilot_assign` | false | Atribuir issues ao Copilot por default |
| `strict_gates` | false | Gates obrigatórios (bloqueia avanço) |
| `ab_experiments` | false | Experimentos A/B nos fluxos |

## Arquivo de Flags

As flags são armazenadas em `.claude/flags.yml`:

```yaml
flags:
  github_projects:
    enabled: true
    description: "Integração com GitHub Projects V2"
    since: "1.0.0"
    
  wiki_sync:
    enabled: true
    description: "Sincronização automática de Wiki"
    since: "1.0.0"
    
  rag_indexing:
    enabled: true
    description: "Indexação automática do RAG"
    since: "1.0.0"
    
  session_analyzer:
    enabled: true
    description: "Análise de sessões para learnings"
    since: "1.0.0"
    
  auto_commit:
    enabled: false
    description: "Commits automáticos por fase"
    since: "1.0.0"
    experimental: true
    
  copilot_assign:
    enabled: false
    description: "Atribuir issues ao Copilot por default"
    since: "1.0.0"
    
  strict_gates:
    enabled: false
    description: "Gates obrigatórios (bloqueia avanço)"
    since: "1.0.0"
    
  ab_experiments:
    enabled: false
    description: "Experimentos A/B nos fluxos"
    since: "1.0.0"
    experimental: true
```

## Exemplos

### Listar flags
```
/sdlc-flags list
```

### Habilitar auto-commit
```
/sdlc-flags enable auto_commit
```

### Desabilitar wiki sync
```
/sdlc-flags disable wiki_sync
```

## Experimentação A/B

Quando `ab_experiments` está habilitado:

```yaml
experiments:
  - name: "gate_notifications"
    description: "Testar notificações de gate"
    variants:
      - name: "control"
        weight: 50
        config: {}
      - name: "treatment"
        weight: 50
        config:
          verbose_notifications: true
    metrics:
      - "time_to_complete_phase"
      - "user_satisfaction"
```

## API para Scripts

```python
from sdlc_flags import is_enabled

if is_enabled("github_projects"):
    # Executar integração
    pass
```

## Relacionado

- `/sdlc-version` - Gerenciar versão
- `/sdlc-config` - Configuração geral
