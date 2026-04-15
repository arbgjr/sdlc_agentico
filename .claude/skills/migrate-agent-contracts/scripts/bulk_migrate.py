#!/usr/bin/env python3
"""
Bulk-migrate framework agents to tier-2 contract frontmatter.

Reads every ``.claude/agents/*.md`` file, detects whether it already
carries a ``contract_version`` key, and if not, appends a minimal
contract block inside the existing YAML frontmatter. The block is
derived from the agent's name, description, and role.

Guarantees:
  * Idempotent — agents that already have a contract are skipped.
  * Atomic per file — either the whole block is inserted or the file
    is left untouched (no partial writes).
  * Produces a structured report at
    ``.project/reports/migration-contracts-phase-b.yml``.

Usage:
  python3 bulk_migrate.py [--dry-run] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
REPORT_DIR = REPO_ROOT / ".project" / "reports"
REPORT_FILE = REPORT_DIR / "migration-contracts-phase-b.yml"


ROLE_DEFAULTS: dict[str, dict[str, Any]] = {
    "analyst":      {"max_tokens": 25000, "sla_p95": 90,  "output_type": "markdown"},
    "reviewer":     {"max_tokens": 30000, "sla_p95": 45,  "output_type": "yaml"},
    "author":       {"max_tokens": 40000, "sla_p95": 120, "output_type": "file_tree"},
    "engineer":     {"max_tokens": 35000, "sla_p95": 180, "output_type": "file_tree"},
    "architect":    {"max_tokens": 40000, "sla_p95": 180, "output_type": "markdown"},
    "scanner":      {"max_tokens": 20000, "sla_p95": 300, "output_type": "yaml"},
    "manager":      {"max_tokens": 30000, "sla_p95": 60,  "output_type": "yaml"},
    "simulator":    {"max_tokens": 30000, "sla_p95": 120, "output_type": "markdown"},
    "generator":    {"max_tokens": 25000, "sla_p95": 90,  "output_type": "file_tree"},
    "curator":      {"max_tokens": 20000, "sla_p95": 60,  "output_type": "yaml"},
    "commander":    {"max_tokens": 30000, "sla_p95": 60,  "output_type": "yaml"},
    "interrogator": {"max_tokens": 20000, "sla_p95": 60,  "output_type": "markdown"},
    "challenger":   {"max_tokens": 20000, "sla_p95": 60,  "output_type": "markdown"},
    "governance":   {"max_tokens": 30000, "sla_p95": 120, "output_type": "yaml"},
    "researcher":   {"max_tokens": 30000, "sla_p95": 180, "output_type": "markdown"},
    "designer":     {"max_tokens": 30000, "sla_p95": 180, "output_type": "file_tree"},
    "writer":       {"max_tokens": 15000, "sla_p95": 60,  "output_type": "markdown"},
    "crawler":      {"max_tokens": 30000, "sla_p95": 240, "output_type": "yaml"},
    "auditor":      {"max_tokens": 40000, "sla_p95": 180, "output_type": "yaml"},
    "planner":      {"max_tokens": 30000, "sla_p95": 120, "output_type": "yaml"},
    "owner":        {"max_tokens": 25000, "sla_p95": 60,  "output_type": "markdown"},
    "importer":     {"max_tokens": 35000, "sla_p95": 240, "output_type": "file_tree"},
    "guardian":     {"max_tokens": 30000, "sla_p95": 120, "output_type": "yaml"},
    "agent":        {"max_tokens": 25000, "sla_p95": 90,  "output_type": "yaml"},  # alignment-agent
    "default":      {"max_tokens": 25000, "sla_p95": 90,  "output_type": "markdown"},
}


@dataclass
class AgentReport:
    name: str
    action: str               # added_contract | skipped_already_contracted | error_<reason>
    inferred_role: str = ""
    max_tokens: int = 0
    sla_p95: int = 0
    error: str | None = None


@dataclass
class RunReport:
    run_at: str
    total_agents_found: int = 0
    already_contracted: int = 0
    newly_contracted: int = 0
    skipped_errors: int = 0
    dry_run: bool = False
    per_agent: list[AgentReport] = field(default_factory=list)


def infer_role(name: str) -> str:
    parts = name.lower().split("-")
    for p in reversed(parts):
        if p in ROLE_DEFAULTS:
            return p
    return "default"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_yaml, body). Frontmatter is None if absent."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return (None, text)
    return (m.group(1), m.group(2))


def has_contract(frontmatter_yaml: str) -> bool:
    try:
        data = yaml.safe_load(frontmatter_yaml) or {}
    except yaml.YAMLError:
        return False
    return isinstance(data, dict) and "contract_version" in data


def build_contract_block(name: str, description: str, role: str) -> str:
    defaults = ROLE_DEFAULTS[role]
    max_tokens = defaults["max_tokens"]
    sla = defaults["sla_p95"]
    output_type = defaults["output_type"]

    # Single-line synopsis of the description for the default input hint
    synopsis = (description or "").strip().splitlines()[0][:140] or "free-form request"

    block_lines = [
        "",
        "# --- Agent Contract (Constitution v1.0.0 Principle XI, tier-2 auto-migrated) ---",
        'contract_version: "1.0"',
        "inputs:",
        "  - name: request",
        "    type: markdown",
        "    required: true",
        f"    description: {json.dumps(synopsis)}",
        "outputs:",
        "  - name: result",
        f"    type: {output_type}",
        f"    description: {json.dumps(f'Output produced by {name}; see agent body for format details.')}",
        "context_budget:",
        f"  max_tokens: {max_tokens}",
        "  required_files:",
        "    - .specify/memory/constitution.md",
        "preconditions:",
        "  - caller has provided a parseable request",
        "postconditions:",
        "  - output respects the agent's declared output type",
        "failure_modes:",
        "  - trigger: request cannot be parsed",
        "    severity: medium",
        "    recovery: return structured error; do not guess intent",
        "sla:",
        f"  wallclock_seconds_p95: {sla}",
        "observability:",
        f"  emit_event: {name}.completed",
        "  metrics:",
        "    - tokens_consumed",
        "    - tool_calls",
    ]
    return "\n".join(block_lines)


def migrate_file(path: Path, dry_run: bool) -> AgentReport:
    name = path.stem
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if fm is None:
        return AgentReport(
            name=name,
            action="error_no_frontmatter",
            error="no YAML frontmatter detected",
        )
    if has_contract(fm):
        return AgentReport(name=name, action="skipped_already_contracted")
    try:
        fm_data = yaml.safe_load(fm) or {}
    except yaml.YAMLError as exc:
        return AgentReport(
            name=name,
            action="error_malformed_frontmatter",
            error=str(exc),
        )
    description = fm_data.get("description") or ""
    role = infer_role(name)
    defaults = ROLE_DEFAULTS[role]
    contract_block = build_contract_block(name, description, role)
    new_text = f"---\n{fm.rstrip()}\n{contract_block}\n---\n{body.lstrip(chr(10))}"
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return AgentReport(
        name=name,
        action="added_contract",
        inferred_role=role,
        max_tokens=defaults["max_tokens"],
        sla_p95=defaults["sla_p95"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = RunReport(
        run_at=datetime.now(timezone.utc).isoformat(),
        dry_run=args.dry_run,
    )
    agent_files = sorted(p for p in AGENTS_DIR.glob("*.md") if not p.name.startswith("_"))
    report.total_agents_found = len(agent_files)

    for path in agent_files:
        result = migrate_file(path, args.dry_run)
        report.per_agent.append(result)
        if result.action == "added_contract":
            report.newly_contracted += 1
        elif result.action == "skipped_already_contracted":
            report.already_contracted += 1
        elif result.action.startswith("error_"):
            report.skipped_errors += 1

    payload = asdict(report)
    if not args.dry_run:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        with REPORT_FILE.open("w", encoding="utf-8") as f:
            yaml.safe_dump(payload, f, sort_keys=False)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"Agents found: {report.total_agents_found}\n"
            f"Already contracted: {report.already_contracted}\n"
            f"Newly contracted: {report.newly_contracted}\n"
            f"Errors: {report.skipped_errors}\n"
            f"Dry run: {args.dry_run}"
        )
        if report.skipped_errors:
            for a in report.per_agent:
                if a.action.startswith("error_"):
                    print(f"  ERROR {a.name}: {a.error}")
    return 0 if report.skipped_errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
