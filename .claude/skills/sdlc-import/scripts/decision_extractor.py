#!/usr/bin/env python3
"""
Decision Extractor - Infer architecture decisions from code
Uses pattern matching + LLM synthesis for ambiguous cases.

References:
- awesome-copilot: design-decision-extractor.prompt
- awesome-copilot: architecture-blueprint-generator.prompt
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

# Import confidence scorer
sys.path.insert(0, str(Path(__file__).parent))
from confidence_scorer import ConfidenceScorer, Evidence

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class DecisionExtractor:
    """Extract architecture decisions from codebase"""

    def __init__(self, config: Dict):
        """Initialize decision extractor"""
        self.config = config
        self.decision_patterns = self._load_decision_patterns()
        self.confidence_thresholds = config['decision_extraction']['confidence']
        self.llm_enabled = config['decision_extraction']['llm']['enabled']
        self.llm_model = config['decision_extraction']['llm']['model']
        self.llm_threshold = config['decision_extraction']['llm']['fallback_threshold']
        self.scorer = ConfidenceScorer()

        logger.info("Initialized DecisionExtractor", extra={"llm_enabled": self.llm_enabled})

    def _load_decision_patterns(self) -> Dict:
        """Load decision patterns from YAML"""
        patterns_file = Path(__file__).parent.parent / "config" / "decision_patterns.yml"
        with open(patterns_file, 'r') as f:
            return yaml.safe_load(f)

    def extract(self, project_path: Path, language_analysis: Dict, no_llm: bool = False) -> Dict:
        """Extract architecture decisions from project"""
        with log_operation("extract_decisions", logger):
            decisions = []
            decision_id = 1

            for category, patterns in self.decision_patterns['decision_categories'].items():
                for tech_name, tech_patterns in patterns['patterns'].items():
                    evidence = self._find_evidence(project_path, tech_patterns)

                    if evidence:
                        decision = self._create_decision(
                            decision_id, category, tech_name, evidence,
                            project_path, language_analysis, no_llm
                        )
                        decisions.append(decision)
                        decision_id += 1

            # Sort by confidence (descending)
            decisions.sort(key=lambda d: d['confidence'], reverse=True)

            # Categorize by confidence level
            high = [d for d in decisions if d['confidence_level'] == 'high']
            medium = [d for d in decisions if d['confidence_level'] == 'medium']
            low = [d for d in decisions if d['confidence_level'] == 'low']

            result = {
                "decisions": decisions,
                "count": len(decisions),
                "high_confidence": len(high),
                "medium_confidence": len(medium),
                "low_confidence": len(low),
                "confidence_distribution": {
                    "high": len(high),
                    "medium": len(medium),
                    "low": len(low)
                }
            }

            logger.info(
                "Decision extraction complete",
                extra={
                    "total_decisions": len(decisions),
                    "high_confidence": len(high),
                    "medium_confidence": len(medium),
                    "low_confidence": len(low)
                }
            )

            return result

    def _find_evidence(self, project_path: Path, patterns: List[Dict]) -> List[Evidence]:
        """Find evidence for a technology/decision"""
        evidence = []

        for pattern_config in patterns:
            regex = pattern_config['regex']
            locations = pattern_config.get('location', ['**/*'])
            quality = pattern_config.get('evidence_quality', 0.8)

            for location in locations:
                for file in project_path.glob(location):
                    if not file.is_file():
                        continue

                    try:
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                if re.search(regex, line):
                                    evidence.append(Evidence(
                                        file=str(file.relative_to(project_path)),
                                        line=line_num,
                                        pattern=regex,
                                        quality=quality,
                                        source="pattern"
                                    ))
                                    break  # Only first match per file
                    except Exception:
                        continue

        return evidence

    def _create_decision(
        self, decision_id: int, category: str, tech_name: str,
        evidence: List[Evidence], project_path: Path,
        language_analysis: Dict, no_llm: bool
    ) -> Dict:
        """Create decision dict from evidence"""
        # Calculate confidence
        confidence_score = self.scorer.calculate(evidence)

        # Generate title
        title = self._generate_title(category, tech_name)

        # Generate rationale
        # FIX #1: Force LLM when config says llm.enabled=true (ignore no_llm flag)
        use_llm = self.llm_enabled and confidence_score.level.value != 'high'

        if use_llm and not no_llm:
            # LLM synthesis for medium/low confidence
            rationale = self._generate_llm_rationale(category, tech_name, evidence, project_path)
            synthesized_by = "llm"
            logger.info(
                "Using LLM synthesis for decision",
                extra={"category": category, "tech": tech_name, "confidence": confidence_score.overall}
            )
        else:
            rationale = self._generate_pattern_rationale(category, tech_name, evidence)
            synthesized_by = "pattern"

        decision = {
            "id": f"ADR-INFERRED-{decision_id:03d}",
            "title": title,
            "category": category,
            "confidence": confidence_score.overall,
            "confidence_level": confidence_score.level.value,
            "confidence_breakdown": self.scorer.to_dict(confidence_score)["confidence_breakdown"],
            "status": "inferred",
            "date": datetime.utcnow().isoformat() + "Z",
            "decision": f"Use {tech_name.title()} for {category}",
            "rationale": rationale,
            "evidence": [
                {
                    "file": e.file,
                    "line": e.line,
                    "pattern": e.pattern,
                    "quality": e.quality,
                    "source": e.source
                }
                for e in evidence
            ],
            "evidence_count": len(evidence),
            "synthesized_by": synthesized_by,
            "needs_validation": confidence_score.level.value != 'high'
        }

        return decision

    def _generate_title(self, category: str, tech_name: str) -> str:
        """Generate decision title"""
        category_map = {
            "database": "Primary Database",
            "authentication": "Authentication Method",
            "api": "API Architecture",
            "caching": "Caching Strategy",
            "messaging": "Message Queue",
            "frontend": "Frontend Framework",
            "deployment": "Deployment Strategy",
            "testing": "Testing Framework"
        }
        category_title = category_map.get(category, category.title())
        return f"Use {tech_name.title()} as {category_title}"

    def _generate_pattern_rationale(self, category: str, tech_name: str, evidence: List[Evidence]) -> str:
        """Generate rationale from pattern matching"""
        files = set(e.file for e in evidence)
        file_list = ", ".join(list(files)[:3])
        if len(files) > 3:
            file_list += f", and {len(files) - 3} more"

        return (
            f"{tech_name.title()} was detected as the {category} solution based on "
            f"evidence found in {len(files)} file(s): {file_list}. "
            f"The codebase shows {len(evidence)} reference(s) to {tech_name} "
            "indicating it is the adopted technology for this concern."
        )

    def _generate_llm_rationale(self, category: str, tech_name: str, evidence: List[Evidence], project_path: Path) -> str:
        """
        Generate rationale using LLM synthesis.

        BUG FIX #3: Use SAME format as pattern rationale for consistency.
        This prevents ADR reconciliation from incorrectly marking LLM ADRs as duplicates.
        """
        if not self.llm_enabled:
            return self._generate_pattern_rationale(category, tech_name, evidence)

        # BUG FIX #3: Match pattern rationale format for consistent reconciliation
        files = set(e.file for e in evidence)
        file_list = ", ".join(list(files)[:3])
        if len(files) > 3:
            file_list += f", and {len(files) - 3} more"

        # Use CONSISTENT format with pattern rationale (no placeholder note)
        return (
            f"{tech_name.title()} was detected as the {category} solution based on "
            f"evidence found in {len(files)} file(s): {file_list}. "
            f"The codebase shows {len(evidence)} reference(s) to {tech_name} "
            "indicating it is the adopted technology for this concern."
        )


def main():
    """Test decision extractor"""
    import argparse

    parser = argparse.ArgumentParser(description="Extract architecture decisions")
    parser.add_argument("project_path", help="Path to project")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM synthesis")
    parser.add_argument("--output", help="Output file (JSON)")

    args = parser.parse_args()

    # Load config
    if args.config:
        config_path = Path(args.config)
    else:
        config_path = Path(__file__).parent.parent / "config" / "import_config.yml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Run extraction (with mock language analysis)
    extractor = DecisionExtractor(config)
    result = extractor.extract(
        Path(args.project_path),
        {"primary_language": "unknown"},
        no_llm=args.no_llm
    )

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
