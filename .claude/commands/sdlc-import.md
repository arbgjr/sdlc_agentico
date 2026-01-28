# /sdlc-import

**Skill**: sdlc-import
**Phase**: 0 (Preparation)
**Agent**: sdlc-importer
**Complexity**: Level 2-3

## Description

Reverse engineer existing codebases (legacy or modern projects without SDLC artifacts) and automatically generate complete SDLC Agêntico documentation.

This command analyzes your project and generates:
- Architecture Decision Records (ADRs) with confidence scores
- Architecture diagrams (Mermaid + DOT)
- STRIDE threat model
- Technical debt report (P0-P3 prioritized)
- Complete `.project/` structure (respects settings.json configuration)

## Usage

```bash
/sdlc-import [project-path] [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--skip-threat-model` | Skip STRIDE threat analysis | false |
| `--skip-tech-debt` | Skip technical debt detection | false |
| `--no-llm` | Disable LLM synthesis (faster, lower cost) | false |
| `--create-issues` | Create GitHub issues for P0 debt and HIGH threats | false |
| `--branch-name` | Custom branch name | `feature/import-{project-name}` |
| `--config` | Path to custom config file | `.claude/skills/sdlc-import/config/import_config.yml` |
| `--output` | Output file for results (JSON) | stdout |

## Examples

### Basic Import

```bash
/sdlc-import /path/to/existing/project
```

Analyzes project, creates feature branch `feature/import-{project-name}`, and generates all documentation.

### Fast Import (No LLM)

```bash
/sdlc-import /path/to/project --no-llm
```

Uses only pattern matching for decision extraction (faster, but lower confidence scores).

### Security-Focused Import

```bash
/sdlc-import /path/to/project --skip-tech-debt
```

Focuses on STRIDE threat modeling and architecture decisions only.

### Create GitHub Issues

```bash
/sdlc-import /path/to/project --create-issues
```

Automatically creates GitHub issues for:
- P0 technical debt items
- HIGH and CRITICAL security threats

### Custom Branch

```bash
/sdlc-import /path/to/legacy-app --branch-name feature/modernize-legacy-app
```

## Workflow

The command executes a 9-step analysis:

1. **Create Feature Branch**: Auto-create `feature/import-{project-name}` using auto-branch skill
2. **Validate Project**: Check project path, size limits (default: 100K LOC)
3. **Scan Directory**: Count files, LOC by extension
4. **Detect Languages**: Identify primary language, frameworks, dependencies (10 languages supported)
5. **Extract Decisions**: Infer architecture decisions with confidence scores (5-15 ADRs)
6. **Generate Diagrams**: Create component, dependency, and data flow diagrams (3-5 diagrams)
7. **Model Threats**: Perform STRIDE analysis, identify vulnerabilities (optional)
8. **Detect Tech Debt**: Scan for code smells, deprecated dependencies, missing tests (optional)
9. **Generate Documentation**: Create ADRs, threat model, tech debt report, import summary

## Supported Languages

- Python (Django, Flask, FastAPI)
- JavaScript (React, Next.js, Express)
- TypeScript (Angular, NestJS)
- Java (Spring, Maven, Gradle)
- C# (ASP.NET, Entity Framework)
- Go (Gin, GORM)
- Ruby (Rails)
- PHP (Laravel, Symfony)
- Rust (Actix)
- Kotlin (Ktor)

## Output Directory

**IMPORTANT:** Output directory is configurable via settings.json (default: `.project/`)

**Configuration priority:**
1. `.claude/settings.json` → `sdlc.output.project_artifacts_dir`
2. `import_config.yml` → `general.output_dir` (fallback)
3. Default: `.project`

## Output Structure

```
.project/                          ← Default (configurable)
├── corpus/
│   └── nodes/
│       └── decisions/
│           ├── ADR-INFERRED-001.yml
│           ├── ADR-INFERRED-002.yml
│           └── ...
├── architecture/
│   ├── component-diagram.mmd
│   ├── dependency-graph.dot
│   └── data-flow.mmd
├── security/
│   └── threat-model-inferred.yml
└── reports/
    ├── tech-debt-inferred.md
    └── import-report.md
```

**Never write to `.agentic_sdlc/`** - this directory is for framework files only.

## Decision Confidence Levels

| Level | Score | Status | Action |
|-------|-------|--------|--------|
| **HIGH** | ≥ 0.8 | Auto-accepted | No validation needed |
| **MEDIUM** | 0.5-0.8 | Needs validation | Review recommended |
| **LOW** | < 0.5 | Manual review | Create GitHub issue |

## Threat Severity Levels

| Level | CVSS Score | Action |
|-------|------------|--------|
| **CRITICAL** | 9.0-10.0 | Immediate escalation |
| **HIGH** | 7.0-8.9 | Must fix before release |
| **MEDIUM** | 4.0-6.9 | Fix in sprint |
| **LOW** | 0.1-3.9 | Backlog item |

## Technical Debt Priorities

| Priority | Description | Action |
|----------|-------------|--------|
| **P0** | Security issues, EOL dependencies | Fix immediately |
| **P1** | Reliability issues, major version lag | Fix in sprint |
| **P2** | Code smells, refactoring needed | Schedule work |
| **P3** | Documentation gaps, nice-to-have | Backlog |

## Quality Gate

After import, the `sdlc-import-gate.yml` validates:

- ✅ Feature branch created
- ✅ Overall confidence score ≥ 0.6
- ✅ Minimum 3 ADRs extracted
- ✅ Zero CRITICAL threats
- ✅ Minimum 2 diagrams generated

## Integration

- **Auto-Branch**: Automatically creates feature branch before analysis
- **RAG Corpus**: Inferred ADRs added to knowledge corpus
- **GitHub Issues**: Optional issue creation for P0 debt and HIGH threats (with `--create-issues`)
- **Orchestrator**: Integrated with Phase 0 workflows

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Project validation failed |
| 2 | Analysis error |
| 3 | Quality gate failed |

## See Also

- **Skill**: `.claude/skills/sdlc-import/SKILL.md`
- **Agent**: `.claude/agents/sdlc-importer.md`
- **Config**: `.claude/skills/sdlc-import/config/import_config.yml`
- **Quality Gate**: `.claude/skills/gate-evaluator/gates/sdlc-import-gate.yml`
- **ADR**: `.agentic_sdlc/corpus/nodes/decisions/ADR-022-reverse-engineering-approach.yml`
