# SDLC Agentico - Estrutura de Artefatos

Este diretorio contem todos os artefatos gerados pelo SDLC Agentico.

## Estrutura

```
.agentic_sdlc/
├── projects/           # Projetos gerenciados pelo SDLC
│   └── {project-id}/   # Cada projeto tem sua propria pasta
│       ├── manifest.yml    # Metadados do projeto
│       ├── phases/         # Contexto por fase
│       ├── decisions/      # ADRs do projeto
│       ├── specs/          # Especificacoes (SpecKit)
│       ├── security/       # Threat models, scans
│       ├── docs/           # Documentacao gerada
│       └── iac/            # Infrastructure as Code
│
├── references/         # Documentos de referencia externos
│   ├── legal/          # Leis, regulamentos, normas
│   ├── technical/      # RFCs, especificacoes tecnicas
│   ├── business/       # Regras de negocio, manuais
│   └── internal/       # Documentos internos
│
├── templates/          # Templates reutilizaveis
│   ├── adr-template.yml
│   ├── spec-template.md
│   └── threat-model-template.yml
│
├── corpus/             # RAG corpus
│   ├── indexed/        # Documentos indexados
│   └── pending/        # Aguardando indexacao
│
└── sessions/           # Historico de sessoes
    └── session-{timestamp}.yml
```

## Como Usar

### Iniciar Novo Projeto

```bash
/sdlc-start "Nome do Projeto"
```

O orchestrator criara automaticamente:
- Pasta do projeto em `projects/{project-id}/`
- Arquivo `manifest.yml` com metadados
- Estrutura de subdiretorios

### Adicionar Documentos de Referencia

1. Coloque o documento na pasta apropriada em `references/`
2. Execute `/ref-add {caminho}` para indexar no corpus RAG

### Criar ADR

```bash
/adr-create "Titulo da Decisao"
```

### Verificar Status

```bash
/phase-status
```

## Migracao de .claude/memory/

Se voce tem artefatos antigos em `.claude/memory/`, execute:

```bash
./.claude/scripts/migrate-to-agentic-sdlc.sh {project-id}
```

## Convencoes

- IDs de projeto: lowercase, kebab-case (ex: `duplicatas-eletronicas`)
- Timestamps: ISO 8601 com timezone UTC
- YAML: flow style false, allow unicode true
