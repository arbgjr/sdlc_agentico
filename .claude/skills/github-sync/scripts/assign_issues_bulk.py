#!/usr/bin/env python3
"""
Bulk assign GitHub issues to sprint milestones based on task breakdown.

Usage:
    python assign_issues_bulk.py <task-breakdown.yml>
"""

import argparse
import json
import subprocess
import sys
import time
import yaml
from pathlib import Path


def run_gh_command(cmd):
    """Execute gh CLI command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr
    return result.stdout.strip(), None


def get_milestone_number(milestone_title: str) -> int:
    """Get milestone number by title."""
    output, error = run_gh_command(
        f'gh api repos/{{owner}}/{{repo}}/milestones -X GET -f state=all --jq \'.[] | select(.title == "{milestone_title}") | .number\''
    )

    if error or not output:
        return None

    try:
        return int(output)
    except ValueError:
        return None


def build_task_to_milestone_map(task_breakdown: dict) -> dict:
    """Build mapping from task ID to milestone title."""
    task_to_milestone = {}

    # Sprint 0
    if 'sprint_0_infrastructure' in task_breakdown:
        sprint_0 = task_breakdown['sprint_0_infrastructure']
        milestone_title = sprint_0.get('name', 'Sprint 0 - Infrastructure & Setup')

        for task in sprint_0.get('tasks', []):
            task_to_milestone[task['id']] = milestone_title

    # EPICs
    for epic_key in ['epic_001_tasks', 'epic_002_tasks', 'epic_003_tasks',
                     'epic_004_tasks', 'epic_005_tasks']:
        if epic_key not in task_breakdown:
            continue

        epic_data = task_breakdown[epic_key]

        for key, value in epic_data.items():
            if not key.startswith('story_'):
                continue

            if not isinstance(value, dict) or 'tasks' not in value:
                continue

            for task in value.get('tasks', []):
                sprint_num = task.get('assigned_sprint', 1)

                # Find milestone by sprint number
                # This is a heuristic - look for "Sprint {num}" in title
                milestone_title = f"Sprint {sprint_num}"
                task_to_milestone[task['id']] = milestone_title

    # Sprint 6
    if 'sprint_6_polish' in task_breakdown:
        sprint_6 = task_breakdown['sprint_6_polish']
        milestone_title = sprint_6.get('name', 'Sprint 6 - Polish & QA')

        for task in sprint_6.get('tasks', []):
            task_to_milestone[task['id']] = milestone_title

    return task_to_milestone


def assign_issues_to_milestones(yaml_path: str):
    """Assign issues to milestones based on task breakdown."""

    # Load task breakdown
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    task_breakdown = data.get('task_breakdown', {})

    # Build mapping
    task_to_milestone = build_task_to_milestone_map(task_breakdown)

    if not task_to_milestone:
        print("No task-to-milestone mapping found.", file=sys.stderr)
        return 1

    print(f"Mapping {len(task_to_milestone)} tasks to milestones...")
    print()

    # Get all issues
    output, error = run_gh_command('gh issue list --limit 200 --json number,title,milestone')

    if error:
        print(f"Failed to fetch issues: {error}", file=sys.stderr)
        return 1

    try:
        issues = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Failed to parse issues JSON: {e}", file=sys.stderr)
        return 1

    # Cache milestone numbers
    milestone_cache = {}

    updated_count = 0
    skipped_count = 0
    failed_count = 0

    for issue in issues:
        issue_number = issue['number']
        issue_title = issue['title']

        # Extract task ID from title (format: [TASK-XXX] ...)
        if not issue_title.startswith('[TASK-'):
            skipped_count += 1
            continue

        try:
            task_id = issue_title.split(']')[0][1:]  # Extract TASK-XXX
        except IndexError:
            print(f"⚠ Issue #{issue_number}: Invalid title format")
            skipped_count += 1
            continue

        if task_id not in task_to_milestone:
            print(f"⚠ Issue #{issue_number} ({task_id}): No milestone mapping found")
            skipped_count += 1
            continue

        milestone_title = task_to_milestone[task_id]

        # Get milestone number (with caching)
        if milestone_title not in milestone_cache:
            milestone_number = get_milestone_number(milestone_title)

            if milestone_number is None:
                print(f"✗ Milestone '{milestone_title}' not found for {task_id}")
                failed_count += 1
                continue

            milestone_cache[milestone_title] = milestone_number

        milestone_number = milestone_cache[milestone_title]

        # Update issue milestone (use title, not number)
        _, error = run_gh_command(f'gh issue edit {issue_number} --milestone "{milestone_title}"')

        if error:
            print(f"✗ Failed to update issue #{issue_number}: {error}")
            failed_count += 1
        else:
            print(f"✓ Issue #{issue_number} ({task_id}) → Milestone #{milestone_number} ({milestone_title})")
            updated_count += 1

        time.sleep(0.3)  # Rate limiting

    print()
    print("="*60)
    print(f"✓ Updated: {updated_count}")
    print(f"⊘ Skipped: {skipped_count}")
    print(f"✗ Failed: {failed_count}")
    print("="*60)

    return 0 if failed_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Bulk assign issues to milestones from task breakdown"
    )
    parser.add_argument(
        "yaml_path",
        help="Path to task-breakdown.yml"
    )

    args = parser.parse_args()

    if not Path(args.yaml_path).exists():
        print(f"Error: File not found: {args.yaml_path}", file=sys.stderr)
        return 1

    return assign_issues_to_milestones(args.yaml_path)


if __name__ == "__main__":
    sys.exit(main())
