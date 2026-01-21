#!/usr/bin/env python3
"""
Worker State Tracker

Manages worker state persistence using JSON files.
Adapted from claude-orchestrator for SDLC Agêntico.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parents[3] / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="parallel-workers", phase=5)


class WorkerState(str, Enum):
    """Worker state machine states"""
    UNKNOWN = "UNKNOWN"
    NEEDS_INIT = "NEEDS_INIT"
    WORKING = "WORKING"
    PR_OPEN = "PR_OPEN"
    MERGED = "MERGED"
    ERROR = "ERROR"


class StateTracker:
    """Manages worker state persistence"""

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path.home() / ".claude" / "worker-states"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        logger.info("StateTracker initialized", extra={"state_dir": str(self.state_dir)})

    def _state_file(self, worker_id: str) -> Path:
        """Get state file path for worker"""
        return self.state_dir / f"{worker_id}.json"

    def get(self, worker_id: str) -> Dict[str, Any]:
        """Get worker state"""
        state_file = self._state_file(worker_id)

        if not state_file.exists():
            logger.warning(
                "Worker state not found",
                extra={"worker_id": worker_id, "file": str(state_file)}
            )
            return {
                "worker_id": worker_id,
                "state": WorkerState.UNKNOWN,
                "exists": False
            }

        with log_operation(f"read_state:{worker_id}", logger):
            with open(state_file, "r") as f:
                state = json.load(f)
                state["exists"] = True
                logger.debug("State loaded", extra={"worker_id": worker_id, "state": state})
                return state

    def set(
        self,
        worker_id: str,
        state: WorkerState,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Set worker state"""
        state_file = self._state_file(worker_id)

        # Load existing state
        if state_file.exists():
            with open(state_file, "r") as f:
                existing = json.load(f)
        else:
            existing = {}

        # Update state
        updated = {
            **existing,
            "worker_id": worker_id,
            "state": state.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **(metadata or {})
        }

        # Add created_at if new
        if "created_at" not in updated:
            updated["created_at"] = updated["updated_at"]

        # Write atomically
        with log_operation(f"write_state:{worker_id}", logger):
            temp_file = state_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(updated, f, indent=2)
            temp_file.replace(state_file)

            logger.info(
                "State updated",
                extra={
                    "worker_id": worker_id,
                    "state": state.value,
                    "metadata": metadata or {}
                }
            )

    def list(self) -> list[Dict[str, Any]]:
        """List all workers"""
        with log_operation("list_workers", logger):
            workers = []
            for state_file in self.state_dir.glob("*.json"):
                with open(state_file, "r") as f:
                    workers.append(json.load(f))

            logger.debug("Workers listed", extra={"count": len(workers)})
            return workers

    def remove(self, worker_id: str) -> None:
        """Remove worker state"""
        state_file = self._state_file(worker_id)

        if not state_file.exists():
            logger.warning("Worker state not found", extra={"worker_id": worker_id})
            return

        with log_operation(f"remove_state:{worker_id}", logger):
            state_file.unlink()
            logger.info("State removed", extra={"worker_id": worker_id})

    def transition(
        self,
        worker_id: str,
        from_state: WorkerState,
        to_state: WorkerState,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Transition worker state with validation"""
        current = self.get(worker_id)

        if not current.get("exists", True):
            logger.error(
                "Cannot transition non-existent worker",
                extra={"worker_id": worker_id}
            )
            return False

        current_state = WorkerState(current["state"])

        if current_state != from_state:
            logger.error(
                "Invalid state transition",
                extra={
                    "worker_id": worker_id,
                    "expected": from_state.value,
                    "actual": current_state.value,
                    "target": to_state.value
                }
            )
            return False

        # Valid transitions
        valid_transitions = {
            WorkerState.UNKNOWN: [WorkerState.NEEDS_INIT, WorkerState.ERROR],
            WorkerState.NEEDS_INIT: [WorkerState.WORKING, WorkerState.ERROR],
            WorkerState.WORKING: [WorkerState.PR_OPEN, WorkerState.ERROR],
            WorkerState.PR_OPEN: [WorkerState.MERGED, WorkerState.WORKING, WorkerState.ERROR],
            WorkerState.MERGED: [],  # Terminal state
            WorkerState.ERROR: [WorkerState.NEEDS_INIT, WorkerState.WORKING]  # Recovery
        }

        if to_state not in valid_transitions.get(current_state, []):
            logger.error(
                "Invalid state transition",
                extra={
                    "worker_id": worker_id,
                    "from": current_state.value,
                    "to": to_state.value,
                    "allowed": [s.value for s in valid_transitions[current_state]]
                }
            )
            return False

        # Perform transition
        self.set(worker_id, to_state, metadata)
        logger.info(
            "State transition",
            extra={
                "worker_id": worker_id,
                "from": current_state.value,
                "to": to_state.value
            }
        )
        return True


def main():
    parser = argparse.ArgumentParser(description="Worker State Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get command
    get_parser = subparsers.add_parser("get", help="Get worker state")
    get_parser.add_argument("worker_id", help="Worker ID")

    # set command
    set_parser = subparsers.add_parser("set", help="Set worker state")
    set_parser.add_argument("worker_id", help="Worker ID")
    set_parser.add_argument(
        "state",
        choices=[s.value for s in WorkerState],
        help="Target state"
    )
    set_parser.add_argument("--task-id", help="Task ID")
    set_parser.add_argument("--pr-url", help="Pull request URL")
    set_parser.add_argument("--error", help="Error message")

    # list command
    list_parser = subparsers.add_parser("list", help="List all workers")
    list_parser.add_argument(
        "--state",
        choices=[s.value for s in WorkerState],
        help="Filter by state"
    )

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove worker state")
    remove_parser.add_argument("worker_id", help="Worker ID")

    # transition command
    transition_parser = subparsers.add_parser("transition", help="Transition worker state")
    transition_parser.add_argument("worker_id", help="Worker ID")
    transition_parser.add_argument("from_state", choices=[s.value for s in WorkerState])
    transition_parser.add_argument("to_state", choices=[s.value for s in WorkerState])

    args = parser.parse_args()
    tracker = StateTracker()

    if args.command == "get":
        state = tracker.get(args.worker_id)
        print(json.dumps(state, indent=2))

    elif args.command == "set":
        metadata = {}
        if args.task_id:
            metadata["task_id"] = args.task_id
        if args.pr_url:
            metadata["pr_url"] = args.pr_url
        if args.error:
            metadata["error"] = args.error

        tracker.set(args.worker_id, WorkerState(args.state), metadata)
        print(f"State set: {args.worker_id} -> {args.state}")

    elif args.command == "list":
        workers = tracker.list()
        if args.state:
            workers = [w for w in workers if w["state"] == args.state]

        print(json.dumps(workers, indent=2))

    elif args.command == "remove":
        tracker.remove(args.worker_id)
        print(f"State removed: {args.worker_id}")

    elif args.command == "transition":
        success = tracker.transition(
            args.worker_id,
            WorkerState(args.from_state),
            WorkerState(args.to_state)
        )
        if success:
            print(f"Transition successful: {args.from_state} -> {args.to_state}")
            sys.exit(0)
        else:
            print(f"Transition failed: {args.from_state} -> {args.to_state}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
