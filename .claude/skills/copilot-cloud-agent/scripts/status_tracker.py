#!/usr/bin/env python3
"""
Status tracker for dispatched Copilot Cloud Agent tasks.

Reads .project/issue-mapping.yml, polls each open issue/PR via gh CLI,
and updates state for downstream tooling (dashboards, gate-evaluator).

State per entry:
  dispatched  -> issue created, no PR yet
  in_progress -> PR opened by copilot, CI running
  ci_failing  -> PR open, CI red
  ready       -> CI green, awaiting review relay
  in_review   -> review relay posted findings, copilot retrying
  merged      -> PR merged, issue closed
  abandoned   -> gave up (retries exceeded)

Usage:
  python3 status_tracker.py [--json] [--write]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
MAPPING_FILE = REPO_ROOT / ".project" / "issue-mapping.yml"


def gh_json(args: list[str]) -> dict | list:
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, timeout=30
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout) if proc.stdout else {}


def issue_state(issue_url: str) -> dict[str, Any]:
    # gh expects issue number or URL
    data = gh_json(
        [
            "issue",
            "view",
            issue_url,
            "--json",
            "number,state,closedAt,labels,url",
        ]
    )
    return data  # type: ignore[return-value]


def linked_pr(issue_number: int) -> dict[str, Any] | None:
    """Find a PR that references this issue via 'closes #N' etc."""
    res = gh_json(
        [
            "pr",
            "list",
            "--search",
            f"in:body closes #{issue_number}",
            "--json",
            "number,state,isDraft,mergeable,statusCheckRollup,url",
            "--limit",
            "1",
        ]
    )
    if isinstance(res, list) and res:
        return res[0]
    return None


def derive_state(entry: dict[str, Any]) -> str:
    url = entry.get("issue_url")
    if not url:
        return "dispatched"
    try:
        iss = issue_state(url)
    except RuntimeError:
        return "dispatched"
    if iss.get("state") == "CLOSED":
        return "merged"
    number = iss.get("number")
    if not isinstance(number, int):
        return "dispatched"
    pr = linked_pr(number)
    if not pr:
        return "dispatched"
    if pr.get("isDraft"):
        return "in_progress"
    rollup = pr.get("statusCheckRollup") or []
    conclusions = {
        c.get("conclusion")
        for c in rollup
        if isinstance(c, dict)
    }
    if "FAILURE" in conclusions or "TIMED_OUT" in conclusions:
        return "ci_failing"
    if conclusions and conclusions.issubset({"SUCCESS", "NEUTRAL", "SKIPPED"}):
        return "ready"
    return "in_progress"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write", action="store_true", help="Persist state back to mapping file"
    )
    args = parser.parse_args()

    if not MAPPING_FILE.exists():
        print("no mapping file", file=sys.stderr)
        return 0
    with MAPPING_FILE.open() as f:
        data = yaml.safe_load(f) or {}
    entries = data.get("mapping", [])
    summary: dict[str, int] = {}
    updated: list[dict[str, Any]] = []
    for e in entries:
        state = derive_state(e)
        e["state"] = state
        e["state_checked_at"] = datetime.now(timezone.utc).isoformat()
        summary[state] = summary.get(state, 0) + 1
        updated.append(e)
    data["mapping"] = updated
    data["summary"] = summary
    if args.write:
        with MAPPING_FILE.open("w") as f:
            yaml.safe_dump(data, f, sort_keys=False)
    if args.json:
        print(json.dumps({"summary": summary, "entries": updated}, indent=2))
    else:
        print("state summary:")
        for k, v in sorted(summary.items()):
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
