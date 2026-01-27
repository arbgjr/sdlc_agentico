#!/usr/bin/env python3
"""
Unit tests for architecture_visualizer.py
"""

import sys
import pytest
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from architecture_visualizer import ArchitectureVisualizer


@pytest.fixture
def config():
    """Default config for visualizer"""
    return {
        "general": {
            "output_dir": ".project"
        }
    }


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        yield project_path


class TestArchitectureVisualizer:
    """Test architecture diagram generation"""

    def test_init(self, config):
        """Test ArchitectureVisualizer initialization"""
        visualizer = ArchitectureVisualizer(config)

        assert visualizer.config == config
        assert visualizer.output_dir == Path(".project/architecture")

    def test_init_output_dir(self):
        """Test output directory configuration"""
        config = {"general": {"output_dir": "/custom/path"}}
        visualizer = ArchitectureVisualizer(config)

        assert visualizer.output_dir == Path("/custom/path/architecture")

    def test_generate_creates_output_dir(self, config, temp_project):
        """Test that generate() creates output directory"""
        # Use temp_project as output dir
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check directory was created
        assert visualizer.output_dir.exists()
        assert visualizer.output_dir.is_dir()

    def test_generate_no_components(self, config, temp_project):
        """Test generation with empty project (no components)"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {}
        decisions = {"decisions": []}

        result = visualizer.generate(temp_project, language_analysis, decisions)

        # Should generate 2 diagrams (component + dataflow)
        assert result["count"] == 2
        assert len(result["diagrams"]) == 2

    def test_generate_component_diagram_frontend_only(self, config, temp_project):
        """Test component diagram with frontend only"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "frontend": ["React"]
            }
        }
        decisions = {"decisions": []}

        result = visualizer.generate(temp_project, language_analysis, decisions)

        # Check component diagram content
        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        assert "graph TD" in content
        assert "Frontend[React]" in content

    def test_generate_component_diagram_backend_only(self, config, temp_project):
        """Test component diagram with backend only"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "backend": ["Django"]
            }
        }
        decisions = {"decisions": []}

        result = visualizer.generate(temp_project, language_analysis, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        assert "Backend[Django]" in content

    def test_generate_component_diagram_database_only(self, config, temp_project):
        """Test component diagram with database decision only"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {}
        decisions = {
            "decisions": [
                {
                    "category": "database",
                    "decision": "Use PostgreSQL for database"
                }
            ]
        }

        result = visualizer.generate(temp_project, language_analysis, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        assert "Database[(PostgreSQL)]" in content

    def test_generate_component_diagram_full_stack(self, config, temp_project):
        """Test component diagram with frontend, backend, and database"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "frontend": ["React"],
                "backend": ["Django"]
            }
        }
        decisions = {
            "decisions": [
                {
                    "category": "database",
                    "decision": "Use PostgreSQL for database"
                }
            ]
        }

        result = visualizer.generate(temp_project, language_analysis, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        # Check all components
        assert "Frontend[React]" in content
        assert "Backend[Django]" in content
        assert "Database[(PostgreSQL)]" in content

        # Check connections
        assert "Frontend --> Backend" in content
        assert "Backend --> Database" in content

    def test_generate_component_diagram_connections(self, config, temp_project):
        """Test that component connections are correct"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "frontend": ["Vue"],
                "backend": ["Flask"]
            }
        }
        decisions = {"decisions": []}

        result = visualizer.generate(temp_project, language_analysis, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        # Should connect frontend to backend
        assert "Frontend --> Backend" in content

    def test_generate_dataflow_diagram(self, config, temp_project):
        """Test data flow diagram generation"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check dataflow diagram
        dataflow_path = visualizer.output_dir / "data-flow.mmd"
        content = dataflow_path.read_text()

        assert "graph LR" in content
        assert "User((User))" in content
        assert "API[API Gateway]" in content
        assert "Backend[Backend Service]" in content
        assert "DB[(Database)]" in content
        assert "HTTP Request" in content
        assert "HTTP Response" in content

    def test_generate_mermaid_syntax(self, config, temp_project):
        """Test that generated diagrams have valid Mermaid syntax"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "frontend": ["React"],
                "backend": ["Django"]
            }
        }

        result = visualizer.generate(temp_project, language_analysis, {"decisions": []})

        # Component diagram should start with 'graph TD'
        component_path = visualizer.output_dir / "component-diagram.mmd"
        component_content = component_path.read_text()
        assert component_content.startswith("graph TD")

        # Dataflow diagram should start with 'graph LR'
        dataflow_path = visualizer.output_dir / "data-flow.mmd"
        dataflow_content = dataflow_path.read_text()
        assert dataflow_content.startswith("graph LR")

    def test_generate_result_structure(self, config, temp_project):
        """Test that generate() returns correct structure"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check result structure
        assert "diagrams" in result
        assert "count" in result
        assert isinstance(result["diagrams"], list)
        assert result["count"] == len(result["diagrams"])

        # Check diagram structure
        for diagram in result["diagrams"]:
            assert "name" in diagram
            assert "path" in diagram
            assert "type" in diagram
            assert "format" in diagram
            assert diagram["format"] == "mermaid"

    def test_generate_file_creation(self, config, temp_project):
        """Test that diagram files are actually created"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check files exist
        component_path = visualizer.output_dir / "component-diagram.mmd"
        dataflow_path = visualizer.output_dir / "data-flow.mmd"

        assert component_path.exists()
        assert component_path.is_file()
        assert dataflow_path.exists()
        assert dataflow_path.is_file()

        # Check files are not empty
        assert len(component_path.read_text()) > 0
        assert len(dataflow_path.read_text()) > 0

    def test_component_diagram_database_extraction(self, config, temp_project):
        """Test database name extraction from decision text"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        # Test different database decision formats
        decisions = {
            "decisions": [
                {
                    "category": "database",
                    "decision": "Use MongoDB for database"
                }
            ]
        }

        result = visualizer.generate(temp_project, {}, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        # Should extract "MongoDB" from decision text
        assert "Database[(MongoDB)]" in content

    def test_generate_multiple_frameworks(self, config, temp_project):
        """Test that with multiple frameworks, only first is used"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        language_analysis = {
            "frameworks": {
                "frontend": ["React", "Vue", "Angular"],
                "backend": ["Django", "Flask"]
            }
        }

        result = visualizer.generate(temp_project, language_analysis, {"decisions": []})

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        # Should use first framework only
        assert "Frontend[React]" in content
        assert "Backend[Django]" in content
        assert "Vue" not in content
        assert "Flask" not in content

    def test_generate_diagram_types(self, config, temp_project):
        """Test that correct diagram types are set"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check diagram types
        types = [d["type"] for d in result["diagrams"]]
        assert "component" in types
        assert "dataflow" in types

    def test_generate_diagram_names(self, config, temp_project):
        """Test that diagram names are descriptive"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        result = visualizer.generate(temp_project, {}, {"decisions": []})

        # Check diagram names
        names = [d["name"] for d in result["diagrams"]]
        assert "Component Diagram" in names
        assert "Data Flow" in names

    def test_component_diagram_no_connections_without_components(self, config, temp_project):
        """Test that no connections are added when components don't exist"""
        config["general"]["output_dir"] = str(temp_project / ".agentic_sdlc")
        visualizer = ArchitectureVisualizer(config)

        # Empty language analysis
        language_analysis = {}
        decisions = {"decisions": []}

        result = visualizer.generate(temp_project, language_analysis, decisions)

        component_path = visualizer.output_dir / "component-diagram.mmd"
        content = component_path.read_text()

        # Should not have any connections
        assert "-->" not in content
