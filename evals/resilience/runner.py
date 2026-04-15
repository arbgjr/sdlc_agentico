#!/usr/bin/env python3
"""
Eval runner for .claude/lib/python/resilience.py.

Exercises retry, timeout, and circuit-breaker primitives against known
behavioral cases. These are unit-scale tests, but they live under evals/
because they guard framework primitives that multiple skills depend on —
a regression here is a regression for the entire harness.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "lib" / "python"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402

import resilience  # noqa: E402


@dataclass
class _Counter:
    calls: int = 0


def case_retry_eventually_succeeds() -> CaseResult:
    c = _Counter()

    @resilience.with_retry(max_attempts=5, base_delay_seconds=0.01)
    def flaky() -> str:
        c.calls += 1
        if c.calls < 3:
            raise RuntimeError("transient")
        return "ok"

    try:
        result = flaky()
    except Exception as exc:  # noqa: BLE001
        return CaseResult(
            case_id="retry-eventually-succeeds",
            passed=False,
            failures=[f"unexpected raise: {exc}"],
        )
    failures: list[str] = []
    if result != "ok":
        failures.append(f"expected 'ok', got {result!r}")
    if c.calls != 3:
        failures.append(f"expected 3 calls, got {c.calls}")
    return CaseResult(
        case_id="retry-eventually-succeeds",
        passed=not failures,
        failures=failures,
        actual_summary={"calls": c.calls, "result": result},
    )


def case_retry_exhausts() -> CaseResult:
    c = _Counter()

    @resilience.with_retry(max_attempts=3, base_delay_seconds=0.01)
    def always_fails() -> None:
        c.calls += 1
        raise RuntimeError("boom")

    try:
        always_fails()
    except RuntimeError:
        pass
    else:
        return CaseResult(
            case_id="retry-exhausts",
            passed=False,
            failures=["expected raise after exhaustion"],
        )
    failures: list[str] = []
    if c.calls != 3:
        failures.append(f"expected 3 calls, got {c.calls}")
    return CaseResult(
        case_id="retry-exhausts",
        passed=not failures,
        failures=failures,
        actual_summary={"calls": c.calls},
    )


def case_timeout_triggers() -> CaseResult:
    @resilience.with_timeout(seconds=0.05)
    def slow() -> str:
        time.sleep(0.5)
        return "late"

    failures: list[str] = []
    try:
        slow()
    except TimeoutError:
        pass
    else:
        failures.append("expected TimeoutError, got success")
    return CaseResult(
        case_id="timeout-triggers",
        passed=not failures,
        failures=failures,
    )


def case_circuit_opens_after_failures() -> CaseResult:
    c = _Counter()

    @resilience.with_circuit_breaker(
        name="eval-cb-1",
        failure_threshold=0.5,
        window_size=4,
        cooldown_seconds=0.2,
    )
    def always_fails() -> None:
        c.calls += 1
        raise RuntimeError("boom")

    # Fill window with failures
    for _ in range(4):
        try:
            always_fails()
        except RuntimeError:
            pass

    # Next call should be refused by breaker (not increment counter)
    baseline = c.calls
    try:
        always_fails()
    except resilience.CircuitOpenError:
        refused = True
    except RuntimeError:
        refused = False
    else:
        refused = False

    failures: list[str] = []
    if not refused:
        failures.append("expected CircuitOpenError after threshold")
    if c.calls != baseline:
        failures.append(
            f"breaker did not refuse: calls moved from {baseline} to {c.calls}"
        )
    return CaseResult(
        case_id="circuit-opens-after-failures",
        passed=not failures,
        failures=failures,
        actual_summary={"calls": c.calls},
    )


def case_circuit_half_open_after_cooldown() -> CaseResult:
    c = _Counter()

    @resilience.with_circuit_breaker(
        name="eval-cb-2",
        failure_threshold=0.5,
        window_size=4,
        cooldown_seconds=0.1,
    )
    def flaky() -> str:
        c.calls += 1
        if c.calls <= 4:
            raise RuntimeError("boom")
        return "ok"

    for _ in range(4):
        try:
            flaky()
        except RuntimeError:
            pass

    # Breaker should now be open
    try:
        flaky()
    except resilience.CircuitOpenError:
        pass
    else:
        return CaseResult(
            case_id="circuit-half-open-after-cooldown",
            passed=False,
            failures=["expected circuit open"],
        )

    time.sleep(0.15)  # exceed cooldown

    # Half-open: should allow call through; this call now returns "ok"
    try:
        result = flaky()
    except Exception as exc:  # noqa: BLE001
        return CaseResult(
            case_id="circuit-half-open-after-cooldown",
            passed=False,
            failures=[f"post-cooldown call raised: {exc}"],
        )

    failures: list[str] = []
    if result != "ok":
        failures.append(f"expected 'ok' on half-open recovery, got {result!r}")
    return CaseResult(
        case_id="circuit-half-open-after-cooldown",
        passed=not failures,
        failures=failures,
        actual_summary={"calls": c.calls, "result": result},
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="resilience")
    for fn in (
        case_retry_eventually_succeeds,
        case_retry_exhausts,
        case_timeout_triggers,
        case_circuit_opens_after_failures,
        case_circuit_half_open_after_cooldown,
    ):
        report.add(fn())
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
