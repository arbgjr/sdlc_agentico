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
        # BUG FIX #2: Use absolute path (project_path + output_dir)
        project_path = Path(config['project_path'])
        self.output_dir = project_path / config['general']['output_dir'] / "architecture"

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

        # NEW (v2.1.7 - G3): Internal architecture diagram
        internal_arch_path = self.output_dir / "internal-architecture.mmd"
        internal_arch_mmd = self._generate_internal_architecture_diagram(language_analysis, decisions)
        internal_arch_path.write_text(internal_arch_mmd)
        diagrams.append({"name": "Internal Architecture", "path": str(internal_arch_path), "type": "internal", "format": "mermaid"})

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

    def _generate_internal_architecture_diagram(self, language_analysis: Dict, decisions: Dict) -> str:
        """
        NEW (v2.1.7 - G3): Generate internal architecture diagram.

        Shows:
        - Controller/Endpoint → MediatR Command/Query
        - Handler → Repository → DbContext
        - FluentValidation pipeline
        - AutoMapper

        Returns:
            Mermaid sequence diagram
        """
        # Detect if using CQRS/MediatR pattern (common in .NET)
        uses_mediatr = False
        backend_frameworks = language_analysis.get('frameworks', {}).get('backend', [])
        if any('asp' in fw.lower() or '.net' in fw.lower() for fw in backend_frameworks):
            uses_mediatr = True

        if uses_mediatr:
            # CQRS/MediatR architecture (ASP.NET)
            return """sequenceDiagram
    participant Client
    participant Endpoint as API Endpoint
    participant Validator as FluentValidator
    participant Mediator as MediatR
    participant Handler as CommandHandler
    participant Repo as Repository
    participant DB as DbContext

    Client->>Endpoint: POST /resource
    Endpoint->>Validator: Validate DTO
    Validator-->>Endpoint: Valid
    Endpoint->>Mediator: Send Command
    Mediator->>Handler: Handle Command
    Handler->>Repo: Save Entity
    Repo->>DB: SaveChanges()
    DB-->>Repo: Success
    Repo-->>Handler: Entity
    Handler-->>Mediator: Result
    Mediator-->>Endpoint: Result
    Endpoint-->>Client: 201 Created"""
        else:
            # Traditional MVC/layered architecture
            return """sequenceDiagram
    participant Client
    participant Controller
    participant Service
    participant Repository
    participant Database

    Client->>Controller: HTTP Request
    Controller->>Service: Business Logic
    Service->>Repository: Data Access
    Repository->>Database: Query
    Database-->>Repository: Result
    Repository-->>Service: Data
    Service-->>Controller: Response
    Controller-->>Client: HTTP Response"""


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
