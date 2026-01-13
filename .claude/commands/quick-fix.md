---
description: "Inicia fluxo rapido para bug fix ou correcao simples (Level 0)"
argument-hint: "[descricao do bug]"
---

# Quick Fix Flow (Level 0)

Fluxo otimizado para correcoes rapidas sem overhead de SDLC completo.

## Criterios de Elegibilidade

Este fluxo e apropriado quando:

- Bug simples com causa conhecida
- Alteracao em ate 3 arquivos
- Sem mudanca de API/contrato
- Sem impacto em seguranca
- Sem necessidade de revisao de arquitetura

## Descricao do Bug

$ARGUMENTS

## Fluxo de Execucao

### 1. Criar Branch

Automaticamente cria branch seguindo padrao:

```bash
.claude/hooks/auto-branch.sh fix "{descricao-normalizada}"
```

Branch criada: `fix/{descricao-normalizada}`

### 2. Analisar Bug

Use @code-author para:

1. Identificar arquivo(s) afetado(s)
2. Entender causa raiz
3. Propor correcao minima

### 3. Implementar Correcao

Use @code-author para:

1. Implementar fix
2. Criar/atualizar teste unitario que cobre o bug
3. Garantir que testes existentes continuam passando

### 4. Revisar

Use @code-reviewer para quick review:

- [ ] Fix endereca o problema reportado
- [ ] Nao introduz regressoes
- [ ] Teste cobre o cenario do bug
- [ ] Codigo segue padroes do projeto

### 5. Validar

Executar validacoes:

```bash
# Build
dotnet build  # ou comando equivalente

# Testes
dotnet test   # ou comando equivalente
```

### 6. Finalizar

1. Criar PR para main
2. Aguardar aprovacao humana
3. Merge apos CI passar

## Output Esperado

```yaml
quick_fix_result:
  branch: "fix/{descricao}"
  description: "{descricao do bug}"
  root_cause: "{causa identificada}"
  files_changed:
    - path: "{arquivo}"
      change: "{descricao da mudanca}"
  tests_added:
    - path: "{arquivo de teste}"
      coverage: "{cenario coberto}"
  build_status: pass | fail
  test_status: pass | fail
  pr_url: "{url do PR}"
```

## Gatilhos de Escalacao

Se durante o fix for identificado:

| Situacao | Acao |
|----------|------|
| Problema mais profundo | Escalar para Level 1 (/new-feature) |
| Impacto em seguranca | Escalar para @security-scanner |
| Mudanca de API | Escalar para @system-architect |
| Mais de 3 arquivos | Considerar Level 1 |
| Mudanca de DB | Escalar para @data-architect |

## Convencao de Commit

```
fix: {descricao curta}

{descricao mais detalhada se necessario}

Closes #{issue-number}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Exemplo de Uso

```
/quick-fix "Timeout na conexao com a API da registradora CERC"
```

Resultado:
- Branch: `fix/timeout-conexao-api-registradora-cerc`
- Analise: Timeout de 30s muito baixo para operacoes de lote
- Fix: Aumentar timeout para 120s e adicionar retry
- Teste: Adicionar teste de timeout no RegistradoraClientTests
- PR: #123

## Checklist Rapido

- [ ] Entendi o problema
- [ ] Identifiquei a causa raiz
- [ ] Implementei fix minimo
- [ ] Adicionei teste
- [ ] Build passa
- [ ] Testes passam
- [ ] Nao ha regressoes
