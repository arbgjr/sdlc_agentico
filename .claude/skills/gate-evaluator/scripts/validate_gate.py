#!/usr/bin/env python3
"""
Validate an SDLC quality gate.

Reads gate definition from .claude/skills/gate-evaluator/gates/<gate>.yml,
checks required artifacts against the project directory, evaluates quality
metrics, and emits a structured decision (approve/reject/escalate).

This is the executable extraction of the inline pseudocode that previously
lived in SKILL.md. It is the *single source of truth* invoked by:
  - /gate-check command
  - check-gate.py hook
  - evals/gate-evaluator/runner.py (regression suite)

Usage:
  python3 validate_gate.py --from-phase 2 --to-phase 3 \
      --project-dir /path/to/project [--metrics metrics.yml] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import yaml


GATES_DIR = Path(__file__).resolve().parent.parent / "gates"


@dataclass
class ArtifactCheck:
    artifact_type: str
    pattern: str
    required: bool
    present: bool
    paths: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class QualityCheck:
    name: str
    metric: str
    threshold: float
    actual: float
    comparison: str
    passed: bool


@dataclass
class GateBlocker:
    type: str  # artifact | quality | approval
    description: str
    severity: str  # critical | high | medium
    remediation: str


@dataclass
class GateResult:
    gate_name: str
    from_phase: int
    to_phase: int
    passed: bool
    score: float
    artifact_checks: list[ArtifactCheck]
    quality_checks: list[QualityCheck]
    blockers: list[GateBlocker]
    can_proceed: bool
    human_approval_required: bool
    decision: str  # approve | reject | escalate
    recommendations: list[str] = field(default_factory=list)


class GateNotFoundError(FileNotFoundError):
    pass


def load_gate_definition(from_phase: int, to_phase: int) -> dict[str, Any]:
    gate_file = GATES_DIR / f"phase-{from_phase}-to-{to_phase}.yml"
    if not gate_file.exists():
        raise GateNotFoundError(f"Gate definition not found: {gate_file}")
    with gate_file.open(encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}
    # Some gate files nest under "gate:" — flatten for uniform access
    if "gate" in loaded and isinstance(loaded["gate"], dict):
        nested = loaded["gate"]
        loaded = {**nested, **{k: v for k, v in loaded.items() if k != "gate"}}
    return loaded


def _resolve_pattern(pattern: str, project_dir: Path, project_id: str) -> str:
    """Substitute {project_dir} and {id} tokens used in gate YAML patterns."""
    return pattern.replace("{project_dir}", str(project_dir)).replace(
        "{id}", project_id
    )


def check_artifacts(
    gate_def: dict[str, Any], project_dir: Path, project_id: str
) -> list[ArtifactCheck]:
    results: list[ArtifactCheck] = []
    for artifact in gate_def.get("required_artifacts", []) or []:
        raw_pattern = artifact.get("path") or artifact.get("path_pattern") or "*"
        artifact_type = artifact.get("type") or artifact.get("description", "artifact")
        resolved = _resolve_pattern(raw_pattern, project_dir, project_id)

        # Glob is anchored to project_dir if pattern is relative
        glob_root = project_dir if not Path(resolved).is_absolute() else Path("/")
        glob_pattern = (
            resolved
            if not Path(resolved).is_absolute()
            else str(Path(resolved).relative_to("/"))
        )

        try:
            matches = list(glob_root.glob(glob_pattern))
        except (ValueError, OSError) as exc:
            matches = []
            issues = [f"Pattern resolution error: {exc}"]
        else:
            issues = [] if matches else [f"Artifact not found: {resolved}"]

        results.append(
            ArtifactCheck(
                artifact_type=artifact_type,
                pattern=resolved,
                required=True,
                present=bool(matches),
                paths=[str(p) for p in matches],
                issues=issues,
            )
        )
    return results


def _run_shell_check(command: str, cwd: Path) -> bool:
    """Execute a gate's ``validation:`` shell snippet, scoped to project_dir.

    Pass = exit code 0 AND non-empty stdout. Many gates use ``grep ... | head``
    where the convention is "match found means pass". We treat empty output as
    fail to make that explicit.
    """
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0 and bool(proc.stdout.strip())


def check_quality(
    gate_def: dict[str, Any],
    metrics: dict[str, float],
    project_dir: Path | None = None,
) -> list[QualityCheck]:
    """Evaluate quality_checks. Supports two YAML dialects:

    * ``metric/threshold/comparison`` — numeric metric compared to threshold
    * ``check/validation`` — shell snippet that must succeed and emit output
    """
    results: list[QualityCheck] = []
    for check in gate_def.get("quality_checks", []) or []:
        if "metric" in check:
            metric_name = check["metric"]
            threshold = float(check["threshold"])
            comparison = check.get("comparison", "greater_or_equal")
            actual = float(metrics.get(metric_name, 0))

            if comparison == "greater_or_equal":
                passed = actual >= threshold
            elif comparison == "less_or_equal":
                passed = actual <= threshold
            elif comparison == "equal":
                passed = actual == threshold
            else:
                raise ValueError(f"Unknown comparison: {comparison}")

            results.append(
                QualityCheck(
                    name=check.get("name", metric_name),
                    metric=metric_name,
                    threshold=threshold,
                    actual=actual,
                    comparison=comparison,
                    passed=passed,
                )
            )
        elif "validation" in check:
            cwd = project_dir or Path.cwd()
            command = check["validation"]
            passed = _run_shell_check(command, cwd)
            results.append(
                QualityCheck(
                    name=check.get("check", "shell-check"),
                    metric=f"shell:{shlex.quote(command)[:40]}",
                    threshold=1.0,
                    actual=1.0 if passed else 0.0,
                    comparison="shell_exit_zero",
                    passed=passed,
                )
            )
        else:
            # Malformed quality check — fail loudly with a structured marker
            results.append(
                QualityCheck(
                    name=check.get("name", "malformed-check"),
                    metric="<malformed>",
                    threshold=0.0,
                    actual=0.0,
                    comparison="malformed",
                    passed=False,
                )
            )
    return results


def _decide(passed: bool, human_required: bool, blockers: list[GateBlocker]) -> str:
    if not passed:
        return "reject"
    if human_required:
        return "escalate"
    return "approve"


def evaluate_gate(
    from_phase: int,
    to_phase: int,
    project_dir: str,
    metrics: dict[str, float] | None = None,
    project_id: str = "current",
) -> GateResult:
    gate_def = load_gate_definition(from_phase, to_phase)
    project_path = Path(project_dir).resolve()
    metrics = metrics or {}

    artifact_results = check_artifacts(gate_def, project_path, project_id)
    quality_results = check_quality(gate_def, metrics, project_path)

    all_artifacts = bool(artifact_results) and all(a.present for a in artifact_results)
    all_quality = all(q.passed for q in quality_results)  # vacuously true if empty

    # If gate has no required_artifacts at all, treat as undefined and reject.
    if not artifact_results and not quality_results:
        passed = False
    else:
        passed = all_artifacts and all_quality

    artifact_score = (
        sum(1 for a in artifact_results if a.present) / max(len(artifact_results), 1)
    )
    quality_score = (
        sum(1 for q in quality_results if q.passed) / max(len(quality_results), 1)
        if quality_results
        else 1.0
    )
    score = 0.5 * artifact_score + 0.5 * quality_score

    blockers: list[GateBlocker] = []
    for a in artifact_results:
        if not a.present:
            blockers.append(
                GateBlocker(
                    type="artifact",
                    description=f"Missing artifact: {a.artifact_type} ({a.pattern})",
                    severity="critical",
                    remediation=f"Create artifact matching {a.pattern}",
                )
            )
    for q in quality_results:
        if not q.passed:
            blockers.append(
                GateBlocker(
                    type="quality",
                    description=(
                        f"Failed quality check {q.name}: "
                        f"{q.metric}={q.actual} {q.comparison} {q.threshold}"
                    ),
                    severity="high",
                    remediation=f"Improve {q.name} to satisfy {q.comparison} {q.threshold}",
                )
            )

    human_required = bool(
        gate_def.get("human_approval", {}).get("required")
        or gate_def.get("approval_required")
    )
    decision = _decide(passed, human_required, blockers)

    return GateResult(
        gate_name=gate_def.get("gate_name", gate_def.get("name", "unnamed")),
        from_phase=from_phase,
        to_phase=to_phase,
        passed=passed,
        score=round(score, 4),
        artifact_checks=artifact_results,
        quality_checks=quality_results,
        blockers=blockers,
        can_proceed=passed,
        human_approval_required=human_required,
        decision=decision,
        recommendations=[],
    )


def _result_to_dict(result: GateResult) -> dict[str, Any]:
    return asdict(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SDLC quality gate")
    parser.add_argument("--from-phase", type=int, required=True)
    parser.add_argument("--to-phase", type=int, required=True)
    parser.add_argument("--project-dir", type=str, required=True)
    parser.add_argument(
        "--project-id", type=str, default=os.environ.get("SDLC_PROJECT_ID", "current")
    )
    parser.add_argument(
        "--metrics", type=str, help="Optional YAML/JSON file with quality metrics"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of YAML")
    args = parser.parse_args()

    metrics: dict[str, float] = {}
    if args.metrics:
        metrics_path = Path(args.metrics)
        if not metrics_path.exists():
            print(f"ERROR: metrics file not found: {metrics_path}", file=sys.stderr)
            return 2
        with metrics_path.open(encoding="utf-8") as f:
            content = f.read()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = yaml.safe_load(content) or {}
        metrics = {k: float(v) for k, v in parsed.items() if isinstance(v, (int, float))}

    try:
        result = evaluate_gate(
            args.from_phase, args.to_phase, args.project_dir, metrics, args.project_id
        )
    except GateNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload = _result_to_dict(result)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(yaml.dump(payload, default_flow_style=False, sort_keys=False))

    # Exit code: 0 approve, 1 reject, 2 escalate (allows shell pipelines)
    return {"approve": 0, "reject": 1, "escalate": 2}.get(result.decision, 1)


if __name__ == "__main__":
    sys.exit(main())
