#!/usr/bin/env python3
"""
Post-Import Validator - Orchestrates validation and auto-correction
Coordinates all validators/fixers and generates quality report.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

# Add logging utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

from validators import (
    ADREvidenceFixer,
    TechDebtFixer,
    DiagramQualityFixer,
    ArtifactCompletenessFixer
)

logger = get_logger(__name__, skill="sdlc-import", phase=0)


@dataclass
class ValidationResult:
    """Result of post-import validation"""
    passed: bool
    overall_score: float
    corrections_applied: Dict[str, Any]
    issues_detected: List[Dict]
    metrics: Dict[str, float]


class PostImportValidator:
    """Orchestrates post-import validation and auto-correction."""

    def __init__(self, config: Dict):
        self.config = config
        self.fixers = {
            'adr_evidence': ADREvidenceFixer(config),
            'tech_debt': TechDebtFixer(config),
            'diagrams': DiagramQualityFixer(config),
            'completeness': ArtifactCompletenessFixer(config)
        }

    def validate_and_fix(
        self,
        import_results: Dict,
        project_path: str,
        output_dir: Path,
        correlation_id: str
    ) -> ValidationResult:
        """
        Validate artifacts and apply automatic corrections.

        Flow:
        1. Detect problems in each category
        2. Apply automatic corrections
        3. Update import_results with corrected data
        4. Return validation result

        Args:
            import_results: Results from project_analyzer
            project_path: Path to project root
            output_dir: Output directory (.agentic_sdlc/)
            correlation_id: Correlation ID for logging

        Returns:
            ValidationResult with score, corrections, issues
        """
        logger.info(
            "Starting post-import validation and auto-fix",
            extra={'correlation_id': correlation_id}
        )

        corrections_applied = {}
        issues_detected = []

        # 1. Fix ADRs (remove false positives)
        if self.config.get('adr_validation', {}).get('enabled', True):
            adr_result = self.fixers['adr_evidence'].fix(
                decisions=import_results.get('decisions', {}).get('decisions', []),
                project_path=project_path
            )

            # Update results with filtered ADRs
            if 'decisions' not in import_results:
                import_results['decisions'] = {}

            import_results['decisions']['decisions'] = adr_result['decisions']
            import_results['decisions']['count'] = adr_result['filtered_count']

            corrections_applied['adr_filtering'] = {
                'original_count': adr_result['original_count'],
                'filtered_count': adr_result['filtered_count'],
                'removed_adrs': adr_result['removed_adrs']
            }

            if adr_result['removed_adrs']:
                issues_detected.append({
                    'category': 'adr_evidence',
                    'severity': 'warning',
                    'message': f"Removed {len(adr_result['removed_adrs'])} false positive ADRs",
                    'details': adr_result['removed_reasons']
                })

        # 2. Fix Tech Debt Report (already handled by documentation_generator.py)
        # BUG FIX #1: Initialize with safe defaults to prevent UnboundLocalError
        tech_debt_result = {"was_incomplete": False, "original_count": 0, "rendered_count": 0, "report_path": ""}

        if self.config.get('tech_debt_validation', {}).get('enabled', True):
            try:
                tech_debt_result = self.fixers['tech_debt'].fix(
                    tech_debt=import_results.get('tech_debt', {}),
                    output_dir=output_dir,
                    correlation_id=correlation_id
                )

                corrections_applied['tech_debt_regeneration'] = {
                    'original_item_count': tech_debt_result['original_count'],
                    'rendered_item_count': tech_debt_result['rendered_count'],
                    'report_path': str(tech_debt_result['report_path'])
                }

                if tech_debt_result['was_incomplete']:
                    issues_detected.append({
                        'category': 'tech_debt',
                        'severity': 'critical',
                        'message': f"Tech debt report was incomplete (missing {tech_debt_result['original_count']} items)",
                        'correction': 'Regenerated with full item list'
                    })
            except Exception as e:
                logger.error(f"Tech debt validation failed: {e}", exc_info=True)
                tech_debt_result = {"was_incomplete": True, "error": str(e), "original_count": 0, "rendered_count": 0, "report_path": ""}
                issues_detected.append({
                    'category': 'tech_debt',
                    'severity': 'error',
                    'message': f"Tech debt validation crashed: {str(e)}",
                    'correction': 'Using default values'
                })

        # 3. Fix Diagrams (validate quality)
        # BUG FIX #1: Initialize with safe defaults to prevent UnboundLocalError
        diagram_result = {"regenerated": False, "regenerated_diagrams": []}

        if self.config.get('diagram_validation', {}).get('enabled', True):
            try:
                # Extract diagrams list from the diagrams dict (contains {"diagrams": [...], "count": N})
                diagrams_dict = import_results.get('diagrams', {})
                diagrams_list = diagrams_dict.get('diagrams', []) if isinstance(diagrams_dict, dict) else []

                diagram_result = self.fixers['diagrams'].fix(
                    diagrams=diagrams_list,
                    language_analysis=import_results.get('language_analysis', {}),
                    output_dir=output_dir
                )

                if diagram_result['regenerated']:
                    corrections_applied['diagram_regeneration'] = {
                        'regenerated_count': len(diagram_result['regenerated_diagrams']),
                        'reason': 'Diagrams were too generic'
                    }

                    issues_detected.append({
                        'category': 'diagrams',
                        'severity': 'warning',
                        'message': 'Diagrams were generic templates',
                        'correction': f"Regenerated {len(diagram_result['regenerated_diagrams'])} diagrams"
                    })
            except Exception as e:
                logger.error(f"Diagram validation failed: {e}", exc_info=True)
                diagram_result = {"regenerated": False, "regenerated_diagrams": [], "error": str(e)}
                issues_detected.append({
                    'category': 'diagrams',
                    'severity': 'error',
                    'message': f"Diagram validation crashed: {str(e)}",
                    'correction': 'Using default values'
                })

        # 4. Validate artifact completeness
        completeness_result = self.fixers['completeness'].fix(output_dir=output_dir)

        if completeness_result['missing_artifacts']:
            issues_detected.append({
                'category': 'completeness',
                'severity': 'warning',
                'message': f"Missing {len(completeness_result['missing_artifacts'])} required artifacts",
                'details': completeness_result['missing_artifacts']
            })

        # 5. Calculate overall score
        overall_score = self._calculate_score(
            corrections_applied=corrections_applied,
            import_results=import_results,
            completeness=completeness_result
        )

        # 6. Determine if passed
        passed = (
            overall_score >= self.config.get('pass_threshold', 0.70)
            and not any(issue['severity'] == 'critical' for issue in issues_detected)
        )

        result = ValidationResult(
            passed=passed,
            overall_score=overall_score,
            corrections_applied=corrections_applied,
            issues_detected=issues_detected,
            metrics={
                'adr_quality_score': self._calculate_adr_score(import_results),
                'tech_debt_completeness': 1.0 if not tech_debt_result.get('was_incomplete') else 0.5,
                'diagram_quality': 1.0 if not diagram_result.get('regenerated') else 0.5,
                'artifact_completeness': len(completeness_result['present_artifacts']) / len(self.fixers['completeness'].required) if self.fixers['completeness'].required else 1.0
            }
        )

        logger.info(
            f"Post-import validation complete: score={overall_score:.2%}, passed={passed}",
            extra={
                'correlation_id': correlation_id,
                'score': overall_score,
                'passed': passed,
                'corrections': len(corrections_applied),
                'issues': len(issues_detected)
            }
        )

        return result

    def _calculate_score(
        self,
        corrections_applied: Dict,
        import_results: Dict,
        completeness: Dict
    ) -> float:
        """
        Calculate overall quality score (0.0-1.0).

        Penalties:
        - ADRs removed: -0.05 per ADR removed
        - Tech debt incomplete: -0.10
        - Diagrams regenerated: -0.05 per diagram
        - Missing artifacts: -0.05 per artifact

        Base score: 1.0
        """
        score = 1.0

        # Penalty for ADRs removed
        adr_filtering = corrections_applied.get('adr_filtering', {})
        removed_count = len(adr_filtering.get('removed_adrs', []))
        score -= removed_count * 0.05

        # Penalty for tech debt incomplete
        tech_debt_regen = corrections_applied.get('tech_debt_regeneration', {})
        if tech_debt_regen:
            score -= 0.10

        # Penalty for diagrams regenerated
        diagram_regen = corrections_applied.get('diagram_regeneration', {})
        regen_count = diagram_regen.get('regenerated_count', 0)
        score -= regen_count * 0.05

        # Penalty for missing artifacts
        missing_count = len(completeness.get('missing_artifacts', []))
        score -= missing_count * 0.05

        return max(0.0, min(1.0, score))  # Clamp 0.0-1.0

    def _calculate_adr_score(self, import_results: Dict) -> float:
        """Calculate ADR quality score based on filtering ratio."""
        decisions = import_results.get('decisions', {})
        original_count = decisions.get('count', 0)
        filtered_count = len(decisions.get('decisions', []))

        if original_count == 0:
            return 1.0

        return filtered_count / original_count


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="Post-import validation")
    parser.add_argument("results_file", help="Path to import results JSON")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument("--output-dir", default=".agentic_sdlc", help="Output directory")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    # Load results
    with open(args.results_file) as f:
        import_results = json.load(f)

    # Load config
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    else:
        # Default config
        config_path = Path(__file__).parent.parent / "config" / "post_import_validation_rules.yml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            config = {
                'adr_validation': {'enabled': True, 'max_suspicious_ratio': 0.70},
                'tech_debt_validation': {'enabled': True},
                'diagram_validation': {'enabled': True},
                'completeness_validation': {'enabled': True},
                'pass_threshold': 0.70
            }

    # Validate
    validator = PostImportValidator(config)
    result = validator.validate_and_fix(
        import_results=import_results,
        project_path=args.project_path,
        output_dir=Path(args.output_dir),
        correlation_id='test-correlation-id'
    )

    # Output result
    output = {
        'passed': result.passed,
        'overall_score': result.overall_score,
        'corrections_applied': result.corrections_applied,
        'issues_detected': result.issues_detected,
        'metrics': result.metrics
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
