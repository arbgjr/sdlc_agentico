#!/usr/bin/env python3
"""
Tech Debt Detector - Identify technical debt
Uses code-review plugin patterns.

NEW (v2.1.7): Risk Analysis for Tech Debt
- probability × impact = risk_score
- ROI calculation for prioritization

References:
- awesome-copilot: code-gap-audit.prompt
- claude-plugins-official: code-review
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Literal
from dataclasses import dataclass
import yaml

# Add logging utilities (absolute path from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


@dataclass
class RiskAnalysis:
    """NEW (v2.1.7): Risk analysis for tech debt"""
    probability: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    impact: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_score: float  # 0.0-10.0
    remediation_cost: Literal["LOW", "MEDIUM", "HIGH"]
    roi: float  # risk_score / remediation_cost


def calculate_risk_score(probability: str, impact: str) -> float:
    """Calculate risk score from probability and impact"""
    prob_scores = {"LOW": 0.25, "MEDIUM": 0.50, "HIGH": 0.75, "CRITICAL": 1.0}
    impact_scores = {"LOW": 2.5, "MEDIUM": 5.0, "HIGH": 7.5, "CRITICAL": 10.0}
    return prob_scores[probability] * impact_scores[impact]


class TechDebtDetector:
    """Detect technical debt"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config['tech_debt']['enabled']
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        rules_file = Path(__file__).parent.parent / "config" / "tech_debt_rules.yml"
        with open(rules_file) as f:
            return yaml.safe_load(f)

    def scan(self, project_path: Path) -> Dict:
        """Scan for technical debt"""
        if not self.enabled:
            return {"status": "skipped"}

        debt_items = []
        debt_items.extend(self._detect_code_smells(project_path))
        debt_items.extend(self._detect_deprecated_deps(project_path))
        debt_items.extend(self._detect_security_issues(project_path))
        debt_items.extend(self._detect_missing_authorization(project_path))  # NEW (v2.1.7)

        # NEW (v2.1.7 - G2): Analyze existing tests before reporting "no tests"
        test_coverage = self._analyze_test_coverage(project_path)
        if test_coverage['status'] == 'no_tests':
            debt_items.extend(self._detect_missing_tests(project_path, test_coverage))

        p0 = [d for d in debt_items if d['priority'] == 'P0']
        p1 = [d for d in debt_items if d['priority'] == 'P1']
        p2 = [d for d in debt_items if d['priority'] == 'P2']
        p3 = [d for d in debt_items if d['priority'] == 'P3']

        total_effort = sum(d['effort_estimate'] for d in debt_items)

        logger.info(f"Tech debt scan complete: {len(debt_items)} items ({len(p0)} P0, {len(p1)} P1)")

        return {
            "tech_debt": debt_items,
            "total": len(debt_items),
            "total_effort": total_effort,
            "p0": len(p0),
            "p1": len(p1),
            "p2": len(p2),
            "p3": len(p3),
            "debt_summary": {"P0": len(p0), "P1": len(p1), "P2": len(p2), "P3": len(p3)}
        }

    def _detect_code_smells(self, path: Path) -> List[Dict]:
        """Detect code smells"""
        smells = []
        threshold = self.rules['code_smells']['long_functions']['threshold']

        for file in path.rglob("*.py"):
            try:
                lines = file.read_text().splitlines()
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        func_lines = 1
                        for j in range(i+1, len(lines)):
                            if lines[j].strip() and not lines[j].startswith(' '):
                                break
                            func_lines += 1

                        if func_lines > threshold:
                            smells.append({
                                "id": f"DEBT-{len(smells)+1:03d}",
                                "title": f"Long function detected ({func_lines} lines)",
                                "category": "code_smell",
                                "priority": "P2",
                                "file": str(file),
                                "line": i+1,
                                "effort_estimate": 4
                            })
            except:
                pass

        return smells

    def _detect_deprecated_deps(self, path: Path) -> List[Dict]:
        """Detect deprecated dependencies"""
        deps = []
        req_file = path / "requirements.txt"

        if req_file.exists():
            content = req_file.read_text()
            if 'django==2.' in content or 'django==1.' in content:
                deps.append({
                    "id": f"DEBT-DEP-001",
                    "title": "Django EOL version detected",
                    "category": "deprecated_dependency",
                    "priority": "P0",
                    "file": "requirements.txt",
                    "line": 1,
                    "effort_estimate": 16
                })

        return deps

    def _detect_security_issues(self, path: Path) -> List[Dict]:
        """Detect security issues"""
        issues = []
        for file in path.rglob("*.py"):
            try:
                content = file.read_text()
                if re.search(r'(password|secret)\s*=\s*["\'][^"\']+["\']', content):
                    issues.append({
                        "id": f"DEBT-SEC-{len(issues)+1:03d}",
                        "title": "Hardcoded secret",
                        "category": "security",
                        "priority": "P0",
                        "file": str(file),
                        "line": 1,
                        "effort_estimate": 2
                    })
            except:
                pass

        return issues

    def _detect_missing_authorization(self, path: Path) -> List[Dict]:
        """
        NEW (v2.1.7): Detect missing authorization in API endpoints.

        Multi-pattern detection for various authorization methods:
        - ASP.NET Core: [Authorize], .RequireAuthorization()
        - Minimal API: .WithMetadata(new AuthorizeAttribute), .RequirePermission()
        - Custom: RequirePermissionAttribute, RequireRole, RequirePolicy
        - Infrastructure: IAuthorizationService, AddAuthorization(), UseAuthorization()

        Returns:
            List of tech debt items for endpoints without authorization
        """
        issues = []

        # Authorization patterns (comprehensive list)
        AUTHORIZATION_PATTERNS = [
            # ASP.NET Core standard
            r'\[Authorize(?:\(.*?\))?\]',
            r'\.RequireAuthorization\(',

            # Minimal API metadata
            r'\.WithMetadata\(new AuthorizeAttribute',
            r'\.RequirePermission\(',
            r'RequirePermissionAttribute',

            # Custom patterns
            r'RequireRole',
            r'RequirePolicy',
            r'IAuthorizationService',
            r'\.RequireAssertion\(',
            r'\.RequireClaim\(',

            # Policy-based
            r'AddPolicy\(',
            r'AuthorizationPolicyBuilder',
        ]

        # Search for C# API endpoint files
        endpoint_files = []
        for pattern in ["*Endpoints.cs", "*Controller.cs", "Program.cs", "Startup.cs"]:
            endpoint_files.extend(path.rglob(f"**/{pattern}"))

        # Check each endpoint file
        for file in endpoint_files:
            if file.name == "Program.cs" or file.name == "Startup.cs":
                # Check for authorization infrastructure
                try:
                    content = file.read_text()
                    has_authorization_service = 'AddAuthorization()' in content or 'AddAuthorization(' in content
                    has_middleware = 'UseAuthorization()' in content
                    has_custom_service = 'IAuthorizationService' in content

                    if not (has_authorization_service or has_middleware or has_custom_service):
                        issues.append({
                            "id": f"DEBT-AUTH-{len(issues)+1:03d}",
                            "title": "Missing authorization infrastructure configuration",
                            "category": "security",
                            "priority": "P0",
                            "file": str(file),
                            "line": 1,
                            "effort_estimate": 4,
                            "description": "No AddAuthorization() or UseAuthorization() found in Program.cs/Startup.cs",
                            "remediation": "Add services.AddAuthorization() and app.UseAuthorization() to configure authorization infrastructure"
                        })
                except Exception as e:
                    logger.warning(f"Failed to check {file}: {e}")

                continue  # Skip endpoint analysis for infrastructure files

            # Analyze endpoints in *Endpoints.cs or *Controller.cs
            try:
                content = file.read_text()

                # Check if file has ANY authorization pattern
                has_any_authorization = False
                for pattern in AUTHORIZATION_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        has_any_authorization = True
                        break

                # Find HTTP method declarations (MapPost, MapGet, etc. or [HttpPost], [HttpGet])
                http_methods = re.findall(
                    r'(Map(Get|Post|Put|Delete|Patch)|HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch)',
                    content,
                    re.IGNORECASE
                )

                # If has HTTP methods but NO authorization patterns -> potential issue
                if len(http_methods) > 0 and not has_any_authorization:
                    # Check if it's a public endpoint intentionally (whitelist patterns)
                    is_public_endpoint = any(pattern in content for pattern in [
                        'AllowAnonymous',
                        '// Public endpoint',
                        '// No authorization required',
                        'HealthCheck',
                        'Swagger'
                    ])

                    if not is_public_endpoint:
                        # Reduce severity if custom authorization detected elsewhere
                        priority = "P1"  # Not P0 since we might miss custom patterns
                        note = "No standard authorization pattern detected. Manual verification required."

                        issues.append({
                            "id": f"DEBT-AUTH-{len(issues)+1:03d}",
                            "title": f"Potential missing authorization in {file.name}",
                            "category": "security",
                            "priority": priority,
                            "file": str(file),
                            "line": 1,
                            "effort_estimate": 3,
                            "description": f"Found {len(http_methods)} HTTP endpoints but no standard authorization patterns ([Authorize], RequireAuthorization, RequirePermission, etc.)",
                            "remediation": "Add [Authorize] attribute or .RequireAuthorization() to endpoints. If using custom authorization, verify it's correctly applied.",
                            "note": note
                        })

            except Exception as e:
                logger.warning(f"Failed to analyze {file}: {e}")

        logger.info(f"Authorization analysis complete: {len(issues)} potential issues found")
        return issues

    def _analyze_test_coverage(self, path: Path) -> Dict:
        """
        NEW (v2.1.7 - G2): Analyze existing test coverage.

        Checks:
        - Test files count (test*, *test.*, *spec.*, *Test.cs, *Tests.cs)
        - Test projects count (.Tests.csproj, test_*.py)
        - Estimated test count (via `dotnet test --list-tests` if .NET)

        Returns:
            Dict with coverage status and statistics
        """
        import subprocess

        test_files = []
        test_projects = []

        # Find test files (language-agnostic patterns)
        test_patterns = [
            "**/*Test*.cs",
            "**/*Tests*.cs",
            "**/test_*.py",
            "**/*_test.py",
            "**/*.test.ts",
            "**/*.test.js",
            "**/*.spec.ts",
            "**/*.spec.js",
            "**/Test*.java",
            "**/*Test.java",
        ]

        for pattern in test_patterns:
            test_files.extend(path.rglob(pattern))

        # Find test projects (.NET specific)
        for csproj in path.rglob("*.csproj"):
            if "Test" in csproj.stem:
                test_projects.append(csproj)

        # Remove duplicates
        test_files = list(set(test_files))

        # Try to count tests (.NET)
        estimated_test_count = 0
        if test_projects:
            try:
                # Run dotnet test --list-tests on first test project
                result = subprocess.run(
                    ['dotnet', 'test', str(test_projects[0]), '--list-tests'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Count lines that look like test names (heuristic)
                    test_lines = [line for line in result.stdout.split('\n') if '.' in line and not line.strip().startswith('Test')]
                    estimated_test_count = len(test_lines)
            except Exception as e:
                logger.warning(f"Failed to count .NET tests: {e}")

        # Determine status
        if test_files or test_projects:
            status = "has_tests"
        else:
            status = "no_tests"

        coverage_info = {
            "status": status,
            "test_files_count": len(test_files),
            "test_projects_count": len(test_projects),
            "estimated_test_count": estimated_test_count,
            "test_files": [str(f.relative_to(path)) for f in test_files[:10]]  # First 10 for debugging
        }

        logger.info(
            f"Test coverage analysis: {status}",
            extra={
                "test_files": len(test_files),
                "test_projects": len(test_projects),
                "estimated_tests": estimated_test_count
            }
        )

        return coverage_info

    def _detect_missing_tests(self, path: Path, test_coverage: Dict) -> List[Dict]:
        """
        NEW (v2.1.7 - G2): Detect missing tests.

        Only reports as P0 if truly no tests found.
        If tests exist but coverage unknown, reports as P2.

        Args:
            path: Project path
            test_coverage: Result from _analyze_test_coverage()

        Returns:
            List of tech debt items
        """
        issues = []

        if test_coverage['status'] == 'no_tests':
            # Truly no tests found
            issues.append({
                "id": "DEBT-TEST-001",
                "title": "No automated tests found",
                "category": "testing",
                "priority": "P0",
                "file": str(path),
                "line": 1,
                "effort_estimate": 20,
                "description": f"No test files found in project (searched {len(['**/*Test*.cs', '**/*.test.ts', 'test_*.py', '**/*.spec.js'])} patterns)",
                "remediation": "Add automated tests (unit, integration, E2E). Aim for >70% code coverage.",
                "impact": "High risk of regressions, bugs in production"
            })
        elif test_coverage['estimated_test_count'] == 0:
            # Tests exist but count unknown
            issues.append({
                "id": "DEBT-TEST-002",
                "title": "Test coverage unknown",
                "category": "testing",
                "priority": "P2",
                "file": str(path),
                "line": 1,
                "effort_estimate": 8,
                "description": f"Found {test_coverage['test_files_count']} test files but coverage not measured. Cannot verify if tests are comprehensive.",
                "remediation": "Run coverage analysis: `dotnet test --collect:\"XPlat Code Coverage\"` or equivalent",
                "impact": "Unknown test quality, potential gaps in coverage"
            })

        return issues


def main():
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    args = parser.parse_args()

    config_path = Path(__file__).parent.parent / "config" / "import_config.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    detector = TechDebtDetector(config)
    result = detector.scan(Path(args.project_path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
