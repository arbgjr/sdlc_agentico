#!/usr/bin/env python3
"""
Tech Debt Detector - Identify technical debt
Uses code-review plugin patterns.

References:
- awesome-copilot: code-gap-audit.prompt
- claude-plugins-official: code-review
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
import yaml

sys.path.insert(0, '.claude/lib/python')
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=0)


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
