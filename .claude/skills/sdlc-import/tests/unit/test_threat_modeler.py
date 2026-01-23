#!/usr/bin/env python3
"""
Unit tests for threat_modeler.py
"""

import sys
import pytest
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from threat_modeler import ThreatModeler


@pytest.fixture
def config():
    """Default config for threat modeling"""
    return {
        "threat_modeling": {
            "enabled": True,
            "escalation_threshold": 7.0
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


class TestThreatModeler:
    """Test threat modeling"""

    def test_init(self, config):
        """Test ThreatModeler initialization"""
        modeler = ThreatModeler(config)

        assert modeler.config == config
        assert modeler.enabled is True
        assert modeler.escalation_threshold == 7.0

    def test_init_disabled(self):
        """Test initialization with threat modeling disabled"""
        config = {
            "threat_modeling": {
                "enabled": False,
                "escalation_threshold": 7.0
            }
        }
        modeler = ThreatModeler(config)

        assert modeler.enabled is False

    def test_analyze_disabled(self, temp_project):
        """Test analysis when threat modeling is disabled"""
        config = {
            "threat_modeling": {
                "enabled": False,
                "escalation_threshold": 7.0
            }
        }
        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        assert result == {"status": "skipped"}

    def test_analyze_no_threats(self, config, temp_project):
        """Test analysis of clean project with no threats"""
        # Create safe files
        create_file(temp_project / "main.py", "print('hello world')\n")
        create_file(temp_project / "README.md", "# Project\n")

        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        assert "threats" in result
        assert result["total"] == 0
        assert result["critical"] == 0
        assert result["high"] == 0
        assert result["severity_distribution"]["CRITICAL"] == 0

    def test_detect_spoofing_jwt_disabled(self, config, temp_project):
        """Test detection of JWT verification disabled"""
        # Create file with JWT vulnerability
        create_file(
            temp_project / "auth.py",
            "import jwt\ntoken = jwt.decode(payload, verify=False)\n"
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_spoofing(temp_project)

        assert len(threats) >= 1
        threat = threats[0]
        assert threat["id"].startswith("THREAT-SPOOF-")
        assert "JWT" in threat["title"]
        assert threat["severity"] == "HIGH"
        assert threat["cvss_score"] == 7.5
        assert "auth.py" in threat["file"]
        assert "mitigation" in threat

    def test_detect_spoofing_no_threats(self, config, temp_project):
        """Test spoofing detection with no threats"""
        # Create safe file
        create_file(temp_project / "auth.py", "import jwt\ntoken = jwt.decode(payload)\n")

        modeler = ThreatModeler(config)
        threats = modeler._detect_spoofing(temp_project)

        assert len(threats) == 0

    def test_detect_info_disclosure_hardcoded_password(self, config, temp_project):
        """Test detection of hardcoded password"""
        # Create file with hardcoded secret
        create_file(
            temp_project / "config.py",
            'password = "SuperSecret123"\n'
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_info_disclosure(temp_project)

        assert len(threats) >= 1
        threat = threats[0]
        assert threat["id"].startswith("THREAT-INFO-")
        assert "Secret" in threat["title"]
        assert threat["severity"] == "CRITICAL"
        assert threat["cvss_score"] == 9.0
        assert "config.py" in threat["file"]

    def test_detect_info_disclosure_hardcoded_api_key(self, config, temp_project):
        """Test detection of hardcoded API key"""
        # Create file with hardcoded API key
        create_file(
            temp_project / "settings.py",
            'api_key = "sk-1234567890abcdef"\n'
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_info_disclosure(temp_project)

        assert len(threats) >= 1
        threat = threats[0]
        assert threat["severity"] == "CRITICAL"

    def test_detect_info_disclosure_hardcoded_secret(self, config, temp_project):
        """Test detection of hardcoded secret"""
        # Create file with hardcoded secret
        create_file(
            temp_project / "app.py",
            'secret = "my-secret-value"\n'
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_info_disclosure(temp_project)

        assert len(threats) >= 1

    def test_detect_info_disclosure_no_threats(self, config, temp_project):
        """Test info disclosure detection with no threats"""
        # Create safe file (environment variables)
        create_file(
            temp_project / "config.py",
            'import os\npassword = os.environ.get("PASSWORD")\n'
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_info_disclosure(temp_project)

        assert len(threats) == 0

    def test_detect_tampering(self, config, temp_project):
        """Test tampering detection (empty implementation)"""
        modeler = ThreatModeler(config)
        threats = modeler._detect_tampering(temp_project)

        assert threats == []

    def test_detect_repudiation(self, config, temp_project):
        """Test repudiation detection (empty implementation)"""
        modeler = ThreatModeler(config)
        threats = modeler._detect_repudiation(temp_project)

        assert threats == []

    def test_detect_dos(self, config, temp_project):
        """Test DoS detection (empty implementation)"""
        modeler = ThreatModeler(config)
        threats = modeler._detect_dos(temp_project)

        assert threats == []

    def test_detect_eop(self, config, temp_project):
        """Test elevation of privilege detection (empty implementation)"""
        modeler = ThreatModeler(config)
        threats = modeler._detect_eop(temp_project)

        assert threats == []

    def test_analyze_multiple_threats(self, config, temp_project):
        """Test analysis with multiple threats"""
        # Create files with multiple vulnerabilities
        create_file(
            temp_project / "auth.py",
            "import jwt\ntoken = jwt.decode(payload, verify=False)\n"
        )
        create_file(
            temp_project / "config.py",
            'password = "secret123"\n'
        )
        create_file(
            temp_project / "settings.py",
            'api_key = "key-abc"\n'
        )

        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        # Should detect: 1 spoofing + 2 info disclosure = 3 threats
        assert result["total"] >= 3
        assert result["critical"] >= 2  # 2 hardcoded secrets
        assert result["high"] >= 1  # JWT disabled

    def test_severity_distribution(self, config, temp_project):
        """Test severity distribution calculation"""
        # Create threats of different severities
        create_file(
            temp_project / "auth.py",
            "import jwt\ntoken = jwt.decode(payload, verify=False)\n"  # HIGH
        )
        create_file(
            temp_project / "config.py",
            'password = "secret"\n'  # CRITICAL
        )

        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        dist = result["severity_distribution"]
        assert "CRITICAL" in dist
        assert "HIGH" in dist
        assert "MEDIUM" in dist
        assert "LOW" in dist

        # Check counts
        assert dist["CRITICAL"] >= 1
        assert dist["HIGH"] >= 1
        assert dist["CRITICAL"] + dist["HIGH"] + dist["MEDIUM"] + dist["LOW"] == result["total"]

    def test_threat_id_format(self, config, temp_project):
        """Test threat ID format (THREAT-<CATEGORY>-###)"""
        # Create spoofing threat
        create_file(
            temp_project / "auth.py",
            "import jwt\ntoken = jwt.decode(payload, verify=False)\n"
        )

        modeler = ThreatModeler(config)
        threats = modeler._detect_spoofing(temp_project)

        assert len(threats) >= 1
        # ID format: THREAT-SPOOF-001
        assert threats[0]["id"].startswith("THREAT-SPOOF-")
        id_num = threats[0]["id"].split("-")[2]
        assert len(id_num) == 3  # 3-digit number
        assert id_num.isdigit()

    def test_analyze_result_structure(self, config, temp_project):
        """Test that analyze() returns correct structure"""
        create_file(temp_project / "main.py", "print('hello')\n")

        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        # Check required keys
        assert "threats" in result
        assert "total" in result
        assert "critical" in result
        assert "high" in result
        assert "severity_distribution" in result

        # Check threats structure (STRIDE categories)
        threats = result["threats"]
        assert "spoofing" in threats
        assert "tampering" in threats
        assert "repudiation" in threats
        assert "information_disclosure" in threats
        assert "denial_of_service" in threats
        assert "elevation_of_privilege" in threats

    def test_file_read_error_handling(self, config, temp_project):
        """Test that file read errors are handled gracefully"""
        # Create binary file that can't be read as text
        binary_file = temp_project / "binary.dat"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xFF\xFE')

        modeler = ThreatModeler(config)
        result = modeler.analyze(temp_project, {})

        # Should not crash, just skip the binary file
        assert "threats" in result
        assert result["total"] >= 0

    def test_escalation_threshold(self, config):
        """Test escalation threshold configuration"""
        modeler = ThreatModeler(config)

        assert modeler.escalation_threshold == 7.0

        # Change threshold
        config["threat_modeling"]["escalation_threshold"] = 9.0
        modeler2 = ThreatModeler(config)
        assert modeler2.escalation_threshold == 9.0
