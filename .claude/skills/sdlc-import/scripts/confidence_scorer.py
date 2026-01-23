#!/usr/bin/env python3
"""
Confidence Scoring Module
Calculates confidence scores for inferred architecture decisions.

Formula:
    confidence = 0.4 * evidence_quality +
                 0.3 * evidence_quantity +
                 0.2 * consistency +
                 0.1 * llm_bonus

Thresholds:
    HIGH   (>= 0.8) - Auto-accept
    MEDIUM (0.5-0.8) - Needs validation
    LOW    (< 0.5) - Create issue for manual review
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration"""
    HIGH = "high"      # >= 0.8
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"        # < 0.5


@dataclass
class Evidence:
    """Evidence for a decision"""
    file: str
    line: int
    pattern: str
    quality: float  # 0.0-1.0
    source: str     # "pattern" or "llm"


@dataclass
class ConfidenceScore:
    """Confidence score breakdown"""
    overall: float
    level: ConfidenceLevel
    evidence_quality: float
    evidence_quantity: float
    consistency: float
    llm_bonus: float
    evidence_count: int


class ConfidenceScorer:
    """Calculate confidence scores for decisions"""

    # Weights for confidence formula
    WEIGHTS = {
        'evidence_quality': 0.4,
        'evidence_quantity': 0.3,
        'consistency': 0.2,
        'llm_bonus': 0.1
    }

    # Thresholds
    THRESHOLDS = {
        'high': 0.8,
        'medium': 0.5,
        'low': 0.0
    }

    def __init__(self):
        """Initialize confidence scorer"""
        logger.info("Initialized ConfidenceScorer")

    def calculate_evidence_quality(self, evidence: List[Evidence]) -> float:
        """
        Calculate average evidence quality score.

        Args:
            evidence: List of Evidence objects

        Returns:
            Average quality score (0.0-1.0)
        """
        if not evidence:
            return 0.0

        total_quality = sum(e.quality for e in evidence)
        avg_quality = total_quality / len(evidence)

        logger.debug(
            "Calculated evidence quality",
            extra={
                "evidence_count": len(evidence),
                "avg_quality": avg_quality
            }
        )

        return avg_quality

    def calculate_evidence_quantity(self, evidence: List[Evidence]) -> float:
        """
        Calculate evidence quantity score.
        Uses logarithmic scale to handle varying evidence counts.

        Args:
            evidence: List of Evidence objects

        Returns:
            Quantity score (0.0-1.0)
        """
        import math

        count = len(evidence)
        if count == 0:
            return 0.0

        # Logarithmic scale: 1 evidence = 0.3, 3 = 0.6, 5+ = 1.0
        if count == 1:
            score = 0.3
        elif count == 2:
            score = 0.5
        elif count == 3:
            score = 0.7
        elif count == 4:
            score = 0.85
        else:
            score = 1.0

        logger.debug(
            "Calculated evidence quantity",
            extra={
                "evidence_count": count,
                "quantity_score": score
            }
        )

        return score

    def calculate_consistency(self, evidence: List[Evidence]) -> float:
        """
        Calculate consistency score.
        Checks if evidence comes from multiple sources and locations.

        Args:
            evidence: List of Evidence objects

        Returns:
            Consistency score (0.0-1.0)
        """
        if not evidence:
            return 0.0

        # Check source diversity (pattern vs LLM)
        sources = set(e.source for e in evidence)
        source_diversity = len(sources) / 2.0  # Max 2 sources

        # Check location diversity (different files)
        files = set(e.file for e in evidence)
        location_diversity = min(len(files) / 3.0, 1.0)  # Cap at 3 files

        # Consistency = average of diversities
        consistency = (source_diversity + location_diversity) / 2.0

        logger.debug(
            "Calculated consistency",
            extra={
                "source_diversity": source_diversity,
                "location_diversity": location_diversity,
                "consistency_score": consistency
            }
        )

        return consistency

    def calculate_llm_bonus(self, evidence: List[Evidence]) -> float:
        """
        Calculate LLM synthesis bonus.
        Provides bonus if LLM was used to synthesize decision.

        Args:
            evidence: List of Evidence objects

        Returns:
            LLM bonus score (0.0-1.0)
        """
        has_llm = any(e.source == "llm" for e in evidence)
        bonus = 1.0 if has_llm else 0.0

        logger.debug(
            "Calculated LLM bonus",
            extra={"has_llm": has_llm, "bonus": bonus}
        )

        return bonus

    def calculate(self, evidence: List[Evidence]) -> ConfidenceScore:
        """
        Calculate overall confidence score.

        Args:
            evidence: List of Evidence objects

        Returns:
            ConfidenceScore object
        """
        # Calculate components
        evidence_quality = self.calculate_evidence_quality(evidence)
        evidence_quantity = self.calculate_evidence_quantity(evidence)
        consistency = self.calculate_consistency(evidence)
        llm_bonus = self.calculate_llm_bonus(evidence)

        # Apply weights
        overall = (
            self.WEIGHTS['evidence_quality'] * evidence_quality +
            self.WEIGHTS['evidence_quantity'] * evidence_quantity +
            self.WEIGHTS['consistency'] * consistency +
            self.WEIGHTS['llm_bonus'] * llm_bonus
        )

        # Determine level
        if overall >= self.THRESHOLDS['high']:
            level = ConfidenceLevel.HIGH
        elif overall >= self.THRESHOLDS['medium']:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        score = ConfidenceScore(
            overall=overall,
            level=level,
            evidence_quality=evidence_quality,
            evidence_quantity=evidence_quantity,
            consistency=consistency,
            llm_bonus=llm_bonus,
            evidence_count=len(evidence)
        )

        logger.info(
            "Calculated confidence score",
            extra={
                "overall": overall,
                "level": level.value,
                "evidence_count": len(evidence)
            }
        )

        return score

    def to_dict(self, score: ConfidenceScore) -> Dict[str, Any]:
        """
        Convert ConfidenceScore to dictionary.

        Args:
            score: ConfidenceScore object

        Returns:
            Dictionary representation
        """
        return {
            "overall": round(score.overall, 3),
            "level": score.level.value,
            "breakdown": {
                "evidence_quality": round(score.evidence_quality, 3),
                "evidence_quantity": round(score.evidence_quantity, 3),
                "consistency": round(score.consistency, 3),
                "llm_bonus": round(score.llm_bonus, 3)
            },
            "evidence_count": score.evidence_count
        }


def main():
    """Test confidence scorer"""
    import json

    scorer = ConfidenceScorer()

    # Test case 1: High confidence (multiple high-quality evidence)
    evidence1 = [
        Evidence("settings.py", 45, "django.db.backends.postgresql", 1.0, "pattern"),
        Evidence("requirements.txt", 3, "psycopg2", 0.9, "pattern"),
        Evidence("config.py", 12, "DATABASE_URL", 0.8, "pattern"),
    ]
    score1 = scorer.calculate(evidence1)
    print("Test 1 (High confidence):")
    print(json.dumps(scorer.to_dict(score1), indent=2))
    print()

    # Test case 2: Medium confidence (fewer evidence)
    evidence2 = [
        Evidence("auth.py", 23, "jwt.encode", 0.9, "pattern"),
        Evidence("requirements.txt", 5, "PyJWT", 0.8, "pattern"),
    ]
    score2 = scorer.calculate(evidence2)
    print("Test 2 (Medium confidence):")
    print(json.dumps(scorer.to_dict(score2), indent=2))
    print()

    # Test case 3: Low confidence (single evidence + LLM)
    evidence3 = [
        Evidence("views.py", 15, "redis", 0.5, "pattern"),
        Evidence("synthesized", 0, "Redis caching inferred", 0.7, "llm"),
    ]
    score3 = scorer.calculate(evidence3)
    print("Test 3 (Low confidence with LLM):")
    print(json.dumps(scorer.to_dict(score3), indent=2))


if __name__ == "__main__":
    main()
