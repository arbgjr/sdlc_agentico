#!/usr/bin/env python3
"""
Eval runner: every SLO runbook referenced from the index exists, and
every SLO declared in .claude/config/slos.yml has a corresponding
runbook file (or an explicit "pending" marker in the index).

A runbook referenced and missing is silent false comfort. A runbook
written but not indexed is orphaned knowledge. This suite fails on
both.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "evals"))

from _lib.harness import CaseResult, Report, cli_args, emit_report  # noqa: E402

RUNBOOKS_DIR = REPO_ROOT / ".agentic_sdlc" / "docs" / "runbooks"
INDEX_FILE = RUNBOOKS_DIR / "README.md"
SLOS_FILE = REPO_ROOT / ".claude" / "config" / "slos.yml"

RUNBOOK_LINK_RE = re.compile(r"\bslo-[a-z0-9\-]+\.md\b")


def case_referenced_runbooks_exist() -> CaseResult:
    if not INDEX_FILE.exists():
        return CaseResult(
            case_id="runbooks-index-present",
            passed=False,
            failures=[f"index file missing: {INDEX_FILE}"],
        )
    text = INDEX_FILE.read_text(encoding="utf-8")
    referenced = sorted(set(RUNBOOK_LINK_RE.findall(text)))
    failures: list[str] = []
    for name in referenced:
        if not (RUNBOOKS_DIR / name).exists():
            failures.append(f"referenced runbook missing on disk: {name}")
    return CaseResult(
        case_id="referenced-runbooks-exist",
        passed=not failures,
        failures=failures,
        actual_summary={"referenced_count": len(referenced)},
    )


def case_runbooks_not_orphaned() -> CaseResult:
    if not INDEX_FILE.exists():
        return CaseResult(case_id="runbooks-not-orphaned", passed=False,
                          failures=[f"index missing: {INDEX_FILE}"])
    text = INDEX_FILE.read_text(encoding="utf-8")
    referenced = set(RUNBOOK_LINK_RE.findall(text))
    on_disk = {
        p.name for p in RUNBOOKS_DIR.glob("slo-*.md")
    }
    orphaned = sorted(on_disk - referenced)
    failures = [f"runbook on disk but not indexed: {name}" for name in orphaned]
    return CaseResult(
        case_id="runbooks-not-orphaned",
        passed=not failures,
        failures=failures,
        actual_summary={"on_disk": len(on_disk), "indexed": len(referenced)},
    )


def case_slos_covered() -> CaseResult:
    """Each SLO in slos.yml either has a runbook or is explicitly pending.

    Pending is allowed only once per SLO — mentioned in the README with
    the literal text "pending" on a line that references the slo name.
    """
    if not SLOS_FILE.exists():
        return CaseResult(
            case_id="slos-covered-by-runbooks-or-pending",
            passed=False,
            failures=[f"slos.yml missing at {SLOS_FILE}"],
        )
    with SLOS_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    slos = data.get("slos") or []
    slo_names = [s.get("name") for s in slos if isinstance(s, dict) and s.get("name")]

    index_text = INDEX_FILE.read_text(encoding="utf-8") if INDEX_FILE.exists() else ""
    failures: list[str] = []
    covered: list[str] = []
    pending: list[str] = []
    for name in slo_names:
        slug = name.replace("_", "-")
        runbook = RUNBOOKS_DIR / f"slo-{slug}.md"
        if runbook.exists():
            covered.append(name)
            continue
        # Pending check: a line in index that mentions the SLO name and "pending"
        pending_pattern = re.compile(
            rf"^.*{re.escape(name)}.*(pending).*$",
            re.IGNORECASE | re.MULTILINE,
        )
        if pending_pattern.search(index_text):
            pending.append(name)
            continue
        failures.append(f"SLO {name!r} has neither runbook nor pending marker")
    return CaseResult(
        case_id="slos-covered-by-runbooks-or-pending",
        passed=not failures,
        failures=failures,
        actual_summary={
            "total_slos": len(slo_names),
            "covered": len(covered),
            "pending": len(pending),
        },
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="runbooks")
    report.add(case_referenced_runbooks_exist())
    report.add(case_runbooks_not_orphaned())
    report.add(case_slos_covered())
    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
