"""
Unit tests for v2.2.4 critical fixes.

Tests:
- C1: graph.json version path fix
- C2: adr_index.yml generation (config already enabled)
- C3: ADR YAML validation (alternatives_considered removal)
- G2: Version loading in documentation generator
"""

import sys
from pathlib import Path
import yaml
import tempfile
import shutil

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from graph_generator import GraphGenerator
from documentation_generator import DocumentationGenerator


def test_graph_generator_version_path():
    """
    C1: Verify graph generator finds VERSION file at correct path.

    Expected: .claude/VERSION exists and is loaded successfully.
    """
    # Mock minimal config
    config = {
        'graph_generation': {'enabled': True}
    }

    gen = GraphGenerator(config)
    version = gen._load_framework_version()

    # Version should be valid (semver format, may have 'v' prefix)
    assert version, "Version should not be empty"
    assert version != "unknown", "Version should not be 'unknown'"

    # Should match current version in VERSION file
    # Path from test file: tests/ -> sdlc-import/ -> skills/ -> .claude/ -> repo root
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    version_file = repo_root / ".claude" / "VERSION"
    assert version_file.exists(), f"VERSION file not found at {version_file}"

    version_data = yaml.safe_load(version_file.read_text())
    expected_version = version_data['version']
    assert version == expected_version, f"Version mismatch: {version} != {expected_version}"


def test_documentation_generator_version_loading():
    """
    G2: Verify documentation generator loads version dynamically.

    Expected: framework_version is loaded from VERSION file, not hardcoded.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'project_path': tmpdir,
            'general': {
                'output_dir': '.project'
            }
        }

        gen = DocumentationGenerator(config)

        # Version should be loaded and valid
        assert hasattr(gen, 'framework_version'), "DocumentationGenerator should have framework_version attribute"
        assert gen.framework_version, "Version should not be empty"
        assert gen.framework_version != "v1.0.0", "Version should not be hardcoded v1.0.0"

        # Should match VERSION file (may have 'v' prefix added)
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        version_file = repo_root / ".claude" / "VERSION"
        version_data = yaml.safe_load(version_file.read_text())
        expected_version = version_data['version']

        # Doc generator adds 'v' prefix if missing
        if not expected_version.startswith('v'):
            expected_version = f'v{expected_version}'

        assert gen.framework_version == expected_version, f"Version mismatch: {gen.framework_version} != {expected_version}"


def test_adr_yaml_validity():
    """
    C3: Verify generated ADRs have valid YAML without alternatives_considered.

    Expected:
    - ADRs without alternatives_considered parse successfully
    - YAML validation catches invalid structures
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'project_path': tmpdir,
            'general': {
                'output_dir': '.project'
            }
        }

        gen = DocumentationGenerator(config)

        # Test decision without problematic field
        decision = {
            "id": "ADR-TEST-001",
            "title": "Test Decision",
            "status": "accepted",
            "date": "2026-01-28",
            "context": "Test context for decision",
            "decision": "We decided to use approach X",
            "consequences": {
                "positive": ["Benefit 1"],
                "negative": ["Trade-off 1"]
            }
        }

        # Generate ADRs (should succeed)
        decisions = {"decisions": [decision]}
        output_dir = Path(tmpdir) / ".project"
        output_dir.mkdir(parents=True)
        gen.output_dir = output_dir

        adrs = gen._generate_adrs(decisions)

        # Verify file was created
        assert len(adrs) == 1, f"Expected 1 ADR, got {len(adrs)}"

        # Verify YAML is valid
        adr_file = Path(adrs[0])
        assert adr_file.exists(), f"ADR file not created: {adr_file}"

        adr_content = adr_file.read_text()
        parsed = yaml.safe_load(adr_content)

        # Verify structure
        assert parsed['id'] == "ADR-TEST-001"
        assert 'alternatives_considered' not in parsed, "alternatives_considered should be removed"


def test_adr_alternatives_considered_removal():
    """
    C3: Verify alternatives_considered field is removed from decisions.

    Expected: Field is removed before YAML generation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'project_path': tmpdir,
            'general': {
                'output_dir': '.project'
            }
        }

        gen = DocumentationGenerator(config)

        # Test decision WITH problematic field
        decision = {
            "id": "ADR-TEST-002",
            "title": "Test Decision with Alternatives",
            "status": "accepted",
            "date": "2026-01-28",
            "context": "Test context",
            "decision": "Decision text",
            "consequences": {
                "positive": ["Benefit"],
                "negative": ["Trade-off"]
            },
            # Problematic field (nested list structure)
            "alternatives_considered": [
                "Option A",
                ["Sub-option 1", "Sub-option 2"]  # Invalid YAML structure
            ]
        }

        # Generate ADRs
        decisions = {"decisions": [decision]}
        output_dir = Path(tmpdir) / ".project"
        output_dir.mkdir(parents=True)
        gen.output_dir = output_dir

        adrs = gen._generate_adrs(decisions)

        # Verify YAML is valid (should not raise)
        adr_file = Path(adrs[0])
        adr_content = adr_file.read_text()
        parsed = yaml.safe_load(adr_content)  # Should parse without error

        # Verify problematic field was removed
        assert 'alternatives_considered' not in parsed


def test_version_in_import_report():
    """
    G2: Verify import report includes framework version in header.

    Expected: Report header shows "SDLC Import Report - vX.Y.Z"
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'project_path': tmpdir,
            'general': {
                'output_dir': '.project'
            }
        }

        gen = DocumentationGenerator(config)

        # Mock analysis results
        analysis_results = {
            'analysis_id': 'test-123',
            'language_analysis': {'primary_language': 'Python'},
            'decisions': {'count': 5},
            'threats': {'total': 3},
            'tech_debt': {'total': 10}
        }

        # Generate report
        output_dir = Path(tmpdir) / ".project"
        output_dir.mkdir(parents=True)
        gen.output_dir = output_dir

        report_path = gen._generate_import_report(analysis_results)

        # Verify report exists
        report_file = Path(report_path)
        assert report_file.exists(), f"Report not created: {report_file}"

        # Verify header includes version
        report_content = report_file.read_text()
        assert "SDLC Import Report" in report_content, "Report should have SDLC Import Report header"
        assert gen.framework_version in report_content, f"Report should include version {gen.framework_version}"

        # Verify version is in first line (header)
        first_line = report_content.split('\n')[0]
        assert gen.framework_version in first_line, f"Version should be in header: {first_line}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
