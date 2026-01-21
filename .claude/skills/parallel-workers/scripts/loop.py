#!/usr/bin/env python3
"""
Worker Automation Loop

Monitors parallel workers and transitions their states automatically.
Adapted from claude-orchestrator for platform independence.
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add lib to path for logging
sys.path.insert(0, str(Path(__file__).parents[3] / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

# Import worker components
from state_tracker import StateTracker, WorkerState
from worker_manager import WorkerManager

logger = get_logger(__name__, skill="parallel-workers", phase=5)


class AutomationLoop:
    """Monitors and manages worker lifecycle automatically"""

    def __init__(
        self,
        project_name: str,
        poll_interval: int = 5,
        max_iterations: Optional[int] = None
    ):
        self.project_name = project_name
        self.poll_interval = poll_interval
        self.max_iterations = max_iterations
        self.state_tracker = StateTracker()
        self.worker_manager = WorkerManager(project_name)

        logger.info(
            "AutomationLoop initialized",
            extra={
                "project": project_name,
                "poll_interval": poll_interval,
                "max_iterations": max_iterations
            }
        )

    def check_git_status(self, worktree_path: str) -> Dict[str, Any]:
        """Check git status of worktree"""
        try:
            result = subprocess.run(
                ["git", "-C", worktree_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )

            uncommitted = len([line for line in result.stdout.splitlines() if line.strip()])

            return {
                "uncommitted_changes": uncommitted,
                "clean": uncommitted == 0
            }
        except subprocess.CalledProcessError as e:
            logger.error(
                "Failed to check git status",
                extra={
                    "worktree": worktree_path,
                    "error": str(e)
                }
            )
            return {"error": str(e)}

    def check_pr_status(self, worker: Dict[str, Any]) -> Optional[str]:
        """Check if PR exists for worker branch"""
        branch = worker.get("branch")
        if not branch:
            return None

        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--head", branch, "--json", "url", "--jq", ".[0].url"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

            return None
        except FileNotFoundError:
            logger.warning("gh CLI not found, PR checking disabled")
            return None

    def check_pr_merged(self, pr_url: str) -> bool:
        """Check if PR is merged"""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", pr_url, "--json", "state", "--jq", ".state"],
                capture_output=True,
                text=True,
                check=True
            )

            state = result.stdout.strip().upper()
            return state == "MERGED"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def handle_needs_init(self, worker: Dict[str, Any]) -> None:
        """Handle worker in NEEDS_INIT state"""
        worker_id = worker["worker_id"]

        with log_operation(f"handle_needs_init:{worker_id}", logger):
            logger.info(
                "Worker needs initialization",
                extra={
                    "worker_id": worker_id,
                    "task_id": worker.get("task_id")
                }
            )

            # Transition to WORKING (manual init assumed)
            self.state_tracker.transition(
                worker_id,
                WorkerState.NEEDS_INIT,
                WorkerState.WORKING,
                metadata={"auto_transition": True}
            )

    def handle_working(self, worker: Dict[str, Any]) -> None:
        """Handle worker in WORKING state"""
        worker_id = worker["worker_id"]
        worktree_path = worker.get("worktree_path")

        if not worktree_path or not Path(worktree_path).exists():
            logger.warning(
                "Worktree not found",
                extra={"worker_id": worker_id, "path": worktree_path}
            )
            return

        # Check for PR
        pr_url = self.check_pr_status(worker)

        if pr_url:
            with log_operation(f"pr_detected:{worker_id}", logger):
                logger.info(
                    "PR detected for worker",
                    extra={
                        "worker_id": worker_id,
                        "pr_url": pr_url
                    }
                )

                # Transition to PR_OPEN
                self.state_tracker.transition(
                    worker_id,
                    WorkerState.WORKING,
                    WorkerState.PR_OPEN,
                    metadata={
                        "pr_url": pr_url,
                        "detected_at": datetime.now(timezone.utc).isoformat()
                    }
                )

    def handle_pr_open(self, worker: Dict[str, Any]) -> None:
        """Handle worker in PR_OPEN state"""
        worker_id = worker["worker_id"]
        pr_url = worker.get("pr_url")

        if not pr_url:
            logger.warning(
                "No PR URL in PR_OPEN worker",
                extra={"worker_id": worker_id}
            )
            return

        # Check if merged
        if self.check_pr_merged(pr_url):
            with log_operation(f"pr_merged:{worker_id}", logger):
                logger.info(
                    "PR merged for worker",
                    extra={
                        "worker_id": worker_id,
                        "pr_url": pr_url
                    }
                )

                # Transition to MERGED
                self.state_tracker.transition(
                    worker_id,
                    WorkerState.PR_OPEN,
                    WorkerState.MERGED,
                    metadata={
                        "merged_at": datetime.now(timezone.utc).isoformat()
                    }
                )

    def handle_merged(self, worker: Dict[str, Any]) -> None:
        """Handle worker in MERGED state (cleanup)"""
        worker_id = worker["worker_id"]

        with log_operation(f"cleanup_merged:{worker_id}", logger):
            logger.info(
                "Cleaning up merged worker",
                extra={"worker_id": worker_id}
            )

            # Terminate worker (removes worktree and state)
            result = self.worker_manager.terminate(worker_id, force=False)

            if result["success"]:
                logger.info(
                    "Worker cleaned up",
                    extra={"worker_id": worker_id}
                )
            else:
                logger.error(
                    "Failed to cleanup worker",
                    extra={
                        "worker_id": worker_id,
                        "error": result.get("error")
                    }
                )

    def process_worker(self, worker: Dict[str, Any]) -> None:
        """Process a single worker based on state"""
        worker_id = worker["worker_id"]
        state = WorkerState(worker["state"])

        logger.debug(
            "Processing worker",
            extra={
                "worker_id": worker_id,
                "state": state.value,
                "task_id": worker.get("task_id")
            }
        )

        try:
            if state == WorkerState.NEEDS_INIT:
                self.handle_needs_init(worker)
            elif state == WorkerState.WORKING:
                self.handle_working(worker)
            elif state == WorkerState.PR_OPEN:
                self.handle_pr_open(worker)
            elif state == WorkerState.MERGED:
                self.handle_merged(worker)
            elif state == WorkerState.ERROR:
                logger.warning(
                    "Worker in error state",
                    extra={
                        "worker_id": worker_id,
                        "error": worker.get("error")
                    }
                )

        except Exception as e:
            logger.error(
                "Error processing worker",
                extra={
                    "worker_id": worker_id,
                    "state": state.value,
                    "error": str(e)
                }
            )

            # Transition to ERROR
            self.state_tracker.set(
                worker_id,
                WorkerState.ERROR,
                metadata={"error": str(e)}
            )

    def run(self) -> None:
        """Run automation loop"""
        iteration = 0

        logger.info("Starting automation loop")

        try:
            while True:
                iteration += 1

                if self.max_iterations and iteration > self.max_iterations:
                    logger.info(
                        "Max iterations reached",
                        extra={"iterations": iteration}
                    )
                    break

                with log_operation(f"loop_iteration:{iteration}", logger):
                    # List all workers
                    workers = self.worker_manager.list_workers()

                    if not workers:
                        logger.debug("No active workers")
                    else:
                        logger.debug(
                            "Processing workers",
                            extra={"count": len(workers)}
                        )

                        # Process each worker
                        for worker in workers:
                            self.process_worker(worker)

                # Sleep
                logger.debug(f"Sleeping {self.poll_interval}s")
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Automation loop interrupted by user")

        except Exception as e:
            logger.error(
                "Automation loop error",
                extra={"error": str(e)}
            )
            raise

        finally:
            logger.info(
                "Automation loop stopped",
                extra={"iterations": iteration}
            )


def main():
    parser = argparse.ArgumentParser(description="Worker Automation Loop")
    parser.add_argument(
        "--project",
        default="mice_dolphins",
        help="Project name"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=5,
        help="Poll interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum iterations (for testing)"
    )

    args = parser.parse_args()

    loop = AutomationLoop(
        project_name=args.project,
        poll_interval=args.poll_interval,
        max_iterations=args.max_iterations
    )

    loop.run()


if __name__ == "__main__":
    main()
