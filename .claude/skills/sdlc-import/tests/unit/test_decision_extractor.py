#!/usr/bin/env python3
"""
Unit tests for decision_extractor.py
"""

import sys
import pytest
import tempfile
from pathlib import Path
import yaml

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from decision_extractor import DecisionExtractor
from confidence_scorer import Evidence


@pytest.fixture
def config():
    """Load test config"""
    config_path = Path(__file__).parent.parent.parent / "config" / "import_config.yml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


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


class TestDecisionExtractor:
    """Test decision extraction"""

    def test_init(self, config):
        """Test DecisionExtractor initialization"""
        extractor = DecisionExtractor(config)

        assert extractor.config == config
        assert extractor.decision_patterns is not None
        assert extractor.confidence_thresholds is not None
        assert extractor.scorer is not None

    def test_find_evidence_postgresql(self, config, temp_project):
        """Test finding evidence for PostgreSQL"""
        # Create files with PostgreSQL evidence
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\n"
        )
        create_file(
            temp_project / "requirements.txt",
            "django==4.2.0\npsycopg2==2.9.0\n"
        )

        extractor = DecisionExtractor(config)

        # Get PostgreSQL patterns
        patterns = extractor.decision_patterns['decision_categories']['database']['patterns']['postgresql']
        evidence = extractor._find_evidence(temp_project, patterns)

        # Should find at least 1 evidence
        assert len(evidence) >= 1
        assert all(isinstance(e, Evidence) for e in evidence)
        assert all(e.source == "pattern" for e in evidence)

    def test_find_evidence_no_match(self, config, temp_project):
        """Test finding evidence with no matches"""
        # Create files without PostgreSQL evidence
        create_file(temp_project / "empty.py", "# No database config\n")

        extractor = DecisionExtractor(config)
        patterns = extractor.decision_patterns['decision_categories']['database']['patterns']['postgresql']
        evidence = extractor._find_evidence(temp_project, patterns)

        assert len(evidence) == 0

    def test_generate_title(self, config):
        """Test decision title generation"""
        extractor = DecisionExtractor(config)

        # Test database category
        title = extractor._generate_title("database", "postgresql")
        assert "postgresql" in title.lower()
        assert "database" in title.lower()

        # Test authentication category
        title = extractor._generate_title("authentication", "jwt")
        assert "jwt" in title.lower()
        assert "authentication" in title.lower()

    def test_generate_pattern_rationale(self, config):
        """Test pattern-based rationale generation"""
        extractor = DecisionExtractor(config)

        evidence = [
            Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
            Evidence("requirements.txt", 3, "psycopg2", 0.9, "pattern"),
        ]

        rationale = extractor._generate_pattern_rationale("database", "postgresql", evidence)

        assert "PostgreSQL" in rationale or "postgresql" in rationale
        assert "settings.py" in rationale
        assert len(rationale) > 0

    def test_create_decision_high_confidence(self, config, temp_project):
        """Test creating high-confidence decision"""
        extractor = DecisionExtractor(config)

        # Create high-quality evidence
        evidence = [
            Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
            Evidence("requirements.txt", 3, "psycopg2", 0.9, "pattern"),
            Evidence("models.py", 12, "db.Model", 0.9, "pattern"),
            Evidence("config.py", 5, "DATABASE_URL", 0.85, "pattern"),
        ]

        language_analysis = {"primary_language": "python"}
        decision = extractor._create_decision(
            1, "database", "postgresql", evidence,
            temp_project, language_analysis, no_llm=True
        )

        # Validate structure
        assert decision["id"] == "ADR-INFERRED-001"
        assert "postgresql" in decision["title"].lower()
        assert decision["category"] == "database"
        assert decision["status"] == "inferred"
        assert decision["evidence_count"] == 4
        assert decision["synthesized_by"] == "pattern"

        # Should be high confidence (4 high-quality evidence)
        assert decision["confidence"] >= 0.7

    def test_create_decision_low_confidence(self, config, temp_project):
        """Test creating low-confidence decision"""
        extractor = DecisionExtractor(config)

        # Create low-quality evidence
        evidence = [
            Evidence("views.py", 15, "redis", 0.5, "pattern"),
        ]

        language_analysis = {"primary_language": "python"}
        decision = extractor._create_decision(
            1, "caching", "redis", evidence,
            temp_project, language_analysis, no_llm=True
        )

        assert decision["confidence"] < 0.8
        assert decision["confidence_level"] == "low"
        assert decision["needs_validation"] is True

    def test_extract_django_project(self, config, temp_project):
        """Test extracting decisions from Django project"""
        # Create Django project files
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\n"
        )
        create_file(
            temp_project / "requirements.txt",
            "django==4.2.0\npsycopg2==2.9.0\ncelery==5.2.0\nredis==4.3.0\n"
        )
        create_file(
            temp_project / "tasks.py",
            "from celery import Celery\napp = Celery('myapp')\n"
        )

        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": "python", "frameworks": {"backend": ["Django"]}}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        # Validate result structure
        assert "decisions" in result
        assert "count" in result
        assert "confidence_distribution" in result

        # Should find at least database decision (PostgreSQL)
        assert result["count"] >= 1
        assert any(d["category"] == "database" for d in result["decisions"])

        # Decisions should be sorted by confidence (descending)
        confidences = [d["confidence"] for d in result["decisions"]]
        assert confidences == sorted(confidences, reverse=True)

    def test_extract_empty_project(self, config, temp_project):
        """Test extracting decisions from empty project"""
        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": None}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        assert result["count"] == 0
        assert len(result["decisions"]) == 0
        assert result["high_confidence"] == 0
        assert result["medium_confidence"] == 0
        assert result["low_confidence"] == 0

    def test_extract_with_no_llm(self, config, temp_project):
        """Test extraction with LLM disabled"""
        create_file(
            temp_project / "auth.py",
            "import jwt\ntoken = jwt.encode({'user': 1}, 'secret')\n"
        )

        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": "python"}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        # All decisions should be synthesized by pattern (not LLM)
        for decision in result["decisions"]:
            assert decision["synthesized_by"] == "pattern"

    def test_confidence_distribution(self, config, temp_project):
        """Test confidence distribution categorization"""
        # Create mixed-quality evidence
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\nCACHE = 'redis'\n"
        )
        create_file(
            temp_project / "requirements.txt",
            "django==4.2.0\npsycopg2==2.9.0\n"
        )
        create_file(
            temp_project / "views.py",
            "# Some code\nredis_client = None\n"
        )

        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": "python"}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        # Should have distribution
        dist = result["confidence_distribution"]
        assert "high" in dist
        assert "medium" in dist
        assert "low" in dist

        # Total should match
        assert dist["high"] + dist["medium"] + dist["low"] == result["count"]

    def test_decision_id_sequence(self, config, temp_project):
        """Test decision IDs are sequential"""
        # Create multiple decisions
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\n"
        )
        create_file(
            temp_project / "requirements.txt",
            "psycopg2==2.9.0\nredis==4.3.0\n"
        )

        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": "python"}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        # Extract IDs
        ids = [d["id"] for d in result["decisions"]]

        # Should be formatted as ADR-INFERRED-XXX
        for decision_id in ids:
            assert decision_id.startswith("ADR-INFERRED-")
            assert len(decision_id.split("-")[2]) == 3  # 3-digit number

    def test_evidence_in_decision(self, config, temp_project):
        """Test that evidence is included in decision"""
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\n"
        )

        extractor = DecisionExtractor(config)
        language_analysis = {"primary_language": "python"}

        result = extractor.extract(temp_project, language_analysis, no_llm=True)

        if result["count"] > 0:
            decision = result["decisions"][0]

            # Check evidence structure
            assert "evidence" in decision
            assert decision["evidence_count"] == len(decision["evidence"])

            # Each evidence should have required fields
            for evidence in decision["evidence"]:
                assert "file" in evidence
                assert "line" in evidence
                assert "pattern" in evidence
                assert "quality" in evidence
                assert "source" in evidence

    def test_generate_llm_rationale_llm_disabled(self, config):
        """Test LLM rationale generation when LLM is disabled"""
        config["decision_extraction"]["llm"]["enabled"] = False
        extractor = DecisionExtractor(config)

        evidence = [
            Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
            Evidence("requirements.txt", 3, "psycopg2", 0.9, "pattern"),
        ]

        rationale = extractor._generate_llm_rationale("database", "postgresql", evidence)

        # Should fall back to pattern rationale
        assert "PostgreSQL" in rationale or "postgresql" in rationale
        assert "settings.py" in rationale

    def test_generate_llm_rationale_llm_enabled(self, config):
        """Test LLM rationale generation when LLM is enabled"""
        config["decision_extraction"]["llm"]["enabled"] = True
        extractor = DecisionExtractor(config)

        evidence = [
            Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
        ]

        rationale = extractor._generate_llm_rationale("database", "postgresql", evidence)

        # Should return LLM placeholder (case-insensitive)
        assert "postgresql" in rationale.lower()
        assert "database" in rationale.lower()

    def test_find_evidence_with_directory(self, config, temp_project):
        """Test that glob directories are skipped"""
        # Create file with PostgreSQL evidence
        create_file(temp_project / "settings.py", "ENGINE = 'django.db.backends.postgresql'\n")

        # Create a directory with same pattern (should be skipped)
        (temp_project / "postgresql").mkdir()

        extractor = DecisionExtractor(config)
        patterns = extractor.decision_patterns['decision_categories']['database']['patterns']['postgresql']
        evidence = extractor._find_evidence(temp_project, patterns)

        # Should find evidence in file, but skip directory
        assert len(evidence) >= 1
        assert all(e.source == "pattern" for e in evidence)

    def test_find_evidence_with_unreadable_file(self, config, temp_project):
        """Test that file read errors are handled gracefully"""
        # Create a normal file with PostgreSQL evidence
        create_file(temp_project / "settings.py", "ENGINE = 'django.db.backends.postgresql'\n")

        # Create a binary file that will cause decode errors (should be skipped)
        binary_file = temp_project / "binary.dat"
        binary_file.write_bytes(b'\x00\x01\x02\xFF')

        extractor = DecisionExtractor(config)
        patterns = extractor.decision_patterns['decision_categories']['database']['patterns']['postgresql']

        # Should not crash, just skip unreadable files
        evidence = extractor._find_evidence(temp_project, patterns)

        # Should find evidence in readable file
        assert len(evidence) >= 1

    def test_main_cli_basic(self, config, temp_project, monkeypatch, capsys):
        """Test CLI main() function with basic arguments"""
        # Create test project with PostgreSQL evidence
        create_file(
            temp_project / "settings.py",
            "DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql'}}\n"
        )

        # Mock sys.argv to simulate CLI call
        import sys
        test_args = ["decision_extractor.py", str(temp_project), "--no-llm"]
        monkeypatch.setattr(sys, "argv", test_args)

        # Import and call main()
        from decision_extractor import main

        # Should execute without errors
        main()

        # Verify output
        captured = capsys.readouterr()
        assert "decisions" in captured.out
        assert "count" in captured.out
