# Contribuindo para o SDLC Agêntico

Obrigado pelo interesse em contribuir! Este documento explica como participar do desenvolvimento.

## Como Contribuir

### 1. Reportar Bugs

Abra uma issue com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Versão do Claude Code e sistema operacional

### 2. Sugerir Features

Antes de implementar, abra uma issue para discussão:
- Descreva o caso de uso
- Explique o benefício esperado
- Proponha uma solução inicial

### 3. Contribuir Código

```bash
# 1. Fork e clone
git clone https://github.com/arbgjr/mice_dolphins.git
cd mice_dolphins

# 2. Crie uma branch
git checkout -b feat/nome-da-feature

# 3. Faça as mudanças
# ... código ...

# 4. Teste localmente
./.scripts/setup-sdlc.sh
claude
/sdlc-start "teste"

# 5. Commit seguindo Conventional Commits
git commit -m "feat(agents): add new agent for X"

# 6. Push e abra PR
git push origin feat/nome-da-feature
```

## Padrões de Código

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Tipos permitidos:**
- `feat` - Nova funcionalidade
- `fix` - Correção de bug
- `docs` - Documentação
- `refactor` - Refatoração sem mudança funcional
- `test` - Adição/modificação de testes
- `chore` - Manutenção

**Escopos comuns:**
- `agents` - Agentes (.claude/agents/)
- `skills` - Skills (.claude/skills/)
- `commands` - Comandos (.claude/commands/)
- `hooks` - Hooks (.claude/hooks/)
- `gates` - Quality gates
- `docs` - Documentação

**Exemplos:**
```bash
feat(agents): add compliance-guardian agent
fix(hooks): correct phase detection regex
docs(readme): update installation instructions
```

### Estrutura de Agentes

Cada agente deve seguir este template:

```markdown
---
name: agent-name
description: Descrição breve
model: sonnet | opus | haiku
skills:
  - skill-name
tools:
  - Read
  - Write
  - etc
---

# Agent Name

## Propósito
Descrição detalhada do propósito.

## Quando Usar
- Situação 1
- Situação 2

## Input Esperado
```yaml
input:
  field1: type
  field2: type
```

## Output
```yaml
output:
  field1: type
  field2: type
```

## Processo
1. Passo 1
2. Passo 2
3. Passo 3

## Checklist
- [ ] Item 1
- [ ] Item 2
```

### Estrutura de Skills

```markdown
---
name: skill-name
description: Descrição breve
---

# Skill Name

## Propósito
O que a skill faz.

## Como Usar
Instruções de uso.

## Parâmetros
- `param1`: Descrição
- `param2`: Descrição

## Exemplos
```bash
# Exemplo 1
```
```

### Estrutura de Comandos

```markdown
---
name: /command-name
description: Descrição breve
arguments:
  - name: arg1
    required: true
    description: O que é
---

# /command-name

## Uso
```bash
/command-name <arg1> [options]
```

## Parâmetros
- `arg1` (obrigatório): Descrição

## O Que Faz
1. Passo 1
2. Passo 2

## Exemplos
```bash
/command-name valor
```
```

## Adicionando Novos Componentes

### Novo Agente

1. Crie arquivo em `.claude/agents/nome-agente.md`
2. Siga o template acima
3. Adicione ao `settings.json` em `agents.available_agents`
4. Adicione ao `.docs/AGENTS.md`
5. Teste: `"Use o nome-agente para..."`

### Nova Skill

1. Crie diretório em `.claude/skills/nome-skill/`
2. Crie `SKILL.md` com o template
3. Adicione scripts necessários
4. Teste invocando de um agente

### Novo Comando

1. Crie arquivo em `.claude/commands/nome.md`
2. Siga o template acima
3. Adicione ao `.docs/COMMANDS.md`
4. Teste: `/nome-comando`

### Novo Hook

1. Crie script em `.claude/hooks/nome.sh`
2. Torne executável: `chmod +x .claude/hooks/nome.sh`
3. Configure em `.claude/settings.json`
4. Teste a trigger

### Novo Gate

1. Crie arquivo em `.claude/skills/gate-evaluator/gates/phase-X-to-Y.yml`
2. Defina artefatos obrigatórios
3. Defina critérios de qualidade
4. Adicione ao `.docs/COMMANDS.md`

## Testes

### Testes Manuais

```bash
# Testar workflow completo
claude
/sdlc-start "Feature de teste"

# Testar gate específico
/gate-check phase-2-to-3

# Testar comando
/security-scan
```

### Checklist de PR

Antes de abrir PR, verifique:

- [ ] Código segue os padrões estabelecidos
- [ ] Documentação atualizada
- [ ] Testado localmente
- [ ] Sem secrets no código
- [ ] Commits seguem Conventional Commits
- [ ] PR tem descrição clara

## Processo de Review

1. **Autor**: Abre PR com descrição clara
2. **Reviewer**: Revisa código e documentação
3. **CI**: Valida hooks e formatação
4. **Merge**: Squash merge para main

## Governança

### Decisões Arquiteturais

Para mudanças significativas:
1. Abra issue de discussão
2. Se aprovada, crie ADR
3. Implemente após aprovação

### Breaking Changes

- Requer discussão prévia
- Documentar migração
- Bump de versão major

## Contato

- Issues: [GitHub Issues](https://github.com/arbgjr/mice_dolphins/issues)
- Discussões: [GitHub Discussions](https://github.com/arbgjr/mice_dolphins/discussions)

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

Obrigado por contribuir!
