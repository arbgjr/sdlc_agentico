#!/usr/bin/env python3
"""
Documentation Generator - Generate SDLC documentation
Creates ADRs, threat models, tech debt reports, and import summary.
"""

import sys
import json
from pathlib import Path
from typing import Dict
from datetime import datetime
from jinja2 import Template
import yaml

sys.path.insert(0, '.claude/lib/python')
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class DocumentationGenerator:
    """Generate SDLC documentation"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = Path(config['general']['output_dir'])
        self.templates_dir = Path(__file__).parent.parent / "templates"

    def generate(self, analysis_results: Dict) -> Dict:
        """Generate all documentation"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {
            "adrs": self._generate_adrs(analysis_results.get('decisions', {})),
            "threat_model": self._generate_threat_model(analysis_results.get('threats', {})),
            "tech_debt_report": self._generate_tech_debt_report(analysis_results.get('tech_debt', {})),
            "import_report": self._generate_import_report(analysis_results)
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
            adr_content = yaml.dump(decision, default_flow_style=False)
            adr_file.write_text(adr_content)
            adrs.append(str(adr_file))

        return adrs

    def _generate_threat_model(self, threats: Dict) -> str:
        """Generate threat model file"""
        threat_file = self.output_dir / "security/threat-model-inferred.yml"
        threat_file.parent.mkdir(parents=True, exist_ok=True)
        threat_file.write_text(yaml.dump(threats, default_flow_style=False))
        return str(threat_file)

    def _generate_tech_debt_report(self, tech_debt: Dict) -> str:
        """Generate tech debt report"""
        report_file = self.output_dir / "reports/tech-debt-inferred.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# Technical Debt Report

**Date:** {datetime.utcnow().isoformat()}Z
**Total Items:** {tech_debt.get('total', 0)}
**Total Effort:** {tech_debt.get('total_effort', 0)}h

## Summary

- P0 (CRITICAL): {tech_debt.get('p0', 0)} items
- P1 (HIGH): {tech_debt.get('p1', 0)} items
- P2 (MEDIUM): {tech_debt.get('p2', 0)} items
- P3 (LOW): {tech_debt.get('p3', 0)} items

See full analysis in `.agentic_sdlc/`.

**Generated with SDLC Agêntico by @arbgjr**
"""
        report_file.write_text(content)
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

**Generated with SDLC Agêntico by @arbgjr**
"""
        report_file.write_text(content)
        return str(report_file)


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
