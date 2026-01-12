# Slash Commands: Guia Completo

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs/en/slash-commands

---

## 📋 Índice

1. [O Que São?](#o-que-são)
2. [Criando Comandos](#criando-comandos)
3. [Argumentos e Placeholders](#argumentos-e-placeholders)
4. [Frontmatter (Metadados)](#frontmatter-metadados)
5. [Hooks em Commands](#hooks-em-commands)
6. [Bash em Comandos](#bash-em-comandos)
7. [Referenciando Arquivos](#referenciando-arquivos)
8. [Organizando Comandos](#organizando-comandos)
9. [SlashCommand Tool](#slashcommand-tool)
10. [Exemplos Práticos](#exemplos-práticos)
11. [Troubleshooting](#troubleshooting)

---

## O Que São?

Slash commands são **atalhos para prompts frequentes** armazenados como arquivos Markdown que Claude Code executa quando invocados.

**Características:**

- ✅ Ativação **manual** pelo usuário: `/comando`
- ✅ Um arquivo `.md` = um comando
- ✅ Suportam argumentos dinâmicos
- ✅ Podem executar bash e referenciar arquivos
- ✅ Claude pode invocar automaticamente via SlashCommand tool

**Quando usar:**

- Prompts que você repete frequentemente
- Workflows simples que precisam de argumentos
- Atalhos para operações comuns

---

## Criando Comandos

### Estrutura de Armazenamento

```bash
# Comandos de projeto (compartilhados via Git)
.claude/commands/
├── optimize.md              # /optimize
├── review-pr.md             # /review-pr
└── frontend/
    └── component.md         # /component (namespace: frontend)

# Comandos pessoais (apenas você)
~/.claude/commands/
├── my-workflow.md           # /my-workflow
└── personal-scripts.md      # /personal-scripts
```

**Precedência**: Projeto > Pessoal

### Comando Básico

```markdown
---
description: "Analyze code for performance issues"
---

Analyze this code for performance issues and suggest optimizations.
```

**Salvar como**: `.claude/commands/optimize.md`

**Uso**: `/optimize`

### Comando com Argumentos

```markdown
---
description: "Optimize specific file"
argument-hint: "[file-path]"
---

Analyze this code for performance issues and suggest optimizations:

@$1
```

**Uso**: `/optimize src/main.py`

---

## Argumentos e Placeholders

| Placeholder | Descrição | Exemplo |
|-------------|-----------|---------|
| `$ARGUMENTS` | Todos os argumentos passados | `/cmd a b c` → `a b c` |
| `$1`, `$2`, `$3`, ... | Argumentos posicionais | `$1` = primeiro arg |
| `@file` | Incluir conteúdo de arquivo | `@src/utils/helpers.js` |

### Exemplo Completo

```markdown
---
description: "Review PR with priority and assignee"
argument-hint: "[pr-number] [priority] [assignee]"
allowed-tools: Bash(gh pr view:*)
---

Review PR #$1 with priority $2 and assign to $3.

First, fetch PR details:
!gh pr view $1 --json title,body,files

Then analyze the changes and provide feedback.
```

**Uso**: `/review-pr 456 high alice`

**Substituição**:

- `$1` → `456`
- `$2` → `high`
- `$3` → `alice`
- `$ARGUMENTS` → `456 high alice`

---

## Frontmatter (Metadados)

```yaml
---
description: "Brief command overview"              # Recomendado (para SlashCommand tool)
argument-hint: "[expected arguments]"              # Mostrado no autocomplete
allowed-tools: Bash(...), Read, Write              # Ferramentas permitidas
model: opus                                        # Modelo específico
disable-model-invocation: true                     # Impede SlashCommand tool
hooks:                                             # Hooks para eventos
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "echo 'Editing...'"
---
```

### Tabela de Campos

| Campo | Obrigatório | Padrão | Descrição |
|-------|-------------|--------|-----------|
| `description` | Recomendado | - | Descrição para SlashCommand tool e `/help` |
| `argument-hint` | ❌ | - | Hint mostrado no autocomplete |
| `allowed-tools` | ❌ | Herda | Ferramentas permitidas |
| `model` | ❌ | Herda | Modelo: `haiku`, `sonnet`, `opus` |
| `disable-model-invocation` | ❌ | `false` | Impede invocação automática |
| `hooks` | ❌ | Nenhum | Hooks para eventos |

### Campos Detalhados

**`description`** (recomendado):

- Breve descrição do comando
- **Obrigatório** para SlashCommand tool invocar automaticamente
- Aparece no `/help`

**`argument-hint`** (opcional):

- Mostrado durante autocomplete
- Exemplo: `"[pr-number] [priority] [assignee]"`

**`allowed-tools`** (opcional):

- Restringe ferramentas disponíveis
- **Obrigatório** para usar bash: `allowed-tools: Bash(...)`
- Se omitido, herda ferramentas da conversa

**`model`** (opcional):

- Especifica modelo: `haiku`, `sonnet`, `opus`
- Sobrescreve modelo da conversa

**`disable-model-invocation`** (opcional):

- `true`: Impede SlashCommand tool de invocar
- `false` (padrão): Claude pode invocar automaticamente

**`hooks`** (opcional):

- Define hooks que executam durante o comando
- Ver [Hooks em Commands](#hooks-em-commands)

---

## Hooks em Commands

Slash commands podem definir hooks que executam em resposta a eventos durante sua execução.

### Estrutura

```yaml
---
description: "Command with hooks"
hooks:
  PreToolUse:
    - matcher: "Edit(*.py)"
      hooks:
        - type: command
          command: "python -m py_compile \"$TOOL_INPUT_FILE_PATH\""
  PostToolUse:
    - matcher: "Write(*.ts)"
      hooks:
        - type: command
          command: "npx prettier --write \"$TOOL_INPUT_FILE_PATH\""
---
```

### Eventos Disponíveis

| Evento | Quando Dispara | Variáveis |
|--------|----------------|-----------|
| `PreToolUse` | Antes de usar ferramenta | `$TOOL_NAME`, `$TOOL_INPUT_*` |
| `PostToolUse` | Após usar ferramenta | `$TOOL_NAME`, `$TOOL_INPUT_*`, `$TOOL_OUTPUT` |
| `Stop` | Quando comando termina | `$STOP_REASON` |

### Exemplo: Auto-Format

```yaml
---
description: "Develop Python with auto-formatting"
argument-hint: "[file-path]"
hooks:
  PostToolUse:
    - matcher: "Edit(*.py),Write(*.py)"
      hooks:
        - type: command
          command: "black \"$TOOL_INPUT_FILE_PATH\""
---

Implement feature in:
@$1
```

### Exemplo: Validação

```yaml
---
description: "Edit Terraform with validation"
argument-hint: "[file-path]"
hooks:
  PostToolUse:
    - matcher: "Edit(*.tf)"
      hooks:
        - type: command
          command: "terraform validate"
---

Update Terraform configuration:
@$1
```

---

## Bash em Comandos

### Habilitando Bash

**Passo 1**: Adicionar `allowed-tools` no frontmatter:

```yaml
---
allowed-tools: Bash(git log:*, git diff:*)
---
```

**Passo 2**: Prefixar linha com `!`:

```markdown
Analyze recent changes:

!git log --oneline -10
!git diff HEAD~5..HEAD

Based on these changes, suggest improvements.
```

### Padrões de Bash

| Padrão | Descrição | Exemplo |
|--------|-----------|---------|
| `Bash(*)` | Permite qualquer comando bash | Sem restrição |
| `Bash(git *)` | Apenas comandos git | `git log`, `git diff` |
| `Bash(npm:*, yarn:*)` | npm ou yarn | `npm install`, `yarn add` |
| `Bash(python:*)` | Apenas python | `python script.py` |

### Exemplo Completo

```markdown
---
description: "Git changelog generator"
argument-hint: "[from-tag] [to-tag]"
allowed-tools: Bash(git log:*, git tag:*)
---

Generate changelog from $1 to $2:

!git log $1..$2 --oneline --no-merges

Group commits by type (feat, fix, refactor, etc.) and format as Markdown.
```

**Uso**: `/changelog v1.0.0 v1.1.0`

---

## Referenciando Arquivos

Use `@` prefix para incluir conteúdo de arquivo:

```markdown
---
description: "Review code with context"
---

Review this code:

@$1

Compare with our style guide:

@.docs/STYLE_GUIDE.md

Provide feedback on deviations.
```

**Uso**: `/review src/api.py`

**Claude receberá**:

- Conteúdo de `src/api.py`
- Conteúdo de `.docs/STYLE_GUIDE.md`

---

## Organizando Comandos

### Namespacing via Diretórios

```bash
.claude/commands/
├── frontend/
│   ├── component.md    # /component (namespace: frontend)
│   ├── optimize.md     # /optimize (namespace: frontend)
│   └── test.md         # /test (namespace: frontend)
├── backend/
│   ├── api.md          # /api (namespace: backend)
│   └── database.md     # /database (namespace: backend)
└── global/
    └── commit.md       # /commit (namespace: global)
```

**No help (`/help`)**:

- `/component` aparece como `(project:frontend)`
- `/api` aparece como `(project:backend)`
- `/commit` aparece como `(project:global)`

**Nota**: Subdiretórios **NÃO** afetam o nome do comando, apenas o namespace exibido.

### Nomes Conflitantes

Se existir:

- `.claude/commands/optimize.md`
- `.claude/commands/frontend/optimize.md`

Ambos são `/optimize`, mas:

- Primeiro não tem namespace
- Segundo tem namespace `(project:frontend)`

**Recomendação**: Evitar nomes duplicados; use nomes únicos.

---

## SlashCommand Tool

Claude pode invocar slash commands **automaticamente** durante conversas via `SlashCommand` tool.

### Requisitos

✅ Comando deve ter `description` no frontmatter
✅ Comando deve ser definido pelo usuário (não built-in)
✅ SlashCommand tool deve estar disponível (padrão)

### Controlando Acesso

**Via permissões**:

```
/permissions
```

Configure se Claude pode usar SlashCommand tool.

**Via comando específico**:

```yaml
---
disable-model-invocation: true
---
```

Impede este comando específico de ser invocado por Claude.

### Exemplo de Invocação Automática

**Comando**: `.claude/commands/review-pr.md`

```markdown
---
description: "Review GitHub PR with details"
argument-hint: "[pr-number]"
allowed-tools: Bash(gh pr view:*)
---

Review PR #$1:

!gh pr view $1 --json title,body,files

Analyze changes and provide feedback.
```

**Conversa**:

```
user: "Preciso revisar a PR 456"
assistant: [Invoca SlashCommand tool com /review-pr 456]
```

Claude detecta:

- Palavra-chave "revisar"
- "PR 456"
- Match com description do comando
- Invoca automaticamente

---

## Exemplos Práticos

### 1. Otimizador de Código

```markdown
---
description: "Analyze code for performance and suggest optimizations"
argument-hint: "[file-path]"
---

Analyze this code for performance issues:

@$1

Focus on:
- Algorithm complexity
- Memory usage
- I/O operations
- Caching opportunities

Provide specific optimization suggestions with code examples.
```

**Arquivo**: `.claude/commands/optimize.md`
**Uso**: `/optimize src/processor.py`

### 2. Revisor de PR

```markdown
---
description: "Review GitHub PR with priority and assignee"
argument-hint: "[pr-number] [priority] [assignee]"
allowed-tools: Bash(gh pr view:*, gh pr review:*)
---

Review PR #$1 with priority $2 and assign to $3.

Fetch PR details:
!gh pr view $1 --json title,body,files,commits

Analyze:
1. Code quality and best practices
2. Test coverage
3. Breaking changes
4. Security issues

Priority level: $2
Assignee: @$3
```

**Arquivo**: `.claude/commands/review-pr.md`
**Uso**: `/review-pr 456 high alice`

### 3. Gerador de Changelog

```markdown
---
description: "Generate changelog between Git tags"
argument-hint: "[from-tag] [to-tag]"
allowed-tools: Bash(git log:*, git tag:*)
---

Generate changelog from $1 to $2:

!git log $1..$2 --oneline --no-merges --pretty=format:"%s"

Group commits by type:
- feat: New features
- fix: Bug fixes
- refactor: Refactoring
- docs: Documentation
- test: Tests
- chore: Maintenance

Format as Markdown with examples.
```

**Arquivo**: `.claude/commands/changelog.md`
**Uso**: `/changelog v1.0.0 v1.1.0`

### 4. Documentador de Componente

```markdown
---
description: "Generate documentation for code component"
argument-hint: "[file-path]"
---

Generate comprehensive documentation for:

@$1

Include:
- Purpose and responsibility
- Public API
- Usage examples
- Edge cases
- Dependencies

Format as Markdown suitable for docs/ directory.
```

**Arquivo**: `.claude/commands/document.md`
**Uso**: `/document src/components/UserAuth.tsx`

### 5. Test Generator

```markdown
---
description: "Generate unit tests for code file"
argument-hint: "[file-path]"
---

Generate comprehensive unit tests for:

@$1

Include:
- Happy path scenarios
- Edge cases
- Error handling
- Mocking external dependencies

Use the same testing framework already in use in the project.
```

**Arquivo**: `.claude/commands/test.md`
**Uso**: `/test src/services/api.py`

---

## Troubleshooting

### Comando não aparece

**Problema**: Comando não está no `/help`

**Soluções**:

- ✅ Verificar arquivo em `.claude/commands/` ou `~/.claude/commands/`
- ✅ Verificar nome do arquivo (sem espaços)
- ✅ Verificar extensão `.md`
- ✅ Reiniciar Claude Code se necessário

### Argumentos não funcionam

**Problema**: `$1` não substitui

**Soluções**:

- ✅ Verificar sintaxe: `$1`, `$2`, `$ARGUMENTS`
- ✅ Fornecer argumentos ao invocar: `/cmd arg1 arg2`
- ✅ Usar `argument-hint` no frontmatter

### Bash não executa

**Problema**: Linha com `!` não executa

**Soluções**:

- ✅ Adicionar `allowed-tools: Bash(...)` no frontmatter
- ✅ Verificar padrão de permissão: `Bash(git *)` permite apenas git
- ✅ Quote caminhos com espaços: `!python "$1"`

**Exemplo correto**:

```markdown
---
allowed-tools: Bash(git log:*, git diff:*)
---

!git log --oneline -10
```

### Arquivo referenciado não encontrado

**Problema**: `@file` não inclui conteúdo

**Soluções**:

- ✅ Verificar caminho relativo ao projeto root
- ✅ Usar caminhos absolutos quando necessário
- ✅ Verificar se arquivo existe

**Exemplo**:

```markdown
@.docs/GUIDE.md          # ✅ Relativo ao projeto
@/absolute/path/file.md  # ✅ Absoluto
@../file.md              # ⚠️ Evitar (..)
```

### SlashCommand tool não invoca

**Problema**: Claude não invoca automaticamente

**Soluções**:

- ✅ Adicionar `description` no frontmatter
- ✅ Verificar se não tem `disable-model-invocation: true`
- ✅ Verificar permissões: `/permissions`
- ✅ Description deve ter termos-chave relevantes

**Exemplo**:

```yaml
---
# ❌ Sem description - não será invocado
---

# ✅ Com description - pode ser invocado
description: "Review GitHub PR with details"
---
```

### Timeout em bash commands

**Problema**: Comando bash demora muito

**Soluções**:

- ✅ Otimizar comando bash
- ✅ Limitar output: `git log -10` não `git log`
- ✅ Usar flags de performance
- ✅ Considerar mover para skill (com timeout configurável)

---

## Best Practices

### ✅ DO

- **Keep it simple**: Um comando = uma responsabilidade
- **Use argument-hint**: Ajuda usuários a saber o que passar
- **Validate inputs**: Verificar se argumentos foram passados
- **Quote variables**: `"$1"` não `$1` (previne erros com espaços)
- **Provide description**: Permite SlashCommand tool invocar
- **Document examples**: Comentários ajudam usuários
- **Use namespaces**: Organize comandos em diretórios

### ❌ DON'T

- **Hardcode values**: Use argumentos dinâmicos
- **Make it complex**: Comandos > 50 linhas → considerar skill
- **Forget allowed-tools**: Bash precisa de permissão explícita
- **Use absolute paths**: Prefira caminhos relativos
- **Duplicate names**: Evite conflitos entre comandos

---

## Recursos

**Documentação Oficial**:

- [Claude Code: Slash Commands](https://code.claude.com/docs/en/slash-commands)

**Guides**:

- [Quick Reference](../quick-reference.md) - Comparação com Skills e Agents
- [Best Practices](../best-practices.md) - Práticas gerais

**Exemplos no Repositório**:

- `.claude/commands/` - Comandos do projeto

---

**Última Revisão**: 2026-01-11 por Claude Code
