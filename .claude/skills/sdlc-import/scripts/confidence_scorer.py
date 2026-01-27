#!/usr/bin/env python3
"""
Confidence Scoring Module
Calculates confidence scores for inferred architecture decisions.

NEW (v2.1.7): Evidence-based Rubric with Breakdown

Rubric Tiers:
    code_and_tests_passing:      1.00 - Code + Tests + Runtime validation
    code_and_docs_consistent:    0.90 - Code + Documentation
    code_only:                    0.80 - Code evidence only
    docs_only:                    0.70 - Documentation only
    inferred_from_patterns:       0.60 - Inferred from patterns
    speculative:                  0.50 - Speculative/uncertain

Breakdown Components:
    - code_evidence:              Evidence from source code (0.0-1.0)
    - documentation_evidence:     Evidence from docs/comments (0.0-1.0)
    - runtime_validation:         Evidence from runtime (tests/validation) (0.0-1.0)
    - weighted_average:           Final score with margin (± uncertainty)
    - margin:                     Uncertainty margin (default ±0.10)

Validation Status:
    - NOT_VALIDATED:              Static analysis only
    - VALIDATED:                  Runtime validation performed
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
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
    # NEW (v2.1.7): Rubric-based breakdown
    code_evidence: float = 0.0
    documentation_evidence: float = 0.0
    runtime_validation: float = 0.0
    margin: float = 0.10
    validation_status: str = "NOT_VALIDATED"
    validation_recommendations: List[str] = field(default_factory=list)


class ConfidenceRubric:
    """
    NEW (v2.1.7): Evidence-based confidence rubric.

    Provides structured scoring based on evidence types.
    """

    # Rubric tiers (deterministic scoring)
    SCORES = {
        "code_and_tests_passing": 1.00,
        "code_and_docs_consistent": 0.90,
        "code_only": 0.80,
        "docs_only": 0.70,
        "inferred_from_patterns": 0.60,
        "speculative": 0.50,
    }

    @staticmethod
    def calculate(
        code_evidence: float,
        docs_evidence: float,
        runtime_validation: float
    ) -> ConfidenceScore:
        """
        Calculate confidence score using rubric.

        Args:
            code_evidence: Evidence from source code (0.0-1.0)
            docs_evidence: Evidence from documentation (0.0-1.0)
            runtime_validation: Evidence from runtime tests (0.0-1.0)

        Returns:
            ConfidenceScore with rubric-based scoring
        """
        # Weighted formula
        weighted = (
            code_evidence * 0.5 +
            docs_evidence * 0.3 +
            runtime_validation * 0.2
        )

        # Determine level
        if weighted >= 0.8:
            level = ConfidenceLevel.HIGH
        elif weighted >= 0.5:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        # Validation status
        if runtime_validation > 0:
            validation_status = "VALIDATED"
            recommendations = []
        else:
            validation_status = "NOT_VALIDATED - Static analysis only"
            recommendations = [
                "Consider adding runtime validation tests",
                "Validate with integration tests if possible"
            ]

        # Calculate margin (uncertainty)
        # Higher uncertainty if only one type of evidence
        evidence_types = sum([
            1 if code_evidence > 0 else 0,
            1 if docs_evidence > 0 else 0,
            1 if runtime_validation > 0 else 0
        ])

        if evidence_types == 1:
            margin = 0.15  # High uncertainty
        elif evidence_types == 2:
            margin = 0.10  # Medium uncertainty
        else:
            margin = 0.05  # Low uncertainty

        return ConfidenceScore(
            overall=weighted,
            level=level,
            evidence_quality=max(code_evidence, docs_evidence, runtime_validation),
            evidence_quantity=(code_evidence + docs_evidence + runtime_validation) / 3.0,
            consistency=evidence_types / 3.0,  # Consistency = diversity of evidence
            llm_bonus=0.0,  # Deprecated in rubric-based scoring
            evidence_count=evidence_types,
            code_evidence=code_evidence,
            documentation_evidence=docs_evidence,
            runtime_validation=runtime_validation,
            margin=margin,
            validation_status=validation_status,
            validation_recommendations=recommendations
        )

    @staticmethod
    def from_evidence_types(evidence: List[Evidence]) -> ConfidenceScore:
        """
        Calculate confidence from evidence list by categorizing evidence types.

        Categorization logic:
        - Code evidence: .cs/.py/.java files, source code patterns
        - Documentation evidence: README, docs/, comments, markdown files
        - Runtime validation: test files, migration files (validated at runtime)

        Args:
            evidence: List of Evidence objects

        Returns:
            ConfidenceScore using rubric
        """
        # Categorize evidence by file type and source
        code_evidences = []
        docs_evidences = []
        runtime_evidences = []

        for e in evidence:
            file_lower = e.file.lower()

            # Runtime evidence (tests, migrations executed at runtime)
            if any(pattern in file_lower for pattern in ['test', 'spec', 'migration', '__test__']):
                runtime_evidences.append(e)
            # Documentation evidence
            elif any(pattern in file_lower for pattern in ['readme', 'docs/', '.md', 'comment', 'docstring']):
                docs_evidences.append(e)
            # Code evidence (default)
            else:
                code_evidences.append(e)

        # Calculate scores for each category
        code_evidence = sum(e.quality for e in code_evidences) / len(code_evidences) if code_evidences else 0.0
        docs_evidence = sum(e.quality for e in docs_evidences) / len(docs_evidences) if docs_evidences else 0.0
        runtime_validation = sum(e.quality for e in runtime_evidences) / len(runtime_evidences) if runtime_evidences else 0.0

        logger.debug(
            "Categorized evidence",
            extra={
                "code_count": len(code_evidences),
                "docs_count": len(docs_evidences),
                "runtime_count": len(runtime_evidences),
                "code_score": code_evidence,
                "docs_score": docs_evidence,
                "runtime_score": runtime_validation
            }
        )

        return ConfidenceRubric.calculate(code_evidence, docs_evidence, runtime_validation)


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

    def calculate(self, evidence: List[Evidence], use_rubric: bool = True) -> ConfidenceScore:
        """
        Calculate overall confidence score.

        NEW (v2.1.7): Uses rubric-based scoring by default for better calibration.

        Args:
            evidence: List of Evidence objects
            use_rubric: Use ConfidenceRubric for scoring (default: True)

        Returns:
            ConfidenceScore object
        """
        if use_rubric:
            # NEW (v2.1.7): Use rubric-based scoring
            logger.debug("Using rubric-based confidence scoring")
            return ConfidenceRubric.from_evidence_types(evidence)

        # LEGACY: Original formula (deprecated, kept for compatibility)
        logger.warning("Using legacy confidence scoring (deprecated)")

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
            Dictionary representation with rubric breakdown (v2.1.7)
        """
        result = {
            "confidence": round(score.overall, 2),
            "level": score.level.value,
            "confidence_breakdown": {
                "code_evidence": round(score.code_evidence, 2),
                "documentation_evidence": round(score.documentation_evidence, 2),
                "runtime_validation": round(score.runtime_validation, 2),
                "weighted_average": round(score.overall, 2),
                "margin": f"±{score.margin:.2f}"
            },
            "validation_status": score.validation_status,
            "evidence_count": score.evidence_count
        }

        # Add validation recommendations if not validated
        if score.validation_recommendations:
            result["validation_recommendations"] = score.validation_recommendations

        return result


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
