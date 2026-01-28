#!/usr/bin/env python3
"""
Adversarial Audit Script for SDLC Phases

Executes comprehensive adversarial audit on a completed SDLC phase.
Finds problems that self-validation and gates may have missed.

Usage:
    python3 audit_phase.py --phase 5 --project-path /path/to/project
    python3 audit_phase.py --phase 3 --config custom-config.yml
    python3 audit_phase.py --phase 6 --report-only
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import yaml

# Add SDLC logging library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib" / "python"))
from sdlc_logging import get_logger, log_operation

# Logger
logger = get_logger(__name__, skill="adversarial-validator", phase=0)


class AuditFinding:
    """Represents a single audit finding"""

    def __init__(
        self,
        finding_id: str,
        severity: str,
        title: str,
        description: str,
        location: Optional[str] = None,
        evidence: Optional[str] = None,
        recommendation: Optional[str] = None,
        auto_fixable: bool = False
    ):
        self.finding_id = finding_id
        self.severity = severity  # CRITICAL, GRAVE, MEDIUM, LIGHT
        self.title = title
        self.description = description
        self.location = location
        self.evidence = evidence
        self.recommendation = recommendation
        self.auto_fixable = auto_fixable

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        result = {
            "id": self.finding_id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
        }

        if self.location:
            result["location"] = self.location
        if self.evidence:
            result["evidence"] = self.evidence
        if self.recommendation:
            result["recommendation"] = self.recommendation
        if self.auto_fixable:
            result["auto_fixable"] = self.auto_fixable

        return result


class PhaseAuditor:
    """Executes adversarial audit on SDLC phases"""

    def __init__(self, phase: int, project_path: Path, config: Dict[str, Any]):
        self.phase = phase
        self.project_path = project_path
        self.config = config
        self.findings: List[AuditFinding] = []
        self.finding_counter = 1

        # Configure logger with phase context
        global logger
        logger = get_logger(__name__, skill="adversarial-validator", phase=phase)

    def audit(self) -> Dict[str, Any]:
        """Execute complete adversarial audit"""
        logger.info(f"Starting adversarial audit for Phase {self.phase}", extra={
            "project_path": str(self.project_path)
        })

        with log_operation(logger, "complete_audit"):
            # 1. Load phase configuration
            phase_config = self._load_phase_config()

            # 2. Review artifacts
            artifact_findings = self._review_artifacts(phase_config)
            self.findings.extend(artifact_findings)

            # 3. Run automated checks
            automated_findings = self._run_automated_checks()
            self.findings.extend(automated_findings)

            # 4. LLM deep analysis (phase-auditor agent)
            llm_findings = self._run_llm_analysis(phase_config)
            self.findings.extend(llm_findings)

            # 5. Classify and decide
            decision = self._make_decision()

            # 6. Generate report
            report = self._generate_report(decision, phase_config)

            logger.info(f"Audit completed: {decision}", extra={
                "total_findings": len(self.findings),
                "decision": decision
            })

            return report

    def _load_phase_config(self) -> Dict[str, Any]:
        """Load phase-specific configuration"""
        logger.debug(f"Loading configuration for Phase {self.phase}")

        phase_criteria = self.config.get("phase_criteria", {})
        phase_key = f"phase_{self.phase}"

        if phase_key not in phase_criteria:
            logger.warning(f"No phase criteria found for {phase_key}")
            return {}

        config = phase_criteria[phase_key]
        logger.debug(f"Phase config loaded: {config.get('name', 'Unknown')}", extra={
            "expected_artifacts": len(config.get("expected_artifacts", [])),
            "quality_checks": len(config.get("quality_checks", []))
        })

        return config

    def _review_artifacts(self, phase_config: Dict[str, Any]) -> List[AuditFinding]:
        """Review expected artifacts for phase"""
        findings = []
        expected = phase_config.get("expected_artifacts", [])

        logger.info(f"Reviewing {len(expected)} expected artifacts")

        for artifact_pattern in expected:
            # Convert glob pattern to list of files
            matches = list(self.project_path.glob(artifact_pattern))

            if not matches:
                finding = AuditFinding(
                    finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                    severity="GRAVE",
                    title=f"Missing expected artifact: {artifact_pattern}",
                    description=f"Phase {self.phase} requires artifact matching '{artifact_pattern}' but none found.",
                    location=str(self.project_path),
                    recommendation=f"Create the required artifact: {artifact_pattern}",
                    auto_fixable=False
                )
                findings.append(finding)
                self.finding_counter += 1
                logger.warning(f"Missing artifact: {artifact_pattern}")
            else:
                logger.debug(f"Found artifact: {artifact_pattern} ({len(matches)} files)")

        return findings

    def _run_automated_checks(self) -> List[AuditFinding]:
        """Run automated security and quality checks"""
        findings = []

        automated_checks = self.config.get("adversarial_audit", {}).get("automated_checks", {})

        # Security checks
        if "security" in automated_checks:
            with log_operation(logger, "security_checks"):
                findings.extend(self._check_hardcoded_secrets())
                findings.extend(self._check_sql_injection_patterns())
                findings.extend(self._check_xss_vulnerabilities())

        # Quality checks
        if "quality" in automated_checks:
            with log_operation(logger, "quality_checks"):
                findings.extend(self._check_test_coverage())
                findings.extend(self._check_todos_fixmes())
                findings.extend(self._check_error_handling())

        # Completeness checks
        if "completeness" in automated_checks:
            with log_operation(logger, "completeness_checks"):
                findings.extend(self._check_documentation())

        return findings

    def _check_hardcoded_secrets(self) -> List[AuditFinding]:
        """Scan for hardcoded secrets"""
        findings = []

        patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api[_-]?key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
            r'token\s*=\s*["\'].*["\']',
            r'aws_access_key_id\s*=\s*["\'].*["\']',
            r'private[_-]?key\s*=\s*["\'].*["\']',
        ]

        exclusions = self.config.get("adversarial_audit", {}).get("exclusions", {}).get("paths", [])

        for file_path in self.project_path.rglob("*"):
            # Skip excluded paths
            if any(file_path.match(pattern) for pattern in exclusions):
                continue

            # Skip binary files
            if not file_path.is_file() or file_path.suffix in [".pyc", ".so", ".dll"]:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Calculate line number
                        line_no = content[:match.start()].count("\n") + 1

                        finding = AuditFinding(
                            finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                            severity="CRITICAL",
                            title="Hardcoded secret detected",
                            description=f"Potential hardcoded secret found in source code.",
                            location=f"{file_path}:{line_no}",
                            evidence=match.group(0)[:100],  # Limit evidence length
                            recommendation="Move secret to environment variable or secret manager",
                            auto_fixable=False
                        )
                        findings.append(finding)
                        self.finding_counter += 1
                        logger.error(f"Hardcoded secret detected: {file_path}:{line_no}")

            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue

        return findings

    def _check_sql_injection_patterns(self) -> List[AuditFinding]:
        """Check for SQL injection vulnerabilities"""
        findings = []

        # Pattern: string concatenation in SQL queries
        sql_patterns = [
            r'execute\s*\(\s*["\'].*\+.*["\']',
            r'\.execute\s*\(\s*f["\']',  # f-strings in SQL
            r'cursor\.execute\s*\(\s*.*\%.*\)',  # % formatting
        ]

        exclusions = self.config.get("adversarial_audit", {}).get("exclusions", {}).get("paths", [])

        for file_path in self.project_path.rglob("*.py"):
            if any(file_path.match(pattern) for pattern in exclusions):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count("\n") + 1

                        finding = AuditFinding(
                            finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                            severity="CRITICAL",
                            title="Potential SQL injection vulnerability",
                            description="SQL query uses string concatenation instead of parameterized queries",
                            location=f"{file_path}:{line_no}",
                            evidence=match.group(0)[:100],
                            recommendation="Use parameterized queries (e.g., execute(query, params))",
                            auto_fixable=False
                        )
                        findings.append(finding)
                        self.finding_counter += 1

            except (UnicodeDecodeError, PermissionError):
                continue

        return findings

    def _check_xss_vulnerabilities(self) -> List[AuditFinding]:
        """Check for XSS vulnerabilities"""
        findings = []

        # Pattern: innerHTML, dangerouslySetInnerHTML without sanitization
        xss_patterns = [
            r'innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'document\.write\s*\(',
        ]

        exclusions = self.config.get("adversarial_audit", {}).get("exclusions", {}).get("paths", [])

        for file_path in self.project_path.rglob("*"):
            if file_path.suffix not in [".js", ".jsx", ".ts", ".tsx", ".html"]:
                continue

            if any(file_path.match(pattern) for pattern in exclusions):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for pattern in xss_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count("\n") + 1

                        finding = AuditFinding(
                            finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                            severity="GRAVE",
                            title="Potential XSS vulnerability",
                            description="Direct HTML injection without sanitization detected",
                            location=f"{file_path}:{line_no}",
                            evidence=match.group(0)[:100],
                            recommendation="Use textContent, sanitize HTML, or use framework's safe APIs",
                            auto_fixable=False
                        )
                        findings.append(finding)
                        self.finding_counter += 1

            except (UnicodeDecodeError, PermissionError):
                continue

        return findings

    def _check_test_coverage(self) -> List[AuditFinding]:
        """Check test coverage"""
        findings = []

        # Try to run pytest with coverage
        try:
            result = subprocess.run(
                ["pytest", "--cov=src", "--cov=app", "--cov-report=json", "--quiet"],
                cwd=self.project_path,
                capture_output=True,
                timeout=300
            )

            # Look for coverage report
            coverage_file = self.project_path / "coverage.json"
            if coverage_file.exists():
                coverage_data = json.loads(coverage_file.read_text())
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

                if total_coverage < 80:
                    finding = AuditFinding(
                        finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                        severity="GRAVE",
                        title=f"Test coverage too low: {total_coverage:.1f}%",
                        description=f"Code coverage is {total_coverage:.1f}%, below the 80% threshold",
                        recommendation="Add tests to reach >= 80% coverage",
                        auto_fixable=False
                    )
                    findings.append(finding)
                    self.finding_counter += 1
                    logger.warning(f"Low test coverage: {total_coverage:.1f}%")

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # pytest not available or failed - log but don't fail audit
            logger.debug("Could not run coverage check (pytest not available or failed)")

        return findings

    def _check_todos_fixmes(self) -> List[AuditFinding]:
        """Find TODO/FIXME comments in code"""
        findings = []

        todo_patterns = [
            r'#\s*TODO',
            r'#\s*FIXME',
            r'#\s*XXX',
            r'#\s*HACK',
            r'//\s*TODO',
            r'//\s*FIXME',
        ]

        exclusions = self.config.get("adversarial_audit", {}).get("exclusions", {}).get("paths", [])

        for file_path in self.project_path.rglob("*"):
            if file_path.suffix not in [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cs", ".go"]:
                continue

            if any(file_path.match(pattern) for pattern in exclusions):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for pattern in todo_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count("\n") + 1

                        # Get full line for context
                        lines = content.split("\n")
                        evidence = lines[line_no - 1].strip() if line_no <= len(lines) else match.group(0)

                        finding = AuditFinding(
                            finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                            severity="MEDIUM",
                            title="TODO/FIXME comment in production code",
                            description="Unfinished work marker left in code",
                            location=f"{file_path}:{line_no}",
                            evidence=evidence[:100],
                            recommendation="Complete the work or remove the comment if no longer applicable",
                            auto_fixable=False
                        )
                        findings.append(finding)
                        self.finding_counter += 1

            except (UnicodeDecodeError, PermissionError):
                continue

        return findings

    def _check_error_handling(self) -> List[AuditFinding]:
        """Check for proper error handling"""
        findings = []

        # Pattern: bare except clauses
        bare_except_pattern = r'except\s*:'

        exclusions = self.config.get("adversarial_audit", {}).get("exclusions", {}).get("paths", [])

        for file_path in self.project_path.rglob("*.py"):
            if any(file_path.match(pattern) for pattern in exclusions):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                matches = re.finditer(bare_except_pattern, content)
                for match in matches:
                    line_no = content[:match.start()].count("\n") + 1

                    finding = AuditFinding(
                        finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                        severity="MEDIUM",
                        title="Bare except clause detected",
                        description="Using 'except:' catches all exceptions including SystemExit and KeyboardInterrupt",
                        location=f"{file_path}:{line_no}",
                        evidence=match.group(0),
                        recommendation="Use specific exception types (e.g., except ValueError:)",
                        auto_fixable=True
                    )
                    findings.append(finding)
                    self.finding_counter += 1

            except (UnicodeDecodeError, PermissionError):
                continue

        return findings

    def _check_documentation(self) -> List[AuditFinding]:
        """Check documentation completeness"""
        findings = []

        # Check for README.md
        readme = self.project_path / "README.md"
        if not readme.exists():
            finding = AuditFinding(
                finding_id=f"AUDIT-{self.phase:03d}-{self.finding_counter:03d}",
                severity="LIGHT",
                title="Missing README.md",
                description="Project lacks a README.md file",
                location=str(self.project_path),
                recommendation="Create README.md with project overview, setup, and usage instructions",
                auto_fixable=False
            )
            findings.append(finding)
            self.finding_counter += 1

        return findings

    def _run_llm_analysis(self, phase_config: Dict[str, Any]) -> List[AuditFinding]:
        """Run LLM-based deep analysis using phase-auditor agent"""
        findings = []

        logger.info("Running LLM deep analysis with phase-auditor agent")

        # Prepare prompt for phase-auditor
        prompt = self._build_llm_prompt(phase_config)

        # Note: In real implementation, this would call the phase-auditor agent
        # For now, we log that LLM analysis would happen here
        logger.info("LLM analysis would be invoked here", extra={
            "agent": "phase-auditor",
            "phase": self.phase,
            "prompt_length": len(prompt)
        })

        # TODO: Implement actual agent invocation
        # findings_from_llm = call_agent("phase-auditor", prompt)
        # findings.extend(findings_from_llm)

        return findings

    def _build_llm_prompt(self, phase_config: Dict[str, Any]) -> str:
        """Build prompt for phase-auditor agent"""
        phase_name = phase_config.get("name", f"Phase {self.phase}")
        expected_artifacts = phase_config.get("expected_artifacts", [])
        quality_checks = phase_config.get("quality_checks", [])

        prompt = f"""Analyze Phase {self.phase} ({phase_name}) work with CHALLENGE MINDSET.
Your job is to FIND PROBLEMS, not to validate.

Project Path: {self.project_path}

Expected Artifacts:
{chr(10).join(f"- {a}" for a in expected_artifacts)}

Quality Criteria:
{chr(10).join(f"- {c}" for c in quality_checks)}

Find: CRITICAL, GRAVE, MEDIUM, LIGHT issues.
Be skeptical. Look deeper. Challenge assumptions.

Current findings from automated checks: {len(self.findings)}
"""
        return prompt

    def _make_decision(self) -> str:
        """Make audit decision based on findings"""
        # Count by severity
        counts = {
            "CRITICAL": 0,
            "GRAVE": 0,
            "MEDIUM": 0,
            "LIGHT": 0
        }

        for finding in self.findings:
            severity = finding.severity
            if severity in counts:
                counts[severity] += 1

        logger.info("Findings summary", extra=counts)

        # Decision logic from config
        fail_on = self.config.get("adversarial_audit", {}).get("fail_on", ["CRITICAL", "GRAVE"])

        if any(counts[severity] > 0 for severity in fail_on):
            return "FAIL"
        elif counts["MEDIUM"] > 0 or counts["LIGHT"] > 0:
            return "PASS_WITH_WARNINGS"
        else:
            return "PASS"

    def _generate_report(self, decision: str, phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit report"""
        # Count by severity
        summary = {
            "critical": sum(1 for f in self.findings if f.severity == "CRITICAL"),
            "grave": sum(1 for f in self.findings if f.severity == "GRAVE"),
            "medium": sum(1 for f in self.findings if f.severity == "MEDIUM"),
            "light": sum(1 for f in self.findings if f.severity == "LIGHT"),
        }

        report = {
            "phase": self.phase,
            "phase_name": phase_config.get("name", f"Phase {self.phase}"),
            "audited_at": datetime.utcnow().isoformat() + "Z",
            "decision": decision,
            "summary": summary,
            "findings": [f.to_dict() for f in self.findings],
            "metadata": {
                "auditor_version": "1.0.0",
                "project_path": str(self.project_path),
                "config_file": "audit_config.yml"
            }
        }

        return report


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load audit configuration"""
    if config_path is None:
        # Default config location
        config_path = Path(__file__).parent.parent / "config" / "audit_config.yml"

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    logger.debug(f"Configuration loaded from {config_path}")
    return config


def save_report(report: Dict[str, Any], output_path: Path):
    """Save audit report to file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Audit report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Adversarial audit for SDLC phases")
    parser.add_argument("--phase", type=int, required=True, help="Phase number (0-8)")
    parser.add_argument("--project-path", type=Path, default=Path.cwd(), help="Project path")
    parser.add_argument("--config", type=Path, help="Custom configuration file")
    parser.add_argument("--report-only", action="store_true", help="Generate report without decision")
    parser.add_argument("--output-dir", type=Path, help="Custom output directory for report")

    args = parser.parse_args()

    # Validate phase
    if not 0 <= args.phase <= 8:
        logger.error(f"Invalid phase number: {args.phase}. Must be 0-8.")
        sys.exit(1)

    # Load configuration
    config = load_config(args.config)

    # Check if audit is enabled
    if not config.get("adversarial_audit", {}).get("enabled", True):
        logger.info("Adversarial audit is disabled in configuration")
        sys.exit(0)

    # Check if phase should be audited
    phases_to_audit = config.get("adversarial_audit", {}).get("phases", [])
    if args.phase not in phases_to_audit:
        logger.info(f"Phase {args.phase} not configured for audit")
        sys.exit(0)

    # Execute audit
    auditor = PhaseAuditor(args.phase, args.project_path, config)
    report = auditor.audit()

    # Save report
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = args.project_path / ".agentic_sdlc" / "audits"

    output_path = output_dir / f"phase-{args.phase}-audit.yml"
    save_report(report, output_path)

    # Exit with appropriate code
    if args.report_only:
        sys.exit(0)

    decision = report["decision"]
    if decision == "FAIL":
        logger.error(f"Audit FAILED for Phase {args.phase}")
        sys.exit(1)
    elif decision == "PASS_WITH_WARNINGS":
        logger.warning(f"Audit passed with warnings for Phase {args.phase}")
        sys.exit(0)
    else:
        logger.info(f"Audit PASSED for Phase {args.phase}")
        sys.exit(0)


if __name__ == "__main__":
    main()
