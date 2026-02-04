# Bug Report: sdlc-import Skill - Incomplete Implementation

**Date:** 2026-02-02
**Reported By:** Armando Jr (via Claude Code analysis)
**Severity:** HIGH
**Skill:** `/sdlc-import` (version 2.0.0)
**Impact:** 50% functionality failure - skill completes with "success" but delivers incomplete results

---

## Summary

The `/sdlc-import` skill's main orchestrator (`project_analyzer.py`) references **missing Python modules**, causing silent failure. The orchestrator agent attempts manual fallback but completes only ~50% of promised functionality.

---

## Missing Modules

The following modules are imported but **DO NOT EXIST** in the skill directory:

```python
# File: .claude/skills/sdlc-import/scripts/project_analyzer.py
# Lines: 44-48

from decision_extractor import DecisionExtractor      # ❌ MISSING
from threat_modeler import ThreatModeler              # ❌ MISSING
from tech_debt_detector import TechDebtDetector       # ❌ MISSING
```

**Location:** `.claude/skills/sdlc-import/scripts/`

**Expected files:**
- `decision_extractor.py` - Extracts ADRs with confidence scoring
- `threat_modeler.py` - STRIDE threat modeling
- `tech_debt_detector.py` - P0-P3 tech debt detection

**Actual files found:**
- ✅ `project_analyzer.py` (main orchestrator - **broken**)
- ✅ `architecture_visualizer.py`
- ✅ `documentation_generator.py`
- ✅ `language_detector.py`
- ✅ `graph_generator.py`
- ✅ `adr_validator.py`
- ✅ `issue_creator.py`
- ❌ `decision_extractor.py` - **MISSING**
- ❌ `threat_modeler.py` - **MISSING**
- ❌ `tech_debt_detector.py` - **MISSING**

---

## Reproduction Steps

1. Navigate to any project with existing ADRs (e.g., Autoritas GRC Platform)
2. Execute: `/sdlc-import /path/to/project`
3. Observe:
   - Skill reports "success"
   - Only 52% of ADRs converted (11 of 21)
   - No confidence scores calculated
   - Missing DOT diagram format
   - Reports show incomplete data

---

## Expected Behavior

Per skill README.md (lines 20-24):

```
3. **Extracts decisions** - 5-15 ADRs with confidence scores
4. **Generates diagrams** - 3-5 architecture diagrams (Mermaid + DOT)
```

**Should produce:**
- ✅ ALL ADRs converted (100%)
- ✅ Confidence scores for each ADR (0.0-1.0)
- ✅ Both Mermaid (.mmd) AND DOT (.dot) diagrams
- ✅ Complete index.yml referencing all ADRs

---

## Actual Behavior

**What the orchestrator agent does:**
1. Attempts to import missing modules → **fails silently**
2. Falls back to manual implementation using LLM
3. Completes ~50% of work:
   - ✅ Creates directory structure
   - ⚠️ Converts only 52% of ADRs (11/21)
   - ❌ No confidence scores
   - ⚠️ Only Mermaid diagrams (no DOT)
   - ✅ Threat model (complete)
   - ✅ Tech debt (complete)
4. Returns "success" message with **misleading metrics**

**Example from Autoritas import:**

```
### Files Generated (22 files)

**Architecture Decision Records (12 files):**
- adr-001.yml through adr-019.yml
```

**Reality:** Only 11 ADRs converted, not 12. Missing: 008, 009, 012-016, 018, 020, 021.

---

## Impact Analysis

### Severity: HIGH

**Functional Impact:**
- 47% of architectural decisions NOT documented
- Zero confidence scoring capability
- Incomplete visualization options (no DOT)
- Misleading success reporting

**User Impact:**
- Users trust "success" message
- Incomplete documentation propagates to downstream processes
- Manual review required to discover gaps
- Critical decisions (testing, CI/CD, resilience) undocumented

**Example Missing ADRs (Autoritas case):**
- ❌ 008-event-driven-architecture.md (CRITICAL)
- ❌ 009-error-handling-resilience.md (CRITICAL)
- ❌ 012-testing-strategy.md (CRITICAL - referenced in tech debt!)
- ❌ 013-cicd-strategy.md
- ❌ 014-background-jobs.md
- ❌ 020-release-deployment-strategy.md

---

## Root Cause Analysis

### Why Missing Modules?

**Hypothesis 1: Incomplete Migration**
- Skill migrated from older version
- Some modules left in old location
- Import paths not updated

**Hypothesis 2: Work-in-Progress**
- v2.0.0 released prematurely
- Core modules planned but not implemented
- README docs ahead of implementation

**Hypothesis 3: Dependency Issue**
- Modules exist elsewhere (different repo?)
- PYTHONPATH misconfiguration
- Relative import issue

### Why Silent Failure?

The orchestrator agent:
- Does NOT raise exceptions on import failure
- Does NOT log warnings about missing modules
- Attempts "best effort" manual implementation
- Reports success even with partial completion

**This is dangerous** - users assume 100% when it's 50%.

---

## Recommended Fixes

### Immediate (P0)

1. **Add Missing Modules**
   - Implement `decision_extractor.py`
   - Implement `threat_modeler.py`
   - Implement `tech_debt_detector.py`

   OR

   - Refactor `project_analyzer.py` to not import them
   - Move functionality to existing modules

2. **Add Error Handling**
   ```python
   try:
       from decision_extractor import DecisionExtractor
   except ImportError as e:
       logger.error(f"Critical module missing: {e}")
       raise ImportError("sdlc-import skill is incomplete - missing decision_extractor")
   ```

3. **Fix Success Reporting**
   - Add validation step before "success"
   - Check: ADR count matches source files
   - Check: Confidence scores present
   - Check: Both diagram formats exist

### Short-term (P1)

4. **Add Quality Gate**
   - Create `sdlc-import-gate.yml` validator
   - Enforce minimum 90% ADR conversion rate
   - Require confidence scores on all ADRs
   - Verify diagram count (minimum 2 formats)

5. **Add Debug Mode**
   ```bash
   /sdlc-import /path/to/project --debug
   ```
   - Show which modules loaded successfully
   - Log import errors
   - Report step-by-step progress

6. **Update README.md**
   - Mark missing features as "planned"
   - Document current limitations
   - Add "Known Issues" section

### Long-term (P2)

7. **Integration Tests**
   - Test against known projects (Autoritas, TriSky)
   - Verify 100% ADR conversion
   - Validate confidence score calculation
   - Check diagram generation (both formats)

8. **Metrics Dashboard**
   - Track success rate per project
   - Measure coverage (ADRs found vs converted)
   - Report confidence score distribution

---

## Workaround (Current)

Until fixed, users should:

1. **Manual Verification**
   ```bash
   # Count source ADRs
   find ./docs/adr -name "*.md" | wc -l

   # Count converted ADRs
   find .project/corpus/nodes/decisions -name "adr-*.yml" | wc -l

   # Compare - should match!
   ```

2. **Manual Completion**
   - Convert missing ADRs using text editor
   - Add confidence scores manually
   - Generate DOT diagrams with GraphViz

3. **Use Component Scripts Directly**
   ```bash
   # If individual modules work
   python .claude/skills/sdlc-import/scripts/architecture_visualizer.py
   python .claude/skills/sdlc-import/scripts/adr_validator.py
   ```

---

## Test Case

**Project:** Autoritas GRC Platform
**Path:** `/home/armando_jr/source/repos/tripla/autoritas`

**Source ADRs:** 21 markdown files in `autoritas-common/docs/adr/`

**Expected output:**
- 21 YAML ADRs in `.project/corpus/nodes/decisions/`
- Each with `confidence_score` field (0.8-1.0 for documented ADRs)
- 5-6 diagrams (Mermaid + DOT)
- Complete index.yml

**Actual output:**
- 11 YAML ADRs (52%)
- No confidence scores
- 5 Mermaid diagrams only (no DOT)
- Incomplete index.yml

**Reproduction:**
```bash
cd /home/armando_jr/source/repos/tripla/autoritas
/sdlc-import .
# Observe partial completion
```

---

## Related Files

- Skill: `.claude/skills/sdlc-import/`
- Main script: `.claude/skills/sdlc-import/scripts/project_analyzer.py`
- README: `.claude/skills/sdlc-import/README.md`
- Config: `.claude/skills/sdlc-import/config/import_config.yml`

---

## Priority Assessment

| Criterion | Score | Reasoning |
|-----------|-------|-----------|
| **Severity** | HIGH | 50% functionality loss |
| **Frequency** | ALWAYS | Happens on every execution |
| **User Impact** | HIGH | Silent failure misleads users |
| **Data Loss Risk** | MEDIUM | Architectural decisions undocumented |
| **Workaround Available** | YES | Manual completion possible |

**Overall Priority:** **P0 (Critical)** - Fix before next release

---

## Additional Context

**Environment:**
- OS: Linux (WSL2)
- Python: 3.x
- Claude Code: Latest
- Project: Monorepo (Tripla Autoritas)

**Discovered by:** Analyzing SDLC import results and noticing gaps between promised vs delivered artifacts.

**Reporter confidence:** 100% - verified by examining:
- Source ADR count: `21 .md files`
- Output ADR count: `11 .yml files`
- Missing modules: `ModuleNotFoundError` when running script directly

---

**End of Bug Report**
