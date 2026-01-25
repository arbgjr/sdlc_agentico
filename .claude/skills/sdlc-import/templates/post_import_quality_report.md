# Post-Import Quality Report

**Project**: {{ project_name }}
**Quality Score**: {{ "%.1f"|format(quality_score * 100) }}% {{ status_emoji }} {{ status_text }}
**Correlation ID**: `{{ correlation_id }}`
**Generated**: {{ generated_at }}

---

## Executive Summary

{% if passed %}
✅ **Import Quality: PASSED**

The imported artifacts meet quality standards. Automatic corrections have been applied where needed.
{% else %}
❌ **Import Quality: FAILED**

The imported artifacts have significant quality issues that require review or re-import.
{% endif %}

---

## Corrections Applied

{% if corrections_applied %}
{% if corrections_applied.adr_filtering %}
### 1. ADR Filtering
- **Original ADRs**: {{ corrections_applied.adr_filtering.original_count }}
- **Filtered ADRs**: {{ corrections_applied.adr_filtering.filtered_count }}
- **Removed**: {{ corrections_applied.adr_filtering.removed_adrs|length }} false positives
{% if corrections_applied.adr_filtering.removed_adrs %}
  {% for adr_id in corrections_applied.adr_filtering.removed_adrs[:5] %}
  - `{{ adr_id }}`
  {% endfor %}
  {% if corrections_applied.adr_filtering.removed_adrs|length > 5 %}
  - *(and {{ corrections_applied.adr_filtering.removed_adrs|length - 5 }} more)*
  {% endif %}
{% endif %}
{% endif %}

{% if corrections_applied.tech_debt_regeneration %}
### 2. Tech Debt Report Regeneration
- **Original**: Summary only (no item details)
- **Corrected**: Full report with {{ corrections_applied.tech_debt_regeneration.original_item_count }} items
- **Report**: `{{ corrections_applied.tech_debt_regeneration.report_path }}`
{% endif %}

{% if corrections_applied.diagram_regeneration %}
### 3. Diagram Regeneration
- **Original**: Generic {{ corrections_applied.diagram_regeneration.regenerated_count }} diagram(s)
- **Corrected**: Regenerated with actual architecture
- **Reason**: {{ corrections_applied.diagram_regeneration.reason }}
{% endif %}
{% else %}
✅ **No corrections needed** - All artifacts were generated correctly on first attempt.
{% endif %}

---

## Issues Detected

{% if issues_detected %}
{% for issue in issues_detected %}
### {% if issue.severity == 'critical' %}❌ CRITICAL{% elif issue.severity == 'warning' %}⚠️ WARNING{% else %}ℹ️ INFO{% endif %}: {{ issue.category|upper }}

**Message**: {{ issue.message }}

{% if issue.correction %}
**Correction Applied**: {{ issue.correction }}
{% endif %}

{% if issue.details %}
**Details**:
```
{{ issue.details|tojson(indent=2) }}
```
{% endif %}

---
{% endfor %}
{% else %}
✅ **No issues detected** - All artifacts passed validation.
{% endif %}

---

## Quality Metrics

| Metric | Score | Status |
|--------|-------|--------|
| **ADR Quality** | {{ "%.0f"|format(metrics.adr_quality_score * 100) }}% | {% if metrics.adr_quality_score >= 0.85 %}✅{% elif metrics.adr_quality_score >= 0.70 %}⚠️{% else %}❌{% endif %} |
| **Tech Debt Completeness** | {{ "%.0f"|format(metrics.tech_debt_completeness * 100) }}% | {% if metrics.tech_debt_completeness >= 0.85 %}✅{% elif metrics.tech_debt_completeness >= 0.70 %}⚠️{% else %}❌{% endif %} |
| **Diagram Quality** | {{ "%.0f"|format(metrics.diagram_quality * 100) }}% | {% if metrics.diagram_quality >= 0.85 %}✅{% elif metrics.diagram_quality >= 0.70 %}⚠️{% else %}❌{% endif %} |
| **Artifact Completeness** | {{ "%.0f"|format(metrics.artifact_completeness * 100) }}% | {% if metrics.artifact_completeness >= 0.85 %}✅{% elif metrics.artifact_completeness >= 0.70 %}⚠️{% else %}❌{% endif %} |
| **Overall Score** | {{ "%.0f"|format(quality_score * 100) }}% | {% if quality_score >= 0.85 %}✅{% elif quality_score >= 0.70 %}⚠️{% else %}❌{% endif %} |

---

## Recommendation

{% if quality_score >= 0.85 %}
✅ **Excellent Quality**: Import artifacts are high quality and ready for use.

**What Happened**:
{% if corrections_applied %}
- Automatic corrections were applied successfully
- All quality gates passed after corrections
{% else %}
- All artifacts generated correctly on first attempt
- No corrections needed
{% endif %}

**Next Steps**:
- Review corrected artifacts (if any)
- Accept import and continue with SDLC workflow
{% elif quality_score >= 0.70 %}
⚠️ **Review Required**: Import quality is acceptable but has some issues.

**What Happened**:
{% for issue in issues_detected %}
- {{ "✅" if issue.correction else "⚠️" }} {{ issue.message }}{% if issue.correction %} → **FIXED** ({{ issue.correction }}){% endif %}
{% endfor %}

**Next Steps**:
- Review corrected artifacts
- Accept if corrections are satisfactory
- OR re-run import to regenerate artifacts
{% else %}
❌ **Needs Improvement**: Import quality is below acceptable threshold.

**What Happened**:
{% for issue in issues_detected %}
- {{ "❌" if issue.severity == "critical" else "⚠️" }} {{ issue.message }}
{% endfor %}

**Next Steps**:
- Review issues detected
- Re-run import with different settings
- OR manually fix artifacts
{% endif %}

---

**Generated with SDLC Agêntico by @arbgjr**
