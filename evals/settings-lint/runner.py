#!/usr/bin/env python3
"""
Eval runner for settings.json linting rules.

This suite enforces architectural invariants on .claude/settings.json that
cannot be expressed as JSON schema. Currently:

  * ADR-001: hook commands must not use relative `.claude/hooks/*` paths;
    they must resolve via $CLAUDE_PROJECT_DIR (with ${VAR:-.} fallback).

Run:
  python3 evals/settings-lint/runner.py [--json]
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

# Relative invocations of hooks — forbidden per ADR-001.
# Examples matched:
#   "python3 .claude/hooks/foo.py"
#   "python .claude/hooks/foo.py"
# Examples NOT matched (valid forms):
#   "python3 \"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/foo.py\""
#   "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/foo.py\""
RELATIVE_HOOK_RE = re.compile(r'python[23]?\s+\.claude/hooks/')


def _walk_commands(node, path="$"):
    """Yield (json_path, command_string) for every object with a 'command' key."""
    if isinstance(node, dict):
        if isinstance(node.get("command"), str):
            yield (f"{path}.command", node["command"])
        for k, v in node.items():
            yield from _walk_commands(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_commands(v, f"{path}[{i}]")


def run_case_adr_001(settings: dict) -> CaseResult:
    failures: list[str] = []
    for where, command in _walk_commands(settings):
        if RELATIVE_HOOK_RE.search(command):
            failures.append(f"relative hook path at {where}: {command!r}")
    return CaseResult(
        case_id="adr-001-no-relative-hook-paths",
        passed=not failures,
        failures=failures,
        actual_summary={"violations": len(failures)},
    )


def main() -> int:
    (as_json,) = cli_args()
    report = Report(suite="settings-lint")

    if not SETTINGS_PATH.exists():
        report.add(
            CaseResult(
                case_id="settings-json-exists",
                passed=False,
                failures=[f"not found: {SETTINGS_PATH}"],
            )
        )
        emit_report(report, as_json)
        return report.exit_code()

    with SETTINGS_PATH.open(encoding="utf-8") as f:
        settings = json.load(f)

    report.add(run_case_adr_001(settings))

    emit_report(report, as_json)
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
