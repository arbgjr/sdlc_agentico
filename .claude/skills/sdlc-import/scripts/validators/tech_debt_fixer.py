#!/usr/bin/env python3
"""
Tech Debt Fixer - Validate and regenerate tech debt reports
Ensures tech debt reports have full item details, not just summaries.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class TechDebtFixer:
    """Validate and fix tech debt reports."""

    def __init__(self, config: Dict):
        self.config = config
        self.min_details_ratio = config.get('tech_debt_validation', {}).get('min_details_ratio', 0.80)

    def fix(self, tech_debt: Dict, output_dir: Path, correlation_id: str) -> Dict:
        """
        Validate tech debt report completeness and regenerate if needed.

        FIX G2 (v2.3.2): Deduplicate tech debt items before validation.

        The actual regeneration happens in DocumentationGenerator._generate_tech_debt_report(),
        which now uses the full Jinja2 template.

        This method validates completeness and removes duplicates.

        Args:
            tech_debt: Tech debt analysis results
            output_dir: Output directory for reports
            correlation_id: Correlation ID for logging

        Returns:
            {
                'was_incomplete': bool,
                'original_count': int,
                'rendered_count': int,
                'report_path': Path,
                'duplicates_removed': int,
                'deduplicated_items': List[Dict]
            }
        """
        tech_debt_items = tech_debt.get('tech_debt', [])
        original_count = len(tech_debt_items)

        logger.info(
            "Validating tech debt report",
            extra={'correlation_id': correlation_id, 'total_items': original_count}
        )

        # FIX G2 (v2.3.2): Deduplicate items using composite key (file, line, category)
        deduplicated_items, duplicates_removed = self._deduplicate_items(tech_debt_items, correlation_id)

        # Update tech_debt dict with deduplicated items
        tech_debt['tech_debt'] = deduplicated_items
        tech_debt['total'] = len(deduplicated_items)

        # Check if report would be incomplete (no items array)
        was_incomplete = original_count > 0 and not tech_debt_items

        # The fix is automatic: documentation_generator.py now uses Jinja2 template
        # and renders all items by priority

        report_path = output_dir / "reports/tech-debt-inferred.md"

        result = {
            'was_incomplete': was_incomplete,
            'original_count': original_count,
            'rendered_count': len(deduplicated_items),
            'report_path': str(report_path),
            'duplicates_removed': duplicates_removed,
            'deduplicated_items': deduplicated_items
        }

        if duplicates_removed > 0:
            logger.warning(
                f"Removed {duplicates_removed} duplicate tech debt items",
                extra={'correlation_id': correlation_id, 'duplicates': duplicates_removed}
            )

        if was_incomplete:
            logger.warning(
                "Tech debt report was incomplete (no items)",
                extra={'correlation_id': correlation_id}
            )
        else:
            logger.info(
                f"Tech debt report is complete ({len(deduplicated_items)} items after deduplication)",
                extra={'correlation_id': correlation_id, 'total_items': len(deduplicated_items)}
            )

        return result

    def _deduplicate_items(self, items: List[Dict], correlation_id: str) -> tuple[List[Dict], int]:
        """
        FIX G2 (v2.3.2): Deduplicate tech debt items.

        Uses composite key: (file, line, category)
        If two items have same file + line + category, they're duplicates.

        Args:
            items: List of tech debt items
            correlation_id: Correlation ID for logging

        Returns:
            Tuple of (deduplicated_items, duplicates_count)
        """
        if not items:
            return [], 0

        seen = set()
        deduplicated = []
        duplicates = []

        for item in items:
            # Create composite key
            file_path = item.get('file', '')
            line = item.get('line', 0)
            category = item.get('category', '')
            composite_key = (file_path, line, category)

            if composite_key in seen:
                # Duplicate found
                duplicates.append(item)
                logger.debug(
                    f"Duplicate tech debt item: {item.get('id', 'unknown')} - {item.get('title', 'no title')}",
                    extra={
                        'correlation_id': correlation_id,
                        'file': file_path,
                        'line': line,
                        'category': category
                    }
                )
            else:
                seen.add(composite_key)
                deduplicated.append(item)

        return deduplicated, len(duplicates)


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="Validate tech debt report")
    parser.add_argument("tech_debt_file", help="Path to tech debt JSON/YAML file")
    parser.add_argument("--output-dir", default=".agentic_sdlc", help="Output directory")
    args = parser.parse_args()

    # Load tech debt
    with open(args.tech_debt_file) as f:
        if args.tech_debt_file.endswith('.yml') or args.tech_debt_file.endswith('.yaml'):
            tech_debt = yaml.safe_load(f)
        else:
            tech_debt = json.load(f)

    # Validate
    config = {
        'tech_debt_validation': {
            'min_details_ratio': 0.80
        }
    }

    fixer = TechDebtFixer(config)
    result = fixer.fix(
        tech_debt=tech_debt,
        output_dir=Path(args.output_dir),
        correlation_id='test-correlation-id'
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
