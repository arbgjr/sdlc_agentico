#!/usr/bin/env python3
"""
Documentation Generator - Generate SDLC documentation
Creates ADRs, threat models, tech debt reports, and import summary.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class DocumentationGenerator:
    """Generate SDLC documentation"""

    def __init__(self, config: Dict):
        self.config = config
        # BUG FIX #2: Use absolute path (project_path + output_dir)
        project_path = Path(config['project_path'])
        self.output_dir = project_path / config['general']['output_dir']
        self.templates_dir = Path(__file__).parent.parent / "templates"

        # FIX v2.2.4: Load framework version dynamically
        self.framework_version = self._load_framework_version()

        # Configure Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _load_framework_version(self) -> str:
        """
        FIX v2.2.4: Load SDLC framework version from VERSION file.

        Returns:
            Version string (e.g., "v2.2.4")
        """
        try:
            # Path: scripts/ (parent) -> sdlc-import/ (parent.parent) -> skills/ (parent³) -> .claude/ (parent⁴)
            version_file = Path(__file__).resolve().parent.parent.parent.parent / "VERSION"
            if not version_file.exists():
                logger.warning(f"VERSION file not found at {version_file.resolve()}")
                return "v2.2.4"  # Fallback to current version

            version_data = yaml.safe_load(version_file.read_text())
            version = version_data.get('version', 'v2.2.4')

            # Ensure version has 'v' prefix for consistency
            if not version.startswith('v'):
                version = f'v{version}'

            logger.info(f"Loaded framework version: {version}")
            return version
        except Exception as e:
            logger.error(f"Failed to load version: {e}")
            return "v2.2.4"  # Safe fallback

    def generate(self, analysis_results: Dict) -> Dict:
        """Generate all documentation"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FIX #7: Index original ADRs in references/
        project_path = Path(analysis_results.get('project_path', '.'))
        original_adrs = self._index_original_adrs(project_path)

        # NEW (v2.1.7): Generate ADR index for reconciliation
        # FIX BUG C1 (v2.1.15): Always generate adr_index.yml even if reconciliation is empty
        reconciliation_data = analysis_results.get('adr_reconciliation', {})
        adr_index = self._generate_adr_index(reconciliation_data)

        generated_files = {
            "adrs": self._generate_adrs(analysis_results.get('decisions', {})),
            "threat_model": self._generate_threat_model(analysis_results.get('threats', {})),
            "tech_debt_report": self._generate_tech_debt_report(analysis_results.get('tech_debt', {})),
            "import_report": self._generate_import_report(analysis_results),
            "original_adrs": original_adrs,  # FIX #7: Track original ADRs
            "adr_index": adr_index  # NEW (v2.1.7): ADR reconciliation index
        }

        logger.info("Documentation generation complete")
        return generated_files

    def _generate_adrs(self, decisions: Dict) -> List[str]:
        """Generate ADR files with YAML validation"""
        adrs = []
        adr_dir = self.output_dir / "corpus/nodes/decisions"
        adr_dir.mkdir(parents=True, exist_ok=True)

        for decision in decisions.get('decisions', []):
            # FIX v2.2.4: Remove alternatives_considered field (causes YAML issues)
            # This field generates nested lists which are invalid YAML
            if 'alternatives_considered' in decision:
                logger.warning(
                    f"Removing alternatives_considered from {decision.get('id')} "
                    "to prevent YAML parsing errors"
                )
                del decision['alternatives_considered']

            adr_file = adr_dir / f"{decision['id']}.yml"
            # BUG FIX #3: Improve YAML quoting for special characters
            # FIX v2.1.13: Remove default_style='"' which quoted keys incorrectly
            adr_content = yaml.dump(
                decision,
                default_flow_style=False,
                sort_keys=False,           # Preserve original order
                allow_unicode=True,        # Support UTF-8
                # default_style removed - let YAML choose proper quoting
                explicit_start=True,       # Add --- at start
                width=float("inf")         # Avoid line wrapping
            )

            # FIX v2.2.4: Validate generated YAML before writing
            try:
                yaml.safe_load(adr_content)
                logger.debug(f"YAML validation passed for {decision.get('id')}")
            except yaml.YAMLError as e:
                logger.error(f"YAML validation FAILED for {decision.get('id')}: {e}")
                logger.error(f"Content preview:\n{adr_content[:500]}")
                raise ValueError(f"Generated invalid YAML for {decision.get('id')}: {e}")

            adr_file.write_text(adr_content)
            adrs.append(str(adr_file))

        return adrs

    def _generate_adr_index(self, reconciliation: Dict) -> str:
        """
        NEW (v2.1.7): Generate ADR index for reconciliation.

        Creates adr_index.yml that cross-references:
        - Original ADRs (Markdown)
        - Inferred ADRs (YAML)
        - Migration/enrichment status

        Args:
            reconciliation: Reconciliation results from ADRValidator
                            Can be empty dict or {"status": "no_existing_adrs"}

        Returns:
            Path to generated adr_index.yml
        """
        index_file = self.output_dir / "references" / "adr_index.yml"
        index_file.parent.mkdir(parents=True, exist_ok=True)

        # FIX BUG C1 (v2.1.15): Handle empty reconciliation or no existing ADRs
        # Build index entries
        index_entries = []

        # Add entries from reconciliation index
        for adr_id, metadata in reconciliation.get('index', {}).items():
            entry = {
                'id': adr_id,
                'original': metadata.get('original'),
                'format': metadata.get('format'),
                'migrated_to': None,  # Will be populated if migrated
                'status': metadata.get('status'),
                'similarity': metadata.get('similarity')
            }

            # If status is reconciled, set migrated_to path (relative to output_dir)
            if metadata.get('status') == 'reconciled':
                # Use configured output_dir instead of hardcoded ".project"
                output_dir_name = Path(self.config['general']['output_dir']).name
                entry['migrated_to'] = f"{output_dir_name}/corpus/nodes/decisions/{adr_id}.yml"

            index_entries.append(entry)

        # Add duplicates (skipped ADRs)
        for duplicate in reconciliation.get('duplicate', []):
            existing = duplicate.get('existing', {})
            inferred = duplicate.get('inferred', {})
            index_entries.append({
                'id': inferred.get('id'),
                'original': existing.get('path'),
                'format': existing.get('format'),
                'migrated_to': None,  # Not migrated (already exists)
                'status': 'skipped_duplicate',
                'similarity': duplicate.get('similarity')
            })

        # Add enrichment candidates
        for enrich in reconciliation.get('enrich', []):
            existing = enrich.get('existing', {})
            inferred = enrich.get('inferred', {})
            # Use configured output_dir instead of hardcoded ".project"
            output_dir_name = Path(self.config['general']['output_dir']).name
            index_entries.append({
                'id': inferred.get('id'),
                'original': existing.get('path'),
                'format': existing.get('format'),
                'migrated_to': f"{output_dir_name}/corpus/nodes/decisions/{inferred.get('id')}.yml",
                'status': 'enriched',
                'similarity': enrich.get('similarity'),
                'enrichment_note': 'Original ADR enriched with automated analysis'
            })

        # Create full index structure
        # FIX BUG C1 (v2.1.15): Add status field for tracking
        index_data = {
            'adr_index': index_entries,
            'summary': {
                'total_original': reconciliation.get('total_existing', 0),
                'total_inferred': reconciliation.get('total_inferred', 0),
                'duplicates_skipped': len(reconciliation.get('duplicate', [])),
                'enriched': len(reconciliation.get('enrich', [])),
                'new_generated': len(reconciliation.get('new', [])),
                'status': reconciliation.get('status', 'reconciled')  # NEW: Track reconciliation status
            },
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }

        # FIX BUG C1 (v2.1.15): Log reconciliation status for debugging
        logger.info(f"Generating ADR index with {len(index_entries)} entries (status: {reconciliation.get('status', 'reconciled')})")

        # Write YAML
        index_content = yaml.dump(
            index_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            explicit_start=True
        )
        index_file.write_text(index_content)

        logger.info(f"ADR index generated: {index_file}")
        return str(index_file)

    def _generate_threat_model(self, threats: Dict) -> str:
        """Generate threat model file"""
        threat_file = self.output_dir / "security/threat-model-inferred.yml"
        threat_file.parent.mkdir(parents=True, exist_ok=True)
        threat_file.write_text(yaml.dump(threats, default_flow_style=False))
        return str(threat_file)

    def _generate_tech_debt_report(self, tech_debt: Dict) -> str:
        """Generate detailed tech debt report using Jinja2 template"""
        report_file = self.output_dir / "reports/tech-debt-inferred.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # Load template
        template = self.jinja_env.get_template('tech_debt_report.md')

        # Extract items by priority
        debt_items = tech_debt.get('tech_debt', [])
        p0_items = [item for item in debt_items if item.get('priority') == 'P0']
        p1_items = [item for item in debt_items if item.get('priority') == 'P1']
        p2_items = [item for item in debt_items if item.get('priority') == 'P2']
        p3_items = [item for item in debt_items if item.get('priority') == 'P3']

        # Calculate effort by priority
        p0_effort = sum(item.get('effort_estimate', 0) for item in p0_items)
        p1_effort = sum(item.get('effort_estimate', 0) for item in p1_items)
        p2_effort = sum(item.get('effort_estimate', 0) for item in p2_items)
        p3_effort = sum(item.get('effort_estimate', 0) for item in p3_items)

        # Group by category
        categories_dict = {}
        for item in debt_items:
            cat = item.get('category', 'uncategorized')
            if cat not in categories_dict:
                categories_dict[cat] = {'count': 0, 'effort': 0}
            categories_dict[cat]['count'] += 1
            categories_dict[cat]['effort'] += item.get('effort_estimate', 0)

        categories = [
            {'name': name, 'count': data['count'], 'effort': data['effort']}
            for name, data in sorted(categories_dict.items())
        ]

        # Prepare context
        context = {
            'project_name': self.config.get('project_name', 'Unknown'),
            'analysis_id': self.config.get('analysis_id', 'unknown'),
            'date': datetime.utcnow().isoformat() + 'Z',
            'project_path': self.config.get('project_path', '.'),
            'summary': {
                'total': len(debt_items),
                'total_effort': sum(item.get('effort_estimate', 0) for item in debt_items),
                'p0': len(p0_items),
                'p1': len(p1_items),
                'p2': len(p2_items),
                'p3': len(p3_items),
                'p0_effort': p0_effort,
                'p1_effort': p1_effort,
                'p2_effort': p2_effort,
                'p3_effort': p3_effort
            },
            'p0_items': p0_items,
            'p1_items': p1_items,
            'p2_items': p2_items,
            'p3_items': p3_items,
            'categories': categories,
            'recommendations': {
                'immediate': 'Address all P0 items immediately',
                'short_term': 'Plan P1 items for next sprint',
                'medium_term': 'Schedule P2 items for next quarter',
                'backlog': 'Track P3 items in backlog'
            },
            'github_issues': []
        }

        # Render template
        content = template.render(**context)
        report_file.write_text(content)

        logger.info(
            "Tech debt report generated",
            extra={
                'total_items': len(debt_items),
                'p0': len(p0_items),
                'p1': len(p1_items),
                'p2': len(p2_items),
                'p3': len(p3_items)
            }
        )

        return str(report_file)

    def _generate_import_report(self, analysis_results: Dict) -> str:
        """Generate import summary report"""
        report_file = self.output_dir / "reports/import-report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # FIX v2.2.4: Add framework version to report header
        content = f"""# SDLC Import Report - {self.framework_version}

**Analysis ID:** {analysis_results.get('analysis_id', 'unknown')}
**Date:** {datetime.utcnow().isoformat()}Z

## Summary

- **Primary Language:** {analysis_results.get('language_analysis', {}).get('primary_language', 'unknown')}
- **Decisions Extracted:** {analysis_results.get('decisions', {}).get('count', 0)}
- **Threats Identified:** {analysis_results.get('threats', {}).get('total', 0)}
- **Tech Debt Items:** {analysis_results.get('tech_debt', {}).get('total', 0)}
"""

        # FIX L2 (v2.2.0): Add detailed execution metrics section
        if 'execution_metrics' in analysis_results:
            metrics = analysis_results['execution_metrics']
            timing = metrics.get('timing', {})
            quality = metrics.get('analysis_quality', {})

            content += f"""
## ⏱️ Execution Metrics

### Timing Breakdown

Total execution time: **{timing.get('total', 0):.2f}s**

| Phase | Time |
|-------|------|
| Branch Creation | {timing.get('branch_creation', 0):.2f}s |
| Project Validation | {timing.get('validation', 0):.2f}s |
| Directory Scan | {timing.get('directory_scan', 0):.2f}s |
| Language Detection | {timing.get('language_detection', 0):.2f}s |
| Decision Extraction | {timing.get('decision_extraction', 0):.2f}s |
| Diagram Generation | {timing.get('diagram_generation', 0):.2f}s |
| Threat Modeling | {timing.get('threat_modeling', 0):.2f}s |
| Tech Debt Detection | {timing.get('tech_debt_detection', 0):.2f}s |

### Analysis Quality

- **Files Scanned:** {quality.get('files_scanned', 0)}
- **Files Parsed Successfully:** {quality.get('files_parsed_successfully', 0)}
- **Parsing Success Rate:** {quality.get('parsing_success_rate', 0):.1%}
- **Binary Files Skipped:** {analysis_results.get('scan', {}).get('binary_files', 0)}

"""

        content += f"""
## 📊 About Confidence Scores

Confidence scores range from **0.0** (no confidence) to **1.0** (absolute certainty).

### Scoring Factors

The confidence score is calculated using a weighted formula:

```
confidence = 0.40 × code_evidence + 0.30 × documentation + 0.20 × runtime + 0.10 × cross_references
```

**Breakdown:**
- **Code Evidence (40%)**: Presence of implementation in production code (not tests/examples)
- **Documentation Clarity (30%)**: Explicit documentation, ADRs, or design docs referencing the decision
- **Runtime Evidence (20%)**: Configuration files, environment variables, deployment manifests
- **Cross-References (10%)**: References between different parts of the codebase

### Score Interpretation

| Score Range | Status | Interpretation |
|-------------|--------|----------------|
| **0.90-1.00** | ✅ High Confidence | Strong evidence from multiple sources, auto-accept for conversion |
| **0.70-0.89** | ⚠️ Medium Confidence | Good evidence but gaps exist, review recommended |
| **0.50-0.69** | ⚠️ Low Confidence | Weak evidence, manual validation required |
| **0.00-0.49** | ❌ Very Low | Likely false positive, reject or investigate further |

### Margin of Error

Each score includes a margin (±0.05 to ±0.15) based on:
- Evidence diversity (multiple types = lower margin)
- Evidence consistency (agreement between sources)
- Evidence quality (production code > tests > comments)

**Example:**
- Score: `0.85 ± 0.08` means confidence between 77% and 93%
- Higher margin = more uncertainty, needs review

"""

        # FIX G2 (v2.1.15): Correct key name to match project_analyzer.py
        # FIX M2 (v2.2.0): Expand reconciliation section with detailed explanations
        if 'adr_reconciliation' in analysis_results:
            recon = analysis_results['adr_reconciliation']
            total_existing = recon.get('total_existing', 0)
            total_inferred = recon.get('total_inferred', 0)
            duplicates = len(recon.get('duplicate', []))
            enriched = len(recon.get('enrich', []))
            new_adrs = len(recon.get('new', []))

            # FIX G2 (v2.1.15): Log actual count for debugging
            logger.info(f"Import report: total_existing={total_existing}, duplicates={duplicates}, enriched={enriched}, new={new_adrs}")

            content += f"\n## 📚 ADR Reconciliation Details\n\n"
            content += f"**Overview:**\n"
            content += f"- **Existing ADRs detected:** {total_existing}\n"
            content += f"- **ADRs inferred from code:** {total_inferred}\n"
            content += f"- **ADRs converted to YAML:** {enriched}\n"
            content += f"- **New ADRs generated:** {new_adrs}\n"
            content += f"- **ADRs not converted:** {total_existing - enriched - duplicates}\n\n"

            # FIX M2 (v2.2.0): Explain conversion criteria
            content += f"### Conversion Criteria\n\n"
            content += f"ADRs were selected for YAML conversion based on:\n"
            content += f"- **Confidence score > 0.90:** High-confidence decisions backed by strong code evidence\n"
            content += f"- **High relevance:** ADRs with code references found in production code (not tests/examples)\n"
            content += f"- **Core architectural decisions:** Decisions that impact system structure, not configuration\n"
            content += f"- **Similarity threshold: 0.8:** Matches existing ADRs if similarity ≥ 80%\n\n"

            # FIX M2 (v2.2.0): List ADRs not converted with reasons
            adrs_not_converted = total_existing - enriched - duplicates
            if adrs_not_converted > 0:
                content += f"### ADRs Not Converted ({adrs_not_converted})\n\n"
                content += f"The following ADRs were detected but not converted to YAML format:\n\n"

                # List duplicates (skipped because already exist)
                if recon.get('duplicate'):
                    content += f"**Duplicates (Already in YAML format - {duplicates} skipped):**\n\n"
                    for dup in recon['duplicate']:
                        existing = dup.get('existing', {})
                        inferred = dup.get('inferred', {})
                        content += f"- ✓ **{inferred.get('title', 'Unknown')}**\n"
                        content += f"  - Existing: `{existing.get('path', 'N/A')}`\n"
                        content += f"  - Similarity: {dup.get('similarity', 0):.1%}\n"
                        content += f"  - Reason: Already in SDLC format (kept existing)\n\n"

                # Calculate remaining not converted (not duplicates, not enriched, not new)
                remaining_not_converted = adrs_not_converted - duplicates
                if remaining_not_converted > 0:
                    content += f"**Low Confidence or Relevance ({remaining_not_converted}):**\n\n"
                    content += f"These ADRs were detected but did not meet the conversion criteria:\n"
                    content += f"- Confidence score < 0.90\n"
                    content += f"- Limited or no code evidence in production code\n"
                    content += f"- Configuration-only decisions (not architectural)\n"
                    content += f"- Test-only or example-only evidence\n\n"
                    content += f"**Note:** These ADRs remain in their original format and are indexed in `references/adr_index.yml`\n\n"

            # FIX M2 (v2.2.0): Reference to adr_index.yml
            content += f"### Cross-Reference Index\n\n"
            content += f"For a complete mapping of original ADRs to converted YAML files, see:\n"
            content += f"**`{self.config['general']['output_dir']}/references/adr_index.yml`**\n\n"
            content += f"This index contains:\n"
            content += f"- Original ADR paths (Markdown/AsciiDoc)\n"
            content += f"- Converted YAML file locations\n"
            content += f"- Migration status (reconciled/skipped/enriched)\n"
            content += f"- Similarity scores for matches\n\n"

        content += "\n**Generated with SDLC Agêntico by @arbgjr**\n"
        report_file.write_text(content)
        return str(report_file)

    def _index_original_adrs(self, project_path: Path) -> List[str]:
        """
        FIX #7: Index original ADRs from project into references/.

        Searches common ADR locations:
        - docs/adr/
        - documentation/adr/
        - */docs/adr/
        - adr/

        Args:
            project_path: Path to project root

        Returns:
            List of copied ADR file paths
        """
        import shutil

        ref_dir = self.output_dir / "references" / "original-adrs"
        ref_dir.mkdir(parents=True, exist_ok=True)

        copied_adrs = []

        # Common ADR locations
        adr_patterns = [
            "docs/adr/*.md",
            "documentation/adr/*.md",
            "*/docs/adr/*.md",
            "adr/*.md",
            "ADR/*.md",
            "decisions/*.md"
        ]

        for pattern in adr_patterns:
            for adr_file in project_path.glob(pattern):
                if adr_file.is_file():
                    # Copy preserving filename
                    dest = ref_dir / adr_file.name
                    shutil.copy2(adr_file, dest)
                    copied_adrs.append(str(dest.relative_to(self.output_dir)))

                    logger.debug(
                        "Indexed original ADR",
                        extra={"source": str(adr_file), "dest": str(dest)}
                    )

        if copied_adrs:
            # Create index file
            index_file = ref_dir / "INDEX.md"
            index_content = f"""# Original ADRs Index

**Total ADRs Found:** {len(copied_adrs)}
**Indexed:** {datetime.utcnow().isoformat()}Z

## Files

"""
            for adr in sorted(copied_adrs):
                index_content += f"- [{Path(adr).name}]({adr})\n"

            index_file.write_text(index_content)

            logger.info(
                "Original ADRs indexed",
                extra={"count": len(copied_adrs), "ref_dir": str(ref_dir)}
            )

        return copied_adrs


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis_json")
    args = parser.parse_args()

    with open(args.analysis_json) as f:
        analysis_results = json.load(f)

    config_path = Path(__file__).parent.parent / "config" / "import_config.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    generator = DocumentationGenerator(config)
    result = generator.generate(analysis_results)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
