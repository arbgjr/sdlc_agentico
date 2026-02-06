---
name: agent-name
description: |
  Brief description of what this agent does.
  Explain when and why to use it.

  Use este agente para:
  - Primary use case 1
  - Primary use case 2
  - Primary use case 3

  Examples:
  - <example>
    Context: When to use this agent
    user: "User request example"
    assistant: "Vou usar @agent-name para [action]"
    <commentary>
    Why this agent is appropriate for this context
    </commentary>
    </example>

model: sonnet  # or opus for complex reasoning
skills:
  - rag-query
  - 
# Tool Access Control (OpenClaw pattern)
# https://github.com/openclaw/openclaw/blob/main/AGENTS.md
allowed_tools:
  # Whitelist of tools this agent can use
  # Use group: prefix for tool groups
  # Example: group:fs, group:runtime, group:web
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
denied_tools:
  # Blacklist takes precedence over allowed_tools
  # Use to explicitly deny destructive tools
  # Example: Bash, Git, Edit
  - Bash  # No command execution
  - Task  # No spawning sub-agents
references:
  - path: path/to/reference/doc.md
    purpose: Why this reference is relevant
---

# Agent Name

## Missao

Describe the agent's mission and responsibilities.

## O Que Voce Faz

### 1. Primary Responsibility

Description of primary responsibility.

### 2. Secondary Responsibility

Description of secondary responsibility.

## Como Voce Trabalha

### Fluxo de Trabalho

```markdown
1. Step 1: Description
2. Step 2: Description
3. Step 3: Description
```

### Criterios de Qualidade

- Quality criterion 1
- Quality criterion 2
- Quality criterion 3

## Quando Chamar Outros Agentes

- Call `agent-x` when: situation description
- Call `agent-y` when: situation description

## Output Esperado

Description of expected outputs and artifacts.

## Anti-Patterns

What NOT to do:
- ❌ Anti-pattern 1
- ❌ Anti-pattern 2

## Best Practices

What TO do:
- ✅ Best practice 1
- ✅ Best practice 2
