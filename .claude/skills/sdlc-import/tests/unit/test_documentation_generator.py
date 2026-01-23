#!/usr/bin/env python3
"""
Unit tests for documentation_generator.py
"""

import sys
import pytest
import tempfile
from pathlib import Path
import yaml

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from documentation_generator import DocumentationGenerator


@pytest.fixture
def config():
    """Default config for documentation generator"""
    return {
        "general": {
            "output_dir": ".agentic_sdlc"
        }
    }


@pytest.fixture
def temp_output():
    """Create temporary output directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestDocumentationGenerator:
    """Test documentation generation"""

    def test_init(self, config):
        """Test DocumentationGenerator initialization"""
        generator = DocumentationGenerator(config)

        assert generator.config == config
        assert generator.output_dir == Path(".agentic_sdlc")
        assert generator.templates_dir is not None

    def test_init_output_dir(self):
        """Test output directory configuration"""
        config = {"general": {"output_dir": "/custom/path"}}
        generator = DocumentationGenerator(config)

        assert generator.output_dir == Path("/custom/path")

    def test_generate_creates_output_dir(self, temp_output):
        """Test that generate() creates output directory"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {
            "analysis_id": "20260123-120000",
            "decisions": {"decisions": []},
            "threats": {},
            "tech_debt": {}
        }

        result = generator.generate(analysis_results)

        # Check directory was created
        assert generator.output_dir.exists()
        assert generator.output_dir.is_dir()

    def test_generate_no_analysis(self, temp_output):
        """Test generation with minimal analysis results"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {}
        result = generator.generate(analysis_results)

        # Should complete without errors
        assert "adrs" in result
        assert "threat_model" in result
        assert "tech_debt_report" in result
        assert "import_report" in result

    def test_generate_adrs_empty(self, temp_output):
        """Test ADR generation with no decisions"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {"decisions": []}
        adrs = generator._generate_adrs(decisions)

        assert len(adrs) == 0

    def test_generate_adrs_single(self, temp_output):
        """Test ADR generation with single decision"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {
            "decisions": [
                {
                    "id": "ADR-INFERRED-001",
                    "title": "Use PostgreSQL",
                    "category": "database",
                    "confidence": 0.85
                }
            ]
        }

        adrs = generator._generate_adrs(decisions)

        assert len(adrs) == 1
        assert "ADR-INFERRED-001.yml" in adrs[0]

    def test_generate_adrs_multiple(self, temp_output):
        """Test ADR generation with multiple decisions"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {
            "decisions": [
                {"id": "ADR-INFERRED-001", "title": "Use PostgreSQL"},
                {"id": "ADR-INFERRED-002", "title": "Use Redis"},
                {"id": "ADR-INFERRED-003", "title": "Use JWT"}
            ]
        }

        adrs = generator._generate_adrs(decisions)

        assert len(adrs) == 3
        assert any("ADR-INFERRED-001.yml" in adr for adr in adrs)
        assert any("ADR-INFERRED-002.yml" in adr for adr in adrs)
        assert any("ADR-INFERRED-003.yml" in adr for adr in adrs)

    def test_generate_adrs_file_creation(self, temp_output):
        """Test that ADR files are actually created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {
            "decisions": [
                {"id": "ADR-INFERRED-001", "title": "Use PostgreSQL"}
            ]
        }

        adrs = generator._generate_adrs(decisions)

        # Check file exists
        adr_file = Path(adrs[0])
        assert adr_file.exists()
        assert adr_file.is_file()
        assert adr_file.suffix == ".yml"

    def test_generate_adrs_yaml_format(self, temp_output):
        """Test that ADRs are in valid YAML format"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {
            "decisions": [
                {
                    "id": "ADR-INFERRED-001",
                    "title": "Use PostgreSQL",
                    "category": "database",
                    "confidence": 0.85
                }
            ]
        }

        adrs = generator._generate_adrs(decisions)

        # Read and parse YAML
        adr_file = Path(adrs[0])
        content = yaml.safe_load(adr_file.read_text())

        # Check structure
        assert content["id"] == "ADR-INFERRED-001"
        assert content["title"] == "Use PostgreSQL"
        assert content["category"] == "database"
        assert content["confidence"] == 0.85

    def test_generate_threat_model(self, temp_output):
        """Test threat model generation"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        threats = {
            "threats": {
                "spoofing": [{"id": "THREAT-SPOOF-001", "title": "JWT disabled"}]
            },
            "total": 1,
            "critical": 0,
            "high": 1
        }

        threat_file = generator._generate_threat_model(threats)

        assert "threat-model-inferred.yml" in threat_file

    def test_generate_threat_model_file_creation(self, temp_output):
        """Test that threat model file is created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        threats = {"total": 0}
        threat_file = generator._generate_threat_model(threats)

        # Check file exists
        file_path = Path(threat_file)
        assert file_path.exists()
        assert file_path.is_file()
        assert file_path.suffix == ".yml"

    def test_generate_tech_debt_report(self, temp_output):
        """Test tech debt report generation"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        tech_debt = {
            "total": 5,
            "total_effort": 20,
            "p0": 1,
            "p1": 2,
            "p2": 1,
            "p3": 1
        }

        report_file = generator._generate_tech_debt_report(tech_debt)

        assert "tech-debt-inferred.md" in report_file

    def test_generate_tech_debt_report_content(self, temp_output):
        """Test tech debt report content"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        tech_debt = {
            "total": 5,
            "total_effort": 20,
            "p0": 1,
            "p1": 2,
            "p2": 1,
            "p3": 1
        }

        report_file = generator._generate_tech_debt_report(tech_debt)
        content = Path(report_file).read_text()

        # Check content
        assert "# Technical Debt Report" in content
        assert "**Total Items:** 5" in content
        assert "**Total Effort:** 20h" in content
        assert "P0 (CRITICAL): 1 items" in content
        assert "P1 (HIGH): 2 items" in content
        assert "P2 (MEDIUM): 1 items" in content
        assert "P3 (LOW): 1 items" in content
        assert "SDLC Agêntico" in content

    def test_generate_tech_debt_report_markdown(self, temp_output):
        """Test tech debt report is valid markdown"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        tech_debt = {"total": 0, "total_effort": 0, "p0": 0, "p1": 0, "p2": 0, "p3": 0}
        report_file = generator._generate_tech_debt_report(tech_debt)
        content = Path(report_file).read_text()

        # Should have markdown headers and formatting
        assert content.startswith("# ")
        assert "##" in content
        assert "**" in content
        assert "-" in content

    def test_generate_import_report(self, temp_output):
        """Test import report generation"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {
            "analysis_id": "20260123-120000",
            "language_analysis": {"primary_language": "python"},
            "decisions": {"count": 5},
            "threats": {"total": 2},
            "tech_debt": {"total": 3}
        }

        report_file = generator._generate_import_report(analysis_results)

        assert "import-report.md" in report_file

    def test_generate_import_report_content(self, temp_output):
        """Test import report content"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {
            "analysis_id": "20260123-120000",
            "language_analysis": {"primary_language": "python"},
            "decisions": {"count": 5},
            "threats": {"total": 2},
            "tech_debt": {"total": 3}
        }

        report_file = generator._generate_import_report(analysis_results)
        content = Path(report_file).read_text()

        # Check content
        assert "# Import Analysis Report" in content
        assert "**Analysis ID:** 20260123-120000" in content
        assert "**Primary Language:** python" in content
        assert "**Decisions Extracted:** 5" in content
        assert "**Threats Identified:** 2" in content
        assert "**Tech Debt Items:** 3" in content
        assert "SDLC Agêntico" in content

    def test_generate_result_structure(self, temp_output):
        """Test that generate() returns correct structure"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {
            "analysis_id": "20260123-120000",
            "decisions": {"decisions": []},
            "threats": {},
            "tech_debt": {}
        }

        result = generator.generate(analysis_results)

        # Check structure
        assert "adrs" in result
        assert "threat_model" in result
        assert "tech_debt_report" in result
        assert "import_report" in result

        # Check types
        assert isinstance(result["adrs"], list)
        assert isinstance(result["threat_model"], str)
        assert isinstance(result["tech_debt_report"], str)
        assert isinstance(result["import_report"], str)

    def test_generate_all_files_created(self, temp_output):
        """Test that all files are created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        analysis_results = {
            "analysis_id": "20260123-120000",
            "decisions": {
                "decisions": [{"id": "ADR-INFERRED-001", "title": "Decision"}]
            },
            "threats": {"total": 1},
            "tech_debt": {"total": 1, "total_effort": 4, "p0": 1, "p1": 0, "p2": 0, "p3": 0}
        }

        result = generator.generate(analysis_results)

        # Check all files exist
        for adr in result["adrs"]:
            assert Path(adr).exists()
        assert Path(result["threat_model"]).exists()
        assert Path(result["tech_debt_report"]).exists()
        assert Path(result["import_report"]).exists()

    def test_adr_directory_creation(self, temp_output):
        """Test that ADR directory is created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        decisions = {
            "decisions": [{"id": "ADR-INFERRED-001", "title": "Decision"}]
        }

        adrs = generator._generate_adrs(decisions)

        # Check directory structure
        adr_dir = generator.output_dir / "corpus/nodes/decisions"
        assert adr_dir.exists()
        assert adr_dir.is_dir()

    def test_report_directory_creation(self, temp_output):
        """Test that reports directory is created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        tech_debt = {"total": 0, "total_effort": 0, "p0": 0, "p1": 0, "p2": 0, "p3": 0}
        report_file = generator._generate_tech_debt_report(tech_debt)

        # Check directory structure
        reports_dir = generator.output_dir / "reports"
        assert reports_dir.exists()
        assert reports_dir.is_dir()

    def test_security_directory_creation(self, temp_output):
        """Test that security directory is created"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        threats = {"total": 0}
        threat_file = generator._generate_threat_model(threats)

        # Check directory structure
        security_dir = generator.output_dir / "security"
        assert security_dir.exists()
        assert security_dir.is_dir()

    def test_generate_with_missing_keys(self, temp_output):
        """Test generation with missing keys in analysis results"""
        config = {"general": {"output_dir": str(temp_output / ".agentic_sdlc")}}
        generator = DocumentationGenerator(config)

        # Minimal analysis results (missing some keys)
        analysis_results = {"analysis_id": "test"}

        result = generator.generate(analysis_results)

        # Should complete without errors using defaults
        assert "adrs" in result
        assert "threat_model" in result
        assert len(result["adrs"]) == 0
