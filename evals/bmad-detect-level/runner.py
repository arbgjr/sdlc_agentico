#!/usr/bin/env python3
"""
Eval runner for BMAD complexity level detection.

Guards the detect_level.py heuristic. A regression here mis-routes
entire features — e.g. a PII change being classified as Level 1 would
skip threat modeling. The golden cases enumerate known classifications.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "bmad-integration" / "scripts"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402
import detect_level  # noqa: E402


@dataclass
class LevelCase:
    case_id: str
    text: str
    files: list[str]
    expected_level: int
    expected_escalation: str | None = None


CASES = [
    LevelCase(
        case_id="typo-fix-is-level-0",
        text="fix typo in README",
        files=["README.md"],
        expected_level=0,
    ),
    LevelCase(
        case_id="small-feature-is-level-1",
        text="add a new sort option to the product list",
        files=["src/products/list.py", "tests/products/test_list.py"],
        expected_level=1,
    ),
    LevelCase(
        case_id="new-service-is-level-2",
        text="introduce a new billing service for recurring subscriptions",
        files=[],
        expected_level=2,
    ),
    LevelCase(
        case_id="pii-change-escalates-to-level-2",
        text="add a user export endpoint returning CPF and address (PII)",
        files=["src/users/export.py"],
        expected_level=2,
        expected_escalation="PII exposure",
    ),
    LevelCase(
        case_id="compliance-is-level-3",
        text="implement LGPD-compliant data deletion across all microservices",
        files=[],
        expected_level=3,
    ),
    LevelCase(
        case_id="auth-escalates-from-fix",
        text="fix authentication bypass when password is empty",
        files=["src/auth/login.py"],
        expected_level=2,
        expected_escalation="auth/authz change",
    ),
    LevelCase(
        case_id="payment-escalates",
        text="add refund endpoint for credit card charges",
        files=["src/payments/refund.py"],
        expected_level=2,
        expected_escalation="payment flow",
    ),
    LevelCase(
        case_id="many-files-upgrades-from-0",
        text="fix small bugs",
        files=[f"src/f{i}.py" for i in range(10)],
        expected_level=1,
    ),
]


def run_case(c: LevelCase) -> CaseResult:
    d = detect_level.detect(c.text, c.files)
    failures: list[str] = []
    if d.level != c.expected_level:
        failures.append(f"level: expected {c.expected_level}, got {d.level}")
    if c.expected_escalation and c.expected_escalation not in d.triggered_escalations:
        failures.append(
            f"missing expected escalation {c.expected_escalation!r} in "
            f"{d.triggered_escalations}"
        )
    return CaseResult(
        case_id=c.case_id,
        passed=not failures,
        failures=failures,
        actual_summary={
            "level": d.level,
            "command": d.suggested_command,
            "escalations": d.triggered_escalations,
            "keywords": d.matched_keywords,
        },
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="bmad-detect-level")
    for c in CASES:
        report.add(run_case(c))
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
