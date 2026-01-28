# SDLC Import Report - {{ framework_version }} - {{ project_name }}

**Analysis ID:** `{{ analysis_id }}`
**Date:** {{ date }}
**Project Path:** `{{ project_path }}`
**Branch:** `{{ branch }}`

---

## Project Overview

- **Primary Language:** {{ language_analysis.primary_language }}
- **Total Files:** {{ scan.total_files }}
- **Total LOC:** {{ scan.total_loc }}
- **Overall Confidence:** {{ confidence.overall }} ({{ confidence.level }})

### Language Distribution

| Language | Percentage | Files | LOC |
|----------|------------|-------|-----|
{% for lang in language_analysis.languages %}
| {{ lang.name }} | {{ lang.percentage }}% | {{ lang.files }} | {{ lang.loc }} |
{% endfor %}

### Detected Frameworks

**Backend:**
{% for framework in language_analysis.frameworks.backend %}
- {{ framework }}
{% endfor %}

**Frontend:**
{% for framework in language_analysis.frameworks.frontend %}
- {{ framework }}
{% endfor %}

**Database:**
{% for db in language_analysis.frameworks.database %}
- {{ db }}
{% endfor %}

**DevOps:**
{% for tool in language_analysis.frameworks.devops %}
- {{ tool }}
{% endfor %}

---

## Architecture Decisions

**Extracted ADRs:** {{ decisions.count }}

**Confidence Distribution:**
- **HIGH (>= 0.8):** {{ decisions.high_confidence }} ADRs
- **MEDIUM (0.5-0.8):** {{ decisions.medium_confidence }} ADRs
- **LOW (< 0.5):** {{ decisions.low_confidence }} ADRs

### High-Confidence Decisions

{% for decision in decisions.high %}
#### {{ decision.id }}: {{ decision.title }}
- **Category:** {{ decision.category }}
- **Confidence:** {{ decision.confidence }}
- **Evidence Count:** {{ decision.evidence_count }}

**Rationale:** {{ decision.rationale }}

---
{% endfor %}

### Medium-Confidence Decisions (Needs Validation)

{% for decision in decisions.medium %}
#### {{ decision.id }}: {{ decision.title }}
- **Category:** {{ decision.category }}
- **Confidence:** {{ decision.confidence }}

⚠️ **Validation recommended** - Review evidence and confirm decision.

---
{% endfor %}

### Low-Confidence Decisions (Manual Review Required)

{% for decision in decisions.low %}
#### {{ decision.id }}: {{ decision.title }}
- **Category:** {{ decision.category }}
- **Confidence:** {{ decision.confidence }}

🔍 **Manual review required** - GitHub issue created.

---
{% endfor %}

---

## Architecture Diagrams

Generated diagrams are available in `.project/architecture/`:

{% for diagram in diagrams %}
- **{{ diagram.name }}** - `{{ diagram.path }}`
  - Type: {{ diagram.type }}
  - Format: {{ diagram.format }}
  - Nodes: {{ diagram.node_count }}
{% endfor %}

---

## Security Analysis (STRIDE)

{% if threats.enabled %}
**Total Threats Identified:** {{ threats.total }}

**Severity Distribution:**
- **CRITICAL:** {{ threats.critical }}
- **HIGH:** {{ threats.high }}
- **MEDIUM:** {{ threats.medium }}
- **LOW:** {{ threats.low }}

**STRIDE Categories:**
| Category | Count | Max Severity |
|----------|-------|--------------|
| Spoofing | {{ threats.spoofing }} | {{ threats.spoofing_max }} |
| Tampering | {{ threats.tampering }} | {{ threats.tampering_max }} |
| Repudiation | {{ threats.repudiation }} | {{ threats.repudiation_max }} |
| Information Disclosure | {{ threats.information_disclosure }} | {{ threats.info_max }} |
| Denial of Service | {{ threats.dos }} | {{ threats.dos_max }} |
| Elevation of Privilege | {{ threats.eop }} | {{ threats.eop_max }} |

{% if threats.escalation_required %}
⚠️ **ESCALATION REQUIRED**
- Reasons: {{ threats.escalation_reasons }}
- See threat model: `.project/security/threat-model-inferred.yml`
{% endif %}

{% else %}
Threat modeling was skipped (use `--skip-threat-model` flag to re-enable).
{% endif %}

---

## Technical Debt

{% if tech_debt.enabled %}
**Total Debt Items:** {{ tech_debt.total }}
**Estimated Total Effort:** {{ tech_debt.total_effort }}h

**Priority Distribution:**
- **P0 (CRITICAL):** {{ tech_debt.p0 }} items ({{ tech_debt.p0_effort }}h)
- **P1 (HIGH):** {{ tech_debt.p1 }} items ({{ tech_debt.p1_effort }}h)
- **P2 (MEDIUM):** {{ tech_debt.p2 }} items ({{ tech_debt.p2_effort }}h)
- **P3 (LOW):** {{ tech_debt.p3 }} items ({{ tech_debt.p3_effort }}h)

**Category Breakdown:**
| Category | Count | Effort |
|----------|-------|--------|
{% for category in tech_debt.categories %}
| {{ category.name }} | {{ category.count }} | {{ category.effort }}h |
{% endfor %}

See full report: `.project/reports/tech-debt-inferred.md`

{% else %}
Tech debt detection was skipped (use `--skip-tech-debt` flag to re-enable).
{% endif %}

---

## Quality Gate Status

{% if quality_gate.passed %}
✅ **PASSED**

All quality checks passed:
{% for check in quality_gate.checks %}
- ✅ {{ check.name }}: {{ check.status }}
{% endfor %}

**Next Steps:**
1. Review generated documentation in `.agentic_sdlc/`
2. Validate medium/low confidence decisions
3. Address P0 tech debt items
4. Merge feature branch to main

{% else %}
❌ **FAILED**

Failed checks:
{% for check in quality_gate.failed_checks %}
- ❌ {{ check.name }}: {{ check.message }}
{% endfor %}

**Remediation:**
{{ quality_gate.remediation }}

{% endif %}

---

## Generated Files

```
.agentic_sdlc/
├── corpus/nodes/decisions/
{% for adr in generated_files.adrs %}
│   ├── {{ adr }}
{% endfor %}
├── security/
│   └── threat-model-inferred.yml
├── architecture/
{% for diagram in generated_files.diagrams %}
│   ├── {{ diagram }}
{% endfor %}
└── reports/
    ├── tech-debt-inferred.md
    └── import-report.md
```

---

## Plugin Usage

**claude-plugins-official:**
{% for plugin in plugins_used %}
- **{{ plugin.name }}** ({{ plugin.version }}) - {{ plugin.purpose }}
{% endfor %}

**awesome-copilot patterns:**
{% for pattern in patterns_used %}
- {{ pattern.name }} - {{ pattern.url }}
{% endfor %}

---

## Next Steps

1. **Review High-Confidence Decisions** - Confirm they are accurate
2. **Validate Medium-Confidence Decisions** - Review evidence and update if needed
3. **Manual Review for Low-Confidence** - Check GitHub issues created
4. **Address P0 Tech Debt** - Critical items requiring immediate action
5. **Review Threat Model** - Address CRITICAL/HIGH threats
6. **Update RAG Corpus** - Ensure inferred decisions are indexed
7. **Merge Feature Branch** - After all validations complete

---

**Generated with SDLC Agêntico by @arbgjr**
**Analysis Engine:** sdlc-import v1.0.0
