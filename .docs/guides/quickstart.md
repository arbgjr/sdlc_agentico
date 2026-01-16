# Quick Start - SDLC Agêntico

Guia rápido para começar a usar o SDLC Agêntico em 5 minutos.

## Escolha Rápida de Comando

```
┌─────────────────────────────────────────────────────────────┐
│                    QUAL COMANDO USAR?                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  É um bug fix simples?                                      │
│  └─ SIM → /quick-fix "descrição"                            │
│                                                             │
│  É feature em serviço existente?                            │
│  └─ SIM → /new-feature "nome"                               │
│                                                             │
│  É projeto/serviço novo?                                    │
│  └─ SIM → /sdlc-start "descrição"                           │
│                                                             │
│  Precisa de compliance/aprovações?                          │
│  └─ SIM → /sdlc-start "descrição" (Level 3)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 1. Instalação (2 min)

### Linux/macOS/WSL (Recomendado)

```bash
# Definir versão (consulte https://github.com/arbgjr/sdlc_agentico/releases)
VERSION="v1.7.1"

# Download e extração (preserva permissões)
curl -fsSL "https://github.com/arbgjr/sdlc_agentico/releases/download/${VERSION}/sdlc-agentico-${VERSION}.tar.gz" | tar -xzf -

# Execute o setup
./.scripts/setup-sdlc.sh
```

### Alternativa: Clone do Repositório

```bash
git clone https://github.com/arbgjr/sdlc_agentico.git
cd sdlc_agentico
./.scripts/setup-sdlc.sh
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

### Opção A: Bug Fix Rápido (Level 0)

```bash
claude

# Fluxo automático: branch → fix → test → PR
/quick-fix "Corrigir erro de timeout na API de usuários"
```

O sistema automaticamente:
1. Cria branch `fix/corrigir-erro-timeout`
2. Implementa o fix
3. Cria testes
4. Faz review
5. Cria PR

### Opção B: Nova Feature (Level 1)

```bash
claude

# Fluxo: branch → spec → requisitos → implementação → PR
/new-feature "Exportação de relatórios em PDF"
```

O sistema automaticamente:
1. Cria branch `feature/exportacao-relatorios-pdf`
2. Cria spec para requisitos
3. Implementa com testes
4. Faz review e validação
5. Cria PR

### Opção C: Projeto Completo (Level 2/3)

```bash
claude

# Workflow SDLC completo
/sdlc-start "Criar endpoint de listagem de usuários com paginação"
```

O sistema automaticamente:
1. Analisa a demanda (intake-analyst)
2. Classifica complexidade (Level 0-3)
3. Guia você pelas fases necessárias

## 4. Comandos Essenciais

```bash
# Fluxos por complexidade
/quick-fix "descrição"      # Level 0 - Bug fixes
/new-feature "nome"         # Level 1 - Features simples
/sdlc-start "descrição"     # Level 2/3 - Projetos completos

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
/quick-fix "Corrigir erro de null pointer em OrderService.getById"
# → Branch fix/corrigir-erro-null-pointer criada
# → code-author implementa fix
# → test-author cria teste de regressão
# → code-reviewer aprova
# → PR criada automaticamente
```

### Level 1: Feature Simples
```bash
/new-feature "Campo de telefone no cadastro"
# → Branch feature/campo-telefone-cadastro criada
# → Spec criada em .agentic_sdlc/projects/{id}/specs/
# → requirements-analyst define requisitos
# → code-author + test-author implementam
# → code-reviewer + qa-analyst validam
# → PR criada
```

### Level 2: Feature Complexa
```bash
/sdlc-start "Implementar sistema de notificações push"
# → Todas as fases de 0-7
# → Security by Design aplicado
# → Threat model gerado
# → IaC gerado se necessário
```

### Level 3: Projeto Crítico
```bash
/sdlc-start "Migrar sistema de pagamentos para novo gateway"
# → Todas as fases + aprovações humanas em cada gate
# → Security gates obrigatórios
# → Compliance checklist completo
```

## Dicas

1. **Seja específico**: Quanto mais detalhes na descrição, melhor a análise
2. **Use gates**: Sempre verifique `/gate-check` antes de avançar
3. **Documente decisões**: Use `/adr-create` para decisões importantes
4. **Monitore segurança**: Execute `/security-scan` antes de releases

## Próximos Passos

- Leia [AGENTS.md](AGENTS.md) para conhecer todos os agentes
- Veja [COMMANDS.md](COMMANDS.md) para referência completa
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
