"""
Shared primitives for the SDLC Agêntico eval harness.

This module is intentionally tiny: a Case loader, a Report aggregator, and an
assertion helper that fails loudly on unknown expected-keys (no silent passes).

The contract every per-agent runner must honor:
  1. Discover cases by walking <suite_dir>/golden/*/case.yml
  2. For each case, build inputs, invoke the agent, capture the actual outcome
  3. Hand (case, expected, actual) to assert_match
  4. Aggregate via Report and exit with Report.exit_code()
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml


@dataclass
class Case:
    case_id: str
    description: str
    agent: str
    inputs: dict[str, Any]
    expected: dict[str, Any]
    case_dir: Path

    @property
    def project_dir(self) -> Path:
        return self.case_dir / "project"


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    actual_summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    suite: str
    results: list[CaseResult] = field(default_factory=list)

    def add(self, result: CaseResult) -> None:
        self.results.append(result)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def pass_rate(self) -> float:
        return self.passed_count / self.total if self.total else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "total": self.total,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": round(self.pass_rate, 4),
            "results": [
                {
                    "case_id": r.case_id,
                    "passed": r.passed,
                    "failures": r.failures,
                    "actual": r.actual_summary,
                }
                for r in self.results
            ],
        }

    def render_text(self) -> str:
        lines = [
            f"=== Suite: {self.suite} ===",
            f"Passed: {self.passed_count}/{self.total} "
            f"({self.pass_rate * 100:.1f}%)",
            "",
        ]
        for r in self.results:
            mark = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{mark}] {r.case_id}")
            for failure in r.failures:
                lines.append(f"         - {failure}")
        return "\n".join(lines)

    def exit_code(self) -> int:
        return 0 if self.failed_count == 0 else 1


def discover_cases(suite_dir: Path) -> Iterable[Case]:
    """Yield Case objects for every golden/<id>/case.yml under suite_dir."""
    golden = suite_dir / "golden"
    if not golden.is_dir():
        return
    for case_yml in sorted(golden.glob("*/case.yml")):
        with case_yml.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        yield Case(
            case_id=data["case_id"],
            description=data.get("description", ""),
            agent=data["agent"],
            inputs=data.get("inputs", {}) or {},
            expected=data.get("expected", {}) or {},
            case_dir=case_yml.parent,
        )


# Known assertion keys. Adding a new one here is a deliberate harness change.
_KNOWN_EXPECTED_KEYS = {
    "decision",
    "passed",
    "has_blocker_of_type",
    "has_blocker_count_at_least",
    "score_at_least",
    "score_at_most",
    "human_approval_required",
    "artifact_present_count",
}


def assert_match(case: Case, actual: dict[str, Any]) -> CaseResult:
    """Compare ``actual`` (dict from agent) against ``case.expected``.

    Unknown expected-keys are HARNESS errors — they fail the case loudly so a
    typo in case.yml never silently passes.
    """
    failures: list[str] = []

    for key in case.expected:
        if key not in _KNOWN_EXPECTED_KEYS:
            failures.append(
                f"unknown expected key '{key}' "
                f"(known: {sorted(_KNOWN_EXPECTED_KEYS)})"
            )

    def expect_eq(key: str) -> None:
        if key in case.expected and actual.get(key) != case.expected[key]:
            failures.append(
                f"{key}: expected {case.expected[key]!r}, got {actual.get(key)!r}"
            )

    expect_eq("decision")
    expect_eq("passed")
    expect_eq("human_approval_required")

    if "has_blocker_of_type" in case.expected:
        wanted = case.expected["has_blocker_of_type"]
        types = {b.get("type") for b in actual.get("blockers", [])}
        if wanted not in types:
            failures.append(f"no blocker of type '{wanted}' in {sorted(types)}")

    if "has_blocker_count_at_least" in case.expected:
        wanted = int(case.expected["has_blocker_count_at_least"])
        got = len(actual.get("blockers", []))
        if got < wanted:
            failures.append(f"expected >= {wanted} blockers, got {got}")

    if "score_at_least" in case.expected:
        wanted = float(case.expected["score_at_least"])
        got = float(actual.get("score", 0))
        if got < wanted:
            failures.append(f"score: expected >= {wanted}, got {got}")

    if "score_at_most" in case.expected:
        wanted = float(case.expected["score_at_most"])
        got = float(actual.get("score", 0))
        if got > wanted:
            failures.append(f"score: expected <= {wanted}, got {got}")

    if "artifact_present_count" in case.expected:
        wanted = int(case.expected["artifact_present_count"])
        got = sum(1 for a in actual.get("artifact_checks", []) if a.get("present"))
        if got != wanted:
            failures.append(f"artifact_present_count: expected {wanted}, got {got}")

    return CaseResult(
        case_id=case.case_id,
        passed=not failures,
        failures=failures,
        actual_summary={
            "decision": actual.get("decision"),
            "passed": actual.get("passed"),
            "score": actual.get("score"),
            "blocker_count": len(actual.get("blockers", [])),
        },
    )


def emit_report(report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.render_text())


def cli_args(argv: list[str] | None = None) -> tuple[bool]:
    """Tiny shared arg parser: only --json supported."""
    args = list(argv if argv is not None else sys.argv[1:])
    return (("--json" in args),)
