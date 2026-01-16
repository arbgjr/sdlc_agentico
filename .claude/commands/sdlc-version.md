---
name: sdlc-version
description: |
  Gerencia versionamento do SDLC Agêntico.
  Mostra versão atual, changelog, e permite rollback.
allowed-tools:
  - Read
  - Bash
user-invocable: true
version: "1.0.0"
---

# /sdlc-version

Gerencia versionamento semântico do SDLC Agêntico.

## Uso

```
/sdlc-version [subcommand]
```

## Subcomandos

| Comando | Descrição |
|---------|-----------|
| (sem args) | Mostra versão atual |
| `changelog` | Mostra changelog recente |
| `list` | Lista versões disponíveis |
| `info <version>` | Detalhes de uma versão |
| `rollback <version>` | Rollback para versão anterior |
| `upgrade` | Atualiza para última versão |

## Exemplos

### Ver versão atual
```
/sdlc-version
```
Output:
```
SDLC Agêntico v1.0.0
Build: 2026-01-16
```

### Ver changelog
```
/sdlc-version changelog
```

### Listar versões
```
/sdlc-version list
```

### Rollback
```
/sdlc-version rollback 0.9.0
```

## Versionamento Semântico

O SDLC segue SemVer:
- **MAJOR**: Mudanças incompatíveis no workflow
- **MINOR**: Novas features compatíveis
- **PATCH**: Bug fixes e melhorias

## Arquivo de Versão

A versão é definida em `.claude/VERSION`:

```yaml
version: "1.0.0"
build_date: "2026-01-16"
release_notes: "Integração completa com GitHub"
```

## Relacionado

- `/sdlc-flags` - Gerenciar feature flags
- `/sdlc-config` - Configuração do SDLC
