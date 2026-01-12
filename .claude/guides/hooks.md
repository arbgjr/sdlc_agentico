# Hooks: Guia Completo

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs/en/hooks

---

## 📋 Índice

1. [O Que São?](#o-que-são)
2. [Eventos Disponíveis](#eventos-disponíveis)
3. [Tipos de Hooks](#tipos-de-hooks)
4. [Configuração](#configuração)
5. [Matchers](#matchers)
6. [Input/Output](#inputoutput)
7. [Variáveis de Ambiente](#variáveis-de-ambiente)
8. [Plugin Hooks](#plugin-hooks)
9. [Segurança](#segurança)
10. [Exemplos Práticos](#exemplos-práticos)
11. [Debugging](#debugging)
12. [Troubleshooting](#troubleshooting)

---

## O Que São?

Hooks são **comandos shell customizáveis** que executam em pontos específicos do ciclo de vida do Claude Code. Diferente de LLM, hooks garantem **comportamento determinístico**.

**Princípio**: "Hooks provide deterministic control over Claude Code's behavior, ensuring certain actions always happen."

**Características:**

- ✅ Execução **automática** em eventos específicos
- ✅ Comportamento **determinístico** (não depende de LLM)
- ✅ Command hooks (bash scripts) ou Prompt hooks (LLM decisions)
- ✅ Podem bloquear, modificar, ou permitir ações

**Quando usar:**

- Ação deve **sempre** acontecer em determinado evento
- Formatação automática após editar código
- Validação de entrada antes de processar
- Logging de comandos executados
- Notificações customizadas

---

## Eventos Disponíveis

| Evento | Trigger | Propósito Comum |
|--------|---------|-----------------|
| **PreToolUse** | Antes de executar ferramenta | Validação, bloqueio, modificação de parâmetros |
| **PostToolUse** | Após ferramenta completar | Formatação, linting, logging |
| **UserPromptSubmit** | User submete prompt | Validação de entrada, injeção de contexto |
| **Notification** | Claude envia notificação | Roteamento customizado de alertas |
| **Stop** | Claude completa resposta | Continuar ou finalizar conversa |
| **SubagentStop** | Subagent finaliza | Avaliar qualidade do resultado |
| **PreCompact** | Antes de compactar contexto | Monitoramento de compactação |
| **SessionStart** | Sessão inicia/retoma | Carregar contexto, issues, TODOs |
| **SessionEnd** | Sessão termina | Cleanup, logging |

### Eventos Detalhados

**PreToolUse**:

- Executa **antes** de ferramenta rodar
- Pode **bloquear**, **modificar**, ou **permitir**
- Suporta matchers para filtrar ferramentas
- Use para: validação, segurança, modificação de input

**PostToolUse**:

- Executa **após** ferramenta completar com sucesso
- Pode **bloquear** com feedback para Claude
- Suporta matchers para filtrar ferramentas
- Use para: formatação, linting, logging

**UserPromptSubmit**:

- Executa quando user submete prompt
- Pode **bloquear** ou **adicionar contexto**
- Não usa matchers (aplica a todos prompts)
- Use para: validação de input, injeção de contexto

**Stop**:

- Executa quando Claude completa resposta
- Pode **forçar continuação** se tarefa incompleta
- Suporta prompt hooks (LLM decision)
- Use para: validação de completude

**SubagentStop**:

- Executa quando subagent finaliza tarefa
- Pode **forçar continuação** se resultado inadequado
- Suporta prompt hooks (LLM decision)
- Use para: validação de qualidade

**SessionStart**:

- Executa ao iniciar ou retomar sessão
- Pode carregar contexto via stdout
- Acesso a `CLAUDE_ENV_FILE` para persistir env vars
- Use para: carregar TODOs, issues, contexto

**SessionEnd**:

- Executa quando sessão termina
- Use para: cleanup, logging, backup

**Notification**:

- Executa quando Claude envia notificação
- Use para: roteamento customizado de alertas

**PreCompact**:

- Executa antes de compactar contexto
- Use para: monitorar compactação

---

## Tipos de Hooks

### Command Hooks (`type: "command"`)

Executam **bash scripts** com acesso completo ao filesystem.

**Características**:

- ✅ Determinísticos (sempre mesmo resultado)
- ✅ Rápidos (sem LLM)
- ✅ Acesso completo ao sistema
- ✅ Ideal para regras fixas

**Exemplo**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "black \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

**Quando usar**:

- Formatação automática
- Validação de arquivos
- Logging
- Operações de filesystem

### Prompt-Based Hooks (`type: "prompt"`)

Enviam contexto para **LLM (Claude Haiku)** para decisões inteligentes.

**Características**:

- ✅ Decisões inteligentes baseadas em contexto
- ✅ Análise de conversas
- ✅ Apenas para `Stop` e `SubagentStop`
- ⚠️ Mais lento (requer LLM)

**Exemplo**:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the conversation. Are all tasks complete? If not, return {\"decision\": \"block\", \"reason\": \"Specific incomplete task\"}\n\n$ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

**Response schema**:

```json
{
  "decision": "approve" | "block",
  "reason": "explanation",
  "continue": false,
  "stopReason": "message",
  "systemMessage": "context"
}
```

**Quando usar**:

- Validar completude de tarefas
- Avaliar qualidade de resultado
- Decisões que requerem contexto

---

## Configuração

### Localização

**Projeto**: `.claude/settings.json`
**Pessoal**: `~/.claude/settings.json`
**Enterprise**: Configuração centralizada

### Estrutura Básica

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "bash-command",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

### Exemplo Completo

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "black \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 10000
          },
          {
            "type": "command",
            "command": "pylint \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 15000
          }
        ]
      },
      {
        "matcher": "Edit(*.ts)",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 10000
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/.docs/CONTEXT.md\""
          }
        ]
      }
    ]
  }
}
```

---

## Matchers

Matchers aplicam-se a **PreToolUse** e **PostToolUse**.

### Sintaxe

| Matcher | Descrição | Exemplo |
|---------|-----------|---------|
| `"*"` | Wildcard (todas ferramentas) | Qualquer ferramenta |
| `"Edit"` | Exato | Apenas ferramenta `Edit` |
| `"Edit(*)"` | Com argumentos | `Edit` com qualquer arquivo |
| `"Edit(*.ts)"` | Wildcard em argumentos | `Edit` de arquivos TypeScript |
| `"Edit(*.{ts,tsx})"` | Múltiplas extensões | TypeScript ou TSX |
| `"Bash(git *)"` | Regex em argumentos | `Bash` com comandos git |
| `"Write(/path/to/*)"` | Path pattern | Write em diretório específico |

### Exemplos de Matchers

**Todas as edições**:

```json
{
  "matcher": "Edit(*)"
}
```

**Apenas Python**:

```json
{
  "matcher": "Edit(*.py)"
}
```

**TypeScript e TSX**:

```json
{
  "matcher": "Edit(*.{ts,tsx})"
}
```

**Comandos Git via Bash**:

```json
{
  "matcher": "Bash(git *)"
}
```

**Edições em src/**:

```json
{
  "matcher": "Edit(src/**)"
}
```

**⚠️ Case-Sensitive**: `Edit` ≠ `edit`

---

## Input/Output

### Input (via stdin)

Todos hooks recebem **JSON** via stdin:

```json
{
  "session_id": "uuid",
  "transcript_path": "/path/to/conversation.jsonl",
  "cwd": "/working/directory",
  "permission_mode": "auto",
  "hook_event_name": "PreToolUse",
  // Campos específicos do evento
  "tool_name": "Edit",
  "tool_input": {"file_path": "/path/to/file.py", ...},
  "tool_response": {...}
}
```

### Output (via stdout)

**JSON** para controlar comportamento:

#### PreToolUse Decisions

```json
{
  "decision": "allow",          // "allow" | "deny" | "ask"
  "updatedInput": {...}         // Opcional: modificar parâmetros
}
```

**Decisões**:

- `"allow"`: Permite execução, bypass permissões
- `"deny"`: Bloqueia execução
- `"ask"`: Solicita confirmação do usuário
- `"updatedInput"`: Modifica parâmetros antes de executar

#### PostToolUse Decisions

```json
{
  "decision": "block",
  "reason": "Code doesn't pass linting"
}
```

**Decisões**:

- `"block"`: Bloqueia e envia reason para Claude
- `undefined`: Permite (sem JSON output)

#### UserPromptSubmit

**Texto em stdout**: Adiciona automaticamente ao contexto

**JSON para bloquear**:

```json
{
  "decision": "block",
  "reason": "Prompt contains prohibited content"
}
```

#### Stop/SubagentStop

```json
{
  "decision": "block",
  "reason": "Tasks incomplete: need to implement tests"
}
```

**Decisões**:

- `"block"`: Força Claude a continuar
- `undefined`: Permite parar

### Exit Codes

| Code | Significado | Comportamento |
|------|-------------|---------------|
| `0` | Sucesso | Processar JSON stdout |
| `2` | Erro bloqueante | Stderr vira feedback, JSON ignorado |
| Outros | Erro não-bloqueante | Stderr apenas no verbose mode |

---

## Variáveis de Ambiente

| Variável | Disponível em | Descrição |
|----------|---------------|-----------|
| `$CLAUDE_PROJECT_DIR` | Todos | Diretório raiz do projeto |
| `$CLAUDE_CODE_REMOTE` | Todos | `true` se sessão remota |
| `$CLAUDE_ENV_FILE` | SessionStart | Arquivo para persistir env vars |
| `$ARGUMENTS` | Prompt hooks | JSON do evento (placeholder) |
| `$TOOL_INPUT_FILE_PATH` | PostToolUse | Arquivo modificado |
| `$TOOL_NAME` | Pre/PostToolUse | Nome da ferramenta |

### Uso

```bash
# Projeto root
cd "$CLAUDE_PROJECT_DIR"

# Arquivo modificado
black "$TOOL_INPUT_FILE_PATH"

# Persistir env var (SessionStart only)
echo "MY_VAR=value" >> "$CLAUDE_ENV_FILE"

# Prompt hook (JSON via $ARGUMENTS)
prompt: "Analyze this:\n\n$ARGUMENTS"
```

---

## Plugin Hooks

Plugins podem fornecer hooks via `hooks/hooks.json`.

**Estrutura**:

```
my-plugin/
├── hooks/
│   └── hooks.json
└── scripts/
    └── lint.sh
```

**hooks/hooks.json**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit(*)",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh \"$TOOL_INPUT_FILE_PATH\""
          }
        ]
      }
    ]
  }
}
```

**Variável `${CLAUDE_PLUGIN_ROOT}`**: Diretório do plugin

**Merge automático**: Plugin hooks mesclam com configurações do usuário.

---

## Segurança

### ⚠️ AVISO CRÍTICO

**"Claude Code hooks execute arbitrary shell commands on your system automatically."**

**Usuário é 100% responsável** pela segurança dos hooks.

### Best Practices

**1. Validar entradas**:

```bash
#!/bin/bash
set -euo pipefail

# Validar path
if [[ "$TOOL_INPUT_FILE_PATH" =~ \.\. ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi
```

**2. Quote variáveis**:

```bash
# ✅ CORRETO
python scripts/validate.py "$TOOL_INPUT_FILE_PATH"

# ❌ INCORRETO (vulnerável a injection)
python scripts/validate.py $TOOL_INPUT_FILE_PATH
```

**3. Sanitizar paths**:

```bash
# Checar path traversal
if [[ "$FILE" =~ \.\. ]]; then
  exit 2
fi

# Usar caminhos absolutos
FULL_PATH=$(realpath "$FILE")
```

**4. Evitar arquivos sensíveis**:

```bash
# Bloquear arquivos sensíveis
if [[ "$FILE" == *".env"* ]] || [[ "$FILE" == *"secrets"* ]]; then
  echo '{"decision": "deny", "reason": "Sensitive file"}' >&2
  exit 2
fi
```

**5. Limitar operações**:

```bash
# Apenas arquivos dentro do projeto
if [[ "$FULL_PATH" != "$CLAUDE_PROJECT_DIR"* ]]; then
  echo '{"decision": "deny", "reason": "Outside project"}' >&2
  exit 2
fi
```

### Security Checklist

```markdown
- [ ] Validar todas as entradas
- [ ] Quote variáveis: "$VAR" não $VAR
- [ ] Checar path traversal (..)
- [ ] Usar caminhos absolutos quando possível
- [ ] Evitar arquivos sensíveis (.env, secrets)
- [ ] Limitar escopo de operações
- [ ] Testar exaustivamente antes de produção
- [ ] Revisar código de hooks de terceiros
```

---

## Exemplos Práticos

### 1. Auto-formatação após edição

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "black \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 10000
          }
        ]
      },
      {
        "matcher": "Edit(*.{ts,tsx,js,jsx})",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

### 2. Prevenir modificação de arquivos de produção

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit(*prod*)",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"decision\": \"deny\", \"reason\": \"Cannot modify production files. Create a copy first.\"}'"
          }
        ]
      },
      {
        "matcher": "Edit(*.env)",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"decision\": \"ask\", \"reason\": \"Modifying .env file. Confirm?\"}'"
          }
        ]
      }
    ]
  }
}
```

### 3. Carregar contexto ao iniciar sessão

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/.docs/CONTEXT.md\" \"$CLAUDE_PROJECT_DIR/.docs/RULES.md\""
          }
        ]
      }
    ]
  }
}
```

### 4. Validar commit messages

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/scripts/validate-commit.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

**validate-commit.sh**:

```bash
#!/bin/bash
set -euo pipefail

# Extrair mensagem de commit do input JSON
MESSAGE=$(echo "$TOOL_INPUT" | jq -r '.command' | grep -oP '(?<=-m ").*?(?=")')

# Validar conventional commit
if ! echo "$MESSAGE" | grep -qE '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'; then
  echo '{
    "decision": "deny",
    "reason": "Commit message must follow Conventional Commits format: type(scope): description"
  }'
  exit 2
fi

# Aprovar
echo '{"decision": "allow"}'
```

### 5. Continuar se tarefa incompleta (Prompt Hook)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Analyze the conversation and determine if all user-requested tasks are complete.\n\nIf any tasks are incomplete, return:\n{\n  \"decision\": \"block\",\n  \"reason\": \"Specific task that is incomplete\"\n}\n\nOtherwise, return:\n{\n  \"decision\": \"approve\"\n}\n\nConversation:\n$ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

### 6. Logging de comandos executados

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[$(date)] Tool: $TOOL_NAME\" >> \"$CLAUDE_PROJECT_DIR/.claude/command-log.txt\"",
            "timeout": 1000
          }
        ]
      }
    ]
  }
}
```

---

## Debugging

### Verificar hooks registrados

```
/hooks
```

Mostra todos os hooks configurados.

### Modo debug

```bash
claude --debug
```

Exibe:

- Hooks matched em cada evento
- Comandos executados
- Output de hooks (stdout/stderr)
- Exit codes
- Decisões tomadas

### Teste manual de hook

```bash
# Simular input JSON
echo '{
  "session_id": "test",
  "tool_name": "Edit",
  "tool_input": {"file_path": "/path/to/file.py"}
}' | bash .claude/scripts/my-hook.sh
```

### Problemas comuns

**Hook não executa**:

- ✅ Verificar `/hooks` (registrado?)
- ✅ Verificar matcher (case-sensitive)
- ✅ Verificar evento correto
- ✅ `claude --debug` para ver decisões

**Hook bloqueia incorretamente**:

- ✅ Verificar exit code (2 = bloqueante)
- ✅ Verificar JSON válido no stdout
- ✅ Verificar field `decision`
- ✅ Revisar lógica de validação

**Timeout**:

- ✅ Aumentar `timeout` field
- ✅ Otimizar script (evitar operações lentas)
- ✅ Verificar loops infinitos

**Variáveis não disponíveis**:

- ✅ Verificar qual evento fornece a variável
- ✅ `$TOOL_INPUT_FILE_PATH` apenas em PostToolUse
- ✅ `$CLAUDE_ENV_FILE` apenas em SessionStart

---

## Troubleshooting

### Hook não executa

**Soluções**:

- ✅ Verificar registro: `/hooks`
- ✅ Matcher case-sensitive: `Edit` ≠ `edit`
- ✅ Evento correto para o matcher
- ✅ Debugar: `claude --debug`
- ✅ Verificar sintaxe JSON

### Hook bloqueia quando não deveria

**Soluções**:

- ✅ Exit code 2 = bloqueante (trocar para 0)
- ✅ JSON com `"decision": "block"` (remover ou mudar)
- ✅ Stderr contém mensagem (limpar stderr se exit 0)
- ✅ Revisar lógica de validação

### Timeout

**Soluções**:

- ✅ Aumentar `timeout` (padrão: 60s, max: não especificado)
- ✅ Otimizar script (remover operações lentas)
- ✅ Evitar network calls se possível
- ✅ Cache results quando aplicável

### Segurança

**Soluções**:

- ✅ Revisar código antes de registrar
- ✅ Validar entradas (path traversal, injection)
- ✅ Quote variáveis: `"$VAR"`
- ✅ Sanitizar paths
- ✅ Limitar escopo de operações
- ✅ Testar com entradas maliciosas

### Variáveis não funcionam

**Soluções**:

- ✅ Verificar evento correto:
  - `$TOOL_INPUT_FILE_PATH`: PostToolUse
  - `$CLAUDE_ENV_FILE`: SessionStart
  - `$ARGUMENTS`: Prompt hooks
- ✅ Quote variáveis: `"$VAR"`
- ✅ Verificar se variável está definida: `${VAR:-default}`

---

## Best Practices

### ✅ DO

- **Security first**: Validar todas as entradas
- **Quote variables**: `"$VAR"` sempre
- **Set timeout**: Prevenir hang
- **Test thoroughly**: Testar antes de produção
- **Use exit codes correctly**: 0=success, 2=block
- **Provide clear errors**: Stderr com mensagens acionáveis
- **Keep it simple**: Hooks devem ser rápidos
- **Log appropriately**: Útil para debugging

### ❌ DON'T

- **Assume inputs safe**: Sempre validar
- **Skip quoting**: Vulnerável a injection
- **Hardcode paths**: Use `$CLAUDE_PROJECT_DIR`
- **Ignore exit codes**: Controla comportamento
- **Make it complex**: Hooks devem ser simples e rápidos
- **Trust third-party hooks**: Revisar código sempre
- **Forget timeout**: Previne hang

---

## Recursos

**Documentação Oficial**:

- [Claude Code: Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code: Hooks Reference](https://code.claude.com/docs/en/hooks)

**Guides**:

- [Quick Reference](../quick-reference.md) - Visão geral
- [Best Practices](../best-practices.md) - Práticas gerais

**Configuração**:

- `.claude/settings.json` - Hooks do projeto

---

**Última Revisão**: 2026-01-11 por Claude Code
