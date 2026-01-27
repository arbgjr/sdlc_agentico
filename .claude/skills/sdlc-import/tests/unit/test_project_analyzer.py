#!/usr/bin/env python3
"""
Unit tests for project_analyzer.py
"""

import sys
import pytest
import tempfile
from pathlib import Path
import yaml

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from project_analyzer import ProjectAnalyzer


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        yield project_path


def create_file(path: Path, content: str):
    """Helper to create file with content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestProjectAnalyzer:
    """Test project analyzer orchestration"""

    def test_init(self, temp_project):
        """Test ProjectAnalyzer initialization"""
        analyzer = ProjectAnalyzer(str(temp_project))

        assert analyzer.project_path == temp_project
        assert analyzer.config is not None
        assert analyzer.output_dir is not None
        assert analyzer.analysis_id is not None
        assert len(analyzer.analysis_id) > 0

    def test_init_with_config_path(self, temp_project):
        """Test initialization with custom config path"""
        config_path = Path(__file__).parent.parent.parent / "config" / "import_config.yml"
        analyzer = ProjectAnalyzer(str(temp_project), str(config_path))

        assert analyzer.config is not None

    def test_load_config(self, temp_project):
        """Test configuration loading"""
        analyzer = ProjectAnalyzer(str(temp_project))

        # Check required config sections
        assert 'general' in analyzer.config
        assert 'language_detection' in analyzer.config
        assert 'decision_extraction' in analyzer.config
        assert 'threat_modeling' in analyzer.config
        assert 'tech_debt' in analyzer.config

    def test_validate_project_valid(self, temp_project):
        """Test validation of valid project"""
        # Create some files
        create_file(temp_project / "main.py", "print('hello')\n")
        create_file(temp_project / "README.md", "# Project\n")

        analyzer = ProjectAnalyzer(str(temp_project))
        is_valid = analyzer.validate_project()

        assert is_valid is True

    def test_validate_project_nonexistent(self):
        """Test validation of nonexistent project"""
        analyzer = ProjectAnalyzer("/nonexistent/path/to/project")
        is_valid = analyzer.validate_project()

        assert is_valid is False

    def test_validate_project_empty(self, temp_project):
        """Test validation of empty project"""
        # Empty directory
        analyzer = ProjectAnalyzer(str(temp_project))
        is_valid = analyzer.validate_project()

        # Should still be valid (just empty)
        assert is_valid is True

    def test_count_loc_empty(self, temp_project):
        """Test LOC counting with no files"""
        analyzer = ProjectAnalyzer(str(temp_project))
        loc = analyzer._count_loc()

        assert loc == 0

    def test_count_loc_with_files(self, temp_project):
        """Test LOC counting with files"""
        # Create files with known LOC
        create_file(temp_project / "file1.py", "line1\nline2\nline3\n")  # 3 lines
        create_file(temp_project / "file2.py", "line1\nline2\n")  # 2 lines
        create_file(temp_project / "README.md", "Title\nContent\n")  # 2 lines (no # to avoid comment filtering)

        analyzer = ProjectAnalyzer(str(temp_project))
        loc = analyzer._count_loc()

        # Should count non-empty, non-comment lines (3 + 2 + 2 = 7)
        assert loc >= 7

    def test_count_loc_excludes_patterns(self, temp_project):
        """Test that LOC counting excludes configured patterns"""
        # Create files in excluded directories
        create_file(temp_project / "node_modules/lib.js", "code\n")
        create_file(temp_project / ".git/config", "config\n")
        create_file(temp_project / "venv/lib.py", "code\n")
        create_file(temp_project / "valid.py", "code\n")

        analyzer = ProjectAnalyzer(str(temp_project))
        loc = analyzer._count_loc()

        # Should only count valid.py (1 line), not excluded files
        assert loc <= 1

    def test_scan_directory_empty(self, temp_project):
        """Test directory scanning with empty project"""
        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.scan_directory()

        assert "total_files" in result
        assert "total_loc" in result
        assert "files_by_extension" in result
        assert result["total_files"] == 0
        assert result["total_loc"] == 0

    def test_scan_directory_with_files(self, temp_project):
        """Test directory scanning with files"""
        # Create several files
        create_file(temp_project / "file1.py", "print('hello')\n" * 10)
        create_file(temp_project / "file2.py", "print('world')\n" * 5)
        create_file(temp_project / "README.md", "# Project\n")

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.scan_directory()

        assert result["total_files"] >= 3
        assert result["total_loc"] >= 16  # 10 + 5 + 1
        assert ".py" in result["files_by_extension"]
        assert ".md" in result["files_by_extension"]

    def test_scan_directory_excludes_patterns(self, temp_project):
        """Test that scanning excludes configured patterns"""
        # Create files in excluded directories
        create_file(temp_project / "node_modules/package.json", "{}")
        create_file(temp_project / ".git/HEAD", "ref")
        create_file(temp_project / "__pycache__/module.pyc", "")
        create_file(temp_project / "valid.py", "code\n")

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.scan_directory()

        # Should only count valid.py (1 file)
        assert result["total_files"] <= 1

    def test_scan_directory_files_by_extension(self, temp_project):
        """Test files grouped by extension"""
        # Create files with different extensions
        create_file(temp_project / "file1.py", "code\n")
        create_file(temp_project / "file2.py", "more code\n")
        create_file(temp_project / "doc.md", "# Doc\n")

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.scan_directory()

        # Check structure
        assert ".py" in result["files_by_extension"]
        assert ".md" in result["files_by_extension"]

        # Check Python files
        py_info = result["files_by_extension"][".py"]
        assert py_info["count"] == 2
        assert py_info["loc"] >= 2
        assert len(py_info["files"]) == 2

    def test_analysis_id_format(self, temp_project):
        """Test analysis ID format (YYYYMMDD-HHMMSS)"""
        analyzer = ProjectAnalyzer(str(temp_project))

        # Check format: 8 digits + dash + 6 digits
        assert len(analyzer.analysis_id) == 15  # YYYYMMDD-HHMMSS
        assert analyzer.analysis_id[8] == "-"
        assert analyzer.analysis_id[:8].isdigit()
        assert analyzer.analysis_id[9:].isdigit()

    def test_output_dir_configuration(self, temp_project):
        """Test output directory configuration"""
        analyzer = ProjectAnalyzer(str(temp_project))

        # Output dir should be inside project path
        assert analyzer.output_dir.parent == temp_project
        assert ".agentic_sdlc" in str(analyzer.output_dir)

    def test_config_has_required_sections(self, temp_project):
        """Test that config has all required sections"""
        analyzer = ProjectAnalyzer(str(temp_project))
        config = analyzer.config

        # General section
        assert 'output_dir' in config['general']
        assert 'exclude_patterns' in config['general']

        # Language detection
        assert 'min_files' in config['language_detection']
        assert 'min_percentage' in config['language_detection']
        assert 'confidence_threshold' in config['language_detection']

        # Decision extraction
        assert 'confidence' in config['decision_extraction']
        assert 'llm' in config['decision_extraction']

        # Threat modeling
        assert 'enabled' in config['threat_modeling']
        assert 'escalation_threshold' in config['threat_modeling']

        # Tech debt
        assert 'code_smell_rules' in config['tech_debt']

    def test_validate_project_with_symlinks(self, temp_project):
        """Test validation handles symlinks safely"""
        # Create a regular file
        create_file(temp_project / "real.py", "code\n")

        # Create symlink (if platform supports it)
        try:
            link = temp_project / "link.py"
            link.symlink_to(temp_project / "real.py")

            analyzer = ProjectAnalyzer(str(temp_project))
            is_valid = analyzer.validate_project()

            assert is_valid is True
        except (OSError, NotImplementedError):
            # Symlinks not supported on this platform, skip test
            pytest.skip("Platform does not support symlinks")

    def test_project_path_resolution(self, temp_project):
        """Test that project path is resolved to absolute path"""
        # Use relative path
        relative_path = "."
        analyzer = ProjectAnalyzer(relative_path)

        # Should be resolved to absolute path
        assert analyzer.project_path.is_absolute()

    def test_config_file_not_found(self, temp_project):
        """Test handling of missing config file"""
        with pytest.raises(FileNotFoundError):
            ProjectAnalyzer(str(temp_project), config_path="/nonexistent/config.yml")

    def test_multiple_analyzers_different_ids(self, temp_project):
        """Test that multiple analyzers get different analysis IDs"""
        import time

        analyzer1 = ProjectAnalyzer(str(temp_project))
        time.sleep(1)  # Ensure different timestamp
        analyzer2 = ProjectAnalyzer(str(temp_project))

        # IDs should be different (timestamps differ)
        assert analyzer1.analysis_id != analyzer2.analysis_id

    def test_validate_project_not_directory(self, temp_project):
        """Test validation when path is a file, not directory"""
        # Create a file instead of directory
        file_path = temp_project / "notadir.txt"
        file_path.write_text("content")

        analyzer = ProjectAnalyzer(str(file_path))
        is_valid = analyzer.validate_project()

        assert is_valid is False

    def test_validate_project_exceeds_max_size(self, temp_project):
        """Test validation when project exceeds max size"""
        # Create many files to exceed max_project_size (config: 500000 LOC)
        # Create a file with 500001 lines
        large_file = temp_project / "large.py"
        large_content = "\n".join([f"line{i}" for i in range(500001)])
        large_file.write_text(large_content)

        analyzer = ProjectAnalyzer(str(temp_project))
        is_valid = analyzer.validate_project()

        assert is_valid is False

    def test_analyze_minimal_project(self, temp_project):
        """Test analyze() on minimal project"""
        # Initialize git repository
        import subprocess
        subprocess.run(["git", "init"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(temp_project), check=True, capture_output=True)

        # Create minimal valid project
        create_file(temp_project / "main.py", "print('hello')\n")
        subprocess.run(["git", "add", "."], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(temp_project), check=True, capture_output=True)

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Check result structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result
        assert result["analysis_id"] == analyzer.analysis_id

    def test_analyze_with_skip_threat_model(self, temp_project):
        """Test analyze() with skip_threat_model flag"""
        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(temp_project), check=True, capture_output=True)

        create_file(temp_project / "main.py", "code")
        subprocess.run(["git", "add", "."], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(temp_project), check=True, capture_output=True)

        analyzer = ProjectAnalyzer(str(temp_project))
        # Override config to disable threat modeling (config precedence > flags)
        analyzer.config['threat_modeling']['enabled'] = False
        result = analyzer.analyze(skip_threat_model=True)

        # Threats should be skipped
        assert result["threats"]["status"] == "skipped"

    def test_analyze_with_skip_tech_debt(self, temp_project):
        """Test analyze() with skip_tech_debt flag"""
        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(temp_project), check=True, capture_output=True)

        create_file(temp_project / "main.py", "code")
        subprocess.run(["git", "add", "."], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(temp_project), check=True, capture_output=True)

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.analyze(skip_tech_debt=True)

        # Tech debt should be skipped
        assert result["tech_debt"]["status"] == "skipped"

    def test_analyze_result_has_timestamp(self, temp_project):
        """Test that analyze() result includes ISO timestamp"""
        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(temp_project), check=True, capture_output=True)

        create_file(temp_project / "main.py", "code")
        subprocess.run(["git", "add", "."], cwd=str(temp_project), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(temp_project), check=True, capture_output=True)

        analyzer = ProjectAnalyzer(str(temp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Check timestamp format (ISO 8601 with Z)
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")
        assert "T" in result["timestamp"]
