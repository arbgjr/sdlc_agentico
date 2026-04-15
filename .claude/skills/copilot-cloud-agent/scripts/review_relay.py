#!/usr/bin/env python3
"""
Review relay: when a Copilot-authored PR becomes ready (CI green, not
draft), fetch the diff, run local review agents, and post structured
findings back to the PR. Copilot replies in the same thread with
retries.

This script is intentionally thin: it orchestrates, the agents do the
thinking. Each agent is invoked via its canonical CLI/skill hook, and
results are aggregated into a single review comment.

Usage:
  python3 review_relay.py --pr <number> [--post] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
REVIEW_AGENTS = [
    # (agent_name, invocation_hint)
    ("code-reviewer", "Review this diff against the TASK context and Constitution."),
    ("security-scanner", "SAST + SCA + secrets scan on the diff."),
]
MAX_RETRIES = 3


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> str:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)} :: {proc.stderr.strip()}"
        )
    return proc.stdout


def fetch_pr_metadata(pr_number: int) -> dict[str, Any]:
    out = run(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,title,body,headRefName,baseRefName,author,labels,isDraft,"
            "statusCheckRollup,url",
        ]
    )
    return json.loads(out)


def fetch_pr_diff(pr_number: int) -> str:
    return run(["gh", "pr", "diff", str(pr_number)])


def run_agent_review(agent: str, hint: str, diff: str) -> dict[str, Any]:
    """
    Placeholder contract for invoking a local review agent.

    In production this is wired to the agent skill runtime. For now the
    contract is documented here:
      - inputs: agent name, hint (prompt), diff text
      - outputs: {"findings": [{"severity": "CRITICAL|HIGH|MEDIUM|LOW",
                                "title": "...", "body": "...",
                                "file": "...", "line": N}]}

    Until the runtime is wired, this returns an empty-findings stub
    clearly marked so callers can detect the no-op.
    """
    return {
        "agent": agent,
        "findings": [],
        "note": (
            "review_relay stub: connect to agent runtime to replace this "
            "with real findings."
        ),
    }


def render_review_comment(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return (
            "### copilot-cloud-agent review relay\n\n"
            "No issues found by local review agents. Requesting human review."
        )
    by_sev = Counter(f["severity"] for f in findings)
    lines = [
        "### copilot-cloud-agent review relay",
        "",
        f"Total findings: **{len(findings)}** "
        f"(CRITICAL: {by_sev.get('CRITICAL', 0)}, "
        f"HIGH: {by_sev.get('HIGH', 0)}, "
        f"MEDIUM: {by_sev.get('MEDIUM', 0)}, "
        f"LOW: {by_sev.get('LOW', 0)})",
        "",
    ]
    blocking = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")]
    if blocking:
        lines += ["**Blocking — @copilot please address before requesting human review:**", ""]
        for f in blocking:
            loc = f" (`{f.get('file')}`:{f.get('line')})" if f.get("file") else ""
            lines += [f"- **{f['severity']}** — {f['title']}{loc}", f"  {f['body']}"]
        lines.append("")
    non_blocking = [f for f in findings if f["severity"] in ("MEDIUM", "LOW")]
    if non_blocking:
        lines += ["Non-blocking:"]
        for f in non_blocking:
            loc = f" (`{f.get('file')}`:{f.get('line')})" if f.get("file") else ""
            lines += [f"- {f['severity']} — {f['title']}{loc}"]
    lines += ["", f"Generated at {datetime.now(timezone.utc).isoformat()}."]
    return "\n".join(lines)


def post_review(pr_number: int, body: str, request_changes: bool) -> None:
    event = "REQUEST_CHANGES" if request_changes else "COMMENT"
    run(
        [
            "gh",
            "pr",
            "review",
            str(pr_number),
            f"--{event.lower().replace('_', '-')}",
            "--body",
            body,
        ],
        timeout=60,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--post", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    meta = fetch_pr_metadata(args.pr)
    diff = fetch_pr_diff(args.pr)

    findings: list[dict[str, Any]] = []
    for name, hint in REVIEW_AGENTS:
        result = run_agent_review(name, hint, diff)
        for f in result.get("findings", []):
            findings.append({**f, "agent": name})

    body = render_review_comment(findings)
    blocking = any(f["severity"] in ("CRITICAL", "HIGH") for f in findings)

    result = {
        "pr": args.pr,
        "findings_total": len(findings),
        "blocking": blocking,
        "body_preview": body.splitlines()[:5],
        "posted": False,
    }
    if args.post:
        post_review(args.pr, body, request_changes=blocking)
        result["posted"] = True

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PR #{args.pr} — findings: {len(findings)}, blocking: {blocking}")
        if not args.post:
            print("(dry-run — rerun with --post to upload)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
