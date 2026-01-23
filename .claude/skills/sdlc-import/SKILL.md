# SKILL: sdlc-import

**Version:** 1.0.0
**Status:** Active
**Category:** Automation
**Phase:** 0 (Preparation)
**Agent:** sdlc-importer

---

## Purpose

Reverse engineer existing codebases (not necessarily legacy - can be modern projects without SDLC artifacts) and automatically generate complete SDLC Agêntico documentation structure.

**Key Capabilities:**
- Detect 10 programming languages and frameworks
- Extract 5-15 architecture decisions with confidence scores
- Generate 3-5 architecture diagrams (Mermaid + DOT)
- Perform STRIDE threat modeling
- Identify 10-50 tech debt items (P0-P3 prioritized)
- Create complete `.agentic_sdlc/` structure
- Auto-create feature branch before analysis

---

## Design Principles

**Hybrid Approach** (per ADR-022):
1. **Pattern Extraction** - Static analysis using regex/AST parsing
2. **LLM Synthesis** - Claude Opus for ambiguous decisions (confidence < 0.5)
3. **Plugin Integration** - claude-plugins-official for production-grade analysis

**Read-Only Analysis:**
- Never modifies source code
- Only creates `.agentic_sdlc/` documentation

**Configuration Over Code:**
- All thresholds in YAML files
- Extensible pattern libraries

---

## Usage

```bash
# Basic usage
/sdlc-import /path/to/project

# With options
/sdlc-import /path/to/project --skip-threat-model --no-llm

# Create GitHub issues for P0 debt
/sdlc-import /path/to/project --create-issues

# Custom branch name
/sdlc-import /path/to/project --branch-name feature/import-my-project
```

**Options:**
- `--skip-threat-model` - Skip STRIDE analysis
- `--skip-tech-debt` - Skip debt detection
- `--no-llm` - Disable LLM synthesis (faster, lower cost)
- `--create-issues` - Create GitHub issues for P0 debt and HIGH threats
- `--branch-name` - Custom branch name (default: auto-generated)

---

## Components

| Script | Purpose |
|--------|---------|
| `project_analyzer.py` | Main orchestrator |
| `language_detector.py` | Language/framework detection (LSP plugins) |
| `decision_extractor.py` | ADR inference engine |
| `architecture_visualizer.py` | Diagram generation (Mermaid/DOT) |
| `threat_modeler.py` | STRIDE analysis (security-guidance plugin) |
| `tech_debt_detector.py` | Tech debt scanner (code-review plugin) |
| `documentation_generator.py` | Output generation |
| `confidence_scorer.py` | Confidence calculation |

---

## Outputs

**Created Files:**
```
.agentic_sdlc/
├── corpus/nodes/decisions/
│   ├── ADR-INFERRED-001.yml
│   ├── ADR-INFERRED-002.yml
│   └── ...
├── security/
│   └── threat-model-inferred.yml
├── architecture/
│   ├── component-diagram.mmd
│   ├── dependency-graph.dot
│   └── data-flow.mmd
└── reports/
    ├── tech-debt-inferred.md
    └── import-report.md
```

---

## Quality Gate

**Gate:** `sdlc-import-gate.yml`

**Validation Checks:**
- Branch created (feature/import-*)
- Overall confidence >= 0.6
- Minimum 3 ADRs extracted
- Zero CRITICAL threats
- Minimum 2 diagrams generated

---

## Integration

**claude-plugins-official Plugins:**
- **LSP Plugins** - Deep language analysis (pyright-lsp, typescript-lsp, jdtls-lsp, csharp-lsp, gopls-lsp, rust-analyzer-lsp)
- **security-guidance** - Vulnerability scanning, STRIDE templates
- **code-review** - Code quality, tech debt detection
- **claude-md-management** - ADR/README generation
- **pr-review-toolkit** - GitHub issue creation

**awesome-copilot Patterns:**
- `reverse-project-analysis.prompt`
- `architecture-blueprint-generator.prompt`
- `language-stack-identifier.prompt`
- `threat-model-generator.prompt`
- `code-gap-audit.prompt`

---

## References

- **ADR:** ADR-022 (Automated Legacy Project Onboarding)
- **Epic:** Issue #52
- **awesome-copilot:** https://github.com/awesome-copilot/awesome-copilot
- **claude-plugins-official:** https://github.com/anthropics/claude-plugins-official

---

## Version History

- **v1.0.0** (2026-01-23) - Initial implementation
