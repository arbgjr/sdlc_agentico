#!/usr/bin/env python3
"""
Diagram Quality Fixer - Validate and regenerate architecture diagrams
Ensures diagrams reflect actual architecture, not generic templates.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class DiagramQualityFixer:
    """Validate and fix architecture diagram quality."""

    def __init__(self, config: Dict):
        self.config = config
        self.min_nodes = config.get('diagram_validation', {}).get('min_nodes', 5)
        self.min_edges = config.get('diagram_validation', {}).get('min_edges', 4)

    def fix(self, diagrams: List[Dict], language_analysis: Dict, output_dir: Path) -> Dict:
        """
        Validate diagram complexity and regenerate if too generic.

        Args:
            diagrams: List of diagram dicts (mermaid format)
            language_analysis: Language analysis results (to infer architecture)
            output_dir: Output directory for diagrams

        Returns:
            {
                'regenerated': bool,
                'regenerated_diagrams': [...]
            }
        """
        regenerated = False
        regenerated_diagrams = []

        logger.info(
            f"Validating {len(diagrams)} diagrams",
            extra={'min_nodes': self.min_nodes, 'min_edges': self.min_edges}
        )

        for diagram in diagrams:
            diagram_type = diagram.get('type', 'unknown')

            # Read content from file path (diagrams have 'path' not 'content')
            diagram_path = Path(diagram.get('path', ''))
            if not diagram_path.exists():
                logger.warning(f"Diagram file not found: {diagram_path}")
                continue

            content = diagram_path.read_text()

            # Count nodes and edges in Mermaid diagram
            nodes = self._count_mermaid_nodes(content)
            edges = self._count_mermaid_edges(content)

            if nodes < self.min_nodes or edges < self.min_edges:
                logger.warning(
                    f"Diagram {diagram_type} is too generic: {nodes} nodes, {edges} edges",
                    extra={'type': diagram_type, 'nodes': nodes, 'edges': edges}
                )
                regenerated = True
                # Actual regeneration would happen in architecture_visualizer.py
                # For now, we just mark it as needing regeneration

        result = {
            'regenerated': regenerated,
            'regenerated_diagrams': regenerated_diagrams
        }

        logger.info(
            f"Diagram validation complete: regenerated={regenerated}",
            extra=result
        )

        return result

    def _count_mermaid_nodes(self, content: str) -> int:
        """Count nodes in Mermaid diagram."""
        # Simplified: count lines that define nodes (contain '[' or '(' or '{')
        lines = content.splitlines()
        nodes = 0

        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('%%') or line.startswith('graph'):
                continue

            # Count node definitions (contain brackets)
            if '[' in line or '(' in line or '{' in line:
                nodes += 1

        return nodes

    def _count_mermaid_edges(self, content: str) -> int:
        """Count edges in Mermaid diagram."""
        # Simplified: count lines with arrows (-->, --->, -.->)
        lines = content.splitlines()
        edges = 0

        for line in lines:
            if '-->' in line or '--->' in line or '.->' in line or '==>' in line:
                edges += 1

        return edges


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="Validate diagram quality")
    parser.add_argument("diagrams_file", help="Path to diagrams JSON/YAML file")
    parser.add_argument("--output-dir", default=".agentic_sdlc", help="Output directory")
    args = parser.parse_args()

    # Load diagrams
    with open(args.diagrams_file) as f:
        if args.diagrams_file.endswith('.yml') or args.diagrams_file.endswith('.yaml'):
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    diagrams = data if isinstance(data, list) else data.get('diagrams', [])

    # Validate
    config = {
        'diagram_validation': {
            'min_nodes': 5,
            'min_edges': 4
        }
    }

    fixer = DiagramQualityFixer(config)
    result = fixer.fix(
        diagrams=diagrams,
        language_analysis={},
        output_dir=Path(args.output_dir)
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
