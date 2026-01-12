---
name: release-prep
description: |
  Prepara um novo release para producao.
  Valida gates, gera notas, cria tag.

  Examples:
  - <example>
    user: "/release-prep v1.2.0"
    assistant: "Vou preparar o release v1.2.0"
    </example>
---

# Preparar Release

## Instrucoes

Voce deve preparar um novo release validando todos os criterios.

## Processo

1. **Validar Versao**: Verificar formato SemVer
2. **Verificar Gates**: Rodar gate-check para phase-6-to-7
3. **Gerar Changelog**: Compilar mudancas desde ultimo release
4. **Criar Release Notes**: Documentar features, fixes, breaking changes
5. **Preparar Rollback Plan**: Documentar como reverter
6. **Criar Tag**: Gerar tag de versao
7. **Notificar**: Comunicar preparacao aos stakeholders

## Checklist Pre-Release

```yaml
pre_release_checklist:
  code:
    - [ ] Testes passando
    - [ ] Code review aprovado
    - [ ] Cobertura >= 80%

  security:
    - [ ] Security scan passando
    - [ ] Zero vulnerabilidades criticas

  documentation:
    - [ ] Release notes escritas
    - [ ] CHANGELOG atualizado

  operations:
    - [ ] Rollback plan documentado
    - [ ] Runbook atualizado
```

## Template de Release Notes

```markdown
# Release Notes - v1.2.0

**Release Date:** 2026-01-11

## Highlights
- Nova feature X
- Melhoria em Y

## New Features
- Feature A
- Feature B

## Improvements
- Melhoria 1
- Melhoria 2

## Bug Fixes
- Fix para issue #123

## Security
- Atualizado pacote X

## Breaking Changes
- Nenhum

## Upgrade Instructions
1. Passo 1
2. Passo 2
```

## Output

```yaml
release_preparation:
  version: "v1.2.0"
  status: "ready"

  checklist_passed:
    - "Tests: OK"
    - "Security: OK"
    - "Documentation: OK"

  artifacts:
    - "CHANGELOG.md atualizado"
    - "Release notes geradas"
    - "Tag v1.2.0 criada"

  next_steps:
    - "Deploy em staging"
    - "Validar stakeholders"
    - "Deploy em producao"
```

## Uso

```
/release-prep v1.2.0              # Preparar release
/release-prep v1.2.0 --dry-run    # Apenas validar, nao criar tag
/release-prep --changelog         # Apenas gerar changelog
```
