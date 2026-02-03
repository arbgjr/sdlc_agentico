#!/usr/bin/env python3
"""
Artifact Completeness Fixer - Ensure all required artifacts are generated
Validates presence of ADR index, tech debt report, diagrams, threat model.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ArtifactCompletenessFixer:
    """Validate and fix missing artifacts."""

    REQUIRED_ARTIFACTS = [
        "corpus/nodes/decisions/adr_index.md",
        "reports/tech-debt-inferred.md",
        "architecture/component-diagram.mmd",
        "security/threat-model-inferred.yml"
    ]

    def __init__(self, config: Dict):
        self.config = config
        self.required = config.get('completeness_validation', {}).get(
            'required_artifacts',
            self.REQUIRED_ARTIFACTS
        )

    def fix(self, output_dir: Path, import_results: Dict = None) -> Dict:
        """
        Validate presence of required artifacts and ADR count consistency.

        FIX BUG-002, BUG-003: Validate ADR count matches across all sources

        Args:
            output_dir: Output directory (e.g., .agentic_sdlc/)
            import_results: Import results containing decisions (optional)

        Returns:
            {
                'missing_artifacts': [...],
                'present_artifacts': [...],
                'adr_count_consistent': bool,
                'adr_count_details': {...}
            }
        """
        missing = []
        present = []

        for artifact_path in self.required:
            full_path = output_dir / artifact_path

            if full_path.exists():
                present.append(artifact_path)
            else:
                missing.append(artifact_path)
                logger.warning(
                    f"Missing required artifact: {artifact_path}",
                    extra={'artifact': artifact_path}
                )

        # FIX BUG-002, BUG-003: Validate ADR count consistency
        adr_count_consistent = True
        adr_count_details = {}

        if import_results:
            adr_count_details = self._validate_adr_counts(output_dir, import_results)
            adr_count_consistent = adr_count_details.get('consistent', True)

            if not adr_count_consistent:
                logger.error(
                    "ADR count mismatch detected",
                    extra=adr_count_details
                )
                missing.append("ADR count consistency")

        result = {
            'missing_artifacts': missing,
            'present_artifacts': present,
            'adr_count_consistent': adr_count_consistent,
            'adr_count_details': adr_count_details
        }

        logger.info(
            f"Artifact completeness check: {len(present)}/{len(self.required)} present, ADR count consistent: {adr_count_consistent}",
            extra=result
        )

        return result

    def _validate_adr_counts(self, output_dir: Path, import_results: Dict) -> Dict:
        """
        Validate ADR count consistency across sources.

        FIX BUG-002, BUG-003:
        - Count source ADR files (if available)
        - Count converted YAML files
        - Count entries in adr_index.yml
        - Verify all match

        Args:
            output_dir: Output directory
            import_results: Import results

        Returns:
            {
                'consistent': bool,
                'source_count': int,
                'converted_count': int,
                'index_count': int,
                'import_results_count': int
            }
        """
        import yaml

        # Count converted ADR YAML files
        adr_dir = output_dir / "corpus/nodes/decisions"
        converted_files = list(adr_dir.glob("adr-*.yml")) if adr_dir.exists() else []
        converted_count = len(converted_files)

        # Count from index.yml
        index_file = output_dir / "corpus/adr_index.yml"
        index_count = 0
        if index_file.exists():
            try:
                with open(index_file) as f:
                    index_data = yaml.safe_load(f)
                    index_count = index_data.get('count', 0)
            except Exception as e:
                logger.warning(f"Failed to read adr_index.yml: {e}")

        # Count from import_results
        import_results_count = import_results.get('decisions', {}).get('count', 0)

        # Determine if consistent
        consistent = (converted_count == index_count == import_results_count)

        result = {
            'consistent': consistent,
            'converted_count': converted_count,
            'index_count': index_count,
            'import_results_count': import_results_count
        }

        if not consistent:
            logger.error(
                "ADR count mismatch",
                extra={
                    'converted_files': converted_count,
                    'index_yml_count': index_count,
                    'import_results_count': import_results_count
                }
            )

        return result


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="Validate artifact completeness")
    parser.add_argument("--output-dir", default=".agentic_sdlc", help="Output directory")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    # Load config
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    else:
        config = {
            'completeness_validation': {
                'required_artifacts': ArtifactCompletenessFixer.REQUIRED_ARTIFACTS
            }
        }

    # Validate
    fixer = ArtifactCompletenessFixer(config)
    result = fixer.fix(output_dir=Path(args.output_dir))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
