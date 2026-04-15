#!/usr/bin/env python3
"""
Eval runner for parallelization routing invariants.

Enforces ADR-002 (Copilot Cloud Agent as default Phase 6 strategy)
mechanically. A silent refactor of .claude/settings.json that contradicts
the ADR fails this suite — the ADR is load-bearing only if the invariants
it claims are tested.

Invariants guarded:
  I1. sdlc.parallelization.default_strategy == "copilot_cloud_agent"
  I2. copilot_cloud_agent.enabled == true
  I3. parallel_workers.role == "fallback_when_local_env_required"
  I4. selection_rules document the four documented routes (human_only,
      local_worker, copilot_cloud_agent, default)
  I5. copilot_cloud_agent.default_for_phases contains 6 (Phase 6)
  I6. copilot_cloud_agent.retry_budget_per_task matches review_relay
      MAX_RETRIES (drift between config and code is the most common
      breakage mode for retry policies)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402

SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
REVIEW_RELAY_PATH = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "copilot-cloud-agent"
    / "scripts"
    / "review_relay.py"
)


def _load_settings() -> dict:
    with SETTINGS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _review_relay_max_retries() -> int | None:
    """Parse MAX_RETRIES = <int> from review_relay.py without importing."""
    text = REVIEW_RELAY_PATH.read_text(encoding="utf-8")
    m = re.search(r"^\s*MAX_RETRIES\s*=\s*(\d+)\s*$", text, re.MULTILINE)
    return int(m.group(1)) if m else None


def case_default_strategy() -> CaseResult:
    s = _load_settings()
    par = (s.get("sdlc") or {}).get("parallelization") or {}
    default = par.get("default_strategy")
    failures = (
        []
        if default == "copilot_cloud_agent"
        else [f"default_strategy: expected 'copilot_cloud_agent', got {default!r}"]
    )
    return CaseResult(
        case_id="default-strategy-is-copilot-cloud-agent",
        passed=not failures,
        failures=failures,
        actual_summary={"default_strategy": default},
    )


def case_copilot_enabled_and_phase6() -> CaseResult:
    s = _load_settings()
    strat = (
        (s.get("sdlc") or {}).get("parallelization", {}).get("strategies", {})
        or {}
    ).get("copilot_cloud_agent") or {}
    failures = []
    if not strat.get("enabled"):
        failures.append("copilot_cloud_agent.enabled is not true")
    phases = strat.get("default_for_phases") or []
    if 6 not in phases:
        failures.append(
            f"copilot_cloud_agent.default_for_phases must include 6 (Phase 6), got {phases}"
        )
    return CaseResult(
        case_id="copilot-enabled-for-phase-6",
        passed=not failures,
        failures=failures,
        actual_summary={"enabled": strat.get("enabled"), "phases": phases},
    )


def case_parallel_workers_role_is_fallback() -> CaseResult:
    s = _load_settings()
    pw = (
        (s.get("sdlc") or {}).get("parallelization", {}).get("strategies", {})
        or {}
    ).get("parallel_workers") or {}
    role = pw.get("role")
    failures = (
        []
        if role == "fallback_when_local_env_required"
        else [
            f"parallel_workers.role: expected "
            f"'fallback_when_local_env_required', got {role!r}"
        ]
    )
    return CaseResult(
        case_id="parallel-workers-is-fallback",
        passed=not failures,
        failures=failures,
        actual_summary={"role": role},
    )


def case_selection_rules_documented() -> CaseResult:
    s = _load_settings()
    par = (s.get("sdlc") or {}).get("parallelization") or {}
    rules = par.get("selection_rules") or []
    failures = []
    if not isinstance(rules, list) or not rules:
        failures.append("selection_rules must be a non-empty list")
    else:
        needed_keywords = [
            "human_only",
            "local_worker",
            "copilot_cloud_agent",
            "default",
        ]
        joined = "\n".join(r if isinstance(r, str) else str(r) for r in rules)
        for kw in needed_keywords:
            if kw not in joined:
                failures.append(f"selection_rules missing mention of {kw!r}")
    return CaseResult(
        case_id="selection-rules-cover-all-hints",
        passed=not failures,
        failures=failures,
        actual_summary={"rule_count": len(rules)},
    )


def case_retry_budget_matches_code() -> CaseResult:
    s = _load_settings()
    strat = (
        (s.get("sdlc") or {}).get("parallelization", {}).get("strategies", {})
        or {}
    ).get("copilot_cloud_agent") or {}
    declared = strat.get("retry_budget_per_task")
    code_value = _review_relay_max_retries()
    failures = []
    if declared is None:
        failures.append("copilot_cloud_agent.retry_budget_per_task missing")
    if code_value is None:
        failures.append("review_relay.py MAX_RETRIES not parseable")
    if (
        declared is not None
        and code_value is not None
        and int(declared) != int(code_value)
    ):
        failures.append(
            f"retry budget drift: settings={declared}, review_relay.MAX_RETRIES={code_value}"
        )
    return CaseResult(
        case_id="retry-budget-matches-review-relay",
        passed=not failures,
        failures=failures,
        actual_summary={"settings": declared, "code": code_value},
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="parallelization-routing")
    for fn in (
        case_default_strategy,
        case_copilot_enabled_and_phase6,
        case_parallel_workers_role_is_fallback,
        case_selection_rules_documented,
        case_retry_budget_matches_code,
    ):
        report.add(fn())
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
