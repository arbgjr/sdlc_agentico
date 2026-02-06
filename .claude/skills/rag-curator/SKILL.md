---
name: rag-curator
description: Curador do corpus RAG. Gerencia adição, organização e manutenção do conhecimento do projeto. Garante qualidade e acessibilidade.
---

# RAG Curator

Skill responsável por curar e manter o corpus RAG do projeto.

## Capabilities

- **Index ADRs**: Copia ADRs de project directory (via path_resolver) para `corpus/nodes/decisions/`
- **Index Learnings**: Copia learnings extraídos para `corpus/nodes/learnings/`
- **Validate Quality**: Verifica qualidade e completude dos nodes
- **Clean Obsolete**: Remove conhecimento obsoleto

## Path Resolution

This skill uses `path_resolver.py` to dynamically resolve project artifacts directory from `settings.json`:

```bash
# Resolve project directory
PROJECT_DIR=$(python3 .claude/lib/python/path_resolver.py --project-dir)

# ADRs are read from: ${PROJECT_DIR}/projects/{id}/decisions/
# Corpus is written to: ${PROJECT_DIR}/corpus/nodes/decisions/
```

**Why this approach**:
- Respects `settings.json` configuration (default: `.project`)
- Compatible with "Natural Language First" policy (system integration connector)
- Never hardcodes `.agentic_sdlc/` (which is for framework files only)

## Usage

**Note**: Scripts automatically use `path_resolver.py` to find project directories.

```bash
# Index ADRs from project to corpus
# (automatically resolves paths from settings.json)
python3 .claude/skills/rag-curator/scripts/index_adrs.py --project-id PROJECT_ID

# Index all projects
python3 .claude/skills/rag-curator/scripts/index_adrs.py --all

# Validate corpus quality
python3 .claude/skills/rag-curator/scripts/validate_corpus.py

# Manual path resolution (if needed)
PROJECT_DIR=$(python3 .claude/lib/python/path_resolver.py --project-dir)
echo "Project artifacts: $PROJECT_DIR"
```

## Integration

- **Phase 1 (Discovery)**: domain-researcher → rag-curator (index research)
- **Phase 3 (Architecture)**: adr-author → rag-curator (index ADRs)
- **Gate Evaluation**: gate-evaluator → rag-curator (auto-index on gate pass)

## Files

- `scripts/index_adrs.py`: Index ADRs to corpus
- `scripts/index_learnings.py`: Index learnings to corpus
- `scripts/validate_corpus.py`: Validate corpus quality
