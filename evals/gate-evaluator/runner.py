#!/usr/bin/env python3
"""
Eval runner for the gate-evaluator skill.

For each golden case under ``evals/gate-evaluator/golden/<id>/``, this runner
invokes ``validate_gate.evaluate_gate()`` against the synthetic project
directory and asserts the outcome matches ``expected`` in ``case.yml``.

Run:
  python3 evals/gate-evaluator/runner.py [--json]
"""
from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

# Repo-relative imports without packaging
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "gate-evaluator" / "scripts"))

from _lib.harness import (  # noqa: E402
    Report,
    assert_match,
    cli_args,
    discover_cases,
    emit_report,
)
import validate_gate  # noqa: E402


SUITE_DIR = Path(__file__).resolve().parent


def _result_to_dict(result) -> dict:
    payload = asdict(result)
    return payload


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="gate-evaluator")

    for case in discover_cases(SUITE_DIR):
        try:
            outcome = validate_gate.evaluate_gate(
                from_phase=int(case.inputs["from_phase"]),
                to_phase=int(case.inputs["to_phase"]),
                project_dir=str(case.project_dir),
                metrics=case.inputs.get("metrics") or {},
                project_id=case.inputs.get("project_id", "current"),
            )
            actual = _result_to_dict(outcome)
        except Exception as exc:  # noqa: BLE001 — harness must not crash
            report.add(
                __import__("_lib.harness", fromlist=["CaseResult"]).CaseResult(
                    case_id=case.case_id,
                    passed=False,
                    failures=[f"runner exception: {type(exc).__name__}: {exc}"],
                )
            )
            continue
        report.add(assert_match(case, actual))

    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
