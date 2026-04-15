#!/usr/bin/env python3
"""
Eval runner for threat-modeler output-shape contracts.

The threat-modeler is an LLM-backed agent whose semantic output quality
cannot be asserted mechanically in an eval harness. What CAN be asserted
is whether any threat-model.yml that the agent produces meets the
structural contract declared in .claude/agents/threat-modeler.md:

  * methodology == "STRIDE"
  * threats is a non-empty list
  * every threat has category (STRIDE letter) + asset + mitigation
  * every HIGH/CRITICAL threat has an actionable mitigation
  * escalation triggers in sdlc.security_by_design (auth, PII, crypto,
    new public endpoint, payments) are covered by at least one threat
    when the input plan mentions that concern

Golden inputs are under golden/<case>/input/plan.md + data-model.md, and
the expected output is golden/<case>/expected/threat-model.yml.

Today the runner validates the expected/threat-model.yml against the
contract — i.e., it tests the contract checks themselves + the golden
examples. When the agent runtime is wired, the same runner can also
produce threat-models from the inputs and assert THAT output against
the contract. Contract and harness share the validator.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402


SUITE_DIR = Path(__file__).resolve().parent
STRIDE_CATEGORIES = {
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information Disclosure",
    "Denial of Service",
    "Elevation of Privilege",
}
HIGH_SEVERITIES = {"HIGH", "CRITICAL"}


@dataclass
class ContractCheckResult:
    failures: list[str]
    threat_count: int
    high_severity_count: int
    categories_used: set[str]


def validate_threat_model(tm: dict) -> ContractCheckResult:
    failures: list[str] = []
    inner = tm.get("threat_model") or {}
    if inner.get("methodology") != "STRIDE":
        failures.append(
            f"methodology: expected 'STRIDE', got {inner.get('methodology')!r}"
        )
    threats = inner.get("threats") or []
    if not isinstance(threats, list) or not threats:
        failures.append("threats must be a non-empty list")
        return ContractCheckResult(failures, 0, 0, set())
    categories: set[str] = set()
    high_count = 0
    for i, t in enumerate(threats):
        if not isinstance(t, dict):
            failures.append(f"threat[{i}] is not a mapping")
            continue
        for field in ("category", "asset", "mitigation"):
            if not t.get(field):
                failures.append(f"threat[{i}] missing '{field}'")
        cat = t.get("category")
        if cat and cat not in STRIDE_CATEGORIES:
            failures.append(
                f"threat[{i}] category {cat!r} not in STRIDE set"
            )
        elif cat:
            categories.add(cat)
        sev = (t.get("severity") or "").upper()
        if sev in HIGH_SEVERITIES:
            high_count += 1
            mitigation = (t.get("mitigation") or "").strip()
            if len(mitigation) < 10:
                failures.append(
                    f"threat[{i}] HIGH/CRITICAL needs actionable mitigation; got {mitigation!r}"
                )
    return ContractCheckResult(failures, len(threats), high_count, categories)


def _load_yaml(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _case_expectations(case_dir: Path) -> dict:
    meta_file = case_dir / "case.yml"
    if not meta_file.exists():
        return {}
    with meta_file.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_case(case_dir: Path) -> CaseResult:
    case_id = case_dir.name
    expected_file = case_dir / "expected" / "threat-model.yml"
    tm = _load_yaml(expected_file)
    if tm is None:
        return CaseResult(
            case_id=case_id,
            passed=False,
            failures=[f"expected/threat-model.yml missing at {expected_file}"],
        )
    result = validate_threat_model(tm)

    meta = _case_expectations(case_dir)
    expect_failure = bool(meta.get("expect_failure"))
    failures = list(result.failures)

    # Negative case: we EXPECT failures and invert the assertion.
    if expect_failure:
        passed = bool(failures)
        return CaseResult(
            case_id=case_id,
            passed=passed,
            failures=[]
            if passed
            else ["expected contract failures, but threat model passed validation"],
            actual_summary={
                "expected_failure": True,
                "validator_failures": failures,
            },
        )

    if "min_threats" in meta and result.threat_count < meta["min_threats"]:
        failures.append(
            f"min_threats: expected >= {meta['min_threats']}, got {result.threat_count}"
        )
    if "requires_categories" in meta:
        missing_cats = set(meta["requires_categories"]) - result.categories_used
        if missing_cats:
            failures.append(f"missing required STRIDE categories: {sorted(missing_cats)}")
    if "min_high_severity" in meta and result.high_severity_count < meta["min_high_severity"]:
        failures.append(
            f"min_high_severity: expected >= {meta['min_high_severity']}, "
            f"got {result.high_severity_count}"
        )

    return CaseResult(
        case_id=case_id,
        passed=not failures,
        failures=failures,
        actual_summary={
            "threat_count": result.threat_count,
            "high_severity": result.high_severity_count,
            "categories": sorted(result.categories_used),
        },
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="threat-modeler")
    golden = SUITE_DIR / "golden"
    if golden.is_dir():
        for case_dir in sorted(p for p in golden.iterdir() if p.is_dir()):
            report.add(run_case(case_dir))
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
