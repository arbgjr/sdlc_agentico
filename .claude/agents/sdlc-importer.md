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
8. **Quality Assurance** - Ensures that all stages of the Reverse Engineering process have been executed exactly as they were supposed to be.

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

## Mandatory Artifacts

**CRITICAL:** These files MUST be created. If ANY is missing, the import is INCOMPLETE.

| Artifact | Path | Validator | Fallback if Missing |
|----------|------|-----------|---------------------|
| **Knowledge Graph** | `corpus/graph.json` | graph_generator.py | FAIL - graph is mandatory (v1.4.0+) |
| **ADR Index** | `references/adr_index.yml` | documentation_generator.py | FAIL - index is mandatory (v2.1.15+) |
| **Tech Debt Report** | `reports/tech-debt-inferred.md` | documentation_generator.py | Create empty report with note |
| **Import Report** | `reports/import-report.md` | documentation_generator.py | FAIL - import report is mandatory |
| **Threat Model** | `security/threat-model-inferred.yml` | threat_modeler.py | Create basic model or note if skipped |

**Validation Command (run after import):**
```bash
python3 .claude/skills/sdlc-import/scripts/validate_artifacts.py --output-dir .project
```

## Workflow

```
1. Create feature branch (auto-branch skill)
2. Validate project (size, structure)
3. Scan directory (count files, LOC)
4. Detect languages (language_detector.py + LSP plugins)
5. Extract decisions (decision_extractor.py + confidence scoring)
6. RECONCILE ADRs (adr_validator.py.reconcile_adrs() for existing ADRs)
7. Generate diagrams (architecture_visualizer.py)
8. Model threats (threat_modeler.py + security-guidance)
9. Detect tech debt (tech_debt_detector.py + code-review)
10. GENERATE GRAPH (graph_generator.py - MANDATORY)
11. Generate documentation (documentation_generator.py - generates ALL reports)
12. VALIDATE ARTIFACTS (ensure all mandatory files exist)
13. Run quality gate (sdlc-import-gate.yml)
```

## Detailed Workflow Steps

### Step 5: Extract Decisions

**DO THIS:**
```python
# In project_analyzer.py:
from decision_extractor import DecisionExtractor
extractor = DecisionExtractor(config)
inferred_adrs = extractor.infer_decisions(project_path, languages)
```

**DON'T CREATE:** Custom scripts for ADR extraction.

---

### Step 6: Reconcile Existing ADRs (NEW - v2.1.7+)

**IF** project has existing ADRs (docs/adr/, decisions/, etc.):

**DO THIS:**
```python
# In project_analyzer.py:
from adr_validator import ADRValidator
validator = ADRValidator(config)

# 1. Detect existing ADRs
existing_adrs = validator.detect_existing_adrs(project_path)

# 2. Reconcile with inferred ADRs
reconciliation = validator.reconcile_adrs(
    existing_adrs=existing_adrs,
    inferred_adrs=inferred_adrs,
    similarity_threshold=0.8
)

# 3. Store reconciliation result
results['adr_reconciliation'] = {
    'duplicate': reconciliation.duplicate,
    'enrich': reconciliation.enrich,
    'new': reconciliation.new,
    'index': reconciliation.index,
    'total_existing': len(existing_adrs),
    'total_inferred': len(inferred_adrs)
}
```

**DON'T CREATE:** Custom convert_adrs.py script.

**VALIDATE:** Ensure `results['adr_reconciliation']` is populated before documentation generation.

---

### Step 8: Detect Tech Debt

**DO THIS:**
```python
# In project_analyzer.py:
from tech_debt_detector import TechDebtDetector
detector = TechDebtDetector(config)
tech_debt = detector.scan(project_path)

# Store for documentation generation
results['tech_debt'] = tech_debt
```

**DON'T CREATE:** Custom analyze_tech_debt.py script.

**VALIDATE:** Check `tech_debt['total'] > 0` (zero items is suspicious).

---

### Step 10: Generate Knowledge Graph (MANDATORY)

**DO THIS:**
```python
# In project_analyzer.py:
from graph_generator import GraphGenerator
generator = GraphGenerator(config)

# Generate graph
graph = generator.generate(
    corpus_dir=output_dir / "corpus",
    adrs=all_adrs  # imported + inferred
)

# CRITICAL: Ensure parent directory exists
graph_file = output_dir / "corpus/graph.json"
graph_file.parent.mkdir(parents=True, exist_ok=True)

# Write graph
import json
with open(graph_file, 'w') as f:
    json.dump(graph, f, indent=2)

logger.info(f"Knowledge graph generated: {graph_file}")
```

**VALIDATE:** After execution:
```python
assert (output_dir / "corpus/graph.json").exists(), "graph.json MUST exist"
```

**DON'T:** Skip graph generation or ignore errors silently.

---

### Step 11: Generate Documentation (ALL Reports)

**DO THIS:**
```python
# In project_analyzer.py:
from documentation_generator import DocumentationGenerator
doc_gen = DocumentationGenerator(output_dir, config)

# Generate ALL reports using Jinja2 templates
reports = doc_gen.generate_all(results)

# Reports generated:
# - reports/import-report.md (import summary)
# - reports/tech-debt-inferred.md (tech debt via Jinja2)
# - references/adr_index.yml (reconciliation index)
# - architecture/*.mmd (diagrams)
# - security/threat-model-inferred.yml
```

**VALIDATE:** After execution:
```python
assert (output_dir / "reports/import-report.md").exists()
assert (output_dir / "reports/tech-debt-inferred.md").exists()
assert (output_dir / "references/adr_index.yml").exists()
```

**DON'T:** Create custom scripts to generate reports.

---

### Step 12: Validate Mandatory Artifacts

**DO THIS (before quality gate):**
```python
# In project_analyzer.py (final validation):
mandatory_artifacts = [
    output_dir / "corpus/graph.json",
    output_dir / "references/adr_index.yml",
    output_dir / "reports/import-report.md",
    output_dir / "reports/tech-debt-inferred.md",
]

missing = [str(f) for f in mandatory_artifacts if not f.exists()]

if missing:
    logger.error(f"Missing mandatory artifacts: {missing}")
    raise ValueError(f"Import INCOMPLETE. Missing: {missing}")
else:
    logger.info("All mandatory artifacts validated ✅")
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

## Error Handling and Recovery

### Graph Generation Failure

**Symptom:** `graph.json` not created

**Diagnosis:**
```python
# Check logs for:
logger.error("Failed to generate graph: ...")
```

**Recovery:**
1. Check if graph_generator.py was invoked
2. Verify parent directory exists: `output_dir / "corpus"`
3. Check for exceptions in graph generation
4. Re-run ONLY graph generation:
   ```python
   from graph_generator import GraphGenerator
   generator = GraphGenerator(config)
   graph = generator.generate(corpus_dir, adrs)
   ```

---

### ADR Index Not Generated

**Symptom:** `adr_index.yml` missing from `references/`

**Diagnosis:**
```python
# Check if adr_reconciliation was populated:
if 'adr_reconciliation' not in results:
    logger.error("adr_reconciliation missing from results!")
```

**Recovery:**
1. Ensure `results['adr_reconciliation']` is populated in Step 6
2. Check reconcile_adrs() was called
3. Re-run documentation generation with reconciliation data

---

### Tech Debt Report Empty or Missing

**Symptom:** `tech-debt-inferred.md` missing or shows 0 items

**Diagnosis:**
```python
# Check if tech_debt was populated:
if results.get('tech_debt', {}).get('total', 0) == 0:
    logger.warning("Tech debt scan returned 0 items - suspicious!")
```

**Recovery:**
1. Verify tech_debt_detector.py was invoked
2. Check if project excludes were too broad
3. Re-run tech debt detection:
   ```python
   from tech_debt_detector import TechDebtDetector
   detector = TechDebtDetector(config)
   results['tech_debt'] = detector.scan(project_path)
   ```

---

### Script Creation Detected

**Symptom:** `.project/scripts/*.py` files created

**Root Cause:** Agent instructions were unclear, LLM created custom scripts

**Recovery:**
1. DELETE `.project/scripts/` directory
2. Verify framework scripts were used correctly
3. Re-run import following Detailed Workflow Steps
4. Report to framework maintainers (this indicates agent instruction gap)

---

### General Error Handling

**On ANY Failure:**
- DO NOT create custom scripts to "fix" problems
- DO use framework scripts (tech_debt_detector.py, adr_validator.py, etc.)
- DO log errors with context
- DO raise exceptions (don't fail silently)
- Create GitHub issue with:
  - Error message and stack trace
  - Steps to reproduce
  - Remediation guidance
  - Link to relevant framework script
- Do NOT merge feature branch until ALL mandatory artifacts exist and quality gate passes

## User Commands

- `/sdlc-import [path]` - Run full import
- `/sdlc-import [path] --skip-threat-model` - Skip STRIDE
- `/sdlc-import [path] --create-issues` - Auto-create GitHub issues
- `/sdlc-import [path] --no-llm` - Disable LLM synthesis (faster)

## Success Criteria (Final Checklist)

**Before marking import complete, verify ALL items:**

### Mandatory Artifacts Created

- [ ] `corpus/graph.json` exists and has valid JSON
- [ ] `references/adr_index.yml` exists with reconciliation data
- [ ] `reports/import-report.md` exists with complete sections
- [ ] `reports/tech-debt-inferred.md` exists (even if 0 items, must have report)
- [ ] `security/threat-model-inferred.yml` exists or has skip reason documented

### Quality Gate Validation

- [ ] All quality gate checks passed (sdlc-import-gate.yml)
- [ ] Overall confidence >= 0.6
- [ ] Minimum 3 ADRs extracted (imported OR inferred)
- [ ] Zero CRITICAL threats unaddressed
- [ ] Minimum 2 diagrams generated

### Data Quality Validation

- [ ] Knowledge graph has nodes and edges (not empty)
- [ ] ADR index shows reconciliation summary (duplicates/enrichments/new)
- [ ] Tech debt report shows > 0 items OR explains why 0 is correct
- [ ] Import report includes reconciliation section (v2.2.0 M2)
- [ ] All timestamps are real UTC (not rounded to :00:00 or 00:00:00)

### Code Quality Validation

- [ ] NO custom scripts created in `.project/scripts/`
- [ ] Framework scripts used correctly (tech_debt_detector.py, adr_validator.py, etc.)
- [ ] No hardcoded paths in generated files
- [ ] All file paths use output_dir from settings.json

### Repository State

- [ ] Feature branch created and ready for review
- [ ] Branch pushed to remote (if --auto-push enabled)
- [ ] No uncommitted changes in framework files
- [ ] Documentation created in correct output directory (settings.json)

### Final Validation Command

```bash
# Run this before marking complete:
python3 .claude/skills/sdlc-import/scripts/validate_import.py \
  --output-dir .project \
  --strict

# Expected output:
# ✅ All mandatory artifacts exist
# ✅ All artifacts have valid structure
# ✅ Quality gate passed
# ✅ Import COMPLETE
```

---

**Version:** 1.0.0
**Epic:** #52
**ADR:** ADR-022
