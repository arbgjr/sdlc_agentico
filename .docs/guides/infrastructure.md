# Infraestrutura do SDLC Agêntico

## Estrutura de Diretórios

```
.claude/
├── agents/           # 28 agentes especializados
├── skills/           # 9 skills reutilizáveis
├── commands/         # 10 comandos do usuário
├── hooks/            # 5 hooks de automação
└── settings.json     # Configuração central

.agentic_sdlc/        # Artefatos do SDLC
├── projects/         # Projetos gerenciados
│   └── {project-id}/
│       ├── manifest.yml      # Metadados do projeto
│       ├── phases/           # Contexto por fase
│       ├── decisions/        # ADRs do projeto
│       ├── specs/            # Especificações (SpecKit)
│       ├── security/         # Threat models, scans
│       ├── docs/             # Documentação gerada
│       └── iac/              # Infrastructure as Code
├── references/       # Documentos de referência
│   ├── legal/        # Leis, regulamentos
│   ├── technical/    # RFCs, specs técnicas
│   ├── business/     # Regras de negócio
│   └── internal/     # Docs internos (link para DESENVOLVIMENTO.md)
├── templates/        # Templates reutilizáveis
│   ├── adr-template.yml
│   ├── spec-template.md
│   └── threat-model-template.yml
├── corpus/           # RAG corpus
│   ├── indexed/
│   └── pending/
└── sessions/         # Histórico de sessões

.docs/                # Documentação do usuário
.scripts/             # Scripts de instalação
```

---

## Requisitos

### Planos GitHub Copilot (Escolha um)
- **Copilot Pro+** - Individual com coding agent
- **Copilot Business** - Organizacoes
- **Copilot Enterprise** - Empresas com custom agents

### Ferramentas Locais

| Ferramenta | Versao Minima | Instalacao |
|------------|---------------|------------|
| Python | 3.11+ | `sudo apt install python3.11` ou `brew install python@3.11` |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | 2.30+ | `sudo apt install git` ou `brew install git` |
| Claude Code | Latest | `npm install -g @anthropic-ai/claude-code` |
| GitHub CLI | 2.40+ | `sudo apt install gh` ou `brew install gh` |

---

## Instalacao Automatizada

### Script de Setup (Linux/macOS)

```bash
# Baixar e executar
curl -fsSL https://raw.githubusercontent.com/arbgjr/mice_dolphins/main/.scripts/setup-sdlc.sh | bash
```

Ou manualmente:

```bash
# 1. Instalar uv (gerenciador Python)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # ou ~/.zshrc

# 2. Instalar Spec Kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 3. Verificar instalacao
specify check

# 4. Inicializar projeto (se novo)
specify init . --ai claude --force

# 5. Autenticar GitHub CLI
gh auth login

# 6. Habilitar Copilot Coding Agent no repo
gh api repos/{owner}/{repo} --method PATCH -f allow_copilot_coding_agent=true
```

---

## Integracao com GitHub Copilot Coding Agent

### O Que E

O [GitHub Copilot Coding Agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent) e um agente autonomo que:
- Recebe **Issues atribuidas** a ele
- Analisa o codigo do repositorio
- Cria **Pull Requests** automaticamente
- Responde a **@copilot** mentions em PRs

### Como Funciona com Nosso SDLC

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO INTEGRADO                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Usuario executa /sdlc-start com demanda                 │
│              ↓                                              │
│  2. intake-analyst analisa e classifica (Level 0-3)         │
│              ↓                                              │
│  3. Agentes Claude Code produzem:                           │
│     - Spec (especificacao)                                  │
│     - Technical Plan                                        │
│     - Tasks detalhadas                                      │
│              ↓                                              │
│  4. /sdlc-create-issues cria Issues no GitHub               │
│     (1 issue por task)                                      │
│              ↓                                              │
│  5. Usuario atribui Issues ao Copilot                       │
│     (assignee: @copilot ou via API)                         │
│              ↓                                              │
│  6. Copilot Coding Agent implementa cada Issue              │
│              ↓                                              │
│  7. PRs criados automaticamente                             │
│              ↓                                              │
│  8. code-reviewer (Claude) faz review                       │
│     ou @copilot recebe feedback                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Habilitando no Repositorio

**Via GitHub UI:**
1. Acesse Settings > Copilot > Coding agent
2. Habilite "Allow Copilot to work on issues"

**Via GitHub CLI:**
```bash
# Habilitar coding agent
gh api repos/OWNER/REPO --method PATCH \
  -f allow_copilot_coding_agent=true

# Verificar status
gh api repos/OWNER/REPO --jq '.allow_copilot_coding_agent'
```

**Via GitHub Actions (CI/CD):**
```yaml
# .github/workflows/enable-copilot-agent.yml
name: Enable Copilot Coding Agent
on:
  workflow_dispatch:

jobs:
  enable:
    runs-on: ubuntu-latest
    steps:
      - name: Enable Copilot Coding Agent
        run: |
          gh api repos/${{ github.repository }} --method PATCH \
            -f allow_copilot_coding_agent=true
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Criando Issues para o Copilot

### Formato Recomendado

O Copilot Coding Agent funciona melhor com Issues bem estruturadas:

```markdown
## Descricao
[Descricao clara do que precisa ser feito]

## Criterios de Aceite
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Contexto Tecnico
- Arquivos relevantes: `src/services/auth.py`
- Dependencias: `requirements.txt`
- Testes: `tests/test_auth.py`

## Restricoes
- Manter compatibilidade com API v2
- Nao quebrar testes existentes
```

### Comando para Criar Issues

```bash
# Criar issue e atribuir ao Copilot
gh issue create \
  --title "Implementar autenticacao JWT" \
  --body-file .specify/tasks/TASK-001.md \
  --assignee "@copilot" \
  --label "copilot-agent"
```

### Atribuindo Issues Existentes

```bash
# Atribuir issue existente ao Copilot
gh issue edit 123 --add-assignee "@copilot"
```

---

## MCPs (Model Context Protocol)

### MCPs Disponiveis para Copilot Coding Agent

O Copilot Coding Agent ja inclui automaticamente:
- **GitHub MCP** - Acesso a issues, PRs, repos
- **Playwright MCP** - Navegacao web e screenshots

### MCPs Customizados (Enterprise)

Para Copilot Enterprise, voce pode adicionar MCPs remotos:

```yaml
# .github/copilot-agent.yml
mcp_servers:
  - name: "database"
    url: "https://mcp.mycompany.com/database"
    auth: "oauth"

  - name: "internal-docs"
    url: "https://mcp.mycompany.com/docs"
```

### MCPs para Claude Code (Este Projeto)

Nosso SDLC ja tem skills que funcionam como "MCPs locais":
- `rag-query` - Consulta conhecimento do projeto
- `memory-manager` - Persistencia de contexto
- `gate-evaluator` - Validacao de quality gates

---

## Skills Disponíveis

| Skill | Propósito | Comando |
|-------|-----------|---------|
| `gate-evaluator` | Avalia quality gates entre fases | `/gate-check` |
| `memory-manager` | Gerencia persistência de contexto | Automático |
| `rag-query` | Consulta corpus de conhecimento | Automático |
| `spec-kit-integration` | Integra com GitHub Spec Kit | `/speckit.*` |
| `bmad-integration` | Integra com BMAD Method | Automático |
| `auto-branch` | Cria branches automaticamente | Automático |
| `iac-generator` | Gera Infrastructure as Code | Via `iac-engineer` |
| `doc-blueprint` | Gera blueprints de documentação | Via `doc-generator` |
| `reference-indexer` | Indexa documentos de referência | `/ref-add`, `/ref-search` |

---

## Hooks Disponíveis

| Hook | Trigger | Propósito |
|------|---------|-----------|
| `validate-commit.sh` | PreToolUse (git commit) | Valida mensagens e conteúdo |
| `check-gate.sh` | PreToolUse (git push) | Verifica quality gate |
| `auto-branch.sh` | Via skill | Cria branches (fix/, feature/, etc.) |
| `update-project-timestamp.sh` | PreToolUse (git commit) | Atualiza timestamp no manifest |
| `detect-phase.sh` | UserPromptSubmit | Detecta fase atual do SDLC |
| `detect-adr-need.sh` | PostToolUse (src/**, infrastructure/**) | Sugere ADR para mudanças arquiteturais |

---

## Arquivo de Permissões Local

### settings.local.json

O arquivo `.claude/settings.local.json` contém permissões específicas para este repositório. **Este arquivo não deve ser commitado** pois pode conter permissões sensíveis.

**Propósito**: Pré-aprovar comandos frequentes para evitar prompts repetitivos durante o desenvolvimento.

**Estrutura**:
```json
{
  "permissions": {
    "allow": [
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)"
      // ... outros comandos pré-aprovados
    ]
  }
}
```

**Quando usar**:
- Para pré-aprovar comandos git que você usa frequentemente
- Para permitir ferramentas de build específicas
- Para evitar prompts em comandos seguros e repetitivos

**Segurança**:
- Adicione `.claude/settings.local.json` ao `.gitignore`
- Revise as permissões periodicamente
- Não pré-aprove comandos destrutivos

**Exemplo de permissões comuns**:
```json
{
  "permissions": {
    "allow": [
      "Bash(tree:*)",
      "Bash(wc:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(npm test:*)",
      "Bash(dotnet build:*)"
    ]
  }
}
```

---

## Integracao Spec Kit + SDLC

### Fluxo Completo

```bash
# 1. Iniciar projeto com Spec Kit
specify init . --ai claude

# 2. Definir principios (constituicao)
# No Claude Code:
/speckit.constitution

# 3. Criar especificacao
/speckit.specify "Sistema de autenticacao com OAuth2"

# 4. Gerar plano tecnico
/speckit.plan

# 5. Quebrar em tasks
/speckit.tasks

# 6. Criar issues no GitHub (nosso comando customizado)
/sdlc-create-issues

# 7. Implementar com Copilot ou Claude
# Opcao A: Atribuir issues ao Copilot
# Opcao B: /speckit.implement (Claude Code local)
```

---

## Arquitetura de Integracao

```
┌─────────────────────────────────────────────────────────────────┐
│                         SEU AMBIENTE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   Claude Code    │    │  VS Code +       │                   │
│  │   (Terminal)     │    │  GitHub Copilot  │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────────────────────────────┐                    │
│  │            .claude/                      │                   │
│  │  ├── agents/     (28 agentes)           │                   │
│  │  ├── skills/     (9 skills)             │                   │
│  │  ├── commands/   (10 comandos)          │                   │
│  │  └── hooks/      (5 hooks)              │                   │
│  └────────────────────┬────────────────────┘                    │
│                       │                                         │
│           ┌───────────┼───────────┐                             │
│           ▼           ▼           ▼                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │  .agentic_sdlc/ │ │    .specify/    │ │  .github/       │   │
│  │  (Artefatos)    │ │  (Spec Kit)     │ │  (Copilot)      │   │
│  │  - projects/    │ │  - specs/       │ │  - prompts/     │   │
│  │  - references/  │ │  - plans/       │ │  - copilot-     │   │
│  │  - templates/   │ │  - tasks/       │ │    agent.yml    │   │
│  │  - corpus/      │ │                 │ │                 │   │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘   │
│           │                   │                   │             │
└───────────┼───────────────────┼───────────────────┼─────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌───────────────────────────────────────────────────────────────┐
│                        GITHUB                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Issues    │  │    PRs      │  │  Actions    │           │
│  │ (Tasks)     │→ │ (Copilot)   │→ │ (CI/CD)     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│         ↑                                                     │
│         │                                                     │
│  ┌─────────────────────────────────────────────┐             │
│  │     GitHub Copilot Coding Agent             │             │
│  │     (Executa em GitHub Actions)             │             │
│  └─────────────────────────────────────────────┘             │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Comandos Uteis

### Setup Inicial
```bash
# Verificar pre-requisitos
specify check

# Instalar Claude Code
npm install -g @anthropic-ai/claude-code

# Autenticar GitHub
gh auth login
```

### Workflow Diario
```bash
# Ver status do SDLC
claude "/phase-status"

# Criar issue para Copilot
gh issue create --assignee "@copilot" --title "..."

# Ver PRs do Copilot
gh pr list --author "app/copilot-workspace"

# Revisar PR do Copilot
gh pr review 123 --comment --body "@copilot Please add unit tests"
```

### Troubleshooting
```bash
# Ver logs do Copilot agent
gh api repos/OWNER/REPO/copilot/agent/sessions

# Re-atribuir issue
gh issue edit 123 --remove-assignee "@copilot"
gh issue edit 123 --add-assignee "@copilot"
```

---

## Limitacoes Conhecidas

### Copilot Coding Agent
- Apenas 1 PR por vez por issue
- Nao funciona com branch protection "Require signed commits"
- Apenas repositorios hospedados no GitHub
- Nao suporta OAuth para MCPs remotos (ainda)

### Integracao SDLC
- Quality gates sao avaliados pelo Claude Code, nao pelo Copilot
- Review final requer humano ou Claude Code
- Copilot nao tem acesso ao RAG do projeto (ainda)

---

## Custos

| Componente | Custo |
|------------|-------|
| Copilot Pro+ | $39/mes |
| Copilot Business | $19/usuario/mes |
| Copilot Enterprise | $39/usuario/mes |
| Claude Code | Por uso (API) |
| GitHub Actions | Incluso no plano |

**Nota**: Copilot Coding Agent usa "premium requests" - 1 request por chamada de modelo.

---

## Proximos Passos

1. Executar script de setup
2. Habilitar Copilot Coding Agent no repo
3. Criar primeira Spec com `/speckit.specify`
4. Gerar Tasks com `/speckit.tasks`
5. Atribuir primeira Issue ao Copilot
6. Observar PR sendo criado

## Referencias

- [GitHub Copilot Coding Agent Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [MCP e Copilot Coding Agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent)
- [From Idea to PR - Agentic Workflows](https://github.blog/ai-and-ml/github-copilot/from-idea-to-pr-a-guide-to-github-copilots-agentic-workflows/)
