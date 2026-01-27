#!/usr/bin/env python3
"""
Unit tests for output directory configuration (v2.1.7)

Tests that output_dir is correctly loaded from settings.json with proper fallback.
"""

import sys
import json
from pathlib import Path
import pytest
from unittest.mock import patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
@patch('project_analyzer.DocumentationGenerator')
@patch('project_analyzer.GraphGenerator')
@patch('project_analyzer.IssueCreator')
@patch('project_analyzer.MigrationAnalyzer')
@patch('project_analyzer.ADRValidator')
@patch('project_analyzer.InfrastructurePreserver')
def test_output_dir_from_settings_json(
    mock_infra, mock_adr, mock_migration, mock_issue, mock_graph, mock_doc,
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path
):
    """
    Test that output_dir is correctly loaded from settings.json
    """
    from project_analyzer import ProjectAnalyzer

    # Create project structure
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create .claude/settings.json with custom output_dir
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir()

    settings = {
        "sdlc": {
            "output": {
                "project_artifacts_dir": ".custom-output",
                "framework_artifacts_dir": ".agentic_sdlc"
            }
        }
    }

    settings_file = claude_dir / "settings.json"
    settings_file.write_text(json.dumps(settings, indent=2))

    # Create minimal config file
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "import_config.yml"
    config_file.write_text("""
general:
  output_dir: ".project"
  max_project_size: 900000
  analysis_timeout: 300

language_detection:
  enabled: true
  min_files: 3
  min_percentage: 5.0
  confidence_threshold: 0.7
  lsp_enabled: false

decision_extraction:
  enabled: true
  min_confidence: 0.5

threat_modeling:
  enabled: false

tech_debt:
  enabled: false
""")

    # Initialize analyzer
    analyzer = ProjectAnalyzer(
        str(project_dir),
        config_path=str(config_file)
    )

    # Verify output_dir is from settings.json, not import_config.yml
    assert analyzer.output_dir == project_dir / ".custom-output"
    assert analyzer.output_dir != project_dir / ".project"


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
@patch('project_analyzer.DocumentationGenerator')
@patch('project_analyzer.GraphGenerator')
@patch('project_analyzer.IssueCreator')
@patch('project_analyzer.MigrationAnalyzer')
@patch('project_analyzer.ADRValidator')
@patch('project_analyzer.InfrastructurePreserver')
def test_output_dir_fallback_to_config(
    mock_infra, mock_adr, mock_migration, mock_issue, mock_graph, mock_doc,
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path
):
    """
    Test that output_dir falls back to import_config.yml when settings.json doesn't exist
    """
    from project_analyzer import ProjectAnalyzer

    # Create project without .claude/settings.json
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create config file with output_dir
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "import_config.yml"
    config_file.write_text("""
general:
  output_dir: ".project"
  max_project_size: 900000
  analysis_timeout: 300

language_detection:
  enabled: true
  min_files: 3
  min_percentage: 5.0
  confidence_threshold: 0.7
  lsp_enabled: false

decision_extraction:
  enabled: true
  min_confidence: 0.5

threat_modeling:
  enabled: false

tech_debt:
  enabled: false
""")

    # Initialize analyzer (no settings.json)
    analyzer = ProjectAnalyzer(
        str(project_dir),
        config_path=str(config_file)
    )

    # Verify output_dir is from import_config.yml
    assert analyzer.output_dir == project_dir / ".project"


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
@patch('project_analyzer.DocumentationGenerator')
@patch('project_analyzer.GraphGenerator')
@patch('project_analyzer.IssueCreator')
@patch('project_analyzer.MigrationAnalyzer')
@patch('project_analyzer.ADRValidator')
@patch('project_analyzer.InfrastructurePreserver')
def test_output_dir_default_when_no_config(
    mock_infra, mock_adr, mock_migration, mock_issue, mock_graph, mock_doc,
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path
):
    """
    Test that output_dir defaults to .project when neither settings.json nor config specify it
    """
    from project_analyzer import ProjectAnalyzer

    # Create project
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create minimal config WITHOUT output_dir
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "import_config.yml"
    config_file.write_text("""
general:
  max_project_size: 900000
  analysis_timeout: 300

language_detection:
  enabled: true
  min_files: 3
  min_percentage: 5.0
  confidence_threshold: 0.7
  lsp_enabled: false

decision_extraction:
  enabled: true
  min_confidence: 0.5

threat_modeling:
  enabled: false

tech_debt:
  enabled: false
""")

    # Initialize analyzer
    analyzer = ProjectAnalyzer(
        str(project_dir),
        config_path=str(config_file)
    )

    # Verify output_dir defaults to .project
    assert analyzer.output_dir == project_dir / ".project"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
