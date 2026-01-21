#!/usr/bin/env python3
"""
Worker Manager

Manages lifecycle of parallel workers for SDLC Phase 5 Implementation.
Adapted from claude-orchestrator for multiplataform compatibility.
"""

import sys
import json
import argparse
import subprocess
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parents[3] / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

# Import state tracker
from state_tracker import StateTracker, WorkerState

logger = get_logger(__name__, skill="parallel-workers", phase=5)


class WorkerManager:
    """Manages worker lifecycle"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.state_tracker = StateTracker()
        self.worktree_script = (
            Path(__file__).parent / "worktree_manager.sh"
        ).resolve()

        if not self.worktree_script.exists():
            raise FileNotFoundError(f"worktree_manager.sh not found: {self.worktree_script}")

        logger.info(
            "WorkerManager initialized",
            extra={"project": project_name}
        )

    def _run_worktree_command(self, *args: str) -> subprocess.CompletedProcess:
        """Run worktree_manager.sh command"""
        cmd = [str(self.worktree_script)] + list(args)
        logger.debug("Running worktree command", extra={"cmd": " ".join(cmd)})

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(
                "Worktree command failed",
                extra={
                    "cmd": " ".join(cmd),
                    "returncode": result.returncode,
                    "stderr": result.stderr
                }
            )

        return result

    def spawn(
        self,
        task_id: str,
        description: str,
        agent: str,
        base_branch: str,
        priority: int = 5
    ) -> Dict[str, Any]:
        """Spawn a new worker"""
        worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        correlation_id = uuid.uuid4().hex

        with log_operation(f"spawn_worker:{worker_id}", logger):
            logger.info(
                "Spawning worker",
                extra={
                    "worker_id": worker_id,
                    "task_id": task_id,
                    "agent": agent,
                    "base_branch": base_branch,
                    "correlation_id": correlation_id
                }
            )

            # Create worktree
            result = self._run_worktree_command(
                "create",
                self.project_name,
                task_id,
                base_branch
            )

            if result.returncode != 0:
                logger.error(
                    "Failed to create worktree",
                    extra={
                        "worker_id": worker_id,
                        "task_id": task_id,
                        "error": result.stderr
                    }
                )
                return {
                    "success": False,
                    "worker_id": worker_id,
                    "error": result.stderr
                }

            worktree_path = result.stdout.strip()

            # Initialize worker state
            self.state_tracker.set(
                worker_id,
                WorkerState.NEEDS_INIT,
                metadata={
                    "task_id": task_id,
                    "description": description,
                    "agent": agent,
                    "base_branch": base_branch,
                    "worktree_path": worktree_path,
                    "branch": f"feature/{task_id}",
                    "priority": priority,
                    "correlation_id": correlation_id,
                    "spawned_at": datetime.now(timezone.utc).isoformat()
                }
            )

            logger.info(
                "Worker spawned successfully",
                extra={
                    "worker_id": worker_id,
                    "task_id": task_id,
                    "worktree_path": worktree_path,
                    "correlation_id": correlation_id
                }
            )

            return {
                "success": True,
                "worker_id": worker_id,
                "task_id": task_id,
                "worktree_path": worktree_path,
                "branch": f"feature/{task_id}",
                "state": WorkerState.NEEDS_INIT.value,
                "correlation_id": correlation_id
            }

    def spawn_batch(self, spec_file: Path) -> List[Dict[str, Any]]:
        """Spawn multiple workers from spec file"""
        with log_operation("spawn_batch", logger):
            logger.info("Spawning batch", extra={"spec_file": str(spec_file)})

            # Load spec
            import yaml
            with open(spec_file, "r") as f:
                spec = yaml.safe_load(f)

            base_branch = spec.get("base_branch", "main")
            tasks = spec.get("tasks", [])

            results = []
            for task in tasks:
                result = self.spawn(
                    task_id=task["id"],
                    description=task["description"],
                    agent=task.get("agent", "code-author"),
                    base_branch=base_branch,
                    priority=task.get("priority", 5)
                )
                results.append(result)

            successful = sum(1 for r in results if r["success"])
            logger.info(
                "Batch spawn complete",
                extra={
                    "total": len(results),
                    "successful": successful,
                    "failed": len(results) - successful
                }
            )

            return results

    def list_workers(self, state_filter: Optional[WorkerState] = None) -> List[Dict[str, Any]]:
        """List all workers"""
        workers = self.state_tracker.list()

        if state_filter:
            workers = [w for w in workers if w["state"] == state_filter.value]

        logger.debug("Workers listed", extra={"count": len(workers), "filter": state_filter})
        return workers

    def get_worker(self, worker_id: str) -> Dict[str, Any]:
        """Get worker details"""
        return self.state_tracker.get(worker_id)

    def terminate(self, worker_id: str, force: bool = False) -> Dict[str, Any]:
        """Terminate a worker"""
        with log_operation(f"terminate_worker:{worker_id}", logger):
            logger.info("Terminating worker", extra={"worker_id": worker_id, "force": force})

            # Get worker state
            worker = self.state_tracker.get(worker_id)

            if not worker.get("exists", True):
                logger.error("Worker not found", extra={"worker_id": worker_id})
                return {"success": False, "error": "Worker not found"}

            task_id = worker.get("task_id")

            # Remove worktree
            result = self._run_worktree_command(
                "remove",
                self.project_name,
                task_id
            )

            if result.returncode != 0 and not force:
                logger.error(
                    "Failed to remove worktree",
                    extra={"worker_id": worker_id, "error": result.stderr}
                )
                return {"success": False, "error": result.stderr}

            # Remove state
            self.state_tracker.remove(worker_id)

            logger.info("Worker terminated", extra={"worker_id": worker_id})

            return {"success": True, "worker_id": worker_id}

    def cleanup(self, state_filter: Optional[WorkerState] = None) -> Dict[str, Any]:
        """Cleanup workers by state"""
        with log_operation("cleanup_workers", logger):
            workers = self.list_workers(state_filter)

            results = []
            for worker in workers:
                worker_id = worker["worker_id"]
                result = self.terminate(worker_id, force=True)
                results.append({
                    "worker_id": worker_id,
                    "success": result["success"]
                })

            successful = sum(1 for r in results if r["success"])
            logger.info(
                "Cleanup complete",
                extra={
                    "total": len(results),
                    "successful": successful,
                    "failed": len(results) - successful
                }
            )

            return {
                "total": len(results),
                "successful": successful,
                "failed": len(results) - successful,
                "results": results
            }


def main():
    parser = argparse.ArgumentParser(description="Worker Manager")
    parser.add_argument(
        "--project",
        default="mice_dolphins",
        help="Project name"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a worker")
    spawn_parser.add_argument("--task-id", required=True, help="Task ID")
    spawn_parser.add_argument("--description", required=True, help="Task description")
    spawn_parser.add_argument("--agent", default="code-author", help="Agent to use")
    spawn_parser.add_argument("--base-branch", default="main", help="Base branch")
    spawn_parser.add_argument("--priority", type=int, default=5, help="Priority (1-10)")

    # spawn-batch command
    batch_parser = subparsers.add_parser("spawn-batch", help="Spawn multiple workers")
    batch_parser.add_argument("--spec-file", required=True, type=Path, help="Spec YAML file")

    # list command
    list_parser = subparsers.add_parser("list", help="List workers")
    list_parser.add_argument(
        "--state",
        choices=[s.value for s in WorkerState],
        help="Filter by state"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get worker details")
    get_parser.add_argument("worker_id", help="Worker ID")

    # terminate command
    terminate_parser = subparsers.add_parser("terminate", help="Terminate a worker")
    terminate_parser.add_argument("worker_id", help="Worker ID")
    terminate_parser.add_argument("--force", action="store_true", help="Force termination")

    # cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup workers")
    cleanup_parser.add_argument(
        "--state",
        choices=[s.value for s in WorkerState],
        help="Filter by state"
    )

    args = parser.parse_args()
    manager = WorkerManager(args.project)

    if args.command == "spawn":
        result = manager.spawn(
            task_id=args.task_id,
            description=args.description,
            agent=args.agent,
            base_branch=args.base_branch,
            priority=args.priority
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.command == "spawn-batch":
        results = manager.spawn_batch(args.spec_file)
        print(json.dumps(results, indent=2))
        successful = sum(1 for r in results if r["success"])
        sys.exit(0 if successful == len(results) else 1)

    elif args.command == "list":
        state_filter = WorkerState(args.state) if args.state else None
        workers = manager.list_workers(state_filter)
        print(json.dumps(workers, indent=2))

    elif args.command == "get":
        worker = manager.get_worker(args.worker_id)
        print(json.dumps(worker, indent=2))

    elif args.command == "terminate":
        result = manager.terminate(args.worker_id, args.force)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.command == "cleanup":
        state_filter = WorkerState(args.state) if args.state else None
        result = manager.cleanup(state_filter)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["successful"] == result["total"] else 1)


if __name__ == "__main__":
    main()
