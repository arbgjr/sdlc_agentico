#!/usr/bin/env python3
"""
Unit tests for confidence_scorer.py
"""

import sys
import pytest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from confidence_scorer import (
    ConfidenceScorer,
    ConfidenceLevel,
    Evidence,
    ConfidenceScore
)


class TestConfidenceScorer:
    """Test confidence scoring"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return ConfidenceScorer()

    def test_evidence_quality_empty(self, scorer):
        """Test evidence quality with no evidence"""
        result = scorer.calculate_evidence_quality([])
        assert result == 0.0

    def test_evidence_quality_single(self, scorer):
        """Test evidence quality with single evidence"""
        evidence = [Evidence("file.py", 1, "pattern", 0.8, "pattern")]
        result = scorer.calculate_evidence_quality(evidence)
        assert result == 0.8

    def test_evidence_quality_multiple(self, scorer):
        """Test evidence quality with multiple evidence"""
        evidence = [
            Evidence("file1.py", 1, "pattern1", 1.0, "pattern"),
            Evidence("file2.py", 2, "pattern2", 0.8, "pattern"),
            Evidence("file3.py", 3, "pattern3", 0.6, "pattern"),
        ]
        result = scorer.calculate_evidence_quality(evidence)
        # Average: (1.0 + 0.8 + 0.6) / 3 = 0.8
        assert result == pytest.approx(0.8, abs=0.01)

    def test_evidence_quantity_empty(self, scorer):
        """Test evidence quantity with no evidence"""
        result = scorer.calculate_evidence_quantity([])
        assert result == 0.0

    def test_evidence_quantity_scale(self, scorer):
        """Test evidence quantity logarithmic scale"""
        # 1 evidence = 0.3
        evidence_1 = [Evidence("file.py", 1, "p", 1.0, "pattern")]
        assert scorer.calculate_evidence_quantity(evidence_1) == 0.3

        # 2 evidence = 0.5
        evidence_2 = evidence_1 + [Evidence("file2.py", 2, "p", 1.0, "pattern")]
        assert scorer.calculate_evidence_quantity(evidence_2) == 0.5

        # 3 evidence = 0.7
        evidence_3 = evidence_2 + [Evidence("file3.py", 3, "p", 1.0, "pattern")]
        assert scorer.calculate_evidence_quantity(evidence_3) == 0.7

        # 4 evidence = 0.85
        evidence_4 = evidence_3 + [Evidence("file4.py", 4, "p", 1.0, "pattern")]
        assert scorer.calculate_evidence_quantity(evidence_4) == 0.85

        # 5+ evidence = 1.0
        evidence_5 = evidence_4 + [Evidence("file5.py", 5, "p", 1.0, "pattern")]
        assert scorer.calculate_evidence_quantity(evidence_5) == 1.0

    def test_consistency_empty(self, scorer):
        """Test consistency with no evidence"""
        result = scorer.calculate_consistency([])
        assert result == 0.0

    def test_consistency_single_source(self, scorer):
        """Test consistency with single source and file"""
        evidence = [Evidence("file.py", 1, "pattern", 1.0, "pattern")]
        result = scorer.calculate_consistency(evidence)
        # source_diversity = 1/2 = 0.5
        # location_diversity = 1/3 = 0.333
        # consistency = (0.5 + 0.333) / 2 = 0.416
        assert result == pytest.approx(0.416, abs=0.01)

    def test_consistency_multiple_sources(self, scorer):
        """Test consistency with multiple sources"""
        evidence = [
            Evidence("file1.py", 1, "pattern1", 1.0, "pattern"),
            Evidence("file2.py", 2, "pattern2", 0.9, "llm"),
        ]
        result = scorer.calculate_consistency(evidence)
        # source_diversity = 2/2 = 1.0
        # location_diversity = 2/3 = 0.666
        # consistency = (1.0 + 0.666) / 2 = 0.833
        assert result == pytest.approx(0.833, abs=0.01)

    def test_consistency_multiple_files(self, scorer):
        """Test consistency with evidence from multiple files"""
        evidence = [
            Evidence("file1.py", 1, "pattern1", 1.0, "pattern"),
            Evidence("file2.py", 2, "pattern2", 0.9, "pattern"),
            Evidence("file3.py", 3, "pattern3", 0.8, "pattern"),
        ]
        result = scorer.calculate_consistency(evidence)
        # source_diversity = 1/2 = 0.5
        # location_diversity = 3/3 = 1.0 (capped)
        # consistency = (0.5 + 1.0) / 2 = 0.75
        assert result == pytest.approx(0.75, abs=0.01)

    def test_llm_bonus_no_llm(self, scorer):
        """Test LLM bonus without LLM evidence"""
        evidence = [
            Evidence("file.py", 1, "pattern", 1.0, "pattern"),
            Evidence("file2.py", 2, "pattern", 0.9, "pattern"),
        ]
        result = scorer.calculate_llm_bonus(evidence)
        assert result == 0.0

    def test_llm_bonus_with_llm(self, scorer):
        """Test LLM bonus with LLM evidence"""
        evidence = [
            Evidence("file.py", 1, "pattern", 1.0, "pattern"),
            Evidence("synthesized", 0, "llm result", 0.8, "llm"),
        ]
        result = scorer.calculate_llm_bonus(evidence)
        assert result == 1.0

    def test_calculate_high_confidence(self, scorer):
        """Test high confidence scenario (>= 0.8)"""
        # Multiple high-quality evidence from multiple sources
        evidence = [
            Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
            Evidence("requirements.txt", 3, "psycopg2", 0.9, "pattern"),
            Evidence("config.py", 12, "DATABASE_URL", 0.9, "pattern"),
            Evidence("models.py", 5, "db.Model", 0.85, "pattern"),
            Evidence("synthesized", 0, "PostgreSQL confirmed", 0.9, "llm"),
        ]
        score = scorer.calculate(evidence)

        assert score.overall >= 0.8
        assert score.level == ConfidenceLevel.HIGH
        assert score.evidence_count == 5
        assert score.evidence_quality > 0.8
        assert score.evidence_quantity == 1.0  # 5+ evidence
        assert score.llm_bonus == 1.0

    def test_calculate_medium_confidence(self, scorer):
        """Test medium confidence scenario (0.5-0.8)"""
        # Fewer evidence, no LLM
        evidence = [
            Evidence("auth.py", 23, "jwt.encode", 0.9, "pattern"),
            Evidence("requirements.txt", 5, "PyJWT", 0.8, "pattern"),
        ]
        score = scorer.calculate(evidence)

        assert 0.5 <= score.overall < 0.8
        assert score.level == ConfidenceLevel.MEDIUM
        assert score.evidence_count == 2
        assert score.llm_bonus == 0.0

    def test_calculate_low_confidence(self, scorer):
        """Test low confidence scenario (< 0.5)"""
        # Single low-quality evidence
        evidence = [
            Evidence("views.py", 15, "redis", 0.5, "pattern"),
        ]
        score = scorer.calculate(evidence)

        assert score.overall < 0.5
        assert score.level == ConfidenceLevel.LOW
        assert score.evidence_count == 1

    def test_calculate_empty_evidence(self, scorer):
        """Test calculation with no evidence"""
        score = scorer.calculate([])

        assert score.overall == 0.0
        assert score.level == ConfidenceLevel.LOW
        assert score.evidence_count == 0

    def test_to_dict(self, scorer):
        """Test conversion to dictionary"""
        evidence = [
            Evidence("file.py", 1, "pattern", 1.0, "pattern"),
            Evidence("file2.py", 2, "pattern", 0.8, "llm"),
        ]
        score = scorer.calculate(evidence)
        result = scorer.to_dict(score)

        # Check structure
        assert "overall" in result
        assert "level" in result
        assert "breakdown" in result
        assert "evidence_count" in result

        # Check breakdown
        assert "evidence_quality" in result["breakdown"]
        assert "evidence_quantity" in result["breakdown"]
        assert "consistency" in result["breakdown"]
        assert "llm_bonus" in result["breakdown"]

        # Check types
        assert isinstance(result["overall"], float)
        assert isinstance(result["level"], str)
        assert isinstance(result["evidence_count"], int)

        # Check rounding (3 decimal places)
        assert len(str(result["overall"]).split(".")[1]) <= 3

    def test_confidence_formula_weights(self, scorer):
        """Test that formula weights are correctly applied"""
        # Create evidence with known values
        evidence = [
            Evidence("file.py", 1, "p", 1.0, "pattern"),  # quality=1.0
            Evidence("file.py", 2, "p", 1.0, "pattern"),  # quantity=2 (0.5)
        ]
        score = scorer.calculate(evidence)

        # Manual calculation:
        # quality = 1.0
        # quantity = 0.5 (2 evidence)
        # consistency = (0.5 + 0.333) / 2 = 0.416 (1 source, 1 file)
        # llm_bonus = 0.0
        # overall = 0.4*1.0 + 0.3*0.5 + 0.2*0.416 + 0.1*0.0 = 0.633

        expected = 0.4 * 1.0 + 0.3 * 0.5 + 0.2 * 0.416 + 0.1 * 0.0
        assert score.overall == pytest.approx(expected, abs=0.01)

    def test_threshold_boundaries(self, scorer):
        """Test confidence level boundaries"""
        # Test HIGH boundary (>= 0.8)
        evidence_high = [
            Evidence("f1.py", 1, "p", 1.0, "pattern"),
            Evidence("f2.py", 2, "p", 1.0, "pattern"),
            Evidence("f3.py", 3, "p", 1.0, "pattern"),
            Evidence("f4.py", 4, "p", 1.0, "pattern"),
            Evidence("s", 0, "llm", 1.0, "llm"),
        ]
        score_high = scorer.calculate(evidence_high)
        assert score_high.overall >= 0.8
        assert score_high.level == ConfidenceLevel.HIGH

        # Test MEDIUM boundary (0.5 - 0.8)
        # Need 3+ evidence with decent quality to reach 0.5
        evidence_medium = [
            Evidence("f1.py", 1, "p", 0.7, "pattern"),
            Evidence("f2.py", 2, "p", 0.7, "pattern"),
            Evidence("f3.py", 3, "p", 0.7, "pattern"),
        ]
        score_medium = scorer.calculate(evidence_medium)
        assert 0.5 <= score_medium.overall < 0.8
        assert score_medium.level == ConfidenceLevel.MEDIUM

        # Test LOW (below 0.5)
        evidence_low = [Evidence("f.py", 1, "p", 0.3, "pattern")]
        score_low = scorer.calculate(evidence_low)
        assert score_low.overall < 0.5
        assert score_low.level == ConfidenceLevel.LOW

    def test_evidence_dataclass(self):
        """Test Evidence dataclass"""
        evidence = Evidence(
            file="test.py",
            line=42,
            pattern="test_pattern",
            quality=0.9,
            source="pattern"
        )

        assert evidence.file == "test.py"
        assert evidence.line == 42
        assert evidence.pattern == "test_pattern"
        assert evidence.quality == 0.9
        assert evidence.source == "pattern"

    def test_confidence_score_dataclass(self):
        """Test ConfidenceScore dataclass"""
        score = ConfidenceScore(
            overall=0.85,
            level=ConfidenceLevel.HIGH,
            evidence_quality=0.9,
            evidence_quantity=0.85,
            consistency=0.8,
            llm_bonus=1.0,
            evidence_count=5
        )

        assert score.overall == 0.85
        assert score.level == ConfidenceLevel.HIGH
        assert score.evidence_quality == 0.9
        assert score.evidence_quantity == 0.85
        assert score.consistency == 0.8
        assert score.llm_bonus == 1.0
        assert score.evidence_count == 5
