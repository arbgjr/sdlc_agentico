#!/usr/bin/env python3
"""
Unit tests for project_path detection and correction (v2.1.7)

Tests the bug fix where skill base directory was being used as project_path
instead of the current working directory.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
def test_detects_skill_directory_as_project_path(
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path, monkeypatch
):
    """
    Test that ProjectAnalyzer detects when it's passed the skill directory
    and corrects it to use CWD instead.

    This simulates the bug where /sdlc-import without arguments was passed
    the skill's base directory (.claude/skills/sdlc-import) instead of the
    actual project directory.
    """
    # Import here to get mocked dependencies
    from project_analyzer import ProjectAnalyzer

    # Create fake project structure
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create fake skill directory inside project
    skill_dir = project_dir / ".claude" / "skills" / "sdlc-import"
    skill_dir.mkdir(parents=True)

    # Create marker file that identifies this as the skill directory
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "project_analyzer.py").touch()

    # Create config directory
    config_dir = skill_dir / "config"
    config_dir.mkdir()

    # Create minimal config file
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

    # Change to project directory (simulate CWD)
    monkeypatch.chdir(project_dir)

    # Initialize analyzer with skill directory path (BUG scenario)
    analyzer = ProjectAnalyzer(
        str(skill_dir),
        config_path=str(config_file)
    )

    # Verify that project_path was corrected to CWD
    assert analyzer.project_path == project_dir.resolve()
    assert analyzer.project_path != skill_dir.resolve()

    # Verify output directory is correct (in project root, not skill dir)
    expected_output = project_dir / ".project"
    assert analyzer.output_dir == expected_output


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
def test_normal_project_path_unchanged(
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path, monkeypatch
):
    """
    Test that a normal project path (not the skill directory) is not modified.
    """
    from project_analyzer import ProjectAnalyzer

    # Create fake project
    project_dir = tmp_path / "normal-project"
    project_dir.mkdir()

    # Create fake skill directory with config
    skill_dir = tmp_path / "skill-location" / "sdlc-import"
    skill_dir.mkdir(parents=True)
    config_dir = skill_dir / "config"
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

    # Initialize analyzer with normal project path
    analyzer = ProjectAnalyzer(
        str(project_dir),
        config_path=str(config_file)
    )

    # Verify project_path was NOT modified
    assert analyzer.project_path == project_dir.resolve()

    # Verify output directory is in project
    expected_output = project_dir / ".project"
    assert analyzer.output_dir == expected_output


@patch('project_analyzer.LanguageDetector')
@patch('project_analyzer.DecisionExtractor')
@patch('project_analyzer.ArchitectureVisualizer')
@patch('project_analyzer.ThreatModeler')
@patch('project_analyzer.TechDebtDetector')
def test_explicit_project_path_respected(
    mock_tech_debt, mock_threat, mock_arch, mock_decision, mock_lang,
    tmp_path
):
    """
    Test that explicitly provided project paths are always respected,
    even if they happen to be named 'sdlc-import'.
    """
    from project_analyzer import ProjectAnalyzer

    # Create a project actually named 'sdlc-import' (edge case)
    project_dir = tmp_path / "sdlc-import"
    project_dir.mkdir()

    # Create fake skill config
    skill_dir = tmp_path / "skills" / "sdlc-import"
    skill_dir.mkdir(parents=True)
    config_dir = skill_dir / "config"
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

    # This project is named 'sdlc-import' but is NOT the skill directory
    # (no scripts/project_analyzer.py marker file)
    analyzer = ProjectAnalyzer(
        str(project_dir),
        config_path=str(config_file)
    )

    # Should NOT be modified because it lacks the marker file
    assert analyzer.project_path == project_dir.resolve()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
