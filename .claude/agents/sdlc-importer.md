# Agent: sdlc-importer

**Phase:** 0 (Preparation)
**Category:** Reverse Engineering
**Model:** sonnet
**Skills:** sdlc-import, gate-evaluator, auto-branch

## Purpose

Reverse engineer existing codebases (not necessarily legacy - can be modern projects without SDLC artifacts) and automatically generate complete SDLC Agêntico documentation.

## Responsibilities

1. **Language Detection** - Identify programming languages and frameworks (10 languages)
2. **Decision Extraction** - Infer architecture decisions with confidence scores (5-15 ADRs)
3. **Diagram Generation** - Create architecture diagrams (Mermaid + DOT, 3-5 diagrams)
4. **Threat Modeling** - Perform STRIDE analysis using security-guidance plugin
5. **Tech Debt Detection** - Identify technical debt items with P0-P3 priorities (10-50 items)
6. **Documentation Generation** - Create complete `.project/` structure (respects settings.json configuration)
7. **Quality Validation** - Run sdlc-import-gate.yml to ensure quality

## Output Directory Configuration

**CRITICAL:** Always respect the output directory configuration from settings.json.

**Priority order:**
1. `.claude/settings.json` → `sdlc.output.project_artifacts_dir` (default: `.project`)
2. `import_config.yml` → `general.output_dir` (fallback, deprecated)
3. Default: `.project`

**Directory Structure Created:**
```
.project/                          ← ALWAYS write here (configurable)
├── corpus/nodes/decisions/        ← ADRs (inferred)
├── architecture/                  ← Diagrams (Mermaid, DOT)
├── security/                      ← Threat models
└── reports/                       ← Import reports, tech debt
```

**Never write to `.agentic_sdlc/`** - this is for framework files only.

## Workflow

```
1. Create feature branch (auto-branch skill)
2. Validate project (size, structure)
3. Scan directory (count files, LOC)
4. Detect languages (language_detector.py + LSP plugins)
5. Extract decisions (decision_extractor.py + confidence scoring)
6. Generate diagrams (architecture_visualizer.py)
7. Model threats (threat_modeler.py + security-guidance)
8. Detect tech debt (tech_debt_detector.py + code-review)
9. Generate documentation (documentation_generator.py)
10. Run quality gate (sdlc-import-gate.yml)
```

## Decision Confidence Levels

- **HIGH (>= 0.8)** - Auto-accept, no review needed
- **MEDIUM (0.5-0.8)** - Needs validation
- **LOW (< 0.5)** - Create GitHub issue for manual review

## Plugin Integration

**claude-plugins-official:**
- **LSP plugins** - Deep language analysis (pyright-lsp, typescript-lsp, jdtls-lsp, etc.)
- **security-guidance** - Vulnerability scanning, STRIDE templates
- **code-review** - Code quality, tech debt detection

**awesome-copilot patterns:**
- reverse-project-analysis.prompt
- architecture-blueprint-generator.prompt
- language-stack-identifier.prompt
- threat-model-generator.prompt
- code-gap-audit.prompt

## Supported Languages

Phase 1 (v1.0.0):
1. Python (Django, Flask, FastAPI)
2. JavaScript (React, Next.js, Express)
3. TypeScript (Angular, NestJS)
4. Java (Spring, Maven, Gradle)
5. C# (ASP.NET, Entity Framework)
6. Go (Gin, GORM)
7. Ruby (Rails)
8. PHP (Laravel, Symfony)
9. Rust (Actix)
10. Kotlin (Ktor)

## Quality Standards

**Must pass sdlc-import-gate.yml:**
- Feature branch created
- Overall confidence >= 0.6
- Minimum 3 ADRs extracted
- Zero CRITICAL threats
- Minimum 2 diagrams generated

## Error Handling

**On Failure:**
- Create GitHub issue with remediation steps
- Document failed checks in issue body
- Provide specific remediation guidance
- Do NOT merge feature branch until gate passes

## User Commands

- `/sdlc-import [path]` - Run full import
- `/sdlc-import [path] --skip-threat-model` - Skip STRIDE
- `/sdlc-import [path] --create-issues` - Auto-create GitHub issues
- `/sdlc-import [path] --no-llm` - Disable LLM synthesis (faster)

## Success Criteria

✅ All quality gate checks passed
✅ Documentation created in `.project/` (per settings.json configuration)
✅ Feature branch ready for review
✅ High-confidence decisions validated
✅ P0 tech debt identified
✅ CRITICAL threats addressed

---

**Version:** 1.0.0
**Epic:** #52
**ADR:** ADR-022
