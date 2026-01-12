# Claude Code: Quick Reference

**Versão**: 2.0
**Última Atualização**: 2026-01-11
**Referência oficial**: https://code.claude.com/docs

---

## 🎯 Escolha Rápida

| Preciso de... | Use | Ativação | Guia Completo |
|---------------|-----|----------|---------------|
| Atalho para prompt frequente com argumentos | **Slash Command** | Manual: `/comando` | [slash-commands.md](guides/slash-commands.md) |
| Capacidade modular que Claude decide usar | **Skill** | Automática (Claude) | [skills.md](guides/skills.md) |
| Especialista focado em domínio específico | **Agent** | Automática ou `@agent` | [agents.md](guides/agents.md) |
| Automação determinística (sempre executar) | **Hook** | Automática (eventos) | [hooks.md](guides/hooks.md) |
| Modificar comportamento do Claude Code | **Output Style** | Manual: `/output-style` | [output-styles.md](guides/output-styles.md) |

---

## 📊 Comparação Detalhada

| Aspecto | Slash Commands | Skills | Agents |
|---------|----------------|--------|--------|
| **Ativação** | Manual (`/cmd args`) | Automática (Claude decide) | Automática ou `@agent-name` |
| **Estrutura** | 1 arquivo `.md` | Diretório (SKILL.md + recursos) | 1 arquivo `.md` |
| **Argumentos** | ✅ Sim (`$1`, `$ARGUMENTS`) | ❌ Não | ❌ Não |
| **Bash** | ✅ Sim (`!command`) | ✅ Sim (scripts/) | ✅ Sim (via allowed-tools) |
| **Progressive Disclosure** | ❌ Não | ✅ Sim (3 níveis) | ❌ Não |
| **Hooks** | ✅ Sim | ✅ Sim | ❌ Não |
| **Model** | ✅ Sim | ✅ Sim | ✅ Sim |
| **Context Fork** | ❌ Não | ✅ Sim | ❌ Não |
| **Skills Integration** | ❌ Não | ✅ Sim | ✅ Sim |
| **Complexidade** | Baixa | Média | Alta |
| **Casos de Uso** | Workflows simples, atalhos | Processos modulares, automação | Sub-agentes especializados |

---

## 🗂️ Estrutura de Arquivos

```
.claude/
├── quick-reference.md          # Este arquivo (índice rápido)
├── best-practices.md           # Práticas gerais
│
├── commands/                   # Slash commands
│   ├── optimize.md            # /optimize
│   ├── review-pr.md           # /review-pr
│   └── frontend/
│       └── component.md       # /component (namespace: frontend)
│
├── skills/                     # Skills
│   ├── pdf-processing/
│   │   ├── SKILL.md           # Obrigatório
│   │   ├── scripts/
│   │   └── templates/
│   └── api-testing/
│       └── SKILL.md
│
├── agents/                     # Agents
│   ├── backend-developer.md
│   ├── frontend-developer.md
│   └── code-reviewer.md
│
└── guides/                     # Documentação detalhada
    ├── slash-commands.md
    ├── skills.md
    ├── agents.md
    ├── hooks.md
    └── output-styles.md
```

---

## 🚀 Começando Rápido

### Criar um Slash Command

```bash
# 1. Criar arquivo
cat > .claude/commands/optimize.md << 'EOF'
---
description: "Analyze code for performance issues"
argument-hint: "[file-path]"
---

Analyze this code for performance issues and suggest optimizations:

@$1
EOF

# 2. Usar
# /optimize src/main.py
```

### Criar uma Skill

```bash
# 1. Criar estrutura
mkdir -p .claude/skills/my-skill

# 2. Criar SKILL.md
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: "Does X when user needs Y"
---

# My Skill

## Mission
[One sentence]

## Workflow
1. Step 1
2. Step 2
EOF

# 3. Claude ativa automaticamente quando relevante
```

### Criar um Agent

```bash
# 1. Criar arquivo
cat > .claude/agents/my-expert.md << 'EOF'
---
name: my-expert
description: |
  Expert in X. Use when Y.

  Examples:
  - <example>
    user: "Request example"
    assistant: "I'll use @my-expert to..."
  </example>
allowed-tools:
  - Read
  - Grep
  - Bash
model: sonnet
skills:
  - my-skill
---

You are an expert in [domain].

## Core Expertise
- [Skill 1]
- [Skill 2]
EOF

# 2. Invocar manualmente ou deixar Claude decidir
# @my-expert
```

### Criar um Hook

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit(*.py)",
        "hooks": [
          {
            "type": "command",
            "command": "black \"$TOOL_INPUT_FILE_PATH\""
          }
        ]
      }
    ]
  }
}
```

---

## 💡 Quando Usar Cada Um?

### Use **Slash Commands** quando

- ✅ Você tem um prompt que repete frequentemente
- ✅ Precisa passar argumentos específicos
- ✅ Quer controle manual da invocação
- ✅ Workflow é simples (1 arquivo)

**Exemplo**: `/review-pr 456 high alice`

### Use **Skills** quando

- ✅ Claude deve decidir automaticamente quando usar
- ✅ Precisa de múltiplos arquivos (scripts, templates)
- ✅ Progressive disclosure é importante
- ✅ Capacidade reutilizável entre projetos

**Exemplo**: Claude detecta PDF → ativa `pdf-processing` skill

### Use **Agents** quando

- ✅ Precisa de especialista focado em domínio
- ✅ Agent deve delegar para outros especialistas
- ✅ Workflow complexo com múltiplas etapas
- ✅ Output estruturado para outros agents

**Exemplo**: Request de API → Claude invoca `@agent-backend-developer`

### Use **Hooks** quando

- ✅ Ação deve **sempre** acontecer em determinado evento
- ✅ Precisa de comportamento determinístico
- ✅ Automação de formatação, linting, validação
- ✅ Logging, notificações customizadas

**Exemplo**: Após editar Python → sempre roda `black` (formatação)

---

## 📚 Guias Completos

- **[Slash Commands](guides/slash-commands.md)** - Criação, argumentos, bash, troubleshooting
- **[Skills](guides/skills.md)** - Progressive disclosure, built-in skills, custom skills
- **[Agents](guides/agents.md)** - XML examples, tool inheritance, integration patterns
- **[Hooks](guides/hooks.md)** - Eventos, matchers, security, exemplos práticos
- **[Output Styles](guides/output-styles.md)** - Built-in styles, custom styles
- **[Best Practices](best-practices.md)** - Práticas gerais para todos os tipos

---

## 🔗 Links Úteis

**Documentação Oficial:**

- [Claude Code Docs](https://code.claude.com/docs)
- [Anthropic Skills Guide](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)

---

## ⚡ Comandos Úteis

```bash
# Listar comandos disponíveis
/help

# Listar agents
/agents

# Verificar hooks registrados
/hooks

# Mudar output style
/output-style

# Debug mode
claude --debug
```

---

**Última Revisão**: 2026-01-11 por Claude Code
