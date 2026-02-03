#!/usr/bin/env python3
"""
Tech Debt Detector - Technical Debt Analysis Module

Scans codebase for technical debt indicators:
- Code smells (long methods, large classes, duplicated code)
- Deprecated APIs and dependencies
- Missing tests
- TODO/FIXME comments
- Security vulnerabilities
- Performance anti-patterns

Prioritizes findings by severity (P0-P3).
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone

# Add logging utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger

logger = get_logger(__name__, skill="sdlc-import", phase=1)


class TechDebtDetector:
    """Technical debt scanner and analyzer"""

    def __init__(self, config: Dict):
        """
        Initialize tech debt detector.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.debt_patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load technical debt detection patterns"""
        return {
            'todo_comments': [
                r'//\s*TODO',
                r'#\s*TODO',
                r'/\*\s*TODO',
                r'<!--\s*TODO'
            ],
            'fixme_comments': [
                r'//\s*FIXME',
                r'#\s*FIXME',
                r'/\*\s*FIXME'
            ],
            'hack_comments': [
                r'//\s*HACK',
                r'#\s*HACK',
                r'/\*\s*HACK'
            ],
            'deprecated_apis': [
                r'@Deprecated',
                r'deprecated=True',
                r'warnings\.warn.*DeprecationWarning'
            ],
            'security_issues': [
                r'eval\(',
                r'exec\(',
                r'__import__\(',
                r'subprocess\.(?:call|run|Popen)\(',
                r'os\.system\(',
                r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']'  # Hardcoded API keys
            ],
            'code_smells': [
                r'def\s+\w+\s*\([^)]*\):\s*\n(?:\s+[^\n]+\n){50,}',  # Long methods (50+ lines)
                r'class\s+\w+.*:\s*\n(?:\s+[^\n]+\n){200,}',  # Large classes (200+ lines)
            ]
        }

    def scan(self, project_path: Path) -> Dict:
        """
        Scan project for technical debt.

        Args:
            project_path: Path to project

        Returns:
            Dict with tech debt findings
        """
        logger.info("Starting technical debt scan")

        debt_items = []

        # Scan source files
        source_extensions = ['.py', '.js', '.ts', '.java', '.cs', '.rb', '.go']

        for file_path in project_path.rglob("*"):
            if file_path.suffix not in source_extensions:
                continue

            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                file_debt = self._scan_file(file_path, content)
                debt_items.extend(file_debt)
            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {e}")

        # Categorize by priority
        p0 = sum(1 for item in debt_items if item.get('priority') == 'P0')
        p1 = sum(1 for item in debt_items if item.get('priority') == 'P1')
        p2 = sum(1 for item in debt_items if item.get('priority') == 'P2')
        p3 = sum(1 for item in debt_items if item.get('priority') == 'P3')

        result = {
            'total': len(debt_items),
            'p0': p0,  # Critical - security/data loss risks
            'p1': p1,  # High - deprecated APIs, broken functionality
            'p2': p2,  # Medium - code quality, maintainability
            'p3': p3,  # Low - minor improvements, TODOs
            'items': debt_items,
            'timestamp': datetime.now(timezone.utc).isoformat() + 'Z'
        }

        logger.info(
            "Tech debt scan complete",
            extra={
                'total': len(debt_items),
                'p0': p0,
                'p1': p1,
                'p2': p2
            }
        )

        return result

    def _scan_file(self, file_path: Path, content: str) -> List[Dict]:
        """
        Scan a single file for technical debt.

        Args:
            file_path: Path to file
            content: File content

        Returns:
            List of debt items found
        """
        items = []

        # Security issues (P0)
        for pattern in self.debt_patterns['security_issues']:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'security',
                    'priority': 'P0',
                    'title': 'Potential Security Issue',
                    'description': f"Security pattern detected: {match.group(0)[:50]}",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': match.group(0)[:100]
                })

        # Deprecated APIs (P1)
        for pattern in self.debt_patterns['deprecated_apis']:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'deprecated',
                    'priority': 'P1',
                    'title': 'Deprecated API Usage',
                    'description': f"Using deprecated API: {match.group(0)[:50]}",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': match.group(0)[:100]
                })

        # FIXME comments (P1)
        for pattern in self.debt_patterns['fixme_comments']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                # Extract full comment line
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                full_line = content[line_start:line_end] if line_end != -1 else content[line_start:]

                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'fixme',
                    'priority': 'P1',
                    'title': 'FIXME Comment',
                    'description': f"Code marked for fixing: {full_line.strip()}",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': full_line.strip()[:100]
                })

        # HACK comments (P2)
        for pattern in self.debt_patterns['hack_comments']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                full_line = content[line_start:line_end] if line_end != -1 else content[line_start:]

                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'hack',
                    'priority': 'P2',
                    'title': 'HACK Comment',
                    'description': f"Hacky implementation: {full_line.strip()}",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': full_line.strip()[:100]
                })

        # Code smells (P2)
        for pattern in self.debt_patterns['code_smells']:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                smell_type = 'long_method' if 'def' in match.group(0) else 'large_class'

                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'code_smell',
                    'priority': 'P2',
                    'title': f"Code Smell: {smell_type.replace('_', ' ').title()}",
                    'description': f"{'Method' if smell_type == 'long_method' else 'Class'} is too long",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': match.group(0)[:100]
                })

        # TODO comments (P3)
        for pattern in self.debt_patterns['todo_comments']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                full_line = content[line_start:line_end] if line_end != -1 else content[line_start:]

                items.append({
                    'id': f"DEBT-{file_path.name}-{line_num}",
                    'type': 'todo',
                    'priority': 'P3',
                    'title': 'TODO Comment',
                    'description': f"Unfinished work: {full_line.strip()}",
                    'file': str(file_path),
                    'line': line_num,
                    'snippet': full_line.strip()[:100]
                })

        return items
