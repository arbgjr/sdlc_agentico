#!/usr/bin/env python3
"""
ADR Evidence Fixer - Detect and remove ADRs with suspicious evidence
Removes ADRs with evidence primarily from test fixtures, .claude/, or other non-codebase sources.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ADREvidenceFixer:
    """Detect and remove ADRs with suspicious evidence sources."""

    # Paths that indicate evidence is from test/config, not production code
    SUSPICIOUS_PATHS = [
        '.claude/',
        '.agentic_sdlc/',
        'tests/fixtures/',
        'tests/integration/',
        'test/fixtures/',
        'test/integration/',
        'examples/',
        'templates/',
        'docs/examples/',
        '__pycache__/',
        'node_modules/',
        '.git/'
    ]

    # Technology validation patterns
    TECH_PATTERNS = {
        'PostgreSQL': ['psycopg2', 'postgresql://', 'CREATE TABLE', 'pg_', 'postgres', 'Npgsql'],
        'MySQL': ['mysql', 'pymysql', 'MySql', 'SHOW TABLES'],
        'Pytest': ['pytest', 'def test_', '@pytest.fixture', 'import pytest'],
        'Jest': ['jest', 'describe(', 'it(', 'expect('],
        'Docker': ['FROM ', 'COPY ', 'RUN ', 'ENTRYPOINT', 'CMD'],
        'FastAPI': ['from fastapi', 'FastAPI()', '@app.'],
        'Flask': ['from flask import', 'Flask(__name__)'],
        'Django': ['from django', 'django.', 'settings.py'],
        'ASP.NET': ['using Microsoft.', 'WebApplication', '.csproj', 'using System.Web'],
        'React': ['import React', 'from \'react\'', 'useState', 'useEffect'],
        'Angular': ['@angular/', '@Component', '@NgModule'],
        'Vue': ['vue', 'createApp', 'Vue.component'],
        'Redis': ['redis://', 'import redis', 'RedisClient'],
        'MongoDB': ['mongodb://', 'mongoose', 'MongoClient'],
        'Kubernetes': ['apiVersion:', 'kind: Deployment', 'kubectl'],
        'Terraform': ['terraform', 'resource "', 'provider "'],
        'GraphQL': ['graphql', 'type Query', 'schema {']
    }

    def __init__(self, config: Dict):
        self.config = config
        self.max_suspicious_ratio = config.get('adr_validation', {}).get('max_suspicious_ratio', 0.70)
        self.cross_validate = config.get('adr_validation', {}).get('cross_validate_technologies', True)

    def fix(self, decisions: List[Dict], project_path: str) -> Dict:
        """
        Remove ADRs with suspicious evidence or technology mismatches.

        Args:
            decisions: List of ADR decision dicts
            project_path: Path to project root

        Returns:
            {
                'original_count': 19,
                'filtered_count': 15,
                'removed_adrs': ['ADR-001', 'ADR-006'],
                'removed_reasons': {...},
                'decisions': [...]  # Filtered decisions
            }
        """
        original_count = len(decisions)
        filtered_decisions = []
        removed_adrs = []
        removed_reasons = {}

        logger.info(f"Validating {original_count} ADRs", extra={
            'max_suspicious_ratio': self.max_suspicious_ratio
        })

        for adr in decisions:
            adr_id = adr.get('id', 'unknown')

            # Check 1: Suspicious evidence sources
            analysis = self._analyze_evidence_sources(adr)

            if analysis['suspicious_ratio'] > self.max_suspicious_ratio:
                removed_adrs.append(adr_id)
                removed_reasons[adr_id] = {
                    'reason': 'suspicious_evidence',
                    'suspicious_ratio': analysis['suspicious_ratio'],
                    'suspicious_files': analysis['suspicious_files'][:5],  # First 5 examples
                    'total_suspicious': len(analysis['suspicious_files'])
                }

                logger.warning(
                    f"Removing ADR {adr_id}: {analysis['suspicious_ratio']:.0%} suspicious evidence",
                    extra={'adr_id': adr_id, 'suspicious_ratio': analysis['suspicious_ratio']}
                )
                continue

            # Check 2: Cross-validate technology (if enabled)
            if self.cross_validate:
                tech_valid = self._cross_validate_technology(adr, project_path)

                if not tech_valid:
                    removed_adrs.append(adr_id)
                    removed_reasons[adr_id] = {
                        'reason': 'technology_mismatch',
                        'claimed_tech': adr.get('title', 'unknown'),
                        'not_found_in_codebase': True
                    }

                    logger.warning(
                        f"Removing ADR {adr_id}: technology not found in codebase",
                        extra={'adr_id': adr_id, 'title': adr.get('title')}
                    )
                    continue

            # ADR is valid
            filtered_decisions.append(adr)

        result = {
            'original_count': original_count,
            'filtered_count': len(filtered_decisions),
            'removed_adrs': removed_adrs,
            'removed_reasons': removed_reasons,
            'decisions': filtered_decisions
        }

        logger.info(
            f"ADR validation complete: {len(removed_adrs)} removed, {len(filtered_decisions)} retained",
            extra=result
        )

        return result

    def _analyze_evidence_sources(self, adr: Dict) -> Dict:
        """
        Calculate ratio of suspicious evidence sources vs. production code.

        Returns:
            {
                'suspicious_ratio': 0.75,
                'codebase_ratio': 0.25,
                'suspicious_files': [...],
                'codebase_files': [...]
            }
        """
        # Extract file paths from evidence
        evidence_files = []

        # Evidence can be in multiple formats
        evidence = adr.get('evidence', [])
        if isinstance(evidence, list):
            for ev in evidence:
                if isinstance(ev, str):
                    # Format: "file:line" or "file:line:column" or just "file"
                    file_path = ev.split(':')[0]
                    evidence_files.append(file_path)
                elif isinstance(ev, dict):
                    # Format: {"file": "path", "line": 123}
                    evidence_files.append(ev.get('file', ''))

        # Count suspicious vs. codebase files
        suspicious_count = sum(
            1 for file in evidence_files
            if any(file.startswith(path) for path in self.SUSPICIOUS_PATHS)
        )

        total_count = len(evidence_files)

        return {
            'suspicious_ratio': suspicious_count / total_count if total_count > 0 else 0,
            'codebase_ratio': (total_count - suspicious_count) / total_count if total_count > 0 else 0,
            'suspicious_files': [
                f for f in evidence_files
                if any(f.startswith(path) for path in self.SUSPICIOUS_PATHS)
            ],
            'codebase_files': [
                f for f in evidence_files
                if not any(f.startswith(path) for path in self.SUSPICIOUS_PATHS)
            ],
            'total_evidence': total_count
        }

    def _cross_validate_technology(self, adr: Dict, project_path: str) -> bool:
        """
        Verify if technology mentioned in ADR actually exists in codebase.

        Args:
            adr: ADR decision dict
            project_path: Path to project root

        Returns:
            True if technology found in codebase, False otherwise
        """
        # Infer technology from title
        title = adr.get('title', '')
        tech = None

        for tech_name in self.TECH_PATTERNS:
            if tech_name.lower() in title.lower():
                tech = tech_name
                break

        if not tech:
            # Can't infer technology, accept by default
            return True

        # Search for technology patterns in codebase
        patterns = self.TECH_PATTERNS[tech]
        project = Path(project_path)

        # Search strategy: find at least one pattern match in codebase files
        for pattern in patterns:
            for file in project.rglob('*'):
                # Skip hidden dirs, node_modules, etc.
                if any(part.startswith('.') for part in file.parts):
                    continue
                if 'node_modules' in file.parts or '__pycache__' in file.parts:
                    continue

                if file.is_file() and file.stat().st_size < 1_000_000:  # Skip files > 1MB
                    try:
                        content = file.read_text(errors='ignore')
                        if pattern in content:
                            logger.debug(
                                f"Technology {tech} validated: found '{pattern}' in {file}",
                                extra={'tech': tech, 'pattern': pattern, 'file': str(file)}
                            )
                            return True  # Technology found
                    except:
                        pass

        # Technology not found in codebase
        logger.debug(
            f"Technology {tech} not validated: patterns {patterns} not found",
            extra={'tech': tech, 'title': title}
        )
        return False


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="Validate ADR evidence")
    parser.add_argument("decisions_file", help="Path to decisions YAML/JSON file")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument("--config", help="Path to config file")
    args = parser.parse_args()

    # Load decisions
    with open(args.decisions_file) as f:
        if args.decisions_file.endswith('.yml') or args.decisions_file.endswith('.yaml'):
            decisions = yaml.safe_load(f)
        else:
            decisions = json.load(f)

    # Load config
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    else:
        config = {
            'adr_validation': {
                'max_suspicious_ratio': 0.70,
                'cross_validate_technologies': True
            }
        }

    # Fix ADRs
    fixer = ADREvidenceFixer(config)
    result = fixer.fix(
        decisions=decisions if isinstance(decisions, list) else decisions.get('decisions', []),
        project_path=args.project_path
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
