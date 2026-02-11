#!/usr/bin/env python3
"""
Strategy selection script for parallelization in SDLC Agêntico.

Determines optimal strategy (agent_teams, parallel_workers, sequential) based on:
- Current SDLC phase
- Task characteristics (research vs implementation)
- Task count
- Token budget availability
- Feature flags

Usage:
    python3 select_strategy.py --phase 1 --task-type research --task-count 3
    python3 select_strategy.py --phase 6 --task-type implementation --task-count 4
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Literal

StrategyType = Literal["agent_teams", "parallel_workers", "sequential"]


def load_settings() -> Dict[str, Any]:
    """Load settings from .claude/settings.json."""
    settings_path = Path(".claude/settings.json")
    if not settings_path.exists():
        raise FileNotFoundError(
            "Settings file not found: .claude/settings.json"
        )

    with open(settings_path, "r") as f:
        return json.load(f)


def check_agent_teams_enabled(settings: Dict[str, Any]) -> bool:
    """Check if agent_teams feature flag is enabled."""
    try:
        return settings["sdlc"]["feature_flags"].get("agent_teams", False)
    except KeyError:
        return False


def check_env_flag() -> bool:
    """Check if CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is set."""
    return os.getenv("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "0") == "1"


def get_token_budget_remaining(settings: Dict[str, Any]) -> int:
    """Get remaining token budget (mock - would integrate with real tracking)."""
    try:
        max_budget = settings["sdlc"]["token_budget"]["global_max"]
        # TODO: Integrate with actual token tracking
        # For now, assume 70% remaining
        return int(max_budget * 0.7)
    except KeyError:
        return 100000  # Default safe value


def select_strategy(
    phase: int,
    task_type: str,
    task_count: int,
    settings: Dict[str, Any],
    force_strategy: str | None = None
) -> tuple[StrategyType, str]:
    """
    Select optimal parallelization strategy.

    Args:
        phase: Current SDLC phase (0-9)
        task_type: Type of tasks ("research", "implementation", "review", etc.)
        task_count: Number of tasks to parallelize
        settings: Loaded settings.json
        force_strategy: Optional forced strategy (for testing)

    Returns:
        Tuple of (strategy, rationale)
    """
    if force_strategy:
        return force_strategy, f"Forced by user: {force_strategy}"

    # Rule 1: Single task → Sequential
    if task_count < 2:
        return "sequential", "Only 1 task, no parallelization needed"

    # Rule 2: Check if agent_teams is available
    agent_teams_enabled = check_agent_teams_enabled(settings)
    env_flag_set = check_env_flag()

    if not agent_teams_enabled:
        # Fallback to parallel_workers or sequential
        if phase == 6 and task_count >= 2:
            return "parallel_workers", "Agent Teams disabled, using Parallel Workers for Phase 6"
        return "sequential", "Agent Teams disabled, insufficient parallelization alternatives"

    if agent_teams_enabled and not env_flag_set:
        return "sequential", "Agent Teams enabled but CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS not set"

    # Rule 3: Check token budget
    token_budget = get_token_budget_remaining(settings)
    token_multiplier = settings["sdlc"]["parallelization"]["strategies"]["agent_teams"]["token_budget_multiplier"]

    if token_budget < 50000:
        return "sequential", f"Token budget low ({token_budget} remaining), avoiding Agent Teams"

    # Rule 4: Phase and task type detection
    research_phases = [1, 2, 3]
    implementation_phases = [6]
    review_phases = [7]

    research_keywords = ["research", "explore", "investigate", "analyze", "discover", "study"]
    implementation_keywords = ["implement", "code", "write", "build", "develop", "create"]
    review_keywords = ["review", "audit", "validate", "assess", "evaluate", "test", "qa"]

    task_type_lower = task_type.lower()

    # Phase 1, 2, 3 + research → Agent Teams
    if phase in research_phases and any(kw in task_type_lower for kw in research_keywords):
        return "agent_teams", f"Phase {phase} research benefits from parallel discussion"

    # Phase 6 + implementation → Parallel Workers (file isolation)
    if phase in implementation_phases and any(kw in task_type_lower for kw in implementation_keywords):
        return "parallel_workers", "Phase 6 implementation requires file isolation via worktrees"

    # Phase 7 + review → Agent Teams (multiple perspectives)
    if phase in review_phases and any(kw in task_type_lower for kw in review_keywords):
        return "agent_teams", "Phase 7 review benefits from multiple specialized perspectives"

    # Rule 5: Phase 3 (Architecture) always benefits from debate
    if phase == 3:
        return "agent_teams", "Phase 3 architecture requires trade-off debate"

    # Rule 6: Default to sequential (conservative)
    return "sequential", "No clear parallelization benefit detected, defaulting to sequential"


def main():
    parser = argparse.ArgumentParser(
        description="Select parallelization strategy for SDLC tasks"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        help="Current SDLC phase (0-9)"
    )
    parser.add_argument(
        "--task-type",
        type=str,
        required=True,
        help="Type of tasks (research, implementation, review, etc.)"
    )
    parser.add_argument(
        "--task-count",
        type=int,
        required=True,
        help="Number of tasks to parallelize"
    )
    parser.add_argument(
        "--force-strategy",
        type=str,
        choices=["agent_teams", "parallel_workers", "sequential"],
        help="Force a specific strategy (for testing)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    try:
        settings = load_settings()
        strategy, rationale = select_strategy(
            phase=args.phase,
            task_type=args.task_type,
            task_count=args.task_count,
            settings=settings,
            force_strategy=args.force_strategy
        )

        if args.json:
            output = {
                "strategy": strategy,
                "rationale": rationale,
                "phase": args.phase,
                "task_type": args.task_type,
                "task_count": args.task_count
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Strategy: {strategy}")
            print(f"Rationale: {rationale}")

        sys.exit(0)

    except Exception as e:
        if args.json:
            error = {
                "error": str(e),
                "strategy": "sequential",
                "rationale": f"Error occurred: {e}. Defaulting to sequential."
            }
            print(json.dumps(error, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
            print("Defaulting to sequential strategy.", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
