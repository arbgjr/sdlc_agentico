# Project Artifacts

Este diretório contém todos os artifacts **específicos do projeto**, que são gerados durante o workflow SDLC.

## Estrutura

```
.project/
├── corpus/            # RAG knowledge corpus do projeto
│   ├── nodes/
│   │   ├── decisions/     # ADRs do projeto
│   │   ├── learnings/     # Lessons learned
│   │   ├── patterns/      # Patterns identificados
│   │   └── concepts/      # Conceitos extraídos
│   ├── graph.json         # Semantic graph
│   ├── adjacency.json     # Graph index
│   └── index.yml          # Search index
│
├── references/        # External docs (legal, technical, business)
│   └── enriched/      # Enriched documents
│
├── phases/            # SDLC phase outputs
│   ├── phase-0-intake/
│   ├── phase-1-discovery/
│   ├── phase-2-requirements/
│   ├── phase-3-architecture/
│   ├── phase-4-planning/
│   ├── phase-5-implementation/
│   ├── phase-6-quality/
│   ├── phase-7-release/
│   └── phase-8-operations/
│
├── architecture/      # Architecture artifacts (diagrams, data-models)
├── security/          # Security artifacts (threat-models, scan-results)
├── reports/           # Generated reports (quality-gates, metrics)
└── sessions/          # Session history (handoff summaries)
```

## O que Versionar

**Versionar no Git:**
- ✅ `corpus/nodes/decisions/` - ADRs
- ✅ `corpus/nodes/patterns/` - Patterns
- ✅ `architecture/` - Diagramas
- ✅ `security/` - Threat models
- ✅ `phases/` - Artifacts das fases

**NÃO versionar:**
- ❌ `sessions/` - Histórico temporário
- ❌ `reports/` - Relatórios gerados

Adicione ao `.gitignore`:

```gitignore
.project/sessions/
.project/reports/
```

## Separação Framework vs Projeto

- **Framework** (`.agentic_sdlc/`): Templates, schemas, docs → Reutilizável
- **Projeto** (`.project/`): Corpus, decisions, reports → Específico deste projeto

Esta separação permite usar o mesmo framework em múltiplos projetos.
