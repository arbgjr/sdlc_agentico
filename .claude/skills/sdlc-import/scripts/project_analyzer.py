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
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

# Import analysis components
from language_detector import LanguageDetector
from decision_extractor import DecisionExtractor
from architecture_visualizer import ArchitectureVisualizer
from threat_modeler import ThreatModeler
from tech_debt_detector import TechDebtDetector
from documentation_generator import DocumentationGenerator

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class ProjectAnalyzer:
    """Main orchestrator for project analysis"""

    def __init__(self, project_path: str, config_path: Optional[str] = None):
        """
        Initialize project analyzer.

        Args:
            project_path: Path to project to analyze
            config_path: Optional path to config file
        """
        self.project_path = Path(project_path).resolve()
        self.config = self._load_config(config_path)
        self.output_dir = self.project_path / self.config['general']['output_dir']
        self.analysis_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        # Initialize analysis components
        self.language_detector = LanguageDetector(self.config)
        self.decision_extractor = DecisionExtractor(self.config)
        self.architecture_visualizer = ArchitectureVisualizer(self.config)
        self.threat_modeler = ThreatModeler(self.config)
        self.tech_debt_detector = TechDebtDetector(self.config)
        self.documentation_generator = DocumentationGenerator(self.config)

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
        exclude_patterns = self.config['general']['exclude_patterns']
        loc_count = 0

        for file in self.project_path.rglob("*"):
            # Skip excluded patterns
            if any(pattern in str(file) for pattern in exclude_patterns):
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
            exclude_patterns = self.config['general']['exclude_patterns']

            files_by_ext = {}
            total_files = 0
            total_loc = 0

            for file in self.project_path.rglob("*"):
                # Skip excluded patterns
                if any(pattern in str(file) for pattern in exclude_patterns):
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
            # Step 1: Create feature branch
            branch_info = self.create_feature_branch(branch_name)

            # Step 2: Validate project
            if not self.validate_project():
                raise ValueError("Project validation failed")

            # Step 3: Scan directory
            scan_results = self.scan_directory()

            # Step 4: Detect languages
            language_analysis = self.detect_languages()

            # Step 5: Extract decisions
            decisions = self.extract_decisions(language_analysis, no_llm=no_llm)

            # Step 6: Generate diagrams
            diagrams = self.generate_diagrams(language_analysis, decisions)

            # Step 7: Model threats (if not skipped)
            if not skip_threat_model:
                threats = self.model_threats(decisions)
            else:
                threats = {"status": "skipped"}

            # Step 8: Detect tech debt (if not skipped)
            if not skip_tech_debt:
                tech_debt = self.detect_tech_debt()
            else:
                tech_debt = {"status": "skipped"}

            # Build complete results before documentation generation
            results = {
                "analysis_id": self.analysis_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "project_path": str(self.project_path),
                "branch": branch_info,
                "scan": scan_results,
                "language_analysis": language_analysis,
                "decisions": decisions,
                "diagrams": diagrams,
                "threats": threats,
                "tech_debt": tech_debt
            }

            # Step 9: Generate documentation
            documentation = self.generate_documentation(results)
            results["documentation"] = documentation

            logger.info(
                "Analysis complete",
                extra={"analysis_id": self.analysis_id}
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

    args = parser.parse_args()

    try:
        analyzer = ProjectAnalyzer(args.project_path, args.config)
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
        return 1


if __name__ == "__main__":
    sys.exit(main())
