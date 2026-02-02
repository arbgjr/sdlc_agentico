#!/usr/bin/env python3
"""
Hook: post-gate-audit
Executes adversarial audit after quality gate passes.
Version: 3.0.0 (Python-First)

Triggered by: orchestrator after gate-evaluator passes
Purpose: Adversarial quality assurance - find problems self-validation missed

Cross-platform (Linux, macOS, Windows)

Environment Variables:
    PHASE: Current SDLC phase number (0-8)
    PROJECT_PATH: Path to project being audited
    GATE_RESULT: Result of gate evaluation (passed|failed)
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add lib path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "python"))

from sdlc_logging import get_logger


class PostGateAuditor:
    """Manages adversarial audits after gate passes."""

    def __init__(self, phase: int):
        """
        Initialize auditor.

        Args:
            phase: SDLC phase number (0-8)
        """
        self.phase = phase
        self.repo_root = Path.cwd()
        self.config_file = (
            self.repo_root / ".claude" / "config" / "adversarial-audit.yml"
        )
        self.audit_script = (
            self.repo_root / ".claude" / "skills" / "adversarial-validator"
            / "scripts" / "audit_phase.py"
        )
        self.logger = get_logger(
            __name__,
            skill="adversarial-validator",
            phase=phase
        )

    def load_config(self) -> Dict[str, Any]:
        """
        Load audit configuration from YAML.

        Returns:
            Configuration dictionary
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                return config
        except FileNotFoundError:
            self.logger.warning(
                "Config file not found, using defaults",
                extra={"config_file": str(self.config_file)}
            )
            return {
                "adversarial_audit": {
                    "enabled": True,
                    "phases": list(range(9))
                }
            }
        except yaml.YAMLError as e:
            self.logger.error(
                "Failed to parse config file",
                extra={"error": str(e)}
            )
            return {
                "adversarial_audit": {
                    "enabled": True,
                    "phases": list(range(9))
                }
            }

    def should_audit(self, config: Dict[str, Any]) -> bool:
        """
        Check if audit should run for current phase.

        Args:
            config: Audit configuration

        Returns:
            True if audit should run
        """
        audit_config = config.get("adversarial_audit", {})

        # Check if enabled
        if not audit_config.get("enabled", True):
            self.logger.info("Adversarial audit disabled in config")
            return False

        # Check if phase should be audited
        phases_to_audit = audit_config.get("phases", list(range(9)))

        if self.phase not in phases_to_audit:
            self.logger.info(
                "Phase not configured for audit",
                extra={
                    "phase": self.phase,
                    "configured_phases": phases_to_audit
                }
            )
            return False

        return True

    def run_audit(self, project_path: str) -> Optional[Path]:
        """
        Execute audit script and return report path.

        Args:
            project_path: Path to project being audited

        Returns:
            Path to audit report, or None if failed
        """
        report_path = (
            self.repo_root / ".agentic_sdlc" / "audit-reports"
            / f"audit-phase-{self.phase}.yml"
        )

        try:
            self.logger.info(
                "Running adversarial audit",
                extra={
                    "phase": self.phase,
                    "project": project_path
                }
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.audit_script),
                    "--phase", str(self.phase),
                    "--project-path", project_path
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            self.logger.info(
                "Audit execution completed",
                extra={"phase": self.phase}
            )

            return report_path

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Audit script execution failed",
                extra={
                    "phase": self.phase,
                    "exit_code": e.returncode,
                    "stderr": e.stderr
                }
            )
            return None

        except subprocess.TimeoutExpired:
            self.logger.error(
                "Audit script timed out",
                extra={"phase": self.phase, "timeout": 300}
            )
            return None

        except Exception as e:
            self.logger.error(
                "Unexpected error running audit",
                extra={"error": str(e)}
            )
            return None

    def parse_audit_report(self, report_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse audit report YAML.

        Args:
            report_path: Path to audit report

        Returns:
            Report dictionary, or None if failed
        """
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(
                "Audit report not found",
                extra={"path": str(report_path)}
            )
            return None
        except yaml.YAMLError as e:
            self.logger.error(
                "Failed to parse audit report",
                extra={"error": str(e)}
            )
            return None

    def handle_decision(
        self,
        report: Dict[str, Any],
        config: Dict[str, Any]
    ) -> int:
        """
        Handle audit decision and return exit code.

        Args:
            report: Audit report dictionary
            config: Audit configuration

        Returns:
            Exit code (0=pass, 1=fail)
        """
        decision = report.get("decision", "FAIL")
        findings = report.get("findings", {})
        summary = report.get("summary", {})

        if decision == "FAIL":
            self.logger.error(
                "Adversarial audit FAILED",
                extra={
                    "phase": self.phase,
                    "critical": summary.get("critical", 0),
                    "grave": summary.get("grave", 0),
                    "total_findings": findings.get("total", 0)
                }
            )

            # Check auto-correction
            auto_correct = config.get(
                "adversarial_audit", {}
            ).get("auto_correct", {}).get("enabled", False)

            if auto_correct:
                max_retries = config.get(
                    "adversarial_audit", {}
                ).get("auto_correct", {}).get("max_retries", 3)

                self.logger.info(
                    "Attempting auto-correction",
                    extra={"max_retries": max_retries}
                )

                # Auto-correction not yet implemented
                self.logger.warning(
                    "Auto-correction not yet implemented, escalating to human"
                )

            return 1

        elif decision == "PASS_WITH_WARNINGS":
            self.logger.warning(
                "Adversarial audit passed with warnings",
                extra={
                    "phase": self.phase,
                    "medium": summary.get("medium", 0),
                    "light": summary.get("light", 0)
                }
            )

            # TODO: Create GitHub issues for MEDIUM/LIGHT findings
            self.logger.info(
                "Creating tech debt issues for findings",
                extra={"phase": self.phase}
            )

            return 0

        elif decision == "PASS":
            self.logger.info(
                "Adversarial audit PASSED",
                extra={
                    "phase": self.phase,
                    "findings": 0
                }
            )
            return 0

        else:
            self.logger.error(
                "Unknown audit decision",
                extra={
                    "decision": decision,
                    "phase": self.phase
                }
            )
            return 1

    def execute(self, gate_result: str, project_path: str) -> int:
        """
        Main execution flow.

        Args:
            gate_result: Gate evaluation result (passed|failed)
            project_path: Path to project being audited

        Returns:
            Exit code (0=success, 1=failure)
        """
        self.logger.info(
            "Post-gate audit hook triggered",
            extra={
                "phase": self.phase,
                "gate_result": gate_result,
                "project": project_path
            }
        )

        # Only run if gate passed
        if gate_result != "passed":
            self.logger.info(
                "Gate did not pass, skipping adversarial audit",
                extra={"gate_result": gate_result}
            )
            return 0

        # Load config
        config = self.load_config()

        # Check if should audit
        if not self.should_audit(config):
            return 0

        # Run audit
        report_path = self.run_audit(project_path)
        if not report_path:
            self.logger.error("Audit execution failed")
            return 1

        # Parse report
        report = self.parse_audit_report(report_path)
        if not report:
            self.logger.error("Failed to parse audit report")
            return 1

        # Handle decision
        return self.handle_decision(report, config)


def main():
    """Entry point."""
    # Get environment variables
    phase_str = os.environ.get("PHASE", "0")
    gate_result = os.environ.get("GATE_RESULT", "unknown")
    project_path = os.environ.get("PROJECT_PATH", ".")

    try:
        phase = int(phase_str)
    except ValueError:
        print(f"[ERROR] Invalid PHASE: {phase_str}", file=sys.stderr)
        sys.exit(1)

    # Create auditor and execute
    auditor = PostGateAuditor(phase)
    exit_code = auditor.execute(gate_result, project_path)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
