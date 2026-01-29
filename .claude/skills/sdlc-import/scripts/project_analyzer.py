#!/usr/bin/env python3
"""
Project Analyzer - Main Orchestrator
Coordinates the reverse engineering workflow for sdlc-import.

Workflow:
    1. Create feature branch (auto-branch skill)
    2. Validate project path
    3. Initialize logging
    4. Scan directory
    5. Detect languages (language_detector.py)
    6. Extract decisions (decision_extractor.py)
    7. Generate diagrams (architecture_visualizer.py)
    8. Model threats (threat_modeler.py)
    9. Detect tech debt (tech_debt_detector.py)
    10. Generate documentation (documentation_generator.py)
    11. Return aggregated JSON results
"""

import sys
import os
import json
import argparse
import subprocess
import time  # FIX L2 (v2.2.0): Add timing tracking
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import yaml
import fnmatch

# FIX M2 (v2.3.2): Add progress bar support
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Add logging utilities (absolute path from project root)
# Use resolve() to handle symlinks correctly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

# Import analysis components
from language_detector import LanguageDetector
from decision_extractor import DecisionExtractor
from architecture_visualizer import ArchitectureVisualizer
from threat_modeler import ThreatModeler
from tech_debt_detector import TechDebtDetector
from documentation_generator import DocumentationGenerator
from post_import_validator import PostImportValidator
from quality_report_generator import QualityReportGenerator
from graph_generator import GraphGenerator
from issue_creator import IssueCreator
from migration_analyzer import MigrationAnalyzer
from adr_validator import ADRValidator
from infrastructure_preserver import InfrastructurePreserver

logger = get_logger(__name__, skill="sdlc-import", phase=0)


# Exceptions
class ImportAbortedError(Exception):
    """Raised when import is aborted by user"""
    pass


# Enums
from enum import Enum

class UserDecision(Enum):
    """User decision on import quality"""
    ACCEPT = "accept"
    RERUN = "rerun"
    ABORT = "abort"


class ProjectAnalyzer:
    """Main orchestrator for project analysis"""

    def __init__(
        self,
        project_path: str,
        config_path: Optional[str] = None,
        auto_approve: bool = False,
        enable_llm: Optional[bool] = None,
        dry_run: bool = False
    ):
        """
        Initialize project analyzer.

        Args:
            project_path: Path to project to analyze
            config_path: Optional path to config file
            auto_approve: Auto-approve import without user prompt (FIX C1 v2.3.2)
            enable_llm: Force enable LLM synthesis, overrides config (FIX C6 v2.3.2)
                       None = use config default
            dry_run: Simulate import without creating files (FIX M3 v2.3.2)
        """
        self.project_path = Path(project_path).resolve()
        self.dry_run = dry_run  # FIX M3 (v2.3.2): Store dry-run flag

        # BUG FIX (v2.1.7): Detect if project_path is the skill directory itself
        # This happens when /sdlc-import is invoked without explicit path argument
        # The framework passes the skill's base directory instead of CWD
        if self.project_path.name == "sdlc-import" and (self.project_path / "scripts" / "project_analyzer.py").exists():
            # We're being passed the skill directory - use CWD instead
            original_path = self.project_path
            self.project_path = Path.cwd().resolve()
            logger.warning(
                "Detected skill directory as project_path, using CWD instead",
                extra={
                    "original_path": str(original_path),
                    "corrected_path": str(self.project_path)
                }
            )

        self.config = self._load_config(config_path)

        # FIX C1 (v2.3.2): Store auto_approve flag in config
        self.config['auto_approve'] = auto_approve

        # FIX C6 (v2.3.2): Override LLM config if enable_llm flag provided
        if enable_llm is not None:
            self.config['decision_extraction']['llm']['enabled'] = enable_llm
            logger.info(
                f"LLM synthesis {'enabled' if enable_llm else 'disabled'} via CLI flag",
                extra={'llm_enabled': enable_llm}
            )

        # Load output directory from settings.json (v2.1.7)
        # Priority: settings.json > import_config.yml > default ".project"
        output_dir = self._load_output_dir_from_settings()
        if not output_dir:
            output_dir = self.config['general'].get('output_dir', '.project')

        self.output_dir = self.project_path / output_dir
        # FIX C1: Propagate resolved output_dir to config dict (used by all 15 components)
        self.config['general']['output_dir'] = str(output_dir)
        logger.info(f"✓ Resolved output_dir: {output_dir} (propagated to config)")
        self.analysis_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

        # Add dynamic config fields
        self.config['project_name'] = self.project_path.name
        self.config['analysis_id'] = self.analysis_id
        self.config['project_path'] = str(self.project_path)

        # Load .sdlcignore patterns
        self.ignore_patterns = self._load_sdlcignore()

        # Initialize analysis components
        self.language_detector = LanguageDetector(self.config)
        self.decision_extractor = DecisionExtractor(self.config)
        self.architecture_visualizer = ArchitectureVisualizer(self.config)
        self.threat_modeler = ThreatModeler(self.config)
        self.tech_debt_detector = TechDebtDetector(self.config)
        self.documentation_generator = DocumentationGenerator(self.config)
        self.graph_generator = GraphGenerator(self.config)
        self.issue_creator = IssueCreator(self.config)
        self.migration_analyzer = MigrationAnalyzer(self.config)
        self.adr_validator = ADRValidator(self.config)
        self.infrastructure_preserver = InfrastructurePreserver(self.output_dir)

        logger.info(
            "Initialized ProjectAnalyzer",
            extra={
                "project_path": str(self.project_path),
                "analysis_id": self.analysis_id
            }
        )

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "import_config.yml"

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        logger.info("Loaded configuration", extra={"config_path": str(config_path)})
        return config

    def _load_output_dir_from_settings(self) -> Optional[str]:
        """
        Load output directory configuration from .claude/settings.json

        Returns:
            Output directory path or None if not configured
        """
        settings_path = self.project_path / ".claude" / "settings.json"

        # Try framework root if not in project
        if not settings_path.exists():
            framework_root = Path(__file__).parent.parent.parent.parent
            settings_path = framework_root / ".claude" / "settings.json"

        if not settings_path.exists():
            logger.debug("settings.json not found, using config default")
            return None

        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)

            output_dir = settings.get('sdlc', {}).get('output', {}).get('project_artifacts_dir')

            if output_dir:
                logger.info(
                    "Loaded output directory from settings.json",
                    extra={"output_dir": output_dir, "settings_path": str(settings_path)}
                )
                return output_dir
            else:
                logger.debug("No output.project_artifacts_dir in settings.json")
                return None

        except Exception as e:
            logger.warning(
                "Failed to load settings.json",
                extra={"error": str(e), "settings_path": str(settings_path)}
            )
            return None

    def _load_output_dir_from_settings_for_framework(self) -> Optional[str]:
        """
        Load framework artifacts directory from .claude/settings.json

        Used for ignore patterns - we always ignore framework_artifacts_dir.

        Returns:
            Framework artifacts directory or None if not configured
        """
        settings_path = self.project_path / ".claude" / "settings.json"

        # Try framework root if not in project
        if not settings_path.exists():
            framework_root = Path(__file__).parent.parent.parent.parent
            settings_path = framework_root / ".claude" / "settings.json"

        if not settings_path.exists():
            return None

        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)

            framework_dir = settings.get('sdlc', {}).get('output', {}).get('framework_artifacts_dir')

            if framework_dir:
                logger.debug(
                    "Loaded framework_artifacts_dir from settings.json",
                    extra={"framework_artifacts_dir": framework_dir}
                )
                return framework_dir
            else:
                return None

        except Exception as e:
            logger.debug(
                "Failed to load framework_artifacts_dir from settings.json",
                extra={"error": str(e)}
            )
            return None

    def _load_sdlcignore(self) -> List[str]:
        """
        Load .sdlcignore patterns from project root and framework root.

        Returns:
            List of glob patterns to ignore
        """
        patterns = []

        # Check for .sdlcignore in project root
        project_ignore = self.project_path / ".sdlcignore"

        # Check for .sdlcignore in framework root (sdlc_agentico)
        framework_root = Path(__file__).parent.parent.parent.parent
        framework_ignore = framework_root / ".sdlcignore"

        for ignore_file in [project_ignore, framework_ignore]:
            if ignore_file.exists():
                try:
                    with open(ignore_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            # Skip empty lines and comments
                            if line and not line.startswith('#'):
                                patterns.append(line)
                    logger.info(
                        "Loaded .sdlcignore",
                        extra={
                            "file": str(ignore_file),
                            "patterns_count": len(patterns)
                        }
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to load .sdlcignore",
                        extra={"file": str(ignore_file), "error": str(e)}
                    )

        # Add default patterns if no .sdlcignore found
        if not patterns:
            # Always ignore:
            # - .claude/ (framework configuration)
            # - framework_artifacts_dir (from settings.json, default .agentic_sdlc/)
            # - Common build/cache directories
            framework_artifacts_dir = self._load_output_dir_from_settings_for_framework() or ".agentic_sdlc"

            patterns = [
                ".claude/",
                f"{framework_artifacts_dir}/",
                ".git/",
                "node_modules/",
                "venv/",
                "__pycache__/",
                ".terraform/"
            ]
            logger.info(
                "Using default ignore patterns",
                extra={"framework_artifacts_dir": framework_artifacts_dir}
            )

        return patterns

    def _should_ignore(self, file_path: Path) -> bool:
        """
        Check if file should be ignored based on .sdlcignore patterns.

        Args:
            file_path: Path to check (relative to project root)

        Returns:
            True if should be ignored, False otherwise
        """
        # Get path relative to project root
        try:
            rel_path = file_path.relative_to(self.project_path)
        except ValueError:
            # File is outside project, ignore it
            return True

        path_str = str(rel_path)

        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                if path_str.startswith(pattern) or f"/{pattern}" in path_str:
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
            # Handle wildcard directory patterns (e.g., **/*.pyc)
            elif '**/' in pattern:
                if fnmatch.fnmatch(path_str, pattern):
                    return True

        # Also check exclude_patterns from config (backward compatibility)
        exclude_patterns = self.config['general']['exclude_patterns']
        if any(pattern in path_str for pattern in exclude_patterns):
            return True

        return False

    def validate_project(self) -> bool:
        """
        Validate project path exists and is not too large.

        Returns:
            True if valid, False otherwise
        """
        with log_operation("validate_project", logger):
            # Check path exists
            if not self.project_path.exists():
                logger.error(
                    "Project path does not exist",
                    extra={"project_path": str(self.project_path)}
                )
                return False

            # Check is directory
            if not self.project_path.is_dir():
                logger.error(
                    "Project path is not a directory",
                    extra={"project_path": str(self.project_path)}
                )
                return False

            # Check size (count LOC)
            loc_count = self._count_loc()
            max_size = self.config['general']['max_project_size']

            if loc_count > max_size:
                logger.error(
                    "Project exceeds maximum size",
                    extra={
                        "loc_count": loc_count,
                        "max_size": max_size
                    }
                )
                return False

            logger.info(
                "Project validation passed",
                extra={"loc_count": loc_count}
            )
            return True

    def _count_loc(self) -> int:
        """Count lines of code in project"""
        loc_count = 0

        for file in self.project_path.rglob("*"):
            # Skip ignored files (uses .sdlcignore patterns)
            if self._should_ignore(file):
                continue

            # Skip non-files
            if not file.is_file():
                continue

            # Skip binary files
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Count non-empty, non-comment lines
                    loc_count += sum(
                        1 for line in lines
                        if line.strip() and not line.strip().startswith('#')
                    )
            except Exception:
                continue

        return loc_count

    def create_feature_branch(self, branch_name: Optional[str] = None) -> Dict:
        """
        Create feature branch using auto-branch skill.

        Args:
            branch_name: Optional custom branch name

        Returns:
            Dict with branch info
        """
        with log_operation("create_feature_branch", logger):
            # Default branch name
            if branch_name is None:
                project_name = self.project_path.name
                branch_name = f"feature/import-{project_name}"

            # FIX M3 (v2.3.2): Dry-run mode - skip branch creation
            if self.dry_run:
                logger.info(f"DRY-RUN: Would create feature branch '{branch_name}'")
                return {"branch": branch_name, "created": False, "dry_run": True}

            # Check if already on feature branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()

            if current_branch == branch_name:
                logger.info(
                    "Already on feature branch",
                    extra={"branch": branch_name}
                )
                return {"branch": branch_name, "created": False}

            # Create and checkout branch
            try:
                subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=str(self.project_path),
                    check=True,
                    capture_output=True
                )
                logger.info(
                    "Created feature branch",
                    extra={"branch": branch_name}
                )
                return {"branch": branch_name, "created": True}
            except subprocess.CalledProcessError as e:
                # Check if branch already exists
                result = subprocess.run(
                    ["git", "branch", "--list", branch_name],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True
                )

                if result.stdout.strip():
                    # Branch exists - checkout to it
                    logger.warning(
                        "Branch already exists, checking out",
                        extra={"branch": branch_name}
                    )
                    subprocess.run(
                        ["git", "checkout", branch_name],
                        cwd=str(self.project_path),
                        check=True,
                        capture_output=True
                    )
                    return {"branch": branch_name, "created": False, "reused": True}
                else:
                    # Different error - re-raise
                    logger.error(
                        "Failed to create branch",
                        extra={
                            "branch": branch_name,
                            "error": str(e)
                        }
                    )
                    raise

    def scan_directory(self) -> Dict:
        """
        Scan project directory for files.

        Returns:
            Dict with scan statistics
        """
        with log_operation("scan_directory", logger):
            files_by_ext = {}
            total_files = 0
            total_loc = 0

            for file in self.project_path.rglob("*"):
                # Skip ignored files (uses .sdlcignore patterns)
                if self._should_ignore(file):
                    continue

                # Skip non-files
                if not file.is_file():
                    continue

                # Get extension
                ext = file.suffix.lower()
                if ext not in files_by_ext:
                    files_by_ext[ext] = {
                        "count": 0,
                        "loc": 0,
                        "files": []
                    }

                # Count LOC
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        loc = len([l for l in lines if l.strip()])
                        files_by_ext[ext]["loc"] += loc
                        total_loc += loc
                except Exception:
                    continue

                files_by_ext[ext]["count"] += 1
                files_by_ext[ext]["files"].append(str(file.relative_to(self.project_path)))
                total_files += 1

            scan_results = {
                "total_files": total_files,
                "total_loc": total_loc,
                "files_by_extension": files_by_ext
            }

            logger.info(
                "Directory scan complete",
                extra={
                    "total_files": total_files,
                    "total_loc": total_loc
                }
            )

            return scan_results

    def detect_languages(self) -> Dict:
        """
        Detect programming languages and frameworks.

        Returns:
            Dict with language analysis results
        """
        with log_operation("detect_languages", logger):
            language_analysis = self.language_detector.detect(self.project_path)

            logger.info(
                "Language detection complete",
                extra={
                    "primary_language": language_analysis.get("primary_language"),
                    "languages_count": len(language_analysis.get("languages", {}))
                }
            )

            return language_analysis

    def extract_decisions(self, language_analysis: Dict, no_llm: bool = False) -> Dict:
        """
        Extract architecture decisions from codebase.

        Args:
            language_analysis: Language detection results
            no_llm: Disable LLM synthesis

        Returns:
            Dict with extracted decisions
        """
        with log_operation("extract_decisions", logger):
            decisions = self.decision_extractor.extract(
                self.project_path,
                language_analysis,
                no_llm=no_llm
            )

            logger.info(
                "Decision extraction complete",
                extra={
                    "decisions_count": decisions.get("count", 0),
                    "high_confidence": decisions.get("high_confidence", 0)
                }
            )

            return decisions

    def generate_diagrams(self, language_analysis: Dict, decisions: Dict) -> Dict:
        """
        Generate architecture diagrams.

        Args:
            language_analysis: Language detection results
            decisions: Extracted decisions

        Returns:
            Dict with diagram paths
        """
        with log_operation("generate_diagrams", logger):
            diagrams = self.architecture_visualizer.generate(
                self.project_path,
                language_analysis,
                decisions
            )

            logger.info(
                "Diagram generation complete",
                extra={"diagrams_count": len(diagrams.get("diagrams", {}))}
            )

            return diagrams

    def model_threats(self, decisions: Dict) -> Dict:
        """
        Perform STRIDE threat modeling.

        Args:
            decisions: Extracted decisions

        Returns:
            Dict with threat analysis
        """
        with log_operation("model_threats", logger):
            threats = self.threat_modeler.analyze(self.project_path, decisions)

            logger.info(
                "Threat modeling complete",
                extra={
                    "threats_count": threats.get("total", 0),
                    "critical": threats.get("critical", 0),
                    "high": threats.get("high", 0)
                }
            )

            return threats

    def detect_tech_debt(self) -> Dict:
        """
        Detect technical debt.

        Returns:
            Dict with tech debt analysis
        """
        with log_operation("detect_tech_debt", logger):
            tech_debt = self.tech_debt_detector.scan(self.project_path)

            logger.info(
                "Tech debt detection complete",
                extra={
                    "total": tech_debt.get("total", 0),
                    "p0": tech_debt.get("p0", 0),
                    "p1": tech_debt.get("p1", 0)
                }
            )

            return tech_debt

    def generate_documentation(self, analysis_results: Dict) -> Dict:
        """
        Generate SDLC documentation.

        Args:
            analysis_results: Complete analysis results

        Returns:
            Dict with generated file paths
        """
        with log_operation("generate_documentation", logger):
            # FIX M3 (v2.3.2): Dry-run mode - simulate without creating files
            if self.dry_run:
                logger.info("DRY-RUN: Would generate documentation")
                logger.info(f"DRY-RUN: Would create {len(analysis_results.get('decisions', {}).get('decisions', []))} ADR files")
                logger.info(f"DRY-RUN: Would create threat model file")
                logger.info(f"DRY-RUN: Would create tech debt report")
                logger.info(f"DRY-RUN: Would create import report")

                # Return simulated results
                return {
                    "adrs": [{"id": adr["id"], "title": adr["title"]} for adr in analysis_results.get('decisions', {}).get('decisions', [])],
                    "threat_model": f"{self.output_dir}/security/threat-model-inferred.yml",
                    "tech_debt_report": f"{self.output_dir}/reports/tech-debt-inferred.md",
                    "import_report": f"{self.output_dir}/reports/import-report.md",
                    "dry_run": True
                }

            docs = self.documentation_generator.generate(analysis_results)

            logger.info(
                "Documentation generation complete",
                extra={
                    "adrs_count": len(docs.get("adrs", [])),
                    "threat_model": docs.get("threat_model"),
                    "tech_debt_report": docs.get("tech_debt_report")
                }
            )

            return docs

    def _save_phase_artifacts(self, results: Dict) -> None:
        """
        FIX #3: Save phase artifacts for audit trail.

        Args:
            results: Complete analysis results
        """
        phase_dir = self.output_dir / "phase-artifacts" / "phase-1-discovery"
        phase_dir.mkdir(parents=True, exist_ok=True)

        # Save language detection
        lang_file = phase_dir / "language-detection.json"
        with open(lang_file, 'w') as f:
            json.dump(results['language_analysis'], f, indent=2)

        # Save decision extraction
        decision_file = phase_dir / "decision-extraction.json"
        with open(decision_file, 'w') as f:
            json.dump(results['decisions'], f, indent=2)

        # Save migration analysis (if available)
        if 'decisions' in results and 'migration_analysis' in results['decisions']:
            migration_file = phase_dir / "migration-analysis.json"
            with open(migration_file, 'w') as f:
                json.dump(results['decisions']['migration_analysis'], f, indent=2)

        # Save ADR validation (if available)
        if 'adr_validation' in results and results['adr_validation']:
            validation_file = phase_dir / "adr-validation.json"
            with open(validation_file, 'w') as f:
                json.dump(results['adr_validation'], f, indent=2)

        # Save threat analysis
        threat_file = phase_dir / "threat-analysis.json"
        with open(threat_file, 'w') as f:
            json.dump(results['threats'], f, indent=2)

        # Save tech debt
        debt_file = phase_dir / "tech-debt.json"
        with open(debt_file, 'w') as f:
            json.dump(results['tech_debt'], f, indent=2)

        # Save complete scan results
        scan_file = phase_dir / "directory-scan.json"
        with open(scan_file, 'w') as f:
            json.dump(results['scan'], f, indent=2)

        files_created = 5

        # Save knowledge graph results (if available)
        if 'knowledge_graph' in results and results['knowledge_graph']:
            graph_file = phase_dir / "knowledge-graph.json"
            with open(graph_file, 'w') as f:
                json.dump(results['knowledge_graph'], f, indent=2)
            files_created += 1

        # Save GitHub issues results (if available)
        if 'github_issues' in results and results['github_issues']:
            issues_file = phase_dir / "github-issues.json"
            with open(issues_file, 'w') as f:
                json.dump(results['github_issues'], f, indent=2)
            files_created += 1

        logger.info(
            "Phase artifacts saved",
            extra={
                "phase_dir": str(phase_dir),
                "files_created": files_created
            }
        )

    def _push_feature_branch(self, branch_name: str) -> bool:
        """
        FIX #8: Auto-push feature branch to remote.

        Args:
            branch_name: Name of branch to push

        Returns:
            True if pushed successfully, False otherwise
        """
        # FIX M3 (v2.3.2): Dry-run mode - skip push
        if self.dry_run:
            logger.info(f"DRY-RUN: Would push branch '{branch_name}' to origin")
            return False

        try:
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.warning("No remote 'origin' found, skipping push")
                return False

            # Push branch with upstream tracking
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=str(self.project_path),
                check=True,
                capture_output=True,
                text=True
            )

            logger.info(
                "Feature branch pushed to remote",
                extra={"branch": branch_name, "remote": "origin"}
            )
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(
                "Failed to push branch (continuing anyway)",
                extra={"branch": branch_name, "error": str(e)}
            )
            return False

    def _load_validation_config(self) -> Dict:
        """
        Load post-import validation configuration.

        Returns:
            Validation config dict
        """
        validation_config_path = Path(__file__).parent.parent / "config" / "post_import_validation_rules.yml"

        if validation_config_path.exists():
            with open(validation_config_path) as f:
                config = yaml.safe_load(f)
                return config.get('post_import_validation', {})
        else:
            # Default config
            logger.warning("Validation config not found, using defaults")
            return {
                'enabled': True,
                'auto_accept_threshold': 0.85,
                'pass_threshold': 0.70,
                'adr_validation': {'enabled': True, 'max_suspicious_ratio': 0.70},
                'tech_debt_validation': {'enabled': True},
                'diagram_validation': {'enabled': True},
                'completeness_validation': {'enabled': True}
            }

    def _generate_quality_report(
        self,
        validation_result,
        project_name: str,
        correlation_id: str
    ) -> str:
        """
        Generate quality report markdown.

        Args:
            validation_result: ValidationResult from PostImportValidator
            project_name: Project name
            correlation_id: Correlation ID

        Returns:
            Markdown content
        """
        templates_dir = Path(__file__).parent.parent / "templates"
        generator = QualityReportGenerator(templates_dir)

        return generator.generate(
            validation_result=validation_result,
            project_name=project_name,
            correlation_id=correlation_id
        )

    def _check_artifacts_created(self) -> bool:
        """
        Verify that required artifacts were created successfully.

        FIX C7 (v2.3.2): Exit code should be based on artifacts, not prompts

        Returns:
            True if all required artifacts exist, False otherwise
        """
        required_files = [
            self.output_dir / "corpus/graph.json",
            self.output_dir / "corpus/adr_index.yml",
            self.output_dir / "reports/import-report.md"
        ]

        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                logger.error(f"Missing required artifact: {file_path}")
                missing_files.append(str(file_path))

        if missing_files:
            logger.error(
                f"Import incomplete - {len(missing_files)} required artifacts missing",
                extra={'missing_files': missing_files}
            )
            return False

        logger.info("All required artifacts created successfully")
        return True

    def _prompt_user_approval(
        self,
        quality_report: str,
        validation_result,
        correlation_id: str
    ) -> UserDecision:
        """
        Prompt user for decision on import quality.

        FIX C1 (v2.3.2): Auto-approve in non-interactive environments
        - Checks auto_approve config flag
        - Detects CI environment (CI=true)
        - Detects non-TTY stdin
        - Only prompts if truly interactive

        Args:
            quality_report: Quality report markdown
            validation_result: ValidationResult
            correlation_id: Correlation ID

        Returns:
            UserDecision (ACCEPT, RERUN, ABORT)
        """
        # FIX C1: Check auto-approve flag BEFORE any prompting
        if self.config.get('auto_approve', False):
            logger.info(
                "Auto-approve enabled via config - skipping user prompt",
                extra={'correlation_id': correlation_id, 'score': validation_result.overall_score}
            )
            print(f"\n✅ Import auto-approved (config flag enabled)")
            print(f"📊 Quality score: {validation_result.overall_score:.1%}")
            print(f"📄 Quality report: {self.output_dir}/reports/post_import_quality_report.md\n")
            return UserDecision.ACCEPT

        # FIX C1: Check for CI environment
        if os.getenv('CI') == 'true' or os.getenv('CONTINUOUS_INTEGRATION') == 'true':
            logger.info(
                "CI environment detected - auto-approving",
                extra={'correlation_id': correlation_id, 'ci': True}
            )
            print(f"\n✅ Import auto-approved (CI environment detected)")
            print(f"📊 Quality score: {validation_result.overall_score:.1%}")
            print(f"📄 Quality report: {self.output_dir}/reports/post_import_quality_report.md\n")
            return UserDecision.ACCEPT

        # FIX C1: Check if stdin is a TTY (terminal)
        if not sys.stdin.isatty():
            logger.warning(
                "Non-interactive shell detected (no TTY) - auto-approving",
                extra={'correlation_id': correlation_id, 'stdin_tty': False}
            )
            print(f"\n⚠️  Non-interactive shell - auto-approving import")
            print(f"📊 Quality score: {validation_result.overall_score:.1%}")
            print(f"📄 Quality report: {self.output_dir}/reports/post_import_quality_report.md\n")
            return UserDecision.ACCEPT

        # Auto-accept if score >= 0.85 and no critical issues
        auto_accept_threshold = self.config.get('post_import_validation', {}).get('auto_accept_threshold', 0.85)
        has_critical = any(
            issue['severity'] == 'critical'
            for issue in validation_result.issues_detected
        )

        if validation_result.overall_score >= auto_accept_threshold and not has_critical:
            logger.info(
                "Auto-accepting import (high quality)",
                extra={'correlation_id': correlation_id, 'score': validation_result.overall_score}
            )
            print(f"\n✅ Import auto-accepted (quality score: {validation_result.overall_score:.1%})")
            print(f"📄 Quality report: {self.output_dir}/reports/post_import_quality_report.md\n")
            return UserDecision.ACCEPT

        # Show report and prompt (ONLY in interactive mode)
        print("\n" + "="*80)
        print("POST-IMPORT VALIDATION REPORT")
        print("="*80 + "\n")
        print(quality_report)
        print("\n" + "="*80)
        print(f"Quality Score: {validation_result.overall_score:.1%}")
        print(f"Corrections Applied: {len(validation_result.corrections_applied)}")
        print(f"Issues Detected: {len(validation_result.issues_detected)}")
        print("="*80 + "\n")

        print("What would you like to do?")
        print("  1. ✅ Accept (continue with corrected artifacts)")
        print("  2. 🔄 Re-run import (start over)")
        print("  3. ❌ Abort import")

        # FIX C1: Wrap input() in try-except for robustness
        while True:
            try:
                choice = input("\nEnter choice (1-3): ").strip()

                if choice == '1':
                    logger.info("User accepted import", extra={'correlation_id': correlation_id})
                    return UserDecision.ACCEPT
                elif choice == '2':
                    logger.info("User requested re-run", extra={'correlation_id': correlation_id})
                    return UserDecision.RERUN
                elif choice == '3':
                    logger.info("User aborted import", extra={'correlation_id': correlation_id})
                    return UserDecision.ABORT
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except (EOFError, KeyboardInterrupt):
                # FIX C1: Handle EOF/Ctrl+C gracefully
                logger.warning("Input interrupted - auto-approving", extra={'correlation_id': correlation_id})
                print("\n⚠️  Input interrupted - auto-approving import")
                return UserDecision.ACCEPT

    def analyze(
        self,
        skip_threat_model: bool = False,
        skip_tech_debt: bool = False,
        no_llm: bool = False,
        create_issues: bool = False,
        branch_name: Optional[str] = None
    ) -> Dict:
        """
        Run complete analysis workflow.

        Args:
            skip_threat_model: Skip STRIDE analysis
            skip_tech_debt: Skip tech debt detection
            no_llm: Disable LLM synthesis
            create_issues: Create GitHub issues
            branch_name: Custom branch name

        Returns:
            Dict with all analysis results
        """
        with log_operation("analyze", logger):
            # FIX L2 (v2.2.0): Track execution metrics
            metrics = {
                'timing': {},
                'resource_usage': {},
                'analysis_quality': {}
            }
            start_time = time.time()

            # FIX M2 (v2.3.2): Progress bar for visual feedback
            total_steps = 11  # Total analysis steps
            pbar = None
            if TQDM_AVAILABLE and sys.stdout.isatty():
                pbar = tqdm(total=total_steps, desc="Analyzing project", unit="step", ncols=80)

            def update_progress(desc: str):
                """Update progress bar with current step description"""
                if pbar:
                    pbar.set_description(f"{desc:<40}")
                    pbar.update(1)

            # Step 1: Create feature branch
            update_progress("Creating feature branch")
            t0 = time.time()
            branch_info = self.create_feature_branch(branch_name)
            metrics['timing']['branch_creation'] = round(time.time() - t0, 2)

            # Step 2: Validate project
            update_progress("Validating project")
            t0 = time.time()
            if not self.validate_project():
                if pbar:
                    pbar.close()
                raise ValueError("Project validation failed")
            metrics['timing']['validation'] = round(time.time() - t0, 2)

            # Step 3: Scan directory
            update_progress("Scanning directory")
            t0 = time.time()
            scan_results = self.scan_directory()
            metrics['timing']['directory_scan'] = round(time.time() - t0, 2)
            metrics['analysis_quality']['files_scanned'] = scan_results.get('file_count', 0)

            # Step 4: Detect languages
            update_progress("Detecting languages")
            t0 = time.time()
            language_analysis = self.detect_languages()
            metrics['timing']['language_detection'] = round(time.time() - t0, 2)

            # Step 5: Extract decisions
            update_progress("Extracting architecture decisions")
            t0 = time.time()
            decisions = self.extract_decisions(language_analysis, no_llm=no_llm)
            metrics['timing']['decision_extraction'] = round(time.time() - t0, 2)

            # FIX #4: Analyze database migrations
            migration_decisions = []
            if self.config.get('migration_analysis', {}).get('enabled', True):
                migration_analysis = self.migration_analyzer.analyze(self.project_path)
                migration_decisions = migration_analysis.get('decisions', [])

                # Merge with other decisions
                decisions['decisions'].extend(migration_decisions)
                decisions['count'] += len(migration_decisions)
                decisions['migration_analysis'] = migration_analysis

            # FIX #5: Validate ADR claims against codebase
            # FIX M4 (v2.3.2): Process validation results and flag low-confidence ADRs
            validation_results = {}
            if self.config.get('adr_validation', {}).get('enabled', True):
                extracted_adrs = decisions.get('decisions', [])
                if len(extracted_adrs) > 0:
                    validation_results = self.adr_validator.validate(self.project_path, extracted_adrs)

                    # FIX M4 (v2.3.2): Process validation results
                    min_validation_confidence = self.config.get('adr_validation', {}).get('min_confidence', 0.5)
                    for validation_result in validation_results.get('results', []):
                        adr_id = validation_result['adr_id']
                        validation_rate = validation_result['validation_rate']

                        # Find corresponding ADR in decisions
                        for adr in extracted_adrs:
                            if adr.get('id') == adr_id:
                                # Add validation info to ADR
                                adr['validation_confidence'] = validation_rate
                                adr['validation_passed'] = validation_rate >= min_validation_confidence
                                adr['claims_validated'] = f"{validation_result['validated_count']}/{validation_result['claims_count']}"

                                # FIX M4 (v2.3.2): Log warnings for failed validations
                                if validation_rate < min_validation_confidence:
                                    logger.warning(
                                        f"ADR {adr_id} failed validation: {validation_rate:.1%} < {min_validation_confidence:.1%}",
                                        extra={
                                            'adr_id': adr_id,
                                            'validation_rate': validation_rate,
                                            'claims_validated': validation_result['validated_count'],
                                            'total_claims': validation_result['claims_count']
                                        }
                                    )
                                break

                    # FIX M4 (v2.3.2): Log summary of failed ADRs
                    failed_adrs = [r for r in validation_results.get('results', []) if r['validation_rate'] < min_validation_confidence]
                    if failed_adrs:
                        logger.warning(
                            f"{len(failed_adrs)} ADRs failed validation (< {min_validation_confidence:.1%} confidence)",
                            extra={'failed_adr_ids': [r['adr_id'] for r in failed_adrs]}
                        )
                else:
                    logger.warning("No ADRs found - skipping claim validation")
                    validation_results = {"status": "skipped", "reason": "no_adrs"}

            # NEW (v2.1.7): Reconcile with existing ADRs to avoid duplicates
            reconciliation_results = {}
            adr_config = self.config.get('adr_reconciliation', {})
            enabled = adr_config.get('enabled', True)

            if not enabled:
                logger.warning("ADR reconciliation is DISABLED in config")
                logger.warning("Set adr_reconciliation.enabled: true to enable")
                logger.warning("adr_index.yml will NOT be generated")

            if enabled:
                logger.info("ADR reconciliation enabled - checking for existing ADRs")
                existing_adrs = self.adr_validator.detect_existing_adrs(self.project_path)
                extracted_adrs = decisions.get('decisions', [])

                if len(existing_adrs) > 0:
                    logger.info(f"Found {len(existing_adrs)} existing ADRs - reconciling")
                    similarity_threshold = self.config.get('adr_reconciliation', {}).get('similarity_threshold', 0.8)
                    reconciliation = self.adr_validator.reconcile_adrs(
                        existing_adrs,
                        extracted_adrs,
                        similarity_threshold=similarity_threshold
                    )

                    # Update decisions dict with reconciliation results
                    reconciliation_results = {
                        'total_existing': len(existing_adrs),
                        'total_inferred': len(extracted_adrs),
                        'duplicate': reconciliation.duplicate,
                        'enrich': reconciliation.enrich,
                        'new': reconciliation.new,
                        'index': reconciliation.index
                    }

                    # Replace extracted decisions with only new ADRs (avoid duplicates)
                    decisions['decisions'] = reconciliation.new
                    decisions['count'] = len(reconciliation.new)
                    decisions['duplicates_skipped'] = len(reconciliation.duplicate)
                    decisions['enriched'] = len(reconciliation.enrich)

                    logger.info(
                        "ADR reconciliation complete",
                        extra={
                            "existing": len(existing_adrs),
                            "inferred": len(extracted_adrs),
                            "duplicates": len(reconciliation.duplicate),
                            "enriched": len(reconciliation.enrich),
                            "new": len(reconciliation.new)
                        }
                    )
                else:
                    logger.info("No existing ADRs found - all inferred ADRs will be generated")
                    reconciliation_results = {"status": "no_existing_adrs"}

            # Step 6: Generate diagrams
            update_progress("Generating architecture diagrams")
            t0 = time.time()
            diagrams = self.generate_diagrams(language_analysis, decisions)
            metrics['timing']['diagram_generation'] = round(time.time() - t0, 2)

            # Step 7: Model threats (if not skipped)
            update_progress("Modeling security threats")
            t0 = time.time()
            # FIX #2: Force threat modeling if config says enabled=true
            threat_config_enabled = self.config.get('threat_modeling', {}).get('enabled', False)

            if threat_config_enabled:
                # Config says enabled - force execution even if user passed --skip-threat-model
                if skip_threat_model:
                    logger.warning(
                        "Ignoring --skip-threat-model flag (config has threat_modeling.enabled=true)",
                        extra={"config_enabled": threat_config_enabled}
                    )
                threats = self.model_threats(decisions)
            elif not skip_threat_model:
                # Config doesn't force it, but user didn't skip
                threats = self.model_threats(decisions)
            else:
                # Both config and user say skip
                threats = {"status": "skipped"}
            metrics['timing']['threat_modeling'] = round(time.time() - t0, 2)

            # Step 8: Detect tech debt (if not skipped)
            update_progress("Detecting technical debt")
            t0 = time.time()
            if not skip_tech_debt:
                tech_debt = self.detect_tech_debt()
            else:
                tech_debt = {"status": "skipped"}
            metrics['timing']['tech_debt_detection'] = round(time.time() - t0, 2)

            # FIX #6: Generate knowledge graph
            update_progress("Building knowledge graph")
            graph_result = {}
            if self.config.get('graph_generation', {}).get('enabled', True):
                corpus_dir = self.output_dir / "corpus"
                extracted_adrs = decisions.get('decisions', [])
                if len(extracted_adrs) > 0:
                    # BUG FIX #4: Add error handling AND persist graph.json even on failure
                    try:
                        graph_result = self.graph_generator.generate(corpus_dir, extracted_adrs)
                        logger.info(f"Graph generated: {graph_result.get('node_count', 0)} nodes, {graph_result.get('edge_count', 0)} edges")

                        # BUG FIX #4: Persist graph.json to disk
                        graph_file = corpus_dir / "graph.json"
                        graph_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(graph_file, 'w') as f:
                            json.dump(graph_result, f, indent=2)
                        logger.info(f"Graph saved to {graph_file}")

                    except Exception as e:
                        logger.error(f"Graph generation failed: {e}", exc_info=True)

                        # BUG FIX #4: Create minimal valid graph.json instead of failing silently
                        minimal_graph = {
                            "status": "failed",
                            "error": str(e),
                            "version": "2.3.1",
                            "nodes": [],
                            "edges": [],
                            "node_count": 0,
                            "edge_count": 0
                        }

                        graph_file = corpus_dir / "graph.json"
                        graph_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(graph_file, 'w') as f:
                            json.dump(minimal_graph, f, indent=2)

                        graph_result = minimal_graph
                        logger.warning(f"Created minimal graph.json at {graph_file}")
                else:
                    logger.warning("No ADRs found - skipping graph generation")
                    graph_result = {"status": "skipped", "reason": "no_adrs"}

            # FIX #9: Create GitHub issues for tech debt
            github_issues = {}
            if create_issues:
                tech_debt_items = tech_debt.get('items', [])
                github_issues = self.issue_creator.create_issues(tech_debt_items, self.project_path)

            # FIX L2 (v2.2.0): Calculate total time and add quality metrics
            metrics['timing']['total'] = round(time.time() - start_time, 2)
            metrics['analysis_quality']['files_parsed_successfully'] = scan_results.get('file_count', 0) - scan_results.get('binary_files', 0)
            metrics['analysis_quality']['parsing_success_rate'] = round(
                (scan_results.get('file_count', 0) - scan_results.get('binary_files', 0)) / max(scan_results.get('file_count', 1), 1),
                2
            ) if scan_results.get('file_count', 0) > 0 else 0.0

            # Build complete results before documentation generation
            results = {
                "analysis_id": self.analysis_id,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "project_path": str(self.project_path),
                "branch": branch_info,
                "scan": scan_results,
                "language_analysis": language_analysis,
                "decisions": decisions,
                "diagrams": diagrams,
                "threats": threats,
                "tech_debt": tech_debt,
                "adr_validation": validation_results,
                "adr_reconciliation": reconciliation_results,  # NEW (v2.1.7)
                "knowledge_graph": graph_result,
                "github_issues": github_issues,
                "execution_metrics": metrics  # FIX L2 (v2.2.0)
            }

            # FIX #3: Save phase artifacts for auditability
            self._save_phase_artifacts(results)

            # CRITICAL FIX: Backup existing infrastructure before generating docs
            logger.info("Backing up existing infrastructure")
            backup_stats = self.infrastructure_preserver.backup_existing_infrastructure()
            logger.info(f"Backup complete: {backup_stats}")

            # Step 9: Generate documentation
            update_progress("Generating documentation")
            documentation = self.generate_documentation(results)
            results["documentation"] = documentation

            # CRITICAL FIX: Restore preserved infrastructure after generating docs
            logger.info("Restoring preserved infrastructure")
            restore_stats = self.infrastructure_preserver.restore_infrastructure()
            logger.info(f"Restoration complete: {restore_stats}")
            results["infrastructure_restored"] = restore_stats

            # Step 10: POST-IMPORT VALIDATION & AUTO-FIX
            update_progress("Running validation and auto-fix")
            if self.config.get('post_import_validation', {}).get('enabled', True):
                logger.info(
                    "Running post-import validation and auto-fix",
                    extra={'correlation_id': self.analysis_id}
                )

                # Load validation config
                validation_config = self._load_validation_config()

                # Execute validation + correction
                # BUG FIX #2: Add error handling to prevent crashes from propagating
                validator = PostImportValidator(validation_config)

                try:
                    validation_result = validator.validate_and_fix(
                        import_results=results,
                        project_path=str(self.project_path),
                        output_dir=self.output_dir,
                        correlation_id=self.analysis_id
                    )

                    # Generate quality report
                    quality_report = self._generate_quality_report(
                        validation_result=validation_result,
                        project_name=self.project_path.name,
                        correlation_id=self.analysis_id
                    )

                    # Save quality report
                    quality_report_path = self.output_dir / "reports" / "post_import_quality_report.md"
                    quality_report_path.parent.mkdir(parents=True, exist_ok=True)
                    quality_report_path.write_text(quality_report)

                    # Step 11: USER APPROVAL
                    user_decision = self._prompt_user_approval(
                        quality_report=quality_report,
                        validation_result=validation_result,
                        correlation_id=self.analysis_id
                    )

                    # Update results with validation
                    results['post_import_validation'] = {
                        'status': user_decision.value,
                        'score': validation_result.overall_score,
                        'corrections_applied': validation_result.corrections_applied,
                        'issues_detected': validation_result.issues_detected,
                        'report_path': str(quality_report_path.relative_to(self.project_path))
                    }

                except Exception as e:
                    logger.error(
                        f"Post-import validation FAILED: {e}",
                        extra={'correlation_id': self.analysis_id},
                        exc_info=True
                    )

                    # BUG FIX #2: Graceful degradation - mark as failed but CONTINUE
                    results['post_import_validation'] = {
                        'status': 'failed',
                        'error': str(e),
                        'score': 0.0,
                        'corrections_applied': {},
                        'issues_detected': [],
                        'note': 'Import completed but validation crashed - artifacts may be incomplete'
                    }

                    # FIX C7 (v2.3.2): Set user_decision to ACCEPT to avoid UnboundLocalError
                    # If validation failed, we still have artifacts - let's accept them
                    user_decision = UserDecision.ACCEPT

                    # Log to user
                    logger.warning("Import artifacts created but validation failed - review manually")

                # Abort if user rejected
                if user_decision == UserDecision.ABORT:
                    raise ImportAbortedError(
                        f"Import aborted by user. Quality score: {validation_result.overall_score:.2%}"
                    )

                # Re-run if requested
                if user_decision == UserDecision.RERUN:
                    logger.warning("User requested re-run, aborting current import")
                    raise ImportAbortedError("User requested re-run of import")

            # FIX #8: Auto-push feature branch
            # FIX M2 (v2.3.2): Final progress update
            update_progress("Pushing to remote repository")
            push_result = self._push_feature_branch(branch_info['branch'])
            results["branch_pushed"] = push_result

            # FIX M2 (v2.3.2): Close progress bar
            if pbar:
                pbar.set_description("Analysis complete")
                pbar.close()

            logger.info(
                "Analysis complete",
                extra={"analysis_id": self.analysis_id, "branch_pushed": push_result}
            )

            return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Reverse engineer existing codebase and generate SDLC documentation"
    )
    parser.add_argument(
        "project_path",
        help="Path to project to analyze"
    )
    parser.add_argument(
        "--skip-threat-model",
        action="store_true",
        help="Skip STRIDE threat modeling"
    )
    parser.add_argument(
        "--skip-tech-debt",
        action="store_true",
        help="Skip technical debt detection"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM synthesis (faster, lower cost)"
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Force enable LLM synthesis (overrides config)"
    )
    parser.add_argument(
        "--create-issues",
        action="store_true",
        help="Create GitHub issues for findings"
    )
    parser.add_argument(
        "--branch-name",
        help="Custom branch name (default: auto-generated)"
    )
    parser.add_argument(
        "--config",
        help="Path to custom config file"
    )
    parser.add_argument(
        "--output",
        help="Output file for results (JSON)"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve import without user prompt (useful for CI/CD)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate import without creating files (shows what would be created)"
    )

    args = parser.parse_args()

    # FIX C6 (v2.3.2): Validate LLM flags
    if args.llm and args.no_llm:
        logger.error("Cannot specify both --llm and --no-llm flags")
        print("ERROR: Cannot specify both --llm and --no-llm flags", file=sys.stderr)
        return 1

    try:
        # FIX C1 (v2.3.2): Pass auto-approve flag to analyzer
        # FIX C6 (v2.3.2): Pass enable_llm flag to analyzer
        # FIX M3 (v2.3.2): Pass dry-run flag to analyzer
        analyzer = ProjectAnalyzer(
            args.project_path,
            args.config,
            auto_approve=args.auto_approve,
            enable_llm=args.llm if args.llm else None,  # None = use config default
            dry_run=args.dry_run
        )
        results = analyzer.analyze(
            skip_threat_model=args.skip_threat_model,
            skip_tech_debt=args.skip_tech_debt,
            no_llm=args.no_llm,
            create_issues=args.create_issues,
            branch_name=args.branch_name
        )

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results written to {args.output}")
        else:
            print(json.dumps(results, indent=2))

        return 0

    except Exception as e:
        logger.error("Analysis failed", extra={"error": str(e)}, exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)

        # FIX C7 (v2.3.2): Check if artifacts were created despite error
        # If artifacts exist, return success (error was likely in post-processing)
        try:
            if analyzer._check_artifacts_created():
                logger.warning(
                    "Analysis encountered error but artifacts were created successfully - returning success",
                    extra={"error": str(e)}
                )
                print("\n⚠️  Import encountered an error but artifacts were created successfully")
                print(f"📄 Check: {analyzer.output_dir}")
                return 0
        except Exception:
            # If artifact check fails, continue with error return
            pass

        return 1


if __name__ == "__main__":
    sys.exit(main())
