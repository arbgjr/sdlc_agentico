# Claude Code Workflow Cheatsheet (2026 Edition — Corrigido)

> Versão revisada com correções de sintaxe, keybindings e lista completa de hooks.

---

## 1. Getting Started

**Requisitos:** Node.js 18+

```bash
# Instalar Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Iniciar em um projeto
cd seu_projeto
claude
/init   # Gera CLAUDE.md inicial (use CLAUDE_CODE_NEW_INIT=1 para fluxo interativo)
```

---

## 2. Entendendo o CLAUDE.md

Memória persistente do projeto, carregada automaticamente em toda sessão.

| O QUÊ | POR QUÊ | COMO |
|-------|---------|------|
| Tech stack | Propósito de cada módulo | Comandos de build/test/lint |
| Mapa de diretórios | Decisões de design | Workflows e convenções |
| Arquitetura | Restrições de negócio | Gotchas e armadilhas |

---

## 3. Hierarquia de Arquivos de Memória

| Caminho | Escopo |
|---------|--------|
| `~/.claude/CLAUDE.md` | Global — todos os projetos |
| `../CLAUDE.md` | Pai — raiz de monorepo |
| `./CLAUDE.md` | Projeto — versionado no git |
| `./frontend/CLAUDE.md` | Subpasta — carregado *on-demand* |

**Regras:**

- Mantenha cada arquivo abaixo de ~200 linhas
- Subpastas **anexam** contexto, não sobrescrevem
- Nunca sobrescreva contexto pai

---

## 4. Boas Práticas para CLAUDE.md

- Rode `/init` primeiro, depois refine
- Seja específico nas instruções
- Adicione gotchas que Claude não consegue inferir sozinho
- Referencie docs com `@nome_do_arquivo`
- Inclua regras de workflow do time
- Mantenha conciso
- Commite no Git para compartilhar com o time

---

## 5. Estrutura de Arquivos do Projeto

```
seu_projeto/
├── CLAUDE.md
├── .claude/
│   ├── settings.json          # Compartilhado (versionado)
│   ├── settings.local.json    # Pessoal (não versionado)
│   ├── skills/
│   │   ├── code-review/
│   │   │   └── SKILL.md
│   │   └── testing/
│   │       └── SKILL.md
│   ├── commands/
│   │   └── deploy.md          # Slash command custom
│   ├── agents/
│   │   └── security-reviewer.md
│   └── hooks/
├── src/
└── .gitignore
```

---

## 6. Adicionando Skills

> Skills são guias em markdown que Claude **auto-invoca** com base em linguagem natural.

| Tipo | Caminho |
|------|---------|
| Skill do projeto | `.claude/skills/<nome>/SKILL.md` |
| Skill pessoal | `~/.claude/skills/<nome>/SKILL.md` |

**Exemplo de SKILL.md:**

```markdown
---
name: testing-patterns
description: Use describe + it + AAA pattern. Use factory mocks.
allowed-tools: [Read, Grep, Glob]
---

# Testing Patterns

Conteúdo do skill em markdown...
```

O campo `description` é o que dispara a auto-ativação.

---

## 7. Ideias de Skills para AI Engineers

- `code-review` — Padrões de revisão
- `testing-patterns` — AAA, factory mocks
- `commit-messages` — Conventional commits
- `docker-deploy` — Deploy em containers
- `codebase-visualizer` — Diagramas
- `api-design` — Contratos de API

---

## 8. Configurando Hooks

> Hooks são callbacks **determinísticos** disparados por eventos.

**Eventos disponíveis:**

| Evento | Quando dispara |
|--------|----------------|
| `PreToolUse` | Antes de executar uma tool |
| `PostToolUse` | Depois de executar uma tool |
| `UserPromptSubmit` | Quando o usuário envia um prompt |
| `Stop` | Quando Claude finaliza resposta |
| `SubagentStop` | Quando um subagent finaliza |
| `SessionStart` | Início de sessão |
| `SessionEnd` | Fim de sessão |
| `PreCompact` | Antes de compactar contexto |
| `Notification` | Notificações ao usuário |

**Exemplo:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/sec.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## 9. Permissions & Safety

> **Sintaxe correta usa parênteses**, não dois-pontos.

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Bash(git:*)",
      "Write(*)"
    ],
    "deny": [
      "Read(env:*)",
      "Bash(sudo:*)"
    ]
  }
}
```

---

## 10. Arquitetura em 4 Camadas

| Camada | Componente | Função |
|--------|------------|--------|
| **L1** | `CLAUDE.md` | Contexto persistente e regras |
| **L2** | Skills | Pacotes de conhecimento auto-invocados |
| **L3** | Hooks | Gates de segurança e automação |
| **L4** | Agents | Subagentes com contexto próprio |

---

## 11. Padrão de Workflow Diário

```bash
cd projeto && claude
```

1. Descreva a intenção da feature
2. Use `Shift+Tab` para ciclar entre modos: `default → acceptEdits → plan → bypassPermissions`
3. Trabalhe iterativamente
4. Use `/compact` quando o contexto crescer
5. Use `Esc Esc` para rebobinar e reverter
6. Comite com frequência
7. Inicie nova sessão por feature

---

## 12. Quick Reference

### Slash Commands

| Comando | Função |
|---------|--------|
| `/init` | Gera CLAUDE.md inicial |
| `/doctor` | Diagnostica instalação e configuração |
| `/compact` | Compacta o contexto da sessão |
| `/config` | Abre painel de configurações |
| `/help` | Ajuda |

### Keybindings

| Tecla | Ação |
|-------|------|
| `Shift+Tab` | Cicla modos de permissão (default → acceptEdits → plan → bypass) |
| `Option+T` (macOS) / `Alt+T` (Linux/Win) | Toggle extended thinking |
| `Tab` | Autocompletar comandos/sugestões |
| `Esc` | Cancelar input atual |
| `Esc Esc` | Menu de rewind (voltar a turno anterior) |
| `Ctrl+C` | Interromper execução |

---

## Erros comuns no cheatsheet original

1. `"Read:*"` → correto: `"Read(*)"` (permissões usam parênteses)
2. `Tab` ou `Shift+Tab` para extended thinking → correto: `Alt+T` / `Option+T`
3. `Shift+Tab+Tab` para Plan Mode → correto: `Shift+Tab` cicla modos
4. Hooks só com 3 tipos → existem ~9 eventos de hooks
5. `/doctor` "não existe" → existe e diagnostica a instalação
