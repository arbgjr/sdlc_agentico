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

        # Configure Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, analysis_results: Dict) -> Dict:
        """Generate all documentation"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FIX #7: Index original ADRs in references/
        project_path = Path(analysis_results.get('project_path', '.'))
        original_adrs = self._index_original_adrs(project_path)

        # NEW (v2.1.7): Generate ADR index for reconciliation
        adr_index = None
        if 'adr_reconciliation' in analysis_results:
            adr_index = self._generate_adr_index(analysis_results.get('adr_reconciliation', {}))

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
        """Generate ADR files"""
        adrs = []
        adr_dir = self.output_dir / "corpus/nodes/decisions"
        adr_dir.mkdir(parents=True, exist_ok=True)

        for decision in decisions.get('decisions', []):
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

        Returns:
            Path to generated adr_index.yml
        """
        index_file = self.output_dir / "references" / "adr_index.yml"
        index_file.parent.mkdir(parents=True, exist_ok=True)

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
        index_data = {
            'adr_index': index_entries,
            'summary': {
                'total_original': reconciliation.get('total_existing', 0),
                'total_inferred': reconciliation.get('total_inferred', 0),
                'duplicates_skipped': len(reconciliation.get('duplicate', [])),
                'enriched': len(reconciliation.get('enrich', [])),
                'new_generated': len(reconciliation.get('new', []))
            },
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }

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

        content = f"""# Import Analysis Report

**Analysis ID:** {analysis_results.get('analysis_id', 'unknown')}
**Date:** {datetime.utcnow().isoformat()}Z

## Summary

- **Primary Language:** {analysis_results.get('language_analysis', {}).get('primary_language', 'unknown')}
- **Decisions Extracted:** {analysis_results.get('decisions', {}).get('count', 0)}
- **Threats Identified:** {analysis_results.get('threats', {}).get('total', 0)}
- **Tech Debt Items:** {analysis_results.get('tech_debt', {}).get('total', 0)}
"""

        # FIX C3: Add ADR Reconciliation section if available
        if 'reconciliation' in analysis_results:
            recon = analysis_results['reconciliation']
            content += f"\n## 📚 ADR Reconciliation\n\n"
            content += f"- **Existing ADRs found:** {recon.get('total_existing', 0)}\n"
            content += f"- **Inferred ADRs:** {recon.get('total_inferred', 0)}\n"
            content += f"- **Duplicates skipped:** {len(recon.get('duplicate', []))}\n"
            content += f"- **New unique ADRs:** {len(recon.get('new', []))}\n"
            content += f"- **ADRs enriched:** {len(recon.get('enrich', []))}\n\n"

            # List duplicates
            if recon.get('duplicate'):
                content += f"### Duplicates Detected\n\n"
                for dup in recon['duplicate']:
                    existing = dup.get('existing', {})
                    inferred = dup.get('inferred', {})
                    content += f"- ✓ **{inferred.get('title', 'Unknown')}**\n"
                    content += f"  - Existing: `{existing.get('path', 'N/A')}`\n"
                    content += f"  - Similarity: {dup.get('similarity', 0):.1%}\n"
                    content += f"  - Action: Skipped generation (kept existing)\n\n"

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
