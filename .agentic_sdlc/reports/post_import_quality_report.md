# Post-Import Quality Report

**Project**: mice_dolphins
**Quality Score**: 65.0% ❌ NEEDS IMPROVEMENT
**Correlation ID**: `20260125-042656`
**Generated**: 2026-01-25T04:27:07.959306Z

---

## Executive Summary

❌ **Import Quality: FAILED**

The imported artifacts have significant quality issues that require review or re-import.

---

## Corrections Applied

### 1. ADR Filtering
- **Original ADRs**: 6
- **Filtered ADRs**: 2
- **Removed**: 4 false positives
  - `ADR-INFERRED-003`
  - `ADR-INFERRED-001`
  - `ADR-INFERRED-002`
  - `ADR-INFERRED-005`

### 2. Tech Debt Report Regeneration
- **Original**: Summary only (no item details)
- **Corrected**: Full report with 31180 items
- **Report**: `/home/armando_jr/source/repos/arbgjr/mice_dolphins/.agentic_sdlc/reports/tech-debt-inferred.md`

### 3. Diagram Regeneration
- **Original**: Generic 0 diagram(s)
- **Corrected**: Regenerated with actual architecture
- **Reason**: Diagrams were too generic

---

## Issues Detected

### ⚠️ WARNING: ADR_EVIDENCE

**Message**: Removed 4 false positive ADRs


**Details**:
```
{
  "ADR-INFERRED-001": {
    "reason": "suspicious_evidence",
    "suspicious_files": [
      ".claude/skills/sdlc-import/tests/integration/test_gin_integration.py"
    ],
    "suspicious_ratio": 1.0,
    "total_suspicious": 1
  },
  "ADR-INFERRED-002": {
    "reason": "suspicious_evidence",
    "suspicious_files": [
      ".claude/skills/sdlc-import/scripts/validators/adr_evidence_fixer.py"
    ],
    "suspicious_ratio": 1.0,
    "total_suspicious": 1
  },
  "ADR-INFERRED-003": {
    "reason": "suspicious_evidence",
    "suspicious_files": [
      ".claude/skills/sdlc-import/scripts/confidence_scorer.py",
      ".claude/skills/sdlc-import/tests/unit/test_confidence_scorer.py",
      ".claude/skills/sdlc-import/tests/unit/test_decision_extractor.py",
      ".claude/skills/sdlc-import/tests/unit/test_threat_modeler.py"
    ],
    "suspicious_ratio": 1.0,
    "total_suspicious": 4
  },
  "ADR-INFERRED-005": {
    "reason": "suspicious_evidence",
    "suspicious_files": [
      ".claude/skills/sdlc-import/tests/integration/test_django_integration.py"
    ],
    "suspicious_ratio": 1.0,
    "total_suspicious": 1
  }
}
```

---
### ⚠️ WARNING: DIAGRAMS

**Message**: Diagrams were generic templates

**Correction Applied**: Regenerated 0 diagrams


---
### ⚠️ WARNING: COMPLETENESS

**Message**: Missing 1 required artifacts


**Details**:
```
[
  "corpus/nodes/decisions/adr_index.md"
]
```

---

---

## Quality Metrics

| Metric | Score | Status |
|--------|-------|--------|
| **ADR Quality** | 100% | ✅ |
| **Tech Debt Completeness** | 100% | ✅ |
| **Diagram Quality** | 50% | ❌ |
| **Artifact Completeness** | 75% | ⚠️ |
| **Overall Score** | 65% | ❌ |

---

## Recommendation

❌ **Needs Improvement**: Import quality is below acceptable threshold.

**What Happened**:
- ⚠️ Removed 4 false positive ADRs
- ⚠️ Diagrams were generic templates
- ⚠️ Missing 1 required artifacts

**Next Steps**:
- Review issues detected
- Re-run import with different settings
- OR manually fix artifacts

---

**Generated with SDLC Agêntico by @arbgjr**