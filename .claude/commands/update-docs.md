---
name: update-docs
description: Atualiza contadores de componentes em README.md e CLAUDE.md
tags: [documentation, maintenance, automation]
version: 1.0.0
---

# Update Documentation Counts

Atualiza automaticamente os contadores de agents, skills, commands e hooks nos documentos principais.

## Usage

```bash
/update-docs
```

## What it does

1. **Conta componentes atuais**:
   - Agents: arquivos `.md` em `.claude/agents/`
   - Skills: diretórios em `.claude/skills/`
   - Commands: arquivos `.md` em `.claude/commands/`
   - Hooks: arquivos `.sh` em `.claude/hooks/`

2. **Atualiza documentos**:
   - `README.md`: badges, ASCII art, estrutura de diretórios
   - `CLAUDE.md`: descrição do projeto, configuração

3. **Mostra mudanças**:
   - Exibe diff das alterações
   - Sugere commit se houver mudanças

## When to use

- ✅ Após criar novo agent
- ✅ Após adicionar nova skill
- ✅ Após criar novo command
- ✅ Após adicionar novo hook
- ✅ Antes de fazer release
- ✅ Antes de criar PR

**Nota**: Este comando é executado **automaticamente** via hook PostToolUse quando você cria novos componentes, mas pode ser chamado manualmente a qualquer momento.

## Examples

```bash
# Após criar novo agent
/update-docs

# Output:
# 🔄 Atualizando contadores de componentes...
# 📊 Contadores detectados:
#    Agents:   39
#    Skills:   29
#    Commands: 25
#    Hooks:    21
# ✅ Atualizado: README.md
# ✅ Atualizado: CLAUDE.md
# 💡 Próximos passos:
#    1. Revisar as mudanças: git diff
#    2. Commitar: git add README.md CLAUDE.md && git commit -m 'docs: update component counts'
```

## Implementation

Execute o script:
```bash
./.claude/scripts/update-component-counts.sh
```

## Related

- `/doc-generate` - Gera CLAUDE.md e README.md do zero
- PostToolUse hooks - Atualização automática
