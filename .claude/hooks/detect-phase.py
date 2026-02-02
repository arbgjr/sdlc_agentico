#!/usr/bin/env python3
"""
Hook: Detect Phase

Automatically detects SDLC phase based on context.
Executed on UserPromptSubmit hook.
"""

import sys
import subprocess
from typing import Optional, Tuple
from pathlib import Path

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

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class PhaseDetector:
    """Detects current SDLC phase based on context and files."""

    # Agent suggestions per phase
    PHASE_AGENTS = {
        0: "intake-analyst",
        1: "domain-researcher",
        2: "requirements-analyst",
        3: "system-architect",
        4: "delivery-planner",
        5: "code-author",
        6: "security-scanner",
        7: "release-manager",
        8: "incident-commander",
    }

    def __init__(self):
        self.logger = get_logger(__name__, skill="orchestrator")
        self.repo_root = Path.cwd()

    def _has_active_incident(self) -> bool:
        """Check if there's an active incident."""
        # Check old location
        if (self.repo_root / ".claude" / "memory" / "active-incident.yml").exists():
            return True

        # Check new location
        incident_files = list(
            self.repo_root.glob(".agentic_sdlc/projects/*/active-incident.yml")
        )
        return len(incident_files) > 0

    def _has_release_tag(self) -> bool:
        """Check if current commit has a release tag."""
        try:
            result = subprocess.run(
                ["git", "tag", "--points-at", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                tags = result.stdout.strip().split("\n")
                return any(tag.startswith("v") for tag in tags if tag)
        except Exception:
            pass
        return False

    def _has_staged_code(self) -> bool:
        """Check if there's staged code."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                code_extensions = {".py", ".js", ".ts", ".java", ".go", ".cs", ".rb"}
                code_files = [
                    f for f in files
                    if f and Path(f).suffix in code_extensions
                ]
                if code_files:
                    self.logger.debug(
                        f"Staged code detected: {len(code_files)} files"
                    )
                    return True
        except Exception:
            pass
        return False

    def _has_specs(self) -> Tuple[bool, bool]:
        """
        Check if specs and plans exist.

        Returns:
            Tuple of (has_specs, has_plans)
        """
        specs_dir = self.repo_root / ".specify" / "specs"
        plans_dir = self.repo_root / ".specify" / "plans"

        has_specs = specs_dir.exists() and any(specs_dir.iterdir())
        has_plans = plans_dir.exists() and any(plans_dir.iterdir())

        return has_specs, has_plans

    def _has_intake(self) -> bool:
        """Check if intake file exists."""
        # Check old location
        if (self.repo_root / ".claude" / "memory" / "current-intake.yml").exists():
            return True

        # Check new location
        intake_files = list(
            self.repo_root.glob(".agentic_sdlc/projects/*/intake.yml")
        )
        return len(intake_files) > 0

    def _get_phase_from_manifest(self) -> Optional[int]:
        """
        Read phase from project manifest.

        Returns:
            Phase number or None if not found
        """
        manifest_files = list(
            self.repo_root.glob(".agentic_sdlc/projects/*/manifest.yml")
        )

        if not manifest_files:
            return None

        manifest = manifest_files[0]

        try:
            import yaml
            with open(manifest, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                phase = data.get("current_phase")
                if phase is not None:
                    self.logger.debug(f"Phase from manifest: {phase}")
                    return int(phase)
        except Exception as e:
            self.logger.debug(
                f"Could not read phase from manifest: {e}"
            )

        return None

    def detect(self) -> Tuple[int, str]:
        """
        Detect current SDLC phase.

        Returns:
            Tuple of (phase_number, context_label)
        """
        self.logger.debug("Detecting SDLC phase")

        # Check for active incident (Phase 8)
        if self._has_active_incident():
            self.logger.debug("Incident detected")
            return 8, "incident-active"

        # Check for release tag (Phase 7)
        if self._has_release_tag():
            self.logger.debug("Release tag detected")
            return 7, "release"

        # Check for staged code (Phase 5)
        if self._has_staged_code():
            return 5, "implementation"

        # Check for specs/plans (Phases 3-4)
        has_specs, has_plans = self._has_specs()
        if has_specs:
            if has_plans:
                self.logger.debug("Plans detected")
                return 4, "planning"
            else:
                self.logger.debug("Specs detected without plans")
                return 3, "architecture"

        # Check for intake (Phase 2)
        if self._has_intake():
            self.logger.debug("Intake detected")
            return 2, "requirements"

        # Try to read phase from manifest
        manifest_phase = self._get_phase_from_manifest()
        if manifest_phase is not None:
            return manifest_phase, "from-manifest"

        # Default: discovery (Phase 1)
        self.logger.debug("No specific phase indicators found, defaulting to discovery")
        return 1, "discovery"

    def execute(self) -> int:
        """
        Execute phase detection and output results.

        Returns:
            0 always (never block)
        """
        # Detect phase
        phase, context = self.detect()

        # Get suggested agent
        agent = self.PHASE_AGENTS.get(phase, "orchestrator")

        # Output for SDLC
        result = f"phase:{phase} ({context})"

        self.logger.info(f"Phase detected: {result}")
        self.logger.debug(f"Suggested agent: {agent}")

        # Print environment variables for Claude Code
        print(f"SDLC_PHASE={result}")
        print(f"SUGGESTED_AGENT={agent}")

        return 0


def main() -> int:
    """
    Main entry point for detect-phase hook.

    Returns:
        Exit code (0 always)
    """
    detector = PhaseDetector()

    try:
        return detector.execute()
    except Exception as e:
        detector.logger.warning(
            f"Phase detection failed with exception: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Default fallback
        print("SDLC_PHASE=phase:1 (discovery)")
        print("SUGGESTED_AGENT=orchestrator")
        return 0


if __name__ == "__main__":
    sys.exit(main())
