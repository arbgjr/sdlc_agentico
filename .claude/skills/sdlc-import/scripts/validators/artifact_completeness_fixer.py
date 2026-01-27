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

    def fix(self, output_dir: Path) -> Dict:
        """
        Validate presence of required artifacts.

        Args:
            output_dir: Output directory (e.g., .agentic_sdlc/)

        Returns:
            {
                'missing_artifacts': [...],
                'present_artifacts': [...]
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

        result = {
            'missing_artifacts': missing,
            'present_artifacts': present
        }

        logger.info(
            f"Artifact completeness check: {len(present)}/{len(self.required)} present",
            extra=result
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
