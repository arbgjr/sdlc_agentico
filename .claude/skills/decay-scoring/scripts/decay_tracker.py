#!/usr/bin/env python3
"""
Decay Tracker - Track Node Access and Update Metadata.

Records access events and maintains rolling access counts
for decay scoring.

Usage:
    # Record access
    python decay_tracker.py access NODE_ID --type query

    # Record validation
    python decay_tracker.py validate NODE_ID --validator human

    # Cleanup old events
    python decay_tracker.py cleanup --days 90

    # View statistics
    python decay_tracker.py stats --json
"""

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml


class DecayTracker:
    """Tracks access patterns for corpus nodes."""

    def __init__(self, corpus_path: Path):
        self.corpus_path = corpus_path
        self.nodes_dir = corpus_path / "nodes"
        self.access_log_path = corpus_path / "access_log.json"
        self.now = datetime.now(timezone.utc)

    def load_access_log(self) -> Dict[str, Any]:
        """Load access log from file."""
        if self.access_log_path.exists():
            try:
                with open(self.access_log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"events": [], "last_cleanup": None}

    def save_access_log(self, log: Dict[str, Any]) -> None:
        """Save access log to file."""
        self.access_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.access_log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def record_access(self, node_id: str, access_type: str = "query") -> bool:
        """Record an access event for a node."""
        log = self.load_access_log()

        event = {
            "node_id": node_id,
            "timestamp": self.now.isoformat(),
            "type": access_type,  # query, view, reference
        }

        log["events"].append(event)
        self.save_access_log(log)

        # Update node metadata
        return self._update_node_access(node_id)

    def record_validation(self, node_id: str, validator: str = "human") -> bool:
        """Record a validation event for a node."""
        node_path = self._find_node_path(node_id)
        if not node_path:
            print(f"Node not found: {node_id}")
            return False

        with open(node_path, "r", encoding="utf-8") as f:
            node_data = yaml.safe_load(f) or {}

        if "decay_metadata" not in node_data:
            node_data["decay_metadata"] = {}

        dm = node_data["decay_metadata"]
        dm["last_validated_at"] = self.now.isoformat()

        if "validation_history" not in dm:
            dm["validation_history"] = []

        dm["validation_history"].append(
            {"date": self.now.isoformat(), "validator": validator, "action": "validated"}
        )

        with open(node_path, "w", encoding="utf-8") as f:
            yaml.dump(
                node_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )

        print(f"Recorded validation for {node_id}")
        return True

    def _find_node_path(self, node_id: str) -> Optional[Path]:
        """Find the path to a node file by ID."""
        if not self.nodes_dir.exists():
            return None

        for type_dir in self.nodes_dir.iterdir():
            if not type_dir.is_dir():
                continue

            # Check direct path (node_id.yml)
            direct_path = type_dir / f"{node_id}.yml"
            if direct_path.exists():
                return direct_path

            # Check files with matching id field
            for node_file in type_dir.glob("*.yml"):
                try:
                    with open(node_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}

                    # Handle nested structure
                    for key in ["decision", "learning", "pattern", "concept"]:
                        if key in data:
                            data = data[key]
                            break

                    if data.get("id") == node_id:
                        return node_file
                except Exception:
                    continue

        return None

    def _update_node_access(self, node_id: str) -> bool:
        """Update access metadata in node file."""
        node_path = self._find_node_path(node_id)
        if not node_path:
            return False

        with open(node_path, "r", encoding="utf-8") as f:
            node_data = yaml.safe_load(f) or {}

        if "decay_metadata" not in node_data:
            node_data["decay_metadata"] = {}

        dm = node_data["decay_metadata"]
        dm["last_accessed_at"] = self.now.isoformat()
        dm["access_count_total"] = dm.get("access_count_total", 0) + 1

        # Recalculate 30-day count from access log
        dm["access_count_30d"] = self._count_recent_accesses(node_id, days=30)

        with open(node_path, "w", encoding="utf-8") as f:
            yaml.dump(
                node_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )

        return True

    def _count_recent_accesses(self, node_id: str, days: int = 30) -> int:
        """Count accesses in the last N days."""
        log = self.load_access_log()
        cutoff = self.now - timedelta(days=days)

        count = 0
        for event in log["events"]:
            if event["node_id"] != node_id:
                continue

            try:
                ts_str = event["timestamp"]
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                ts = datetime.fromisoformat(ts_str)

                if ts >= cutoff:
                    count += 1
            except Exception:
                continue

        return count

    def cleanup_old_events(self, days: int = 90) -> int:
        """Remove access events older than N days."""
        log = self.load_access_log()
        cutoff = self.now - timedelta(days=days)

        original_count = len(log["events"])

        filtered: List[Dict[str, Any]] = []
        for event in log["events"]:
            try:
                ts_str = event["timestamp"]
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                ts = datetime.fromisoformat(ts_str)

                if ts >= cutoff:
                    filtered.append(event)
            except Exception:
                filtered.append(event)  # Keep unparseable events

        log["events"] = filtered
        log["last_cleanup"] = self.now.isoformat()
        self.save_access_log(log)

        removed = original_count - len(filtered)
        return removed

    def get_access_stats(self) -> Dict[str, Any]:
        """Get access statistics for all nodes."""
        log = self.load_access_log()

        stats: Dict[str, Dict[str, Any]] = {}
        for event in log["events"]:
            node_id = event["node_id"]
            if node_id not in stats:
                stats[node_id] = {
                    "total_accesses": 0,
                    "access_types": {},
                    "first_access": event["timestamp"],
                    "last_access": event["timestamp"],
                }

            stats[node_id]["total_accesses"] += 1

            access_type = event.get("type", "query")
            stats[node_id]["access_types"][access_type] = (
                stats[node_id]["access_types"].get(access_type, 0) + 1
            )

            if event["timestamp"] > stats[node_id]["last_access"]:
                stats[node_id]["last_access"] = event["timestamp"]

        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Track node access and update decay metadata"
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(".agentic_sdlc/corpus"),
        help="Path to corpus directory",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Access command
    access_parser = subparsers.add_parser("access", help="Record node access")
    access_parser.add_argument("node_id", help="Node ID that was accessed")
    access_parser.add_argument(
        "--type",
        choices=["query", "view", "reference"],
        default="query",
        help="Type of access",
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Record node validation")
    validate_parser.add_argument("node_id", help="Node ID that was validated")
    validate_parser.add_argument(
        "--validator",
        default="human",
        help="Who validated (human, system, automated)",
    )

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Remove old access events")
    cleanup_parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Remove events older than this many days",
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show access statistics")
    stats_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    tracker = DecayTracker(args.corpus)

    if args.command == "access":
        success = tracker.record_access(args.node_id, args.type)
        if success:
            print(f"Recorded {args.type} access for {args.node_id}")
        else:
            print(f"Node not found: {args.node_id} (access logged anyway)")

    elif args.command == "validate":
        tracker.record_validation(args.node_id, args.validator)

    elif args.command == "cleanup":
        removed = tracker.cleanup_old_events(args.days)
        print(f"Removed {removed} access events older than {args.days} days")

    elif args.command == "stats":
        stats = tracker.get_access_stats()
        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(f"Access statistics for {len(stats)} nodes:")
            for node_id, data in sorted(
                stats.items(), key=lambda x: x[1]["total_accesses"], reverse=True
            )[:10]:
                print(f"  {node_id}: {data['total_accesses']} accesses")


if __name__ == "__main__":
    main()
