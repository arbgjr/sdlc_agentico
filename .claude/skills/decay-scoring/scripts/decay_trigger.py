#!/usr/bin/env python3
"""
Decay Trigger - Generate Review Suggestions and Curation Actions.

Analyzes decay scores and generates actionable suggestions for
maintaining corpus freshness.

Usage:
    # Generate full report
    python decay_trigger.py

    # Filter by priority
    python decay_trigger.py --priority critical

    # Output as JSON
    python decay_trigger.py --json

    # Save report to file
    python decay_trigger.py --output report.json
"""

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class ReviewSuggestion:
    """A suggested review action for a node."""

    node_id: str
    node_type: str
    score: float
    status: str
    priority: str  # critical, high, medium, low
    action: str  # review, validate, archive, merge, split
    reason: str
    suggested_reviewer: Optional[str] = None


@dataclass
class CurationReport:
    """Report of curation actions needed."""

    generated_at: str
    corpus_health: str  # healthy, needs_attention, critical
    health_score: float
    total_nodes: int
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class DecayTrigger:
    """Generates review suggestions based on decay scores."""

    def __init__(self, decay_index: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        self.index = decay_index
        self.config = config or {}
        self.now = datetime.now(timezone.utc)

    def assess_corpus_health(self) -> tuple:
        """Assess overall corpus health."""
        summary = self.index.get("summary", {})
        total = summary.get("total_nodes", 0)

        if total == 0:
            return "empty", 0.0

        obsolete_ratio = summary.get("obsolete", 0) / total
        stale_ratio = summary.get("stale", 0) / total
        avg_score = summary.get("average_score", 0.5)

        # Calculate health score
        health_score = avg_score * (1 - obsolete_ratio * 2 - stale_ratio)
        health_score = max(0.0, min(1.0, health_score))

        # Determine health status
        if obsolete_ratio > 0.1 or health_score < 0.4:
            status = "critical"
        elif stale_ratio > 0.2 or health_score < 0.6:
            status = "needs_attention"
        else:
            status = "healthy"

        return status, round(health_score, 2)

    def determine_priority(self, score: float, status: str) -> str:
        """Determine review priority based on score and status."""
        if status == "obsolete":
            return "critical"
        elif score < 0.25:
            return "high"
        elif status == "stale":
            return "medium"
        else:
            return "low"

    def suggest_action(self, node_id: str, node_data: Dict[str, Any]) -> str:
        """Suggest appropriate action for a node."""
        status = node_data.get("status", "fresh")
        score = node_data.get("score", 1.0)
        days_since_validation = node_data.get("days_since_validation")

        if status == "obsolete":
            return "archive"
        elif days_since_validation and days_since_validation > 180:
            return "validate"
        elif score < 0.3:
            return "review"
        else:
            return "validate"

    def generate_reason(self, node_id: str, node_data: Dict[str, Any]) -> str:
        """Generate human-readable reason for suggestion."""
        status = node_data.get("status", "fresh")
        score = node_data.get("score", 1.0)
        days = node_data.get("days_since_validation")
        components = node_data.get("components", {})

        reasons: List[str] = []

        if status == "obsolete":
            reasons.append(f"Score critically low ({score:.2f})")
        elif status == "stale":
            reasons.append(f"Content is stale (score: {score:.2f})")

        if days and days > 90:
            reasons.append(f"Not validated in {days} days")

        if components.get("access_score", 1.0) < 0.2:
            reasons.append("Rarely accessed")

        if components.get("age_score", 1.0) < 0.3:
            reasons.append("Content is aging")

        return "; ".join(reasons) if reasons else "Routine review recommended"

    def generate_suggestions(self) -> List[ReviewSuggestion]:
        """Generate all review suggestions."""
        suggestions: List[ReviewSuggestion] = []

        for node_id, node_data in self.index.get("nodes", {}).items():
            status = node_data.get("status", "fresh")
            score = node_data.get("score", 1.0)

            # Only suggest for aging, stale, or obsolete
            if status in ("aging", "stale", "obsolete"):
                suggestion = ReviewSuggestion(
                    node_id=node_id,
                    node_type=node_data.get("type", "unknown"),
                    score=score,
                    status=status,
                    priority=self.determine_priority(score, status),
                    action=self.suggest_action(node_id, node_data),
                    reason=self.generate_reason(node_id, node_data),
                )
                suggestions.append(suggestion)

        # Sort by priority then score
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda s: (priority_order[s.priority], s.score))

        return suggestions

    def generate_report(self) -> CurationReport:
        """Generate complete curation report."""
        health_status, health_score = self.assess_corpus_health()
        suggestions = self.generate_suggestions()

        # Summarize by priority
        summary = {
            "by_priority": {
                "critical": len([s for s in suggestions if s.priority == "critical"]),
                "high": len([s for s in suggestions if s.priority == "high"]),
                "medium": len([s for s in suggestions if s.priority == "medium"]),
                "low": len([s for s in suggestions if s.priority == "low"]),
            },
            "by_action": {
                "archive": len([s for s in suggestions if s.action == "archive"]),
                "review": len([s for s in suggestions if s.action == "review"]),
                "validate": len([s for s in suggestions if s.action == "validate"]),
            },
        }

        return CurationReport(
            generated_at=self.now.isoformat(),
            corpus_health=health_status,
            health_score=health_score,
            total_nodes=self.index.get("summary", {}).get("total_nodes", 0),
            suggestions=[
                {
                    "node_id": s.node_id,
                    "node_type": s.node_type,
                    "score": s.score,
                    "status": s.status,
                    "priority": s.priority,
                    "action": s.action,
                    "reason": s.reason,
                }
                for s in suggestions
            ],
            summary=summary,
        )


def format_report_text(report: CurationReport) -> str:
    """Format report as human-readable text."""
    lines = [
        "=" * 60,
        "CORPUS CURATION REPORT",
        f"Generated: {report.generated_at}",
        "=" * 60,
        "",
        f"Corpus Health: {report.corpus_health.upper()} (score: {report.health_score})",
        f"Total Nodes: {report.total_nodes}",
        "",
        "SUMMARY",
        "-" * 40,
        "By Priority:",
        f"  Critical: {report.summary['by_priority']['critical']}",
        f"  High:     {report.summary['by_priority']['high']}",
        f"  Medium:   {report.summary['by_priority']['medium']}",
        f"  Low:      {report.summary['by_priority']['low']}",
        "",
        "By Action:",
        f"  Archive:  {report.summary['by_action']['archive']}",
        f"  Review:   {report.summary['by_action']['review']}",
        f"  Validate: {report.summary['by_action']['validate']}",
    ]

    if report.suggestions:
        lines.extend(["", "REVIEW QUEUE", "-" * 40])

        for s in report.suggestions[:20]:  # Top 20
            lines.append(f"[{s['priority'].upper():8}] {s['node_id']}")
            lines.append(f"           Action: {s['action']} | Score: {s['score']:.2f}")
            lines.append(f"           Reason: {s['reason']}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate curation suggestions from decay scores"
    )
    parser.add_argument(
        "--decay-index",
        type=Path,
        default=Path(".agentic_sdlc/corpus/decay_index.json"),
        help="Path to decay index JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for curation report",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of text",
    )
    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low", "all"],
        default="all",
        help="Filter suggestions by priority",
    )

    args = parser.parse_args()

    # Load decay index
    if not args.decay_index.exists():
        print(f"Decay index not found: {args.decay_index}")
        print("Run decay_calculator.py first to generate the index.")
        return 1

    with open(args.decay_index, "r", encoding="utf-8") as f:
        decay_index = json.load(f)

    # Generate report
    trigger = DecayTrigger(decay_index, {})
    report = trigger.generate_report()

    # Filter by priority if requested
    if args.priority != "all":
        report.suggestions = [s for s in report.suggestions if s["priority"] == args.priority]

    # Output
    if args.json:
        output = {
            "generated_at": report.generated_at,
            "corpus_health": report.corpus_health,
            "health_score": report.health_score,
            "total_nodes": report.total_nodes,
            "summary": report.summary,
            "suggestions": report.suggestions,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(format_report_text(report))

    # Save if output path specified
    if args.output:
        output_data = {
            "generated_at": report.generated_at,
            "corpus_health": report.corpus_health,
            "health_score": report.health_score,
            "total_nodes": report.total_nodes,
            "summary": report.summary,
            "suggestions": report.suggestions,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        if not args.json:
            print(f"\nReport saved to: {args.output}")

    return 0


if __name__ == "__main__":
    exit(main())
