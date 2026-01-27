#!/usr/bin/env python3
"""
GitHub Issue Creator - Auto-create issues for tech debt items
Reuses patterns from github-sync skill.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "lib/python"))
from sdlc_logging import get_logger, log_operation

logger = get_logger(__name__, skill="sdlc-import", phase=0)


class IssueCreator:
    """Create GitHub issues from tech debt items"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('github_integration', {}).get('create_issues', False)
        self.min_priority = config.get('github_integration', {}).get('min_priority', 'P1')

    def create_issues(self, tech_debt_items: List[Dict], project_path: Path) -> Dict:
        """Create GitHub issues for tech debt items"""
        if not self.enabled:
            logger.info("Issue creation disabled")
            return {"created": 0, "skipped": len(tech_debt_items)}

        with log_operation("create_github_issues", logger):
            # Check if gh CLI is available
            if not self._check_gh_cli():
                logger.error("gh CLI not found - cannot create issues")
                return {"created": 0, "skipped": len(tech_debt_items), "error": "gh CLI not available"}

            # Ensure SDLC labels exist
            self._ensure_labels(project_path)

            created_issues = []
            skipped_count = 0

            for item in tech_debt_items:
                priority = item.get('priority', 'P3')

                # Filter by priority (P0/P1 only by default)
                if not self._should_create_issue(priority):
                    skipped_count += 1
                    continue

                # Create issue
                issue_url = self._create_single_issue(item, project_path)
                if issue_url:
                    created_issues.append({
                        "title": item.get('title'),
                        "priority": priority,
                        "url": issue_url
                    })

            logger.info(
                "GitHub issues created",
                extra={
                    "created_count": len(created_issues),
                    "skipped_count": skipped_count,
                    "total_items": len(tech_debt_items)
                }
            )

            return {
                "created": len(created_issues),
                "skipped": skipped_count,
                "issues": created_issues
            }

    def _check_gh_cli(self) -> bool:
        """Check if gh CLI is available"""
        try:
            subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                check=True,
                text=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _ensure_labels(self, project_path: Path) -> None:
        """Ensure SDLC labels exist in repository"""
        sdlc_labels = [
            {"name": "sdlc:auto", "color": "0366d6", "description": "Created automatically by SDLC Agêntico"},
            {"name": "type:tech-debt", "color": "d73a4a", "description": "Technical debt item"},
            {"name": "priority:P0", "color": "b60205", "description": "Critical priority"},
            {"name": "priority:P1", "color": "d93f0b", "description": "High priority"}
        ]

        for label in sdlc_labels:
            try:
                # Try to create label (will fail silently if exists)
                subprocess.run(
                    [
                        "gh", "label", "create",
                        label["name"],
                        "--color", label["color"],
                        "--description", label["description"]
                    ],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError:
                pass  # Label already exists

    def _should_create_issue(self, priority: str) -> bool:
        """Check if issue should be created based on priority"""
        priority_levels = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        min_level = priority_levels.get(self.min_priority, 1)
        item_level = priority_levels.get(priority, 3)

        return item_level <= min_level

    def _create_single_issue(self, item: Dict, project_path: Path) -> str:
        """Create a single GitHub issue"""
        title = item.get('title', 'Tech Debt Item')
        priority = item.get('priority', 'P2')
        description = item.get('description', 'No description provided')
        file_path = item.get('file', '')
        line = item.get('line', '')

        # Build issue body
        body = f"""## Technical Debt

**Priority:** {priority}
**Category:** {item.get('category', 'unknown')}
**Estimated Effort:** {item.get('effort_hours', 0)}h

### Description

{description}

### Location

- **File:** `{file_path}`
- **Line:** {line}

### Recommendations

{item.get('recommendation', 'See description')}

---

🤖 **Generated with SDLC Agêntico** by @arbgjr
"""

        # Create issue with labels
        labels = ["sdlc:auto", "type:tech-debt", f"priority:{priority}"]

        try:
            result = subprocess.run(
                [
                    "gh", "issue", "create",
                    "--title", f"[{priority}] {title}",
                    "--body", body,
                    "--label", ",".join(labels)
                ],
                cwd=str(project_path),
                capture_output=True,
                check=True,
                text=True
            )

            issue_url = result.stdout.strip()
            logger.info(
                "Created GitHub issue",
                extra={"title": title, "priority": priority, "url": issue_url}
            )

            return issue_url

        except subprocess.CalledProcessError as e:
            logger.warning(
                "Failed to create issue",
                extra={"title": title, "error": str(e)}
            )
            return ""


if __name__ == "__main__":
    # Test issue creation
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Create GitHub issues for tech debt")
    parser.add_argument("project_path", type=Path, help="Project directory")
    parser.add_argument("--tech-debt-file", type=Path, help="Tech debt JSON file")
    parser.add_argument("--config", type=Path, help="Config file")
    args = parser.parse_args()

    config = {"github_integration": {"create_issues": True, "min_priority": "P1"}}
    if args.config and args.config.exists():
        with open(args.config) as f:
            loaded_config = yaml.safe_load(f)
            config.update(loaded_config)

    creator = IssueCreator(config)

    # Load tech debt items
    tech_debt_items = []
    if args.tech_debt_file and args.tech_debt_file.exists():
        with open(args.tech_debt_file) as f:
            data = json.load(f)
            tech_debt_items = data.get('items', [])

    result = creator.create_issues(tech_debt_items, args.project_path)
    print(json.dumps(result, indent=2))
