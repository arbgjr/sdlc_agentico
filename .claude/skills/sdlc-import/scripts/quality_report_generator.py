#!/usr/bin/env python3
"""
Quality Report Generator - Generate post-import quality reports
Creates markdown report showing corrections applied and issues detected.
"""

import sys
from pathlib import Path
from typing import Dict
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Add logging utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

from post_import_validator import ValidationResult

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class QualityReportGenerator:
    """Generate quality reports for post-import validation."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(
        self,
        validation_result: ValidationResult,
        project_name: str,
        correlation_id: str
    ) -> str:
        """
        Generate quality report markdown.

        Args:
            validation_result: Validation result from PostImportValidator
            project_name: Name of the project
            correlation_id: Correlation ID

        Returns:
            Markdown content
        """
        logger.info(
            "Generating quality report",
            extra={'correlation_id': correlation_id, 'score': validation_result.overall_score}
        )

        # Load template
        template = self.jinja_env.get_template('post_import_quality_report.md')

        # Prepare context
        context = {
            'project_name': project_name,
            'correlation_id': correlation_id,
            'quality_score': validation_result.overall_score,
            'passed': validation_result.passed,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'corrections_applied': validation_result.corrections_applied,
            'issues_detected': validation_result.issues_detected,
            'metrics': validation_result.metrics,
            'status_emoji': self._get_status_emoji(validation_result.overall_score),
            'status_text': self._get_status_text(validation_result.overall_score)
        }

        # Render template
        content = template.render(**context)

        logger.info(
            "Quality report generated",
            extra={'correlation_id': correlation_id}
        )

        return content

    def _get_status_emoji(self, score: float) -> str:
        """Get status emoji based on score."""
        if score >= 0.85:
            return "✅"
        elif score >= 0.70:
            return "⚠️"
        else:
            return "❌"

    def _get_status_text(self, score: float) -> str:
        """Get status text based on score."""
        if score >= 0.85:
            return "EXCELLENT"
        elif score >= 0.70:
            return "REVIEW REQUIRED"
        else:
            return "NEEDS IMPROVEMENT"


def main():
    """CLI entry point for testing"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate quality report")
    parser.add_argument("validation_result_file", help="Path to validation result JSON")
    parser.add_argument("--project-name", default="Unknown", help="Project name")
    parser.add_argument("--correlation-id", default="test", help="Correlation ID")
    args = parser.parse_args()

    # Load validation result
    with open(args.validation_result_file) as f:
        data = json.load(f)

    # Reconstruct ValidationResult
    from dataclasses import dataclass
    from post_import_validator import ValidationResult

    result = ValidationResult(
        passed=data['passed'],
        overall_score=data['overall_score'],
        corrections_applied=data['corrections_applied'],
        issues_detected=data['issues_detected'],
        metrics=data['metrics']
    )

    # Generate report
    templates_dir = Path(__file__).parent.parent / "templates"
    generator = QualityReportGenerator(templates_dir)

    report = generator.generate(
        validation_result=result,
        project_name=args.project_name,
        correlation_id=args.correlation_id
    )

    print(report)


if __name__ == "__main__":
    main()
