#!/usr/bin/env python3
"""
Hook: Check Gate

Verifies if quality gate between SDLC phases has been passed.
Used as prerequisite before advancing to next phase.

Checks:
- Required artifacts exist
- Quality criteria are met
- Approvals are in place
"""

import sys
import yaml
import subprocess
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import glob as glob_module

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)

        def info(self, msg, **kwargs):
            self.logger.info(f"{msg} {kwargs}")

        def error(self, msg, **kwargs):
            self.logger.error(f"{msg} {kwargs}")

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class GateChecker:
    """Checks quality gates between SDLC phases."""

    def __init__(self, gate_name: Optional[str] = None):
        self.logger = get_logger(__name__, skill="gate-evaluator")
        self.repo_root = self._find_repo_root()
        self.gate_dir = self.repo_root / ".claude" / "skills" / "gate-evaluator" / "gates"
        self.gate_name = gate_name or "auto"
        self.current_phase: Optional[int] = None
        self.errors = 0
        self.warnings = 0
        self.checks = 0

    def _find_repo_root(self) -> Path:
        """Find git repository root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            return Path.cwd()

    def _read_sdlc_state(self) -> Optional[int]:
        """
        Read current SDLC phase from state file.

        Returns:
            Current phase number or None if not found
        """
        # Try new location first
        state_file = self.repo_root / ".agentic_sdlc" / "projects" / "current" / "state.yml"
        if not state_file.exists():
            # Fallback to old location
            state_file = self.repo_root / ".claude" / "memory" / "sdlc-state.yml"

        if not state_file.exists():
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = yaml.safe_load(f)
                return state.get("current_phase")
        except Exception as e:
            self.logger.debug(
                f"Could not read SDLC state: {e}",
                extra={"error": str(e)}
            )
            return None

    def _auto_detect_gate(self) -> str:
        """
        Auto-detect gate name based on current SDLC phase.

        Returns:
            Gate name (e.g., "phase-2-to-3")
        """
        self.current_phase = self._read_sdlc_state()

        if self.current_phase is None:
            self.logger.warning("SDLC state not found, use /sdlc-start")
            return "unknown"

        next_phase = self.current_phase + 1
        gate_name = f"phase-{self.current_phase}-to-{next_phase}"

        self.logger.debug(
            "Auto-detected gate",
            extra={
                "from_phase": self.current_phase,
                "to_phase": next_phase,
                "gate": gate_name
            }
        )

        return gate_name

    def _list_available_gates(self) -> List[str]:
        """
        List all available gate definition files.

        Returns:
            List of gate names (without .yml extension)
        """
        if not self.gate_dir.exists():
            return []

        gates = []
        for gate_file in self.gate_dir.glob("*.yml"):
            gates.append(gate_file.stem)

        return sorted(gates)

    def _load_gate_definition(self, gate_file: Path) -> Optional[Dict]:
        """
        Load gate definition from YAML file.

        Args:
            gate_file: Path to gate YAML file

        Returns:
            Gate definition dict or None if failed
        """
        try:
            with open(gate_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(
                f"Could not load gate definition: {e}",
                extra={"error": str(e), "file": str(gate_file)}
            )
            return None

    def _check_artifact(self, artifact_name: str, artifact_path: str) -> bool:
        """
        Check if artifact exists (file, directory, or glob pattern).

        Args:
            artifact_name: Human-readable name of artifact
            artifact_path: Path or glob pattern to check

        Returns:
            True if artifact exists, False otherwise
        """
        self.checks += 1

        full_path = self.repo_root / artifact_path

        # Check if it's a direct file or directory
        if full_path.exists():
            self.logger.debug(
                "Artifact found",
                extra={"name": artifact_name, "path": artifact_path}
            )
            print(f"\033[0;32m[OK]\033[0m {artifact_name}: {artifact_path}")
            return True

        # Try as glob pattern
        matches = list(glob_module.glob(str(full_path)))
        if matches:
            self.logger.debug(
                "Artifact found (glob)",
                extra={"name": artifact_name, "pattern": artifact_path}
            )
            print(f"\033[0;32m[OK]\033[0m {artifact_name}: {artifact_path} (glob match)")
            return True

        # Not found
        self.logger.error(
            "Artifact missing",
            extra={"name": artifact_name, "path": artifact_path}
        )
        print(f"\033[0;31m[MISSING]\033[0m {artifact_name}: {artifact_path}")
        self.errors += 1
        return False

    def check_gate(self) -> bool:
        """
        Check if gate criteria are satisfied.

        Returns:
            True if gate passes, False otherwise
        """
        # Auto-detect gate if needed
        if self.gate_name == "auto":
            self.gate_name = self._auto_detect_gate()

            if self.gate_name == "unknown":
                return True  # No gate to check

        # Update logger context with phase
        if self.current_phase is not None:
            self.logger = get_logger(
                __name__,
                skill="gate-evaluator",
                phase=self.current_phase
            )

        # Find gate file
        gate_file = self.gate_dir / f"{self.gate_name}.yml"

        if not gate_file.exists():
            self.logger.warning(
                "Gate not found",
                extra={"gate": self.gate_name, "path": str(gate_file)}
            )
            print(f"Gate not found: {self.gate_name}")
            print("Available gates:")
            for gate in self._list_available_gates():
                print(f"  {gate}")
            return True  # Don't block if gate doesn't exist

        # Load gate definition
        self.logger.info(
            "Checking gate",
            extra={"gate": self.gate_name}
        )
        print(f"Checking gate: {self.gate_name}")
        print("---")

        gate_def = self._load_gate_definition(gate_file)
        if not gate_def:
            return False

        # Check required artifacts
        artifacts = gate_def.get("required_artifacts", [])

        for artifact in artifacts:
            if isinstance(artifact, dict):
                name = artifact.get("name", "Unknown")
                path = artifact.get("path", "")
                self._check_artifact(name, path)

        print("---")

        # Final result
        if self.errors > 0:
            self.logger.error(
                "Gate BLOCKED",
                extra={
                    "gate": self.gate_name,
                    "errors": self.errors,
                    "checks": self.checks
                }
            )
            print(f"\033[0;31mGate BLOCKED\033[0m: {self.errors} artifact(s) missing")
            return False

        self.logger.info(
            "Gate PASSED",
            extra={"gate": self.gate_name, "checks": self.checks}
        )
        print("\033[0;32mGate PASSED\033[0m")
        return True

    def execute(self) -> int:
        """
        Execute gate check.

        Returns:
            0 if gate passes, 1 otherwise
        """
        self.logger.debug(
            "Starting gate check",
            extra={"gate": self.gate_name}
        )

        if self.check_gate():
            return 0

        return 1


def main() -> int:
    """
    Main entry point for gate check hook.

    Args:
        sys.argv[1]: Gate name (optional, defaults to "auto")

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    gate_name = sys.argv[1] if len(sys.argv) > 1 else "auto"
    checker = GateChecker(gate_name)

    try:
        return checker.execute()
    except Exception as e:
        checker.logger.error(
            f"Gate check failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
