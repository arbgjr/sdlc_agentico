#!/usr/bin/env python3
"""
Unit tests for tech_debt_detector.py
"""

import sys
import pytest
import tempfile
from pathlib import Path
import yaml

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from tech_debt_detector import TechDebtDetector


@pytest.fixture
def config():
    """Default config for tech debt detection"""
    return {
        "tech_debt": {
            "enabled": True
        }
    }


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


class TestTechDebtDetector:
    """Test technical debt detection"""

    def test_init(self, config):
        """Test TechDebtDetector initialization"""
        detector = TechDebtDetector(config)

        assert detector.config == config
        assert detector.enabled is True
        assert detector.rules is not None
        assert isinstance(detector.rules, dict)

    def test_init_disabled(self):
        """Test initialization with tech debt detection disabled"""
        config = {
            "tech_debt": {
                "enabled": False
            }
        }
        detector = TechDebtDetector(config)

        assert detector.enabled is False

    def test_load_rules(self, config):
        """Test rules loading from YAML"""
        detector = TechDebtDetector(config)

        # Check required sections exist
        assert "code_smells" in detector.rules
        assert "long_functions" in detector.rules["code_smells"]
        assert "threshold" in detector.rules["code_smells"]["long_functions"]

        # Check threshold value
        assert detector.rules["code_smells"]["long_functions"]["threshold"] == 50

    def test_scan_disabled(self, temp_project):
        """Test scan when tech debt detection is disabled"""
        config = {
            "tech_debt": {
                "enabled": False
            }
        }
        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        assert result == {"status": "skipped"}

    def test_scan_no_debt(self, config, temp_project):
        """Test scan of clean project with no debt"""
        # Create clean files
        create_file(
            temp_project / "main.py",
            "def small_function():\n    return True\n"
        )
        create_file(
            temp_project / "requirements.txt",
            "django==4.2.0\npytest==7.0.0\n"
        )

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        assert result["total"] == 0
        assert result["p0"] == 0
        assert result["total_effort"] == 0

    def test_detect_code_smells_long_function(self, config, temp_project):
        """Test detection of long function (> 50 lines)"""
        # Create file with long function (51 lines)
        long_function = "def long_function():\n" + "\n".join([f"    line{i}" for i in range(51)])
        create_file(temp_project / "code.py", long_function)

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        assert len(smells) >= 1
        smell = smells[0]
        assert smell["id"].startswith("DEBT-")
        assert "Long function" in smell["title"]
        assert smell["category"] == "code_smell"
        assert smell["priority"] == "P2"
        assert smell["effort_estimate"] == 4
        assert "code.py" in smell["file"]

    def test_detect_code_smells_short_function(self, config, temp_project):
        """Test that short functions are not flagged"""
        # Create file with short function (< 50 lines)
        short_function = "def short_function():\n    return True\n"
        create_file(temp_project / "code.py", short_function)

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        assert len(smells) == 0

    def test_detect_code_smells_no_issues(self, config, temp_project):
        """Test code smells detection with no issues"""
        # Create clean file
        create_file(
            temp_project / "clean.py",
            "def clean():\n    pass\n"
        )

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        assert len(smells) == 0

    def test_detect_deprecated_deps_django1(self, config, temp_project):
        """Test detection of Django 1.x (EOL)"""
        # Create requirements.txt with Django 1.x
        create_file(
            temp_project / "requirements.txt",
            "django==1.11.0\npytest==7.0.0\n"
        )

        detector = TechDebtDetector(config)
        deps = detector._detect_deprecated_deps(temp_project)

        assert len(deps) >= 1
        dep = deps[0]
        assert dep["id"] == "DEBT-DEP-001"
        assert "Django EOL" in dep["title"]
        assert dep["category"] == "deprecated_dependency"
        assert dep["priority"] == "P0"
        assert dep["effort_estimate"] == 16

    def test_detect_deprecated_deps_django2(self, config, temp_project):
        """Test detection of Django 2.x (EOL)"""
        # Create requirements.txt with Django 2.x
        create_file(
            temp_project / "requirements.txt",
            "django==2.2.0\n"
        )

        detector = TechDebtDetector(config)
        deps = detector._detect_deprecated_deps(temp_project)

        assert len(deps) >= 1

    def test_detect_deprecated_deps_no_issues(self, config, temp_project):
        """Test deprecated deps detection with no issues"""
        # Create requirements.txt with current Django
        create_file(
            temp_project / "requirements.txt",
            "django==4.2.0\npytest==7.0.0\n"
        )

        detector = TechDebtDetector(config)
        deps = detector._detect_deprecated_deps(temp_project)

        assert len(deps) == 0

    def test_detect_deprecated_deps_no_requirements(self, config, temp_project):
        """Test deprecated deps when no requirements.txt exists"""
        # No requirements.txt file
        detector = TechDebtDetector(config)
        deps = detector._detect_deprecated_deps(temp_project)

        assert len(deps) == 0

    def test_detect_security_hardcoded_password(self, config, temp_project):
        """Test detection of hardcoded password"""
        # Create file with hardcoded password
        create_file(
            temp_project / "config.py",
            'password = "SuperSecret123"\n'
        )

        detector = TechDebtDetector(config)
        issues = detector._detect_security_issues(temp_project)

        assert len(issues) >= 1
        issue = issues[0]
        assert issue["id"].startswith("DEBT-SEC-")
        assert "Hardcoded secret" in issue["title"]
        assert issue["category"] == "security"
        assert issue["priority"] == "P0"
        assert issue["effort_estimate"] == 2

    def test_detect_security_hardcoded_secret(self, config, temp_project):
        """Test detection of hardcoded secret"""
        # Create file with hardcoded secret
        create_file(
            temp_project / "settings.py",
            'secret = "my-secret-key"\n'
        )

        detector = TechDebtDetector(config)
        issues = detector._detect_security_issues(temp_project)

        assert len(issues) >= 1

    def test_detect_security_no_issues(self, config, temp_project):
        """Test security detection with no issues"""
        # Create file with environment variables (safe)
        create_file(
            temp_project / "config.py",
            'import os\npassword = os.environ.get("PASSWORD")\n'
        )

        detector = TechDebtDetector(config)
        issues = detector._detect_security_issues(temp_project)

        assert len(issues) == 0

    def test_scan_multiple_debt_items(self, config, temp_project):
        """Test scan with multiple debt items"""
        # Create file with long function
        long_function = "def long_function():\n" + "\n".join([f"    line{i}" for i in range(51)])
        create_file(temp_project / "code.py", long_function)

        # Create deprecated dependency
        create_file(temp_project / "requirements.txt", "django==1.11.0\n")

        # Create security issue
        create_file(temp_project / "config.py", 'password = "secret"\n')

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        # Should detect: 1 code smell + 1 deprecated dep + 1 security = 3 items
        assert result["total"] >= 3
        assert result["p0"] >= 2  # dep + security
        assert result["p2"] >= 1  # code smell

    def test_priority_distribution(self, config, temp_project):
        """Test priority distribution (P0-P3) calculation"""
        # Create mixed priority debt
        long_function = "def long_function():\n" + "\n".join([f"    line{i}" for i in range(51)])
        create_file(temp_project / "code.py", long_function)  # P2
        create_file(temp_project / "config.py", 'secret = "key"\n')  # P0

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        # Check debt_summary
        summary = result["debt_summary"]
        assert "P0" in summary
        assert "P1" in summary
        assert "P2" in summary
        assert "P3" in summary

        # Check counts
        assert summary["P0"] + summary["P1"] + summary["P2"] + summary["P3"] == result["total"]

    def test_effort_calculation(self, config, temp_project):
        """Test total effort calculation"""
        # Create debt with known effort
        long_function = "def long_function():\n" + "\n".join([f"    line{i}" for i in range(51)])
        create_file(temp_project / "code.py", long_function)  # 4 hours

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        # Total effort should be sum of all effort estimates
        assert result["total_effort"] >= 4

    def test_debt_id_format(self, config, temp_project):
        """Test debt ID format"""
        # Create code smell
        long_function = "def long_function():\n" + "\n".join([f"    line{i}" for i in range(51)])
        create_file(temp_project / "code.py", long_function)

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        # ID format: DEBT-###
        assert smells[0]["id"].startswith("DEBT-")
        id_num = smells[0]["id"].split("-")[1]
        assert id_num.isdigit()
        assert len(id_num) == 3

    def test_scan_result_structure(self, config, temp_project):
        """Test that scan() returns correct structure"""
        create_file(temp_project / "main.py", "def main():\n    pass\n")

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        # Check required keys
        assert "tech_debt" in result
        assert "total" in result
        assert "total_effort" in result
        assert "p0" in result
        assert "p1" in result
        assert "p2" in result
        assert "p3" in result
        assert "debt_summary" in result

        # Check types
        assert isinstance(result["tech_debt"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["total_effort"], (int, float))

    def test_file_read_error_handling(self, config, temp_project):
        """Test that file read errors are handled gracefully"""
        # Create binary file
        binary_file = temp_project / "binary.dat"
        binary_file.write_bytes(b'\x00\x01\x02\xFF')

        detector = TechDebtDetector(config)
        result = detector.scan(temp_project)

        # Should not crash
        assert "tech_debt" in result

    def test_code_smell_function_counting(self, config, temp_project):
        """Test that function line counting works correctly"""
        # Create file with function that has exactly 51 lines (should trigger)
        function_code = "def exactly_51_lines():\n" + "\n".join([f"    line{i}" for i in range(50)])
        create_file(temp_project / "test.py", function_code)

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        # Should detect function (51 > 50 threshold)
        assert len(smells) >= 1

    def test_multiple_functions_same_file(self, config, temp_project):
        """Test detection of multiple long functions in same file"""
        # Create file with 2 long functions
        code = (
            "def long_function1():\n" +
            "\n".join([f"    line{i}" for i in range(51)]) +
            "\n\ndef long_function2():\n" +
            "\n".join([f"    line{i}" for i in range(51)])
        )
        create_file(temp_project / "multi.py", code)

        detector = TechDebtDetector(config)
        smells = detector._detect_code_smells(temp_project)

        # Should detect both functions
        assert len(smells) >= 2
