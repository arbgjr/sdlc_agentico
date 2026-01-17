#!/usr/bin/env python3
"""
Bulk create GitHub issues from task breakdown YAML.
"""
import sys
import yaml
import subprocess
import json
from pathlib import Path
from datetime import datetime
import time

def run_command(cmd, input_text=None):
    """Run a shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        input=input_text
    )
    if result.returncode != 0:
        print(f"Error running command: {cmd}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout.strip()

def create_issue(task, epic_name, sprint_number, project_number):
    """Create a GitHub issue from a task."""
    task_id = task['id']
    title = f"[{task_id}] {task['title']}"

    # Build issue body
    body_parts = []

    # Epic and Sprint info
    body_parts.append(f"**Epic:** {epic_name}")
    body_parts.append(f"**Sprint:** Sprint {sprint_number}")
    body_parts.append(f"**Type:** {task.get('type', 'task')}")
    body_parts.append(f"**Priority:** {task.get('priority', 'medium')}")
    body_parts.append(f"**Story Points:** {task.get('story_points', 0)}")
    body_parts.append(f"**Estimated Hours:** {task.get('estimated_hours', 0)}")
    body_parts.append("")

    # Description
    body_parts.append("## Description")
    body_parts.append(task.get('description', '').strip())
    body_parts.append("")

    # Acceptance Criteria
    if 'acceptance_criteria' in task and task['acceptance_criteria']:
        body_parts.append("## Acceptance Criteria")
        for criterion in task['acceptance_criteria']:
            body_parts.append(f"- [ ] {criterion}")
        body_parts.append("")

    # Dependencies
    if 'dependencies' in task and task['dependencies']:
        body_parts.append("## Dependencies")
        for dep in task['dependencies']:
            body_parts.append(f"- {dep}")
        body_parts.append("")

    # Technical Notes
    if 'technical_notes' in task and task['technical_notes']:
        body_parts.append("## Technical Notes")
        body_parts.append(task['technical_notes'])
        body_parts.append("")

    # Footer
    body_parts.append("---")
    body_parts.append(f"*Created by SDLC Agentic - {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    body = "\n".join(body_parts)

    # Build labels
    labels = ['sdlc:auto', 'type:task']
    labels.append(f"phase:4")  # Implementation phase

    # Add custom labels from task
    if 'labels' in task and task['labels']:
        labels.extend(task['labels'])

    # Priority label
    priority = task.get('priority', 'medium')
    if priority in ['critical', 'high', 'medium', 'low']:
        labels.append(f"priority:{priority}")

    labels_str = ",".join(labels)

    # Create issue using gh CLI
    cmd = f'gh issue create --title "{title}" --body-file - --label "{labels_str}"'

    output = run_command(cmd, input_text=body)

    if output:
        # Extract issue number from URL
        issue_url = output
        issue_number = issue_url.split('/')[-1]
        print(f"✓ Created issue #{issue_number}: {title}")

        # Skip adding to project for now (causing issues)
        # add_to_project(issue_number, project_number)

        return issue_number
    else:
        print(f"✗ Failed to create issue: {title}", file=sys.stderr)
        return None

def add_to_project(issue_number, project_number):
    """Add issue to GitHub Project V2."""
    # Get project ID
    cmd = f'gh project item-add {project_number} --owner @me --url "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/issues/{issue_number}"'
    result = run_command(cmd)
    if result:
        print(f"  → Added to Project #{project_number}")
    else:
        print(f"  ⚠ Failed to add to project", file=sys.stderr)

def process_task_breakdown(yaml_path, project_number):
    """Process task breakdown YAML and create issues."""
    print(f"Reading task breakdown from: {yaml_path}")

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    task_breakdown = data['task_breakdown']
    total_tasks = task_breakdown['metadata']['total_tasks']

    print(f"\nTotal tasks to create: {total_tasks}")
    print(f"Project number: {project_number}")
    print(f"\nStarting issue creation...\n")

    created_count = 0
    failed_count = 0

    # Process Sprint 0
    if 'sprint_0_infrastructure' in task_breakdown:
        sprint_0 = task_breakdown['sprint_0_infrastructure']
        print(f"\n=== {sprint_0['name']} ===")
        for task in sprint_0.get('tasks', []):
            issue_num = create_issue(task, "Infrastructure Setup", 0, project_number)
            if issue_num:
                created_count += 1
            else:
                failed_count += 1
            time.sleep(0.5)  # Rate limiting

    # Process EPICs - corrected structure
    epic_sections = [
        ('epic_001_tasks', 'EPIC-001: Ingestão de Dados', 1),
        ('epic_002_tasks', 'EPIC-002: Métricas de Volatilidade', 2),
        ('epic_003_tasks', 'EPIC-003: Sistema de Alertas', 3),
        ('epic_004_tasks', 'EPIC-004: Dashboard UI', 4),
        ('epic_005_tasks', 'EPIC-005: Notificações', 5)
    ]

    for section_key, epic_name, default_sprint in epic_sections:
        if section_key in task_breakdown:
            epic_data = task_breakdown[section_key]
            print(f"\n=== {epic_name} ===")

            # Epic data contains stories (story_001_tasks, story_002_tasks, etc.)
            for key, value in epic_data.items():
                if not key.startswith('story_'):
                    continue  # Skip metadata keys

                story_data = value
                if isinstance(story_data, dict) and 'tasks' in story_data:
                    tasks = story_data['tasks']
                    story_title = story_data.get('story_title', key)
                    print(f"  Story: {story_title}")

                    for task in tasks:
                        sprint_num = task.get('assigned_sprint', default_sprint)
                        issue_num = create_issue(task, epic_name, sprint_num, project_number)
                        if issue_num:
                            created_count += 1
                        else:
                            failed_count += 1
                        time.sleep(0.5)  # Rate limiting

    # Process Sprint 6 Polish
    if 'sprint_6_polish' in task_breakdown:
        sprint_6 = task_breakdown['sprint_6_polish']
        print(f"\n=== {sprint_6.get('name', 'Sprint 6 - Polish')} ===")
        tasks = sprint_6.get('tasks', [])
        for task in tasks:
            issue_num = create_issue(task, "Polish & QA", 6, project_number)
            if issue_num:
                created_count += 1
            else:
                failed_count += 1
            time.sleep(0.5)  # Rate limiting

    # Summary
    print("\n" + "="*60)
    print(f"Issue Creation Summary")
    print("="*60)
    print(f"✓ Successfully created: {created_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total: {created_count + failed_count}/{total_tasks}")
    print("="*60)

    return created_count, failed_count

def main():
    if len(sys.argv) < 3:
        print("Usage: bulk_create_issues.py <task-breakdown.yml> <project-number>")
        sys.exit(1)

    yaml_path = sys.argv[1]
    project_number = sys.argv[2]

    if not Path(yaml_path).exists():
        print(f"Error: File not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    # Check gh CLI is available
    if not run_command("gh --version"):
        print("Error: GitHub CLI (gh) not found. Please install it.", file=sys.stderr)
        sys.exit(1)

    # Check authentication
    if not run_command("gh auth status"):
        print("Error: Not authenticated with GitHub. Run 'gh auth login'", file=sys.stderr)
        sys.exit(1)

    created, failed = process_task_breakdown(yaml_path, project_number)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
