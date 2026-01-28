#!/usr/bin/env python3
"""
Validate SDLC Import Artifacts

Ensures all mandatory artifacts were created correctly.
Run this after sdlc-import to validate completeness.

Usage:
    python3 validate_import.py --output-dir .project
    python3 validate_import.py --output-dir .project --strict
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

import yaml

# Add logging utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ImportValidator:
    """Validate sdlc-import output"""

    def __init__(self, output_dir: Path, strict: bool = False):
        self.output_dir = output_dir
        self.strict = strict
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Run all validations"""
        logger.info(f"Validating import artifacts in: {self.output_dir}")

        # Mandatory artifacts
        self._check_mandatory_artifacts()

        # Structure validation
        self._validate_graph_structure()
        self._validate_adr_index_structure()
        self._validate_import_report_structure()

        # Quality checks
        self._check_no_custom_scripts()
        self._check_real_timestamps()

        # Report results
        self._report_results()

        # Return success status
        if self.errors:
            return False
        elif self.warnings and self.strict:
            return False
        else:
            return True

    def _check_mandatory_artifacts(self):
        """Check all mandatory artifacts exist"""
        mandatory_files = [
            ("corpus/graph.json", "Knowledge graph"),
            ("references/adr_index.yml", "ADR reconciliation index"),
            ("reports/import-report.md", "Import summary report"),
            ("reports/tech-debt-inferred.md", "Tech debt report"),
        ]

        for file_path, description in mandatory_files:
            full_path = self.output_dir / file_path
            if not full_path.exists():
                self.errors.append(f"MISSING: {description} ({file_path})")
                logger.error(f"Mandatory artifact missing: {file_path}")
            else:
                logger.debug(f"Found: {file_path}")

    def _validate_graph_structure(self):
        """Validate graph.json has valid structure"""
        graph_file = self.output_dir / "corpus/graph.json"
        if not graph_file.exists():
            return  # Already reported as error

        try:
            with open(graph_file) as f:
                graph = json.load(f)

            # Check required fields
            if 'version' not in graph:
                self.errors.append("graph.json missing 'version' field")

            if 'nodes' not in graph or not graph['nodes']:
                self.errors.append("graph.json has no nodes (empty graph)")

            if 'edges' not in graph:
                self.warnings.append("graph.json missing 'edges' field")

            # Validate version is not hardcoded
            version = graph.get('version', '')
            if version == '2.1.0':
                self.errors.append(f"graph.json has hardcoded version '2.1.0' (should read from .claude/VERSION)")

            logger.info(f"Graph validated: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges")

        except json.JSONDecodeError as e:
            self.errors.append(f"graph.json is not valid JSON: {e}")
        except Exception as e:
            self.errors.append(f"Error validating graph.json: {e}")

    def _validate_adr_index_structure(self):
        """Validate adr_index.yml has valid structure"""
        index_file = self.output_dir / "references/adr_index.yml"
        if not index_file.exists():
            return  # Already reported as error

        try:
            with open(index_file) as f:
                index = yaml.safe_load(f)

            # Check required sections
            if 'adr_index' not in index:
                self.errors.append("adr_index.yml missing 'adr_index' root key")
                return

            adr_index = index['adr_index']

            required_fields = ['metadata', 'summary']
            for field in required_fields:
                if field not in adr_index:
                    self.errors.append(f"adr_index.yml missing '{field}' section")

            # Check summary counts
            summary = adr_index.get('summary', {})
            total_existing = adr_index.get('metadata', {}).get('total_existing', 0)
            total_inferred = adr_index.get('metadata', {}).get('total_inferred', 0)

            logger.info(f"ADR index validated: {total_existing} existing, {total_inferred} inferred")

        except yaml.YAMLError as e:
            self.errors.append(f"adr_index.yml is not valid YAML: {e}")
        except Exception as e:
            self.errors.append(f"Error validating adr_index.yml: {e}")

    def _validate_import_report_structure(self):
        """Validate import-report.md has required sections"""
        report_file = self.output_dir / "reports/import-report.md"
        if not report_file.exists():
            return  # Already reported as error

        try:
            content = report_file.read_text()

            # Required sections (v2.2.0 M2)
            required_sections = [
                "Executive Summary",
                "Technology Stack",
                "Architecture Decisions",
            ]

            # Recommended sections
            recommended_sections = [
                "ADR Reconciliation",  # v2.2.0 M2
                "Execution Metrics",   # v2.2.0 L2
            ]

            for section in required_sections:
                if section not in content:
                    self.errors.append(f"import-report.md missing required section: '{section}'")

            for section in recommended_sections:
                if section not in content:
                    self.warnings.append(f"import-report.md missing recommended section: '{section}'")

            logger.info("Import report structure validated")

        except Exception as e:
            self.errors.append(f"Error validating import-report.md: {e}")

    def _check_no_custom_scripts(self):
        """Ensure no custom scripts were created in output directory"""
        scripts_dir = self.output_dir / "scripts"
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob("*.py"))
            if scripts:
                self.errors.append(f"CRITICAL: Custom Python scripts created in output: {scripts}")
                self.errors.append("Scripts should NEVER be created in .project/ - use framework scripts!")
                for script in scripts:
                    logger.error(f"Unauthorized script: {script}")

    def _check_real_timestamps(self):
        """Check for suspicious rounded timestamps in ADRs"""
        decisions_dir = self.output_dir / "corpus/nodes/decisions"
        if not decisions_dir.exists():
            return

        suspicious_timestamps = []

        for adr_file in decisions_dir.glob("*.yml"):
            try:
                with open(adr_file) as f:
                    adr = yaml.safe_load(f)

                timestamp = adr.get('timestamp', '')

                # Check for rounded timestamps
                if timestamp.endswith('T00:00:00') or timestamp.endswith(':00:00'):
                    suspicious_timestamps.append((adr_file.name, timestamp))

            except Exception as e:
                logger.warning(f"Error checking timestamp in {adr_file}: {e}")

        if suspicious_timestamps:
            self.warnings.append(f"Suspicious rounded timestamps detected in {len(suspicious_timestamps)} ADRs")
            self.warnings.append("Timestamps should be real UTC (e.g., 2026-01-28T12:34:56.789123Z)")
            for filename, ts in suspicious_timestamps[:5]:  # Show first 5
                logger.warning(f"  {filename}: {ts}")

    def _report_results(self):
        """Report validation results"""
        print("\n" + "=" * 70)
        print("SDLC Import Validation Results")
        print("=" * 70)

        if not self.errors and not self.warnings:
            print("✅ All validations PASSED")
            print(f"✅ Import artifacts validated in: {self.output_dir}")
            logger.info("All validations passed ✅")
            return

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "=" * 70)

        if self.errors:
            print("❌ Validation FAILED - fix errors above")
            logger.error(f"Validation failed with {len(self.errors)} errors")
        elif self.warnings and self.strict:
            print("⚠️  Validation FAILED (strict mode) - fix warnings above")
            logger.warning(f"Validation failed in strict mode with {len(self.warnings)} warnings")
        else:
            print("⚠️  Validation PASSED with warnings - review recommended")
            logger.warning(f"Validation passed with {len(self.warnings)} warnings")


def main():
    parser = argparse.ArgumentParser(description="Validate SDLC import artifacts")
    parser.add_argument("--output-dir", type=Path, default=Path(".project"),
                        help="Output directory to validate (default: .project)")
    parser.add_argument("--strict", action="store_true",
                        help="Fail on warnings (default: warnings are non-fatal)")

    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f"❌ Error: Output directory does not exist: {args.output_dir}")
        sys.exit(1)

    validator = ImportValidator(args.output_dir, args.strict)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
