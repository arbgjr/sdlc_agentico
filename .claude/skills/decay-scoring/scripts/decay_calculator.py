#!/usr/bin/env python3
"""
Decay Score Calculator for RAG Corpus Nodes.

Calculates freshness scores based on age, validation, access patterns,
and content type stability.

Usage:
    # Calculate and display scores
    python decay_calculator.py

    # Update node files with scores
    python decay_calculator.py --update-nodes

    # Output as JSON
    python decay_calculator.py --json

    # Custom corpus path
    python decay_calculator.py --corpus /path/to/corpus
"""

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml


@dataclass
class DecayConfig:
    """Configuration for decay scoring."""

    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "age": 0.40,
            "validation": 0.30,
            "access": 0.20,
            "type_bonus": 0.10,
        }
    )
    half_lives: Dict[str, int] = field(
        default_factory=lambda: {
            "concepts": 365,
            "patterns": 270,
            "decisions": 180,
            "learnings": 120,
            "tactical": 60,
            "default": 180,
        }
    )
    thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "fresh": 0.70,
            "aging": 0.40,
            "stale": 0.20,
            "obsolete": 0.00,
        }
    )
    type_stability: Dict[str, float] = field(
        default_factory=lambda: {
            "concepts": 1.0,
            "patterns": 0.9,
            "decisions": 0.7,
            "learnings": 0.5,
            "tactical": 0.3,
        }
    )

    @classmethod
    def from_yaml(cls, path: Path) -> "DecayConfig":
        """Load configuration from YAML file."""
        if not path.exists():
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            weights=data.get("weights", cls().weights),
            half_lives=data.get("half_lives", cls().half_lives),
            thresholds=data.get("thresholds", cls().thresholds),
            type_stability=data.get("type_stability_bonus", cls().type_stability),
        )


@dataclass
class DecayMetadata:
    """Decay tracking metadata for a node."""

    last_validated_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_count_30d: int = 0
    access_count_total: int = 0
    decay_score: float = 1.0
    decay_status: str = "fresh"
    last_score_calculated: Optional[datetime] = None
    validation_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class NodeDecayResult:
    """Result of decay calculation for a single node."""

    node_id: str
    node_type: str
    score: float
    status: str
    components: Dict[str, float]
    days_since_creation: int
    days_since_validation: Optional[int]
    days_since_access: Optional[int]


class DecayCalculator:
    """Calculates decay scores for RAG corpus nodes."""

    def __init__(self, config: DecayConfig):
        self.config = config
        self.now = datetime.now(timezone.utc)

    def calculate_age_score(self, created_at: datetime, node_type: str) -> float:
        """Calculate age-based decay score using exponential decay."""
        days_old = (self.now - created_at).days
        half_life = self.config.half_lives.get(
            node_type, self.config.half_lives["default"]
        )
        lambda_decay = math.log(2) / half_life
        return math.exp(-lambda_decay * days_old)

    def calculate_validation_score(
        self, created_at: datetime, last_validated: Optional[datetime]
    ) -> float:
        """Calculate validation recency score."""
        if last_validated is None:
            # Never validated: use 50% of age score
            age_score = self.calculate_age_score(created_at, "default")
            return 0.5 * age_score

        days_since = (self.now - last_validated).days
        lambda_val = math.log(2) / 90  # 90-day half-life
        return math.exp(-lambda_val * days_since)

    def calculate_access_score(
        self, access_count_30d: int, last_accessed: Optional[datetime]
    ) -> float:
        """Calculate access frequency score with recency weighting."""
        if access_count_30d == 0:
            return 0.1  # Minimum score for unused content

        # Logarithmic scaling of access count
        log_score = min(1.0, math.log(1 + access_count_30d) / math.log(10))

        # Recency factor
        if last_accessed is None:
            recency_factor = 0.5
        else:
            days_since = (self.now - last_accessed).days
            recency_factor = math.exp(-0.1 * days_since)

        return log_score * recency_factor

    def calculate_type_bonus(self, node_type: str) -> float:
        """Get stability bonus for content type."""
        return self.config.type_stability.get(node_type, 0.5)

    def determine_status(self, score: float) -> str:
        """Determine decay status from score."""
        if score >= self.config.thresholds["fresh"]:
            return "fresh"
        elif score >= self.config.thresholds["aging"]:
            return "aging"
        elif score >= self.config.thresholds["stale"]:
            return "stale"
        else:
            return "obsolete"

    def calculate_node_score(
        self,
        node_id: str,
        node_type: str,
        created_at: datetime,
        decay_metadata: Optional[DecayMetadata] = None,
    ) -> NodeDecayResult:
        """Calculate complete decay score for a node."""
        if decay_metadata is None:
            decay_metadata = DecayMetadata()

        # Calculate component scores
        age_score = self.calculate_age_score(created_at, node_type)
        validation_score = self.calculate_validation_score(
            created_at, decay_metadata.last_validated_at
        )
        access_score = self.calculate_access_score(
            decay_metadata.access_count_30d, decay_metadata.last_accessed_at
        )
        type_bonus = self.calculate_type_bonus(node_type)

        # Calculate weighted final score
        weights = self.config.weights
        final_score = (
            weights["age"] * age_score
            + weights["validation"] * validation_score
            + weights["access"] * access_score
            + weights["type_bonus"] * type_bonus
        )

        # Clamp to [0, 1]
        final_score = max(0.0, min(1.0, final_score))

        # Calculate days metrics
        days_since_creation = (self.now - created_at).days
        days_since_validation = None
        if decay_metadata.last_validated_at:
            days_since_validation = (self.now - decay_metadata.last_validated_at).days
        days_since_access = None
        if decay_metadata.last_accessed_at:
            days_since_access = (self.now - decay_metadata.last_accessed_at).days

        return NodeDecayResult(
            node_id=node_id,
            node_type=node_type,
            score=round(final_score, 4),
            status=self.determine_status(final_score),
            components={
                "age_score": round(age_score, 4),
                "validation_score": round(validation_score, 4),
                "access_score": round(access_score, 4),
                "type_bonus": round(type_bonus, 4),
            },
            days_since_creation=days_since_creation,
            days_since_validation=days_since_validation,
            days_since_access=days_since_access,
        )


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string to datetime object."""
    if dt_str is None:
        return None
    try:
        # Handle various ISO formats
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def load_node_yaml(path: Path) -> Dict[str, Any]:
    """Load a node YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_node_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Save a node YAML file."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, default_style="'")


def process_corpus(
    corpus_path: Path, config: DecayConfig, update_nodes: bool = False
) -> Dict[str, Any]:
    """Process all nodes in the corpus and calculate decay scores."""
    calculator = DecayCalculator(config)
    results: Dict[str, Any] = {
        "last_calculated": datetime.now(timezone.utc).isoformat(),
        "calculation_version": "1.0.0",
        "summary": {
            "total_nodes": 0,
            "fresh": 0,
            "aging": 0,
            "stale": 0,
            "obsolete": 0,
            "average_score": 0.0,
        },
        "nodes": {},
        "review_queue": [],
    }

    nodes_dir = corpus_path / "nodes"
    if not nodes_dir.exists():
        print(f"Nodes directory not found: {nodes_dir}")
        return results

    total_score = 0.0
    node_count = 0

    # Process each node type directory
    for type_dir in nodes_dir.iterdir():
        if not type_dir.is_dir():
            continue

        node_type = type_dir.name

        for node_file in type_dir.glob("*.yml"):
            try:
                node_data = load_node_yaml(node_file)

                # Handle nested structure (some nodes wrap content)
                for key in ["decision", "learning", "pattern", "concept"]:
                    if key in node_data:
                        node_data = node_data[key]
                        break

                node_id = node_data.get("id", node_file.stem)

                # Parse dates
                created_at = parse_datetime(node_data.get("created_at"))
                if created_at is None:
                    # Use file modification time as fallback
                    created_at = datetime.fromtimestamp(
                        node_file.stat().st_mtime, tz=timezone.utc
                    )

                # Parse decay metadata if exists
                decay_meta = None
                if "decay_metadata" in node_data:
                    dm = node_data["decay_metadata"]
                    decay_meta = DecayMetadata(
                        last_validated_at=parse_datetime(dm.get("last_validated_at")),
                        last_accessed_at=parse_datetime(dm.get("last_accessed_at")),
                        access_count_30d=dm.get("access_count_30d", 0),
                        access_count_total=dm.get("access_count_total", 0),
                        validation_history=dm.get("validation_history", []),
                    )

                # Calculate score
                result = calculator.calculate_node_score(
                    node_id=node_id,
                    node_type=node_type,
                    created_at=created_at,
                    decay_metadata=decay_meta,
                )

                # Update results
                results["nodes"][node_id] = {
                    "score": result.score,
                    "status": result.status,
                    "type": result.node_type,
                    "days_since_creation": result.days_since_creation,
                    "days_since_validation": result.days_since_validation,
                    "components": result.components,
                }

                results["summary"][result.status] += 1
                total_score += result.score
                node_count += 1

                # Add to review queue if needed
                if result.status in ("stale", "obsolete"):
                    reason = f"Score {result.score:.2f}"
                    if result.days_since_validation:
                        reason += f", not validated in {result.days_since_validation} days"

                    results["review_queue"].append(
                        {
                            "id": node_id,
                            "score": result.score,
                            "status": result.status,
                            "reason": reason,
                            "suggested_action": (
                                "archive" if result.status == "obsolete" else "review"
                            ),
                        }
                    )

                # Update node file if requested
                if update_nodes:
                    # Re-load original file to preserve structure
                    original_data = load_node_yaml(node_file)

                    if "decay_metadata" not in original_data:
                        original_data["decay_metadata"] = {}

                    original_data["decay_metadata"]["decay_score"] = result.score
                    original_data["decay_metadata"]["decay_status"] = result.status
                    original_data["decay_metadata"]["last_score_calculated"] = (
                        datetime.now(timezone.utc).isoformat()
                    )

                    save_node_yaml(node_file, original_data)

            except Exception as e:
                print(f"Error processing {node_file}: {e}")

    # Calculate average
    results["summary"]["total_nodes"] = node_count
    if node_count > 0:
        results["summary"]["average_score"] = round(total_score / node_count, 4)

    # Sort review queue by score (lowest first)
    results["review_queue"].sort(key=lambda x: x["score"])

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Calculate decay scores for RAG corpus nodes"
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(".agentic_sdlc/corpus"),
        help="Path to corpus directory",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(".claude/skills/decay-scoring/config/decay_config.yml"),
        help="Path to decay configuration file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for decay index JSON",
    )
    parser.add_argument(
        "--update-nodes",
        action="store_true",
        help="Update node files with calculated scores",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Load configuration
    config = DecayConfig.from_yaml(args.config)

    # Process corpus
    results = process_corpus(args.corpus, config, args.update_nodes)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        summary = results["summary"]
        print(f"\nDecay Score Summary")
        print(f"{'='*40}")
        print(f"Total nodes:    {summary['total_nodes']}")
        print(f"Average score:  {summary['average_score']:.2f}")
        print(f"")
        print(f"Status breakdown:")
        print(f"  Fresh:    {summary['fresh']}")
        print(f"  Aging:    {summary['aging']}")
        print(f"  Stale:    {summary['stale']}")
        print(f"  Obsolete: {summary['obsolete']}")

        if results["review_queue"]:
            print(f"\nNodes requiring review:")
            for item in results["review_queue"][:10]:
                print(f"  - {item['id']}: {item['score']:.2f} ({item['status']})")

    # Save decay index
    output_path = args.output or (args.corpus / "decay_index.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    if not args.json:
        print(f"\nDecay index saved to: {output_path}")


if __name__ == "__main__":
    main()
