#!/usr/bin/env python3
"""
Issue Sync - Gerencia issues com integracao SDLC no GitHub.

Usage:
    python issue_sync.py create --title "[TASK-001] Feature" --body "Descricao" --phase 5 --type task
    python issue_sync.py update --number 123 --phase 6
    python issue_sync.py sync-task --task-path .agentic_sdlc/projects/xxx/tasks/task-001.yml
    python issue_sync.py find --title "[TASK-001]"
    python issue_sync.py list --phase 5
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Issue:
    """Representa uma issue do GitHub."""
    number: int
    title: str
    body: str
    state: str
    labels: list[str]
    milestone: Optional[str]
    html_url: str
    assignees: list[str]


def run_gh_command(args: list[str]) -> subprocess.CompletedProcess:
    """Executa comando gh e retorna resultado."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except FileNotFoundError:
        print("Erro: GitHub CLI (gh) nao encontrado.", file=sys.stderr)
        sys.exit(1)


def get_repo_info() -> tuple[str, str]:
    """Retorna owner e repo do repositorio atual."""
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    if result.returncode != 0:
        print("Erro: Nao foi possivel detectar repositorio.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def build_labels(phase: Optional[int] = None, complexity: Optional[int] = None, item_type: Optional[str] = None) -> list[str]:
    """Constroi lista de labels SDLC."""
    labels = ["sdlc:auto"]

    if phase is not None and 0 <= phase <= 8:
        labels.append(f"phase:{phase}")

    if complexity is not None and 0 <= complexity <= 3:
        labels.append(f"complexity:{complexity}")

    if item_type and item_type in ["story", "task", "epic"]:
        labels.append(f"type:{item_type}")

    return labels


def create_issue(
    title: str,
    body: str,
    phase: Optional[int] = None,
    complexity: Optional[int] = None,
    item_type: Optional[str] = None,
    milestone: Optional[str] = None,
    assignee: Optional[str] = None,
    project_number: Optional[int] = None
) -> Optional[Issue]:
    """Cria uma nova issue com labels SDLC."""
    labels = build_labels(phase, complexity, item_type)

    # Construir comando
    args = ["issue", "create", "--title", title, "--body", body]

    # Adicionar labels
    if labels:
        args.extend(["--label", ",".join(labels)])

    # Adicionar milestone
    if milestone:
        args.extend(["--milestone", milestone])

    # Adicionar assignee
    if assignee:
        args.extend(["--assignee", assignee])

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao criar issue: {result.stderr}", file=sys.stderr)
        return None

    # Extrair URL da issue criada
    issue_url = result.stdout.strip()
    print(f"Issue criada: {issue_url}")

    # Se project_number fornecido, adicionar ao project
    if project_number:
        add_to_project(issue_url, project_number)

    # Buscar issue criada para retornar objeto completo
    issue_number = int(issue_url.split("/")[-1])
    return get_issue_by_number(issue_number)


def update_issue(
    number: int,
    phase: Optional[int] = None,
    state: Optional[str] = None,
    milestone: Optional[str] = None,
    add_labels: Optional[list[str]] = None,
    remove_labels: Optional[list[str]] = None
) -> bool:
    """Atualiza uma issue existente."""
    args = ["issue", "edit", str(number)]

    # Atualizar estado
    if state:
        if state == "closed":
            args.append("--close")
        elif state == "open":
            args.append("--reopen")

    # Atualizar milestone
    if milestone:
        args.extend(["--milestone", milestone])

    # Adicionar labels
    labels_to_add = list(add_labels) if add_labels else []
    if phase is not None:
        # Primeiro remover label de fase anterior
        current = get_issue_by_number(number)
        if current:
            for label in current.labels:
                if label.startswith("phase:"):
                    if not remove_labels:
                        remove_labels = []
                    remove_labels.append(label)
        labels_to_add.append(f"phase:{phase}")

    if labels_to_add:
        args.extend(["--add-label", ",".join(labels_to_add)])

    # Remover labels
    if remove_labels:
        args.extend(["--remove-label", ",".join(remove_labels)])

    result = run_gh_command(args)

    if result.returncode != 0:
        print(f"Erro ao atualizar issue: {result.stderr}", file=sys.stderr)
        return False

    print(f"Issue #{number} atualizada com sucesso.")
    return True


def get_issue_by_number(number: int) -> Optional[Issue]:
    """Busca issue por numero."""
    result = run_gh_command([
        "issue", "view", str(number),
        "--json", "number,title,body,state,labels,milestone,url,assignees"
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        return Issue(
            number=data["number"],
            title=data["title"],
            body=data.get("body", ""),
            state=data["state"],
            labels=[l["name"] for l in data.get("labels", [])],
            milestone=data.get("milestone", {}).get("title") if data.get("milestone") else None,
            html_url=data["url"],
            assignees=[a["login"] for a in data.get("assignees", [])]
        )
    except (json.JSONDecodeError, KeyError):
        return None


def find_issue_by_title(title: str) -> Optional[Issue]:
    """Busca issue por titulo (busca parcial)."""
    result = run_gh_command([
        "issue", "list",
        "--search", f'"{title}" in:title',
        "--json", "number,title,body,state,labels,milestone,url,assignees",
        "--limit", "10"
    ])

    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        for item in data:
            if title.lower() in item["title"].lower():
                return Issue(
                    number=item["number"],
                    title=item["title"],
                    body=item.get("body", ""),
                    state=item["state"],
                    labels=[l["name"] for l in item.get("labels", [])],
                    milestone=item.get("milestone", {}).get("title") if item.get("milestone") else None,
                    html_url=item["url"],
                    assignees=[a["login"] for a in item.get("assignees", [])]
                )
        return None
    except (json.JSONDecodeError, KeyError):
        return None


def list_issues(
    phase: Optional[int] = None,
    state: str = "open",
    milestone: Optional[str] = None,
    limit: int = 50
) -> list[Issue]:
    """Lista issues filtradas."""
    args = ["issue", "list", "--state", state, "--limit", str(limit)]

    # Filtrar por label de fase
    if phase is not None:
        args.extend(["--label", f"phase:{phase}"])

    # Filtrar por milestone
    if milestone:
        args.extend(["--milestone", milestone])

    args.extend(["--json", "number,title,body,state,labels,milestone,url,assignees"])

    result = run_gh_command(args)

    if result.returncode != 0:
        return []

    try:
        data = json.loads(result.stdout)
        return [
            Issue(
                number=item["number"],
                title=item["title"],
                body=item.get("body", ""),
                state=item["state"],
                labels=[l["name"] for l in item.get("labels", [])],
                milestone=item.get("milestone", {}).get("title") if item.get("milestone") else None,
                html_url=item["url"],
                assignees=[a["login"] for a in item.get("assignees", [])]
            )
            for item in data
        ]
    except (json.JSONDecodeError, KeyError):
        return []


def sync_task_to_issue(task_path: str, project_number: Optional[int] = None) -> Optional[Issue]:
    """Converte task YAML em issue do GitHub."""
    path = Path(task_path)
    if not path.exists():
        print(f"Erro: Arquivo nao encontrado: {task_path}", file=sys.stderr)
        return None

    try:
        with open(path) as f:
            task = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Erro ao ler YAML: {e}", file=sys.stderr)
        return None

    # Extrair dados da task
    task_id = task.get("id", path.stem)
    title = f"[{task_id}] {task.get('title', 'Untitled')}"
    description = task.get("description", "")
    acceptance_criteria = task.get("acceptance_criteria", [])
    phase = task.get("phase", 5)
    complexity = task.get("complexity")
    item_type = task.get("type", "task")
    milestone = task.get("sprint")
    assignee = task.get("assignee")

    # Construir body
    body_parts = []
    if description:
        body_parts.append(f"## Descricao\n\n{description}")

    if acceptance_criteria:
        body_parts.append("## Acceptance Criteria\n")
        for ac in acceptance_criteria:
            body_parts.append(f"- [ ] {ac}")

    if task.get("parent"):
        body_parts.append(f"\n## Parent\n\n- Spec: {task.get('parent')}")

    if task.get("dependencies"):
        body_parts.append("\n## Dependencias\n")
        for dep in task.get("dependencies", []):
            body_parts.append(f"- {dep}")

    body_parts.append("\n---\n*Criado automaticamente pelo SDLC Agentico*")
    body = "\n".join(body_parts)

    # Verificar se ja existe
    existing = find_issue_by_title(f"[{task_id}]")
    if existing:
        print(f"Issue para task {task_id} ja existe: #{existing.number}")
        return existing

    # Criar issue
    return create_issue(
        title=title,
        body=body,
        phase=phase,
        complexity=complexity,
        item_type=item_type,
        milestone=milestone,
        assignee=assignee,
        project_number=project_number
    )


def add_to_project(issue_url: str, project_number: int) -> bool:
    """Adiciona issue a um GitHub Project."""
    result = run_gh_command([
        "project", "item-add", str(project_number),
        "--owner", "@me",
        "--url", issue_url
    ])

    if result.returncode != 0:
        print(f"Aviso: Nao foi possivel adicionar ao project: {result.stderr}", file=sys.stderr)
        return False

    print(f"Issue adicionada ao Project #{project_number}")
    return True


def print_issues(issues: list[Issue]):
    """Imprime lista de issues formatada."""
    if not issues:
        print("Nenhuma issue encontrada.")
        return

    print(f"{'#':<6} {'Titulo':<50} {'Estado':<10} {'Fase':<8}")
    print("-" * 80)

    for issue in issues:
        phase = next((l for l in issue.labels if l.startswith("phase:")), "N/A")
        title_short = issue.title[:50] if len(issue.title) > 50 else issue.title
        print(f"{issue.number:<6} {title_short:<50} {issue.state:<10} {phase:<8}")


def print_issue_detail(issue: Issue):
    """Imprime detalhes de uma issue."""
    print(f"Issue #{issue.number}: {issue.title}")
    print(f"  Estado: {issue.state}")
    print(f"  Labels: {', '.join(issue.labels) if issue.labels else 'N/A'}")
    print(f"  Milestone: {issue.milestone or 'N/A'}")
    print(f"  Assignees: {', '.join(issue.assignees) if issue.assignees else 'N/A'}")
    print(f"  URL: {issue.html_url}")


def main():
    parser = argparse.ArgumentParser(
        description="Gerencia issues com integracao SDLC no GitHub"
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Cria issue")
    create_parser.add_argument("--title", "-t", required=True, help="Titulo")
    create_parser.add_argument("--body", "-b", default="", help="Descricao")
    create_parser.add_argument("--body-file", help="Arquivo com descricao")
    create_parser.add_argument("--phase", "-p", type=int, help="Fase SDLC (0-8)")
    create_parser.add_argument("--complexity", "-c", type=int, help="Complexidade (0-3)")
    create_parser.add_argument("--type", dest="item_type", choices=["story", "task", "epic"], help="Tipo")
    create_parser.add_argument("--milestone", "-m", help="Milestone/Sprint")
    create_parser.add_argument("--assignee", "-a", help="Assignee")
    create_parser.add_argument("--project", type=int, help="Numero do Project")

    # update
    update_parser = subparsers.add_parser("update", help="Atualiza issue")
    update_parser.add_argument("--number", "-n", type=int, required=True, help="Numero da issue")
    update_parser.add_argument("--phase", "-p", type=int, help="Nova fase SDLC")
    update_parser.add_argument("--state", "-s", choices=["open", "closed"], help="Estado")
    update_parser.add_argument("--milestone", "-m", help="Milestone")
    update_parser.add_argument("--add-label", action="append", help="Adicionar label")
    update_parser.add_argument("--remove-label", action="append", help="Remover label")

    # list
    list_parser = subparsers.add_parser("list", help="Lista issues")
    list_parser.add_argument("--phase", "-p", type=int, help="Filtrar por fase")
    list_parser.add_argument("--state", "-s", default="open", choices=["open", "closed", "all"])
    list_parser.add_argument("--milestone", "-m", help="Filtrar por milestone")
    list_parser.add_argument("--limit", "-l", type=int, default=50, help="Limite de resultados")

    # find
    find_parser = subparsers.add_parser("find", help="Busca issue por titulo")
    find_parser.add_argument("--title", "-t", required=True, help="Titulo (busca parcial)")

    # sync-task
    sync_parser = subparsers.add_parser("sync-task", help="Sincroniza task YAML para issue")
    sync_parser.add_argument("--task-path", "-t", required=True, help="Caminho do arquivo YAML")
    sync_parser.add_argument("--project", type=int, help="Numero do Project")

    # get
    get_parser = subparsers.add_parser("get", help="Obtem issue por numero")
    get_parser.add_argument("--number", "-n", type=int, required=True, help="Numero da issue")

    args = parser.parse_args()

    if args.action == "create":
        body = args.body
        if args.body_file:
            try:
                with open(args.body_file) as f:
                    body = f.read()
            except IOError as e:
                print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
                return 1

        result = create_issue(
            title=args.title,
            body=body,
            phase=args.phase,
            complexity=args.complexity,
            item_type=args.item_type,
            milestone=args.milestone,
            assignee=args.assignee,
            project_number=args.project
        )
        return 0 if result else 1

    elif args.action == "update":
        return 0 if update_issue(
            number=args.number,
            phase=args.phase,
            state=args.state,
            milestone=args.milestone,
            add_labels=args.add_label,
            remove_labels=args.remove_label
        ) else 1

    elif args.action == "list":
        issues = list_issues(
            phase=args.phase,
            state=args.state,
            milestone=args.milestone,
            limit=args.limit
        )
        print_issues(issues)
        return 0

    elif args.action == "find":
        issue = find_issue_by_title(args.title)
        if issue:
            print_issue_detail(issue)
            return 0
        else:
            print(f"Nenhuma issue encontrada com titulo contendo: {args.title}")
            return 1

    elif args.action == "sync-task":
        result = sync_task_to_issue(args.task_path, args.project)
        return 0 if result else 1

    elif args.action == "get":
        issue = get_issue_by_number(args.number)
        if issue:
            print_issue_detail(issue)
            return 0
        else:
            print(f"Issue #{args.number} nao encontrada.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
