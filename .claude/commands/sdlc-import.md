# /sdlc-import Command

**Agent:** sdlc-importer
**Phase:** 0 (Preparation)
**Skill:** sdlc-import

## Purpose

Reverse engineer existing codebases and automatically generate complete SDLC Agêntico documentation structure.

## Usage

```bash
/sdlc-import [project-path] [options]
```

## Options

- `--skip-threat-model` - Skip STRIDE threat modeling
- `--skip-tech-debt` - Skip technical debt detection
- `--no-llm` - Disable LLM synthesis (faster, lower cost)
- `--create-issues` - Create GitHub issues for P0 debt and HIGH threats
- `--branch-name` - Custom branch name (default: feature/import-{project-name})

## Examples

```bash
# Basic import
/sdlc-import /path/to/project

# Skip threat modeling
/sdlc-import /path/to/project --skip-threat-model

# Create GitHub issues for findings
/sdlc-import /path/to/project --create-issues

# Custom branch
/sdlc-import /path/to/project --branch-name feature/import-my-app
```

## What It Does

1. **Creates feature branch** - Automatic branch creation for clean git history
2. **Detects languages** - 10 programming languages + frameworks
3. **Extracts decisions** - 5-15 ADRs with confidence scores
4. **Generates diagrams** - 3-5 architecture diagrams (Mermaid + DOT)
5. **Models threats** - STRIDE analysis with security-guidance plugin
6. **Identifies tech debt** - 10-50 items with P0-P3 priorities
7. **Creates documentation** - Complete `.agentic_sdlc/` structure
8. **Validates quality** - Runs sdlc-import-gate.yml quality gate

## Outputs

```
.agentic_sdlc/
├── corpus/nodes/decisions/
│   ├── ADR-INFERRED-001.yml
│   └── ...
├── security/
│   └── threat-model-inferred.yml
├── architecture/
│   ├── component-diagram.mmd
│   └── data-flow.mmd
└── reports/
    ├── tech-debt-inferred.md
    └── import-report.md
```

## Quality Gate

**Gate:** sdlc-import-gate.yml

**Requirements:**
- Feature branch created (feature/import-*)
- Overall confidence >= 0.6
- Minimum 3 ADRs extracted
- Zero CRITICAL threats
- Minimum 2 diagrams generated

## Next Steps

After successful import:

1. Review high-confidence decisions
2. Validate medium-confidence decisions
3. Manual review for low-confidence (check GitHub issues)
4. Address P0 tech debt
5. Fix CRITICAL/HIGH threats
6. Merge feature branch to main

---

**Version:** 1.0.0
**Epic:** #52
**ADR:** ADR-022
