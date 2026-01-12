# Quick Start - SDLC Agêntico

Guia rápido para começar a usar o SDLC Agêntico em 5 minutos.

## 1. Instalação (2 min)

```bash
# Clone o repositório (se ainda não fez)
git clone https://github.com/arbgjr/mice_dolphins.git
cd mice_dolphins

# Execute o script de setup
./scripts/setup-sdlc.sh
```

O script instala automaticamente:
- Python 3.11+ e uv
- GitHub CLI e autenticação
- Claude Code CLI
- Spec Kit

## 2. Verificar Instalação

```bash
# Verificar dependências
specify check

# Verificar Claude Code
claude --version

# Verificar GitHub CLI
gh auth status
```

## 3. Primeiro Workflow (3 min)

### Opção A: Workflow Completo

```bash
# Iniciar Claude Code
claude

# Iniciar workflow SDLC
/sdlc-start "Criar endpoint de listagem de usuários com paginação"
```

O sistema automaticamente:
1. Analisa a demanda (intake-analyst)
2. Classifica complexidade (Level 0-3)
3. Guia você pelas fases necessárias

### Opção B: Direto ao Código (Level 0)

Para mudanças simples, pule direto para implementação:

```bash
claude

# O agente code-author implementa diretamente
"Corrija o bug de paginação no endpoint /api/users"
```

## 4. Comandos Essenciais

```bash
# Ver status atual
/phase-status

# Verificar se pode avançar de fase
/gate-check

# Criar issues para GitHub Copilot
/sdlc-create-issues --assign-copilot

# Scan de segurança
/security-scan
```

## 5. Integração com GitHub Copilot

Se você tem Copilot Pro+/Business/Enterprise:

```bash
# 1. Habilitar Copilot Coding Agent no repo
gh api repos/OWNER/REPO --method PATCH -f allow_copilot_coding_agent=true

# 2. Criar issues e atribuir ao Copilot
/sdlc-create-issues --assign-copilot

# 3. Acompanhar PRs do Copilot
gh pr list --author "app/copilot-workspace"
```

## Fluxo Visual

```
Você: "Criar feature X"
        │
        ▼
┌───────────────────┐
│  intake-analyst   │ ──→ Classifica Level 0/1/2/3
└───────────────────┘
        │
        ▼ (Level 2+)
┌───────────────────┐
│ domain-researcher │ ──→ Pesquisa tecnologias
└───────────────────┘
        │
        ▼
┌───────────────────┐
│requirements-analyst──→ Escreve User Stories
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ system-architect  │ ──→ Define arquitetura
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ /sdlc-create-issues ──→ Cria issues no GitHub
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ GitHub Copilot    │ ──→ Implementa e cria PRs
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  code-reviewer    │ ──→ Revisa código
└───────────────────┘
        │
        ▼
    PR Merged! 🎉
```

## Exemplos por Complexidade

### Level 0: Bug Fix
```bash
/sdlc-start "Corrigir erro de null pointer em OrderService.getById"
# → Vai direto para code-author → code-reviewer → done
```

### Level 1: Feature Simples
```bash
/sdlc-start "Adicionar campo de telefone no cadastro de usuário"
# → requirements-analyst → code-author → test-author → code-reviewer
```

### Level 2: Feature Complexa
```bash
/sdlc-start "Implementar sistema de notificações push"
# → Todas as fases de 0-7
```

### Level 3: Projeto Crítico
```bash
/sdlc-start "Migrar sistema de pagamentos para novo gateway"
# → Todas as fases + aprovações humanas em cada gate
```

## Dicas

1. **Seja específico**: Quanto mais detalhes na descrição, melhor a análise
2. **Use gates**: Sempre verifique `/gate-check` antes de avançar
3. **Documente decisões**: Use `/adr-create` para decisões importantes
4. **Monitore segurança**: Execute `/security-scan` antes de releases

## Próximos Passos

- Leia [AGENTS.md](docs/AGENTS.md) para conhecer todos os agentes
- Veja [COMMANDS.md](docs/COMMANDS.md) para referência completa
- Configure [INFRASTRUCTURE.md](INFRASTRUCTURE.md) para integração avançada

## Problemas Comuns

### "Command not found: claude"
```bash
npm install -g @anthropic-ai/claude-code
```

### "GitHub CLI not authenticated"
```bash
gh auth login
```

### "Spec Kit not found"
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### "Copilot Agent not working"
1. Verifique se tem plano Copilot Pro+/Business/Enterprise
2. Habilite em Settings > Copilot > Coding agent
3. Verifique permissões de write no repositório

---

**Tempo total de setup**: ~5 minutos
**Tempo para primeiro workflow**: ~2 minutos
