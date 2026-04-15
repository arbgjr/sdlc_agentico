#!/usr/bin/env python3
"""
Eval runner for the code-reviewer review pipeline.

The pipeline under test is review_relay.run_agent_review, which delegates
to local SAST tools (bandit, ruff) plus an in-process secret scanner.
Golden cases exercise diffs that DO or DO NOT contain known issues; the
runner asserts the resulting severity counts meet expectations.

When bandit or ruff is not installed on the host, the runner tolerates
missing tools — secret-scan MUST still work (stdlib-only). Cases that
depend exclusively on bandit/ruff findings are marked skip_without_tool
and are skipped cleanly with a visible marker.
"""
from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "copilot-cloud-agent" / "scripts"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402
import review_relay  # noqa: E402


@dataclass
class ReviewCase:
    case_id: str
    agent: str
    diff: str
    expect_min_critical: int = 0
    expect_min_high: int = 0
    expect_max_critical: int | None = None
    expect_finding_titles_contain: list[str] = field(default_factory=list)
    expect_files: list[str] = field(default_factory=list)
    skip_without_tool: str | None = None


DIFF_HARDCODED_SECRET = """\
diff --git a/src/config.py b/src/config.py
index e69de29..abc1234 100644
--- /dev/null
+++ b/src/config.py
@@ -0,0 +1,3 @@
+# Configuration
+DATABASE_URL = "postgres://user:pass@db/app"
+GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
"""

DIFF_AWS_KEY = """\
diff --git a/src/aws.py b/src/aws.py
index e69de29..abc1234 100644
--- /dev/null
+++ b/src/aws.py
@@ -0,0 +1,2 @@
+AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
+AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
"""

DIFF_CLEAN_CODE = """\
diff --git a/src/utils.py b/src/utils.py
index e69de29..abc1234 100644
--- /dev/null
+++ b/src/utils.py
@@ -0,0 +1,5 @@
+def add(a: int, b: int) -> int:
+    \"\"\"Return the sum of two integers.\"\"\"
+    return a + b
+
+# No secrets, no bugs, nothing to see here
"""

DIFF_EVAL_CALL = """\
diff --git a/src/bad.py b/src/bad.py
index e69de29..abc1234 100644
--- /dev/null
+++ b/src/bad.py
@@ -0,0 +1,3 @@
+user_input = input("expr: ")
+result = eval(user_input)
+print(result)
"""

CASES = [
    ReviewCase(
        case_id="secret-github-token-flagged-critical",
        agent="code-reviewer",
        diff=DIFF_HARDCODED_SECRET,
        expect_min_critical=1,
        expect_finding_titles_contain=["secret"],
        expect_files=["src/config.py"],
    ),
    ReviewCase(
        case_id="secret-aws-key-flagged-critical",
        agent="security-scanner",
        diff=DIFF_AWS_KEY,
        expect_min_critical=1,
        expect_finding_titles_contain=["AWS"],
    ),
    ReviewCase(
        case_id="clean-code-no-critical",
        agent="code-reviewer",
        diff=DIFF_CLEAN_CODE,
        expect_max_critical=0,
    ),
    ReviewCase(
        case_id="bandit-catches-eval-call",
        agent="code-reviewer",
        diff=DIFF_EVAL_CALL,
        expect_min_high=1,
        skip_without_tool="bandit",
    ),
]


def _run_case(c: ReviewCase) -> CaseResult:
    if c.skip_without_tool and shutil.which(c.skip_without_tool) is None:
        return CaseResult(
            case_id=c.case_id,
            passed=True,  # skip is not a failure
            failures=[],
            actual_summary={"skipped": f"{c.skip_without_tool} not installed"},
        )

    result = review_relay.run_agent_review(c.agent, "eval", c.diff)
    findings = result.get("findings", [])
    by_sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        by_sev[f.get("severity", "LOW")] = by_sev.get(f.get("severity", "LOW"), 0) + 1

    failures: list[str] = []
    if by_sev["CRITICAL"] < c.expect_min_critical:
        failures.append(
            f"CRITICAL: expected >= {c.expect_min_critical}, got {by_sev['CRITICAL']}"
        )
    if by_sev["HIGH"] < c.expect_min_high:
        failures.append(
            f"HIGH: expected >= {c.expect_min_high}, got {by_sev['HIGH']}"
        )
    if c.expect_max_critical is not None and by_sev["CRITICAL"] > c.expect_max_critical:
        failures.append(
            f"CRITICAL: expected <= {c.expect_max_critical}, got {by_sev['CRITICAL']}"
        )
    for needle in c.expect_finding_titles_contain:
        if not any(needle.lower() in (f.get("title") or "").lower() for f in findings):
            failures.append(
                f"no finding title contains {needle!r}; titles: "
                f"{[f.get('title') for f in findings]}"
            )
    for expected_file in c.expect_files:
        if not any((f.get("file") or "") == expected_file for f in findings):
            failures.append(f"no finding on expected file {expected_file}")

    return CaseResult(
        case_id=c.case_id,
        passed=not failures,
        failures=failures,
        actual_summary={"severities": by_sev, "tools": result.get("tools_used")},
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="code-reviewer")
    for c in CASES:
        report.add(_run_case(c))
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
