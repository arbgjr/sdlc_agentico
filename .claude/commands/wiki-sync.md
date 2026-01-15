---
name: wiki-sync
description: |
  Sincroniza documentacao com GitHub Wiki.
  Publica ADRs, docs de arquitetura e API automaticamente.

  Examples:
  - <example>
    Context: Release pronto, docs precisam ir para wiki
    user: "/wiki-sync"
    assistant: "Vou sincronizar a documentacao com a GitHub Wiki"
    </example>
---

# Sincronizar Documentacao com GitHub Wiki

## Instrucoes

Sincronize a documentacao do projeto com a GitHub Wiki.

## Pre-requisitos

1. **Wiki Habilitada**
   - Acesse: Settings > Features > Wikis (checkbox)

2. **Wiki Inicializada**
   - A wiki deve ter pelo menos uma pagina (Home) criada manualmente
   - Acesse: https://github.com/{owner}/{repo}/wiki
   - Se aparecer "Create the first page", crie uma pagina Home simples

3. **Autenticacao GitHub CLI**
   ```bash
   gh auth status
   ```

## Processo

### 1. Executar Sincronizacao

```bash
# Sincronizacao completa
.claude/skills/github-wiki/scripts/wiki_sync.sh

# Com output detalhado
.claude/skills/github-wiki/scripts/wiki_sync.sh --verbose

# Apenas verificar (dry-run)
.claude/skills/github-wiki/scripts/wiki_sync.sh --dry-run
```

### 2. Publicar ADR Especifico

```bash
# Publicar um ADR
.claude/skills/github-wiki/scripts/publish_adr.sh .agentic_sdlc/corpus/nodes/decisions/adr-001.yml

# Publicar todos os ADRs
.claude/skills/github-wiki/scripts/publish_adr.sh --all
```

## Documentos Sincronizados

| Origem | Destino Wiki |
|--------|--------------|
| `.agentic_sdlc/projects/*/docs/README.md` | Getting-Started.md |
| `.agentic_sdlc/projects/*/docs/ARCHITECTURE.md` | Architecture.md |
| `.agentic_sdlc/projects/*/docs/API.md` | API-Reference.md |
| `.agentic_sdlc/corpus/nodes/decisions/*.yml` | ADRs/ADR-NNN.md |

## Estrutura da Wiki Gerada

```
wiki/
├── Home.md               # Pagina inicial com indice
├── Getting-Started.md    # Quick start
├── Architecture.md       # Visao geral da arquitetura
├── API-Reference.md      # Documentacao da API
├── ADRs/
│   ├── adr-001.md       # ADRs convertidos de YAML
│   ├── adr-002.md
│   └── ...
└── _Sidebar.md          # Navegacao lateral
```

## Output Esperado

```yaml
wiki_sync:
  status: success
  documents_synced: 5
  adrs_published: 3

  files:
    - Home.md (generated)
    - Getting-Started.md (from README)
    - Architecture.md (from ARCHITECTURE)
    - ADRs/adr-001.md (from decisions)
    - _Sidebar.md (generated)

  wiki_url: "https://github.com/owner/repo/wiki"
```

## Triggers Automaticos

A wiki e sincronizada automaticamente em:

1. **Phase 7 (Release)**: Apos aprovar gate de release
2. **ADR Create**: Apos criar novo ADR via `/adr-create`

## Troubleshooting

### Erro: "repository not found"

A wiki nao esta inicializada. Solucao:
1. Acesse https://github.com/{owner}/{repo}/wiki
2. Crie uma pagina Home manualmente
3. Tente novamente

### Erro: "Permission denied"

Verifique permissoes:
1. `gh auth status` deve mostrar acesso ao repositorio
2. Usuario deve ter permissao de escrita

### Conflitos

Se a wiki foi editada manualmente:
1. A sincronizacao sobrescreve arquivos gerenciados
2. Faca backup antes se necessario
