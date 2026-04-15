#!/usr/bin/env python3
"""
Discover every per-suite runner under evals/<suite>/runner.py and run them
in sequence. Aggregates exit codes: any non-zero from any suite fails the
overall run.

Usage:
  python3 evals/run_all.py [--json]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


EVALS_DIR = Path(__file__).resolve().parent


def discover_suites() -> list[Path]:
    return sorted(p for p in EVALS_DIR.glob("*/runner.py") if p.is_file())


def main() -> int:
    as_json = "--json" in sys.argv[1:]
    suites = discover_suites()
    if not suites:
        print("No suites found under evals/*/runner.py", file=sys.stderr)
        return 2

    results: list[dict] = []
    overall_exit = 0
    for runner in suites:
        suite_name = runner.parent.name
        cmd = [sys.executable, str(runner)]
        if as_json:
            cmd.append("--json")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        results.append(
            {
                "suite": suite_name,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
        if proc.returncode != 0:
            overall_exit = max(overall_exit, proc.returncode)

    if as_json:
        print(json.dumps({"suites": results, "exit_code": overall_exit}, indent=2))
    else:
        for r in results:
            print(r["stdout"], end="")
            if r["stderr"]:
                print(f"--- stderr from {r['suite']} ---", file=sys.stderr)
                print(r["stderr"], file=sys.stderr)
        print()
        print(f"=== Overall: {'PASS' if overall_exit == 0 else 'FAIL'} ===")

    return overall_exit


if __name__ == "__main__":
    sys.exit(main())
