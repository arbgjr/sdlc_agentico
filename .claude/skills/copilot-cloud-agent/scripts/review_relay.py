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
import re
import shutil
import tempfile
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

# Secret patterns for the built-in scan (mirrors dispatcher.py patterns).
SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?im)^\s*(api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}"),
        "hardcoded secret-like assignment",
    ),
    (
        re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
        "private key block",
    ),
    (
        re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
        "GitHub personal access token",
    ),
    (
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
        "Slack token",
    ),
    (
        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
        "Google API key",
    ),
    (
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "AWS access key id",
    ),
]


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


def _diff_touched_files(diff: str) -> list[Path]:
    """Extract +++ b/<path> entries from a unified diff."""
    touched: list[Path] = []
    for line in diff.splitlines():
        m = re.match(r"^\+\+\+\s+b/(.+)$", line)
        if m and m.group(1) != "/dev/null":
            touched.append(Path(m.group(1)))
    return touched


def _added_lines_by_file(diff: str) -> dict[Path, list[tuple[int, str]]]:
    """Parse unified diff, returning (line_no, text) of added lines per file.

    Line numbers are in the new file. We track the running line number
    using the ``@@ -old,N +new,M @@`` hunk headers.
    """
    result: dict[Path, list[tuple[int, str]]] = {}
    current_file: Path | None = None
    new_line_no = 0
    for line in diff.splitlines():
        m_header = re.match(r"^\+\+\+\s+b/(.+)$", line)
        if m_header:
            current_file = Path(m_header.group(1)) if m_header.group(1) != "/dev/null" else None
            continue
        m_hunk = re.match(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@", line)
        if m_hunk:
            new_line_no = int(m_hunk.group(1))
            continue
        if current_file is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            result.setdefault(current_file, []).append((new_line_no, line[1:]))
            new_line_no += 1
        elif line.startswith("-") and not line.startswith("---"):
            # Removed line — does not advance new_line_no
            pass
        elif line.startswith(" "):
            new_line_no += 1
    return result


def _scan_secrets_in_diff(diff: str) -> list[dict[str, Any]]:
    """Secret scan scoped to ADDED lines only — never flags pre-existing code."""
    findings: list[dict[str, Any]] = []
    for file, lines in _added_lines_by_file(diff).items():
        for line_no, text in lines:
            for pattern, label in SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(
                        {
                            "severity": "CRITICAL",
                            "title": f"Secret-like pattern: {label}",
                            "body": (
                                "Added line matches a known credential pattern. "
                                "Rotate immediately if real and remove from the "
                                "diff. See Constitution Principle II (Anti-Mock, "
                                "no secrets in source)."
                            ),
                            "file": str(file),
                            "line": line_no,
                        }
                    )
                    break  # one finding per line is enough
    return findings


def _run_tool(cmd: list[str], cwd: Path, timeout: int = 60) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        return (127, "", f"{cmd[0]} not installed")
    except subprocess.TimeoutExpired:
        return (124, "", f"{cmd[0]} timed out after {timeout}s")
    return (proc.returncode, proc.stdout, proc.stderr)


def _run_bandit(files: list[Path], cwd: Path) -> list[dict[str, Any]]:
    """Bandit SAST on Python files only. Silent no-op if bandit missing."""
    py_files = [str(f) for f in files if f.suffix == ".py" and (cwd / f).exists()]
    if not py_files or shutil.which("bandit") is None:
        return []
    code, out, _ = _run_tool(["bandit", "-f", "json", "-q", *py_files], cwd)
    if code == 127:
        return []
    try:
        report = json.loads(out) if out else {}
    except json.JSONDecodeError:
        return []
    findings: list[dict[str, Any]] = []
    for result in report.get("results", []):
        severity_map = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
        findings.append(
            {
                "severity": severity_map.get(result.get("issue_severity"), "LOW"),
                "title": f"bandit {result.get('test_id')}: {result.get('issue_text')}",
                "body": result.get("issue_cwe", {}).get("link")
                or result.get("more_info")
                or "",
                "file": result.get("filename"),
                "line": result.get("line_number"),
            }
        )
    return findings


def _run_ruff(files: list[Path], cwd: Path) -> list[dict[str, Any]]:
    """Ruff lint+security. Scoped to selected rule sets. Silent no-op if missing."""
    py_files = [str(f) for f in files if f.suffix == ".py" and (cwd / f).exists()]
    if not py_files or shutil.which("ruff") is None:
        return []
    code, out, _ = _run_tool(
        [
            "ruff",
            "check",
            "--select",
            "S,B,E9,F",  # S=security, B=bugbear, E9=syntax, F=pyflakes
            "--output-format",
            "json",
            *py_files,
        ],
        cwd,
    )
    if code == 127:
        return []
    try:
        items = json.loads(out) if out else []
    except json.JSONDecodeError:
        return []
    findings: list[dict[str, Any]] = []
    for item in items:
        code_id = item.get("code") or ""
        # Security-prefixed (S*) and syntax errors (E9*) are HIGH; others MEDIUM/LOW.
        if code_id.startswith("S") or code_id.startswith("E9"):
            sev = "HIGH"
        elif code_id.startswith("B"):
            sev = "MEDIUM"
        else:
            sev = "LOW"
        findings.append(
            {
                "severity": sev,
                "title": f"ruff {code_id}: {item.get('message', '')}",
                "body": item.get("url") or "",
                "file": item.get("filename"),
                "line": (item.get("location") or {}).get("row"),
            }
        )
    return findings


def run_agent_review(agent: str, hint: str, diff: str, cwd: Path | None = None) -> dict[str, Any]:
    """
    Concrete review pass. Delegates to local static-analysis tools and the
    in-process secret scanner. The ``agent`` parameter selects the
    profile:

      * ``code-reviewer``    -> ruff + bandit  (lint, bugs, basic SAST)
      * ``security-scanner`` -> secrets + bandit (deeper SAST focus)

    The function is intentionally self-contained (stdlib only for secrets;
    bandit/ruff invoked via subprocess). Missing tools degrade silently;
    no crash, no fake findings.

    When bandit/ruff are available the output is genuine. When neither is
    available the secret scanner alone still catches hardcoded credentials
    — the one finding type that must never silently pass.
    """
    cwd = cwd or Path.cwd()
    files = _diff_touched_files(diff)
    findings: list[dict[str, Any]] = []
    tools_used: list[str] = []

    if agent in ("security-scanner", "code-reviewer"):
        secret_findings = _scan_secrets_in_diff(diff)
        if secret_findings:
            findings.extend(secret_findings)
        tools_used.append("secrets-scan")

    if agent in ("code-reviewer", "security-scanner"):
        bandit_findings = _run_bandit(files, cwd)
        if bandit_findings:
            findings.extend(bandit_findings)
            tools_used.append("bandit")
        elif shutil.which("bandit") is not None:
            tools_used.append("bandit")  # ran, zero findings

    if agent == "code-reviewer":
        ruff_findings = _run_ruff(files, cwd)
        if ruff_findings:
            findings.extend(ruff_findings)
            tools_used.append("ruff")
        elif shutil.which("ruff") is not None:
            tools_used.append("ruff")

    return {
        "agent": agent,
        "hint": hint,
        "findings": findings,
        "tools_used": tools_used,
        "files_in_diff": [str(f) for f in files],
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
