#!/usr/bin/env python3
"""
Eval runner for agent contracts.

Enforces Constitution Principle XI: every agent in the priority
allowlist MUST declare a contract_version and the minimum contract
fields in its markdown frontmatter. Agents not in the allowlist are
skipped but counted (visible migration progress).

Run:
  python3 evals/agent-contracts/runner.py [--json]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402


AGENTS_DIR = REPO_ROOT / ".claude" / "agents"

# Tier 1 — priority agents that carry FULL strict contracts (hand-authored).
# These get the strict case body below plus the generic all-agents pass.
TIER1_STRICT_ALLOWLIST = {
    "code-reviewer",
    "requirements-analyst",
    "system-architect",
    "threat-modeler",
    "security-scanner",
    "orchestrator",
}

def _list_all_agents() -> list[str]:
    """Every .md file under .claude/agents/ that isn't a template or dotfile."""
    return sorted(
        p.stem
        for p in AGENTS_DIR.glob("*.md")
        if not p.name.startswith("_") and not p.name.startswith(".")
    )

REQUIRED_CONTRACT_KEYS = {
    "contract_version",
    "inputs",
    "outputs",
    "context_budget",
    "preconditions",
    "postconditions",
    "failure_modes",
    "sla",
    "observability",
}


def _read_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def case_all_agents_have_contract_key() -> list[CaseResult]:
    """Tier-2 check: every agent under .claude/agents MUST declare contract_version.
    Absence of the key is the minimum regression signal.
    """
    results: list[CaseResult] = []
    for name in _list_all_agents():
        path = AGENTS_DIR / f"{name}.md"
        fm = _read_frontmatter(path) or {}
        has_key = "contract_version" in fm
        results.append(
            CaseResult(
                case_id=f"tier2-{name}",
                passed=has_key,
                failures=[] if has_key else ["contract_version missing"],
                actual_summary={
                    "contract_version": fm.get("contract_version"),
                    "role_inferred": True if has_key else False,
                },
            )
        )
    return results


def case_priority_agents_have_contracts() -> list[CaseResult]:
    results: list[CaseResult] = []
    for name in sorted(TIER1_STRICT_ALLOWLIST):
        path = AGENTS_DIR / f"{name}.md"
        failures: list[str] = []
        if not path.exists():
            results.append(
                CaseResult(
                    case_id=f"contract-{name}",
                    passed=False,
                    failures=[f"file not found: {path}"],
                )
            )
            continue
        fm = _read_frontmatter(path)
        if fm is None:
            results.append(
                CaseResult(
                    case_id=f"contract-{name}",
                    passed=False,
                    failures=["frontmatter not parseable as YAML"],
                )
            )
            continue
        missing = REQUIRED_CONTRACT_KEYS - set(fm.keys())
        if missing:
            failures.append(f"missing contract keys: {sorted(missing)}")
        if "contract_version" in fm and not str(fm["contract_version"]).startswith("1."):
            failures.append(
                f"contract_version must start with '1.': got {fm.get('contract_version')!r}"
            )
        inputs = fm.get("inputs") or []
        if not isinstance(inputs, list) or not inputs:
            failures.append("inputs must be a non-empty list")
        outputs = fm.get("outputs") or []
        if not isinstance(outputs, list) or not outputs:
            failures.append("outputs must be a non-empty list")
        ctx = fm.get("context_budget") or {}
        if not isinstance(ctx, dict) or "max_tokens" not in ctx:
            failures.append("context_budget.max_tokens missing")
        results.append(
            CaseResult(
                case_id=f"contract-{name}",
                passed=not failures,
                failures=failures,
                actual_summary={
                    "keys_present": sorted(set(fm.keys()) & REQUIRED_CONTRACT_KEYS),
                    "missing": sorted(REQUIRED_CONTRACT_KEYS - set(fm.keys())),
                },
            )
        )
    return results


def case_migration_progress() -> CaseResult:
    """Informational case: counts how many total agents have a contract."""
    if not AGENTS_DIR.is_dir():
        return CaseResult(
            case_id="migration-progress",
            passed=False,
            failures=[f"{AGENTS_DIR} not found"],
        )
    agent_files = [p for p in AGENTS_DIR.glob("*.md") if not p.name.startswith("_")]
    with_contract: list[str] = []
    without_contract: list[str] = []
    for p in agent_files:
        fm = _read_frontmatter(p) or {}
        if "contract_version" in fm:
            with_contract.append(p.stem)
        else:
            without_contract.append(p.stem)
    return CaseResult(
        case_id="migration-progress",
        passed=True,  # informational — never fails the suite
        failures=[],
        actual_summary={
            "total_agents": len(agent_files),
            "with_contract": len(with_contract),
            "without_contract": len(without_contract),
            "coverage_pct": round(
                len(with_contract) / max(len(agent_files), 1) * 100, 1
            ),
            "migrated": sorted(with_contract),
            "pending": sorted(without_contract)[:10],
        },
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="agent-contracts")
    for r in case_all_agents_have_contract_key():
        report.add(r)
    for r in case_priority_agents_have_contracts():
        report.add(r)
    report.add(case_migration_progress())
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
