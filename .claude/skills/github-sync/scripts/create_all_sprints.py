#!/usr/bin/env python3
"""
Create all sprint milestones from task breakdown YAML.

Usage:
    python create_all_sprints.py <task-breakdown.yml>
    python create_all_sprints.py <task-breakdown.yml> --base-date 2026-01-20
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta

# Import milestone_sync as library
sys.path.insert(0, str(Path(__file__).parent))
from milestone_sync import create_milestone


def parse_sprint_config(task_breakdown: dict) -> dict:
    """Extract sprint configuration from task breakdown."""
    sprints = {}

    # Sprint 0
    if 'sprint_0_infrastructure' in task_breakdown:
        sprint_0 = task_breakdown['sprint_0_infrastructure']
        sprints[0] = {
            'name': sprint_0.get('name', 'Sprint 0 - Infrastructure & Setup'),
            'description': sprint_0.get('goal', 'Preparar repositório, CI/CD e ambiente'),
            'duration_weeks': sprint_0.get('duration_weeks', 1)
        }

    # EPICs (automatically detect sprints from assigned_sprint)
    sprint_names = {}
    sprint_durations = {}

    for epic_key in ['epic_001_tasks', 'epic_002_tasks', 'epic_003_tasks',
                     'epic_004_tasks', 'epic_005_tasks']:
        if epic_key not in task_breakdown:
            continue

        epic_data = task_breakdown[epic_key]
        epic_name = epic_data.get('epic_name', epic_key)

        for key, value in epic_data.items():
            if not key.startswith('story_'):
                continue

            if not isinstance(value, dict) or 'tasks' not in value:
                continue

            for task in value.get('tasks', []):
                sprint_num = task.get('assigned_sprint', 1)

                if sprint_num not in sprint_names:
                    sprint_names[sprint_num] = []

                # Infer duration from estimated_hours (assume 40h/week)
                estimated_hours = task.get('estimated_hours', 0)
                weeks = max(1, round(estimated_hours / 40))
                sprint_durations[sprint_num] = max(
                    sprint_durations.get(sprint_num, 1),
                    weeks
                )

                if epic_name not in sprint_names[sprint_num]:
                    sprint_names[sprint_num].append(epic_name)

    # Build sprint metadata
    for sprint_num in sorted(sprint_names.keys()):
        epics = sprint_names[sprint_num]
        duration = sprint_durations.get(sprint_num, 2)

        sprints[sprint_num] = {
            'name': f"Sprint {sprint_num} - {', '.join(epics[:2])}",
            'description': f"Implementar: {', '.join(epics)}",
            'duration_weeks': duration
        }

    # Sprint 6 (Polish)
    if 'sprint_6_polish' in task_breakdown:
        sprint_6 = task_breakdown['sprint_6_polish']
        sprints[6] = {
            'name': sprint_6.get('name', 'Sprint 6 - Polish & QA'),
            'description': sprint_6.get('goal', 'Polimento, testes E2E e preparação para produção'),
            'duration_weeks': sprint_6.get('duration_weeks', 1)
        }

    return sprints


def calculate_dates(sprints: dict, base_date: str) -> dict:
    """Calculate due dates for all sprints."""
    dates = {}
    current_date = datetime.strptime(base_date, "%Y-%m-%d")

    for sprint_num in sorted(sprints.keys()):
        duration_weeks = sprints[sprint_num]['duration_weeks']
        due_date = current_date + timedelta(weeks=duration_weeks)
        dates[sprint_num] = due_date.strftime("%Y-%m-%d")
        current_date = due_date  # Next sprint starts after this one

    return dates


def create_all_sprints(yaml_path: str, base_date: str = None):
    """Create all sprint milestones from task breakdown."""

    # Load task breakdown
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    task_breakdown = data.get('task_breakdown', {})

    # Parse sprint configuration
    sprints = parse_sprint_config(task_breakdown)

    if not sprints:
        print("No sprints found in task breakdown.", file=sys.stderr)
        return 1

    # Calculate dates
    if base_date is None:
        base_date = datetime.now().strftime("%Y-%m-%d")

    dates = calculate_dates(sprints, base_date)

    print(f"Creating {len(sprints)} sprint milestones...")
    print(f"Base date: {base_date}")
    print()

    # Create milestones
    created_count = 0
    failed_count = 0

    for sprint_num in sorted(sprints.keys()):
        sprint = sprints[sprint_num]
        due_date = dates[sprint_num]

        print(f"Creating {sprint['name']} (due: {due_date})...")

        milestone = create_milestone(
            title=sprint['name'],
            description=sprint['description'],
            due_date=due_date
        )

        if milestone:
            created_count += 1
        else:
            failed_count += 1

    print()
    print("="*60)
    print(f"✓ Created: {created_count}")
    print(f"✗ Failed: {failed_count}")
    print("="*60)

    return 0 if failed_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Create all sprint milestones from task breakdown"
    )
    parser.add_argument(
        "yaml_path",
        help="Path to task-breakdown.yml"
    )
    parser.add_argument(
        "--base-date",
        help="Base date for Sprint 0 start (YYYY-MM-DD). Default: today",
        default=None
    )

    args = parser.parse_args()

    if not Path(args.yaml_path).exists():
        print(f"Error: File not found: {args.yaml_path}", file=sys.stderr)
        return 1

    return create_all_sprints(args.yaml_path, args.base_date)


if __name__ == "__main__":
    sys.exit(main())
