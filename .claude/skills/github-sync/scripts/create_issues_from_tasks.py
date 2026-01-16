#!/usr/bin/env python3
"""
Create GitHub Issues from Tasks - Cria issues automaticamente das tasks do planejamento.

Usage:
    python create_issues_from_tasks.py [--assign-copilot] [--project-id ID]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


def find_project_manifest() -> Optional[Path]:
    """Encontra o manifest do projeto atual."""
    project_root = Path.cwd()
    projects_dir = project_root / ".agentic_sdlc" / "projects"

    # Tentar current.json symlink
    current_json = projects_dir / "current.json"
    if current_json.exists():
        with open(current_json) as f:
            data = json.load(f)
            return projects_dir / data["project_id"] / "manifest.json"

    # Buscar manifest mais recente
    manifests = list(projects_dir.glob("*/manifest.json"))
    if manifests:
        return max(manifests, key=lambda p: p.stat().st_mtime)

    return None


def load_project_manifest(manifest_path: Path) -> Dict:
    """Carrega manifest do projeto."""
    with open(manifest_path) as f:
        return json.load(f)


def find_tasks_file(project_id: str) -> Optional[Path]:
    """Encontra arquivo tasks.md do projeto."""
    project_root = Path.cwd()
    tasks_path = project_root / ".agentic_sdlc" / "projects" / project_id / "tasks" / "tasks.md"

    if tasks_path.exists():
        return tasks_path

    return None


def parse_tasks(tasks_path: Path) -> List[Dict]:
    """Parse tasks.md e extrai lista de tasks estruturadas."""
    tasks = []

    with open(tasks_path) as f:
        content = f.read()

    # Regex para encontrar tasks no formato TASK-XXX
    task_pattern = re.compile(
        r'(?:^|\n)(?:##\s+)?(?P<id>TASK-\d{3}):?\s+(?P<title>[^\n]+)'
        r'(?:\n(?P<body>(?:(?!TASK-\d{3}).)+))?',
        re.MULTILINE | re.DOTALL
    )

    for match in task_pattern.finditer(content):
        task_id = match.group('id')
        title = match.group('title').strip()
        body = match.group('body') or ""

        # Extrair metadados do body
        priority = "medium"
        story_points = 3
        sprint = 1

        if 'critical' in body.lower() or 'alta' in body.lower():
            priority = "high"
        if 'story points:' in body.lower():
            points_match = re.search(r'story points?:\s*(\d+)', body, re.IGNORECASE)
            if points_match:
                story_points = int(points_match.group(1))
        if 'sprint' in body.lower():
            sprint_match = re.search(r'sprint\s*(\d+)', body, re.IGNORECASE)
            if sprint_match:
                sprint = int(sprint_match.group(1))

        tasks.append({
            'id': task_id,
            'title': f"[{task_id}] {title}",
            'body': body.strip(),
            'priority': priority,
            'story_points': story_points,
            'sprint': sprint
        })

    return tasks


def create_github_issue(
    task: Dict,
    milestone: str,
    project_number: int,
    assign_copilot: bool = False
) -> Optional[str]:
    """Cria GitHub issue para a task."""

    # Criar labels
    labels = [
        "phase:4",  # Planning phase
        f"priority:{task['priority']}",
        "type:task"
    ]

    # Criar issue via gh CLI
    cmd = [
        "gh", "issue", "create",
        "--title", task['title'],
        "--body", task['body'] or f"Implementar {task['title']}",
        "--label", ",".join(labels),
        "--milestone", milestone
    ]

    if assign_copilot:
        cmd.extend(["--assignee", "@copilot"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Extrair URL da issue criada
        issue_url = result.stdout.strip()
        print(f"✓ Issue criada: {task['id']} → {issue_url}")

        # Adicionar issue ao Project V2
        add_to_project(issue_url, project_number)

        return issue_url

    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao criar issue {task['id']}: {e.stderr}", file=sys.stderr)
        return None


def add_to_project(issue_url: str, project_number: int):
    """Adiciona issue ao GitHub Project V2."""
    try:
        subprocess.run(
            [
                "python3",
                ".claude/skills/github-projects/scripts/project_manager.py",
                "add-item",
                "--project-number", str(project_number),
                "--issue-url", issue_url
            ],
            check=True,
            capture_output=True
        )
        print(f"  → Adicionada ao Project #{project_number}")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Falha ao adicionar ao Project: {e.stderr}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Cria GitHub issues das tasks")
    parser.add_argument("--assign-copilot", action="store_true", help="Atribuir issues ao @copilot")
    parser.add_argument("--project-id", help="ID do projeto (auto-detecta se omitido)")
    args = parser.parse_args()

    # Encontrar manifest
    manifest_path = find_project_manifest()
    if not manifest_path:
        print("✗ Nenhum projeto encontrado em .agentic_sdlc/projects/", file=sys.stderr)
        return 1

    # Carregar projeto
    project = load_project_manifest(manifest_path)
    project_id = args.project_id or project['project_id']

    # Verificar se tem GitHub info
    if 'github' not in project:
        print("✗ Projeto não tem integração GitHub configurada", file=sys.stderr)
        return 1

    milestone = project['github']['milestone']
    project_number = project['github']['project_number']

    # Encontrar tasks.md
    tasks_path = find_tasks_file(project_id)
    if not tasks_path:
        print(f"✗ Arquivo tasks.md não encontrado para projeto {project_id}", file=sys.stderr)
        return 1

    # Parse tasks
    tasks = parse_tasks(tasks_path)
    if not tasks:
        print("✗ Nenhuma task encontrada em tasks.md", file=sys.stderr)
        return 1

    print(f"\n📋 Criando {len(tasks)} issues no GitHub...")
    print(f"   Project: #{project_number}")
    print(f"   Milestone: {milestone}")
    print(f"   Assign to Copilot: {'Yes' if args.assign_copilot else 'No'}\n")

    # Criar issues
    created_count = 0
    for task in tasks:
        issue_url = create_github_issue(task, milestone, project_number, args.assign_copilot)
        if issue_url:
            created_count += 1

    print(f"\n✓ {created_count}/{len(tasks)} issues criadas com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
