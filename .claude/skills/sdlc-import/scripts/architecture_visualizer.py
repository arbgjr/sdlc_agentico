#!/usr/bin/env python3
"""
Architecture Visualizer - Generate architecture diagrams
Generates Mermaid and DOT format diagrams.

References:
- awesome-copilot: architecture-diagram-generator.prompt
- awesome-copilot: dependency-graph-visualizer.prompt
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ArchitectureVisualizer:
    """Generate architecture diagrams"""

    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = Path(config['general']['output_dir']) / "architecture"

    def generate(self, project_path: Path, language_analysis: Dict, decisions: Dict) -> Dict:
        """Generate all diagram types"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        diagrams = []

        # Component diagram
        component_path = self.output_dir / "component-diagram.mmd"
        component_mmd = self._generate_component_diagram(language_analysis, decisions)
        component_path.write_text(component_mmd)
        diagrams.append({"name": "Component Diagram", "path": str(component_path), "type": "component", "format": "mermaid"})

        # Data flow diagram
        dataflow_path = self.output_dir / "data-flow.mmd"
        dataflow_mmd = self._generate_dataflow_diagram(decisions)
        dataflow_path.write_text(dataflow_mmd)
        diagrams.append({"name": "Data Flow", "path": str(dataflow_path), "type": "dataflow", "format": "mermaid"})

        logger.info(f"Generated {len(diagrams)} diagrams")
        return {"diagrams": diagrams, "count": len(diagrams)}

    def _generate_component_diagram(self, language_analysis: Dict, decisions: Dict) -> str:
        """Generate Mermaid component diagram"""
        lines = ["graph TD"]

        # Add frontend
        if language_analysis.get('frameworks', {}).get('frontend'):
            frontend = language_analysis['frameworks']['frontend'][0]
            lines.append(f"    Frontend[{frontend}]")

        # Add backend
        if language_analysis.get('frameworks', {}).get('backend'):
            backend = language_analysis['frameworks']['backend'][0]
            lines.append(f"    Backend[{backend}]")

        # Add database
        db_decision = next((d for d in decisions.get('decisions', []) if d['category'] == 'database'), None)
        if db_decision:
            lines.append(f"    Database[({db_decision['decision'].split()[1]})]")

        # Add connections
        if 'Frontend' in '\n'.join(lines) and 'Backend' in '\n'.join(lines):
            lines.append("    Frontend --> Backend")
        if 'Backend' in '\n'.join(lines) and 'Database' in '\n'.join(lines):
            lines.append("    Backend --> Database")

        return '\n'.join(lines)

    def _generate_dataflow_diagram(self, decisions: Dict) -> str:
        """Generate data flow diagram"""
        return """graph LR
    User((User)) --> |HTTP Request| API[API Gateway]
    API --> |Route| Backend[Backend Service]
    Backend --> |Query| DB[(Database)]
    DB --> |Result| Backend
    Backend --> |Response| API
    API --> |HTTP Response| User"""


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    parser.add_argument("--config")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else Path(__file__).parent.parent / "config" / "import_config.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    visualizer = ArchitectureVisualizer(config)
    result = visualizer.generate(Path(args.project_path), {}, {"decisions": []})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
